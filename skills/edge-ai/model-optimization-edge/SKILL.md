---
name: model-optimization-edge
description: "Optimisation de modèles pour le déploiement Edge — pruning structurel et non-structuré, quantification-aware training (QAT), clustering de poids, distillation de connaissances, NAS (Neural Architecture Search) pour small models, TensorFlow Model Optimization Toolkit, compilateurs hardware."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags:
      - model-optimization
      - pruning
      - quantization-aware-training
      - qat
      - distillation
      - nas
      - weight-clustering
      - tensorflow-model-optimization
      - edge-ai
    related_skills:
      - tinyml-fundamentals
      - tensorflow-lite-deep-dive
      - onnx-edge-deployment
      - nvidia-jetson-deployment
---

# Optimisation de Modèles pour Edge

## Vue d'ensemble

L'optimisation de modèles pour le déploiement Edge combine **pruning** (élagage), **quantification**, **distillation** et **NAS** (Neural Architecture Search) pour produire des modèles ultra-légers sans sacrifier la précision. Contrairement à la quantification post-entraînement simple, ces techniques sont intégrées dans le cycle d'entraînement.

### Stratégies d'optimisation

```
┌──────────────────────────────────────────────────────────┐
│                    Modèle original (FP32)                 │
├──────────────────────────────────────────────────────────┤
│      Combinaison des techniques d'optimisation :          │
│                                                            │
│  Pruning          QAT           Distillation     NAS      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌────┐   │
│  │ Retirer   │  │ Simuler   │  │ Student      │  │Cher│   │
│  │ poids     │  │ INT8      │  │ apprend de   │  │cher│   │
│  │ inutiles  │  │ pendant   │  │ Teacher      │  │arch│   │
│  │           │  │ training  │  │ (modèle plus │  │    │   │
│  │           │  │           │  │  petit)      │  │    │   │
│  └──────────┘  └──────────┘  └──────────────┘  └────┘   │
│        │              │              │              │      │
│        ▼              ▼              ▼              ▼      │
│  ┌──────────────────────────────────────────────────────┐ │
│  │           Modèle optimisé (INT8, sparse, petit)      │ │
│  │           TFLite / ONNX / TensorRT                   │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### Gains typiques

| Technique | Réduction taille | Perte précision | Effort |
|:----------|:--------------:|:--------------:|:------:|
| Pruning 50% non-structuré | 50% (sparse) | < 1% | Faible |
| Pruning 80% structuré | 80% | 2-5% | Moyen |
| QAT INT8 | 75% | 1-3% | Moyen |
| Clustering (16 clusters) | 93% | 2-5% | Faible |
| Distillation (4× plus petit) | 75% | 3-8% | Élevé |
| NAS + QAT combiné | 90% | < 5% | Très élevé |

---

## 1. Pruning (Élagage)

### 1.1 Pruning non-structuré (poids individuels)

```python
# Pruning non-structuré : retire des poids individuels (les plus petits)
# Résultat : matrice sparse (50-90% de zéros)
# Compatible hardware : limité (nécessite support sparse)

import tensorflow_model_optimization as tfmot
import tensorflow as tf

# Paramètres de pruning
pruning_params = {
    "pruning_schedule": tfmot.sparsity.keras.PolynomialDecay(
        initial_sparsity=0.30,        # 30% au début
        final_sparsity=0.80,          # 80% à la fin
        begin_step=500,               # commence après 500 steps
        end_step=5000,                # finit à 5000 steps
        frequency=100,                # appliquer tous les 100 steps
    ),
    "block_size": (1, 1),             # pruning par poids individuel
    "block_pooling_type": "AVG",
}

# Appliquer le pruning au modèle
model = tf.keras.Sequential([...])  # modèle existant
model_for_pruning = tfmot.sparsity.keras.prune_low_magnitude(
    model, **pruning_params
)

# Compilation et entraînement
model_for_pruning.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

# Callback de pruning
callbacks = [
    tfmot.sparsity.keras.UpdatePruningStep(),
    tfmot.sparsity.keras.PruningSummaries(log_dir="./logs"),
]

model_for_pruning.fit(
    x_train, y_train,
    batch_size=32,
    epochs=50,
    validation_data=(x_val, y_val),
    callbacks=callbacks,
)

# Export du modèle sparse
final_model = tfmot.sparsity.keras.strip_pruning(model_for_pruning)
final_model.save("model_sparse.h5")
```

### 1.2 Pruning structuré (canaux / filtres)

```python
# Pruning structuré : retire des canaux/filtres entiers
# Compatible hardware : toute plateforme (pas de format sparse)
# Réduction réelle de la taille et de la latence

from tensorflow_model_optimization.python.core.sparsity.keras import pruning_wrapper

# Pruning par filtre (Conv2D)
# Retire les filtres les moins importants d'une couche
# → Réduit le nombre de canaux de sortie

class PruningFiltre(tfmot.sparsity.keras.pruning_schedule.PruningSchedule):
    """Pruning par filtre : toute la norme L1 du filtre."""
    
    def __call__(self, step):
        # Masque les filtres entiers (tous les poids d'un filtre)
        pass

# Application manuelle du pruning structuré
# 1. Calculer l'importance de chaque filtre (norme L1)
# 2. Retirer les filtres les moins importants
# 3. Recréer le modèle avec moins de canaux

def prune_filtres_conv(model, couche_name: str, taux_sparsity: float = 0.5):
    """Prune les filtres d'une couche Conv2D par norme L1."""
    couche = model.get_layer(couche_name)
    poids = couche.get_weights()[0]  # (H, W, C_in, C_out)
    
    # Norme L1 par filtre
    norms = np.sum(np.abs(poids), axis=(0, 1, 2))
    
    # Seuil
    n_filtres = len(norms)
    n_a_garder = int(n_filtres * (1 - taux_sparsity))
    seuil = np.sort(norms)[n_a_garder]
    
    # Masque
    mask = norms >= seuil
    return mask
```

### 1.3 Pruning avec re-apprentissage (fine-tuning)

```python
def pruning_avec_finetuning(model, x_train, y_train, x_val, y_val,
                            sparsity_cible: float = 0.7) -> tf.keras.Model:
    """Pipeline complet : pruning progressif + fine-tuning."""
    
    # Phase 1 : Pruning progressif
    pruning_params = {
        "pruning_schedule": tfmot.sparsity.keras.ConstantSparsity(
            target_sparsity=sparsity_cible,
            begin_step=0,
        ),
    }
    
    model_pruned = tfmot.sparsity.keras.prune_low_magnitude(
        model, **pruning_params
    )
    
    model_pruned.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),  # LR réduit
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    
    callbacks = [
        tfmot.sparsity.keras.UpdatePruningStep(),
        tfmot.sparsity.keras.PruningSummaries(),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=5, restore_best_weights=True
        ),
    ]
    
    history = model_pruned.fit(
        x_train, y_train,
        batch_size=32,
        epochs=30,
        validation_data=(x_val, y_val),
        callbacks=callbacks,
    )
    
    # Phase 2 : Strip pruning → modèle dense sans masques
    final_model = tfmot.sparsity.keras.strip_pruning(model_pruned)
    
    # Phase 3 : Fine-tuning post-pruning
    final_model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.00005),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    
    final_model.fit(
        x_train, y_train,
        batch_size=32,
        epochs=10,
        validation_data=(x_val, y_val),
    )
    
    return final_model
```

---

## 2. QAT — Quantization-Aware Training

### 2.1 Pipeline QAT complet

```python
# QAT : simule la quantification INT8 pendant l'entraînement
# → Le modèle apprend à être robuste à l'arrondi
# → Meilleure précision que PTQ (Post-Training Quantization)

import tensorflow_model_optimization as tfmot
import tensorflow as tf

# Étape 1 : Annoter le modèle pour QAT
qat_model = tfmot.quantization.keras.quantize_model(model)

# Ou annoter sélectivement (mélanger QAT + FP32)
# annotate_model = tfmot.quantization.keras.quantize_annotate_model
# qat_model = tfmot.quantization.keras.quantize_apply(annotate_model)

# Étape 2 : Compiler avec LR réduit
qat_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

# Étape 3 : Fine-tuning QAT (peu d'epochs suffit)
qat_model.fit(
    x_train, y_train,
    batch_size=32,
    epochs=15,  # 10-20 epochs suffisent pour QAT
    validation_data=(x_val, y_val),
)

# Étape 4 : Conversion TFLite (la quantification est déjà simulée)
converter = tf.lite.TFLiteConverter.from_keras_model(qat_model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Quantification INT8
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.int8
converter.inference_output_type = tf.int8
converter.representative_dataset = representative_dataset

tflite_qat = converter.convert()
```

### 2.2 QAT sélectif (par couche)

```python
# QAT sélectif : quantifier certaines couches seulement
# → Préserver la précision sur les couches critiques

# Marquer les couches à ne PAS quantifier
def quantiser_selectif(layer):
    """Applique QAT sauf aux couches spécifiques."""
    
    # Ne pas quantifier les couches avec très peu de paramètres
    if isinstance(layer, tf.keras.layers.Dense) and layer.units <= 16:
        return layer  # Skip QAT
    
    # Ne pas quantifier la première et dernière couche
    if layer.name in ["input_conv", "output_dense"]:
        return layer
    
    return tfmot.quantization.keras.quantize_annotate_layer(layer)

# Appliquer
model = tf.keras.Sequential([...])
annotated_model = tf.keras.models.clone_model(
    model, clone_function=quantiser_selectif
)
qat_model = tfmot.quantization.keras.quantize_apply(annotated_model)
```

### 2.3 Configuration QAT fine

```python
# Personnalisation des paramètres QAT
from tensorflow_model_optimization.python.core.quantization.keras import quantize_emulada

# Configuration par défaut
default_config = {
    "quantize_weights": True,
    "quantize_activations": True,
    "num_bits_weight": 8,
    "num_bits_activation": 8,
    "per_channel_quantization": True,
}

# Pour une réduction plus agressive :
config_agressif = {
    "quantize_weights": True,
    "quantize_activations": True,
    "num_bits_weight": 4,        # Poids en INT4
    "num_bits_activation": 8,
    "per_channel_quantization": True,
}

# Pour préserver la précision des activations :
config_precis = {
    "quantize_weights": True,
    "quantize_activations": True,
    "num_bits_weight": 8,
    "num_bits_activation": 16,    # Activations en FP16
    "per_channel_quantization": True,
}
```

### 2.3 QAT + Pruning combiné

```python
# Combinaison puissante : pruning d'abord, puis QAT

# Phase 1 : Pruning
pruned_model = pruning_avec_finetuning(model, ...)

# Phase 2 : QAT
qat_pruned_model = tfmot.quantization.keras.quantize_model(pruned_model)

# Phase 3 : Conversion
converter = tf.lite.TFLiteConverter.from_keras_model(qat_pruned_model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.representative_dataset = representative_dataset

model_final = converter.convert()
# Résultat : 90%+ de réduction avec < 3% de perte de précision
```

---

## 3. Clustering de Poids

### 3.1 Clustering avec TFMO

```python
# Clustering : partage de poids (weight sharing)
# → Plusieurs poids partagent la même valeur (centroid)
# → Compression via réduction de l'entropie

import tensorflow_model_optimization as tfmot

# Paramètres de clustering
cluster_params = {
    "number_of_clusters": 16,    # 16 valeurs uniques → log2(16) = 4 bits
    "cluster_centroids_init": tfmot.clustering.keras.CentroidInitialization.LINEAR,
}

# Appliquer le clustering
clustered_model = tfmot.clustering.keras.cluster_weights(
    model, **cluster_params
)

clustered_model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

clustered_model.fit(
    x_train, y_train,
    epochs=5,  # Fine-tuning court
    validation_data=(x_val, y_val),
)

# Restaurer le modèle (remplacer par les centroids)
final_model = tfmot.clustering.keras.strip_clustering(clustered_model)
final_model.save("model_clustered.h5")
```

### 3.2 Clustering hiérarchique

```python
# Clustering par couche avec nombre différent de clusters
def clusterer_adaptatif(layer):
    """Applique un nombre de clusters adapté à chaque couche."""
    
    if isinstance(layer, tf.keras.layers.Conv2D):
        # Couches convolutionnelles : plus de clusters
        return tfmot.clustering.keras.cluster_weights(
            layer, number_of_clusters=32
        )
    elif isinstance(layer, tf.keras.layers.Dense) and layer.units > 128:
        # Grosses couches Dense : clustering agressif
        return tfmot.clustering.keras.cluster_weights(
            layer, number_of_clusters=8
        )
    else:
        # Petites couches : pas de clustering (risque de perte)
        return layer
```

---

## 4. Distillation de Connaissances

### 4.1 Distillation classique (logits)

```python
# Distillation : un petit modèle (student) apprend d'un grand modèle (teacher)
# Le student apprend à imiter les logits (soft labels) du teacher

import tensorflow as tf

class Distiller(tf.keras.Model):
    """Distillation de connaissances avec température."""
    
    def __init__(self, student, teacher, temperature=4.0, alpha=0.5):
        super().__init__()
        self.student = student
        self.teacher = teacher
        self.temperature = temperature  # T élevé → distribution plus molle
        self.alpha = alpha  # Poids de la distillation vs perte réelle
    
    def compile(self, optimizer, metrics):
        super().compile(optimizer=optimizer, metrics=metrics)
        self.distillation_loss = tf.keras.losses.KLDivergence()
        self.true_loss = tf.keras.losses.CategoricalCrossentropy()
    
    def train_step(self, data):
        x, y_true = data
        
        with tf.GradientTape() as tape:
            # Prédictions student
            student_logits = self.student(x, training=True)
            
            # Prédictions teacher (sans gradient)
            teacher_logits = self.teacher(x, training=False)
            
            # Loss de distillation (soft)
            soft_student = tf.nn.softmax(student_logits / self.temperature)
            soft_teacher = tf.nn.softmax(teacher_logits / self.temperature)
            d_loss = self.distillation_loss(soft_teacher, soft_student)
            
            # Loss sur les vraies étiquettes (hard)
            c_loss = self.true_loss(y_true, student_logits)
            
            # Loss totale
            loss = self.alpha * d_loss + (1 - self.alpha) * c_loss
        
        # Gradients et update
        gradients = tape.gradient(loss, self.student.trainable_variables)
        self.optimizer.apply_gradients(
            zip(gradients, self.student.trainable_variables)
        )
        
        # Métriques
        self.compiled_metrics.update_state(y_true, 
            tf.nn.softmax(student_logits))
        return {m.name: m.result() for m in self.metrics}
    
    def test_step(self, data):
        x, y_true = data
        student_logits = self.student(x, training=False)
        self.compiled_metrics.update_state(y_true,
            tf.nn.softmax(student_logits))
        return {m.name: m.result() for m in self.metrics}


# Utilisation :
# teacher = tf.keras.models.load_model("large_model.h5")
# student = creer_petit_modele()  # 4× plus petit
#
# distiller = Distiller(student=student, teacher=teacher, temperature=4.0)
# distiller.compile(optimizer="adam", metrics=["accuracy"])
# distiller.fit(x_train, y_train, epochs=30, validation_data=(x_val, y_val))
```

### 4.2 Distillation avec features (Hint Learning)

```python
# Hint Learning : le student apprend aussi les features intermédiaires
# → Meilleure généralisation que la distillation seule

class HintDistiller(tf.keras.Model):
    """Distillation avec features intermédiaires."""
    
    def __init__(self, student, teacher, hint_layer="conv2", beta=0.3):
        super().__init__()
        self.student = student
        self.teacher = teacher
        self.hint_layer = hint_layer
        self.beta = beta  # poids de la perte hint
        
        # Modèle partiel pour extraire les hint
        self.teacher_hint = tf.keras.Model(
            inputs=teacher.input,
            outputs=[teacher.get_layer(hint_layer).output, teacher.output],
        )
        
        # Régresseur pour adapter les dimensions student → teacher
        student_hint_out = student.get_layer(hint_layer).output
        self.regressor = tf.keras.layers.Dense(
            teacher.get_layer(hint_layer).output_shape[-1],
            name="hint_regressor",
        )
    
    def train_step(self, data):
        x, y_true = data
        
        with tf.GradientTape() as tape:
            # Student forward
            student_output = self.student(x, training=True)
            
            # Teacher hints
            teacher_hints, teacher_output = self.teacher_hint(x, training=False)
            student_hint = self.regressor(
                self.student.get_layer(self.hint_layer).output
            )
            
            # Perte hint (MSE des features)
            hint_loss = tf.reduce_mean(
                tf.square(teacher_hints - student_hint)
            )
            
            # Perte distillation
            kd_loss = tf.keras.losses.KLDivergence()(
                tf.nn.softmax(teacher_output / 4.0),
                tf.nn.softmax(student_output / 4.0),
            )
            
            # Perte réelle
            ce_loss = tf.keras.losses.CategoricalCrossentropy()(
                y_true, student_output
            )
            
            loss = ce_loss + kd_loss + self.beta * hint_loss
        
        tape.gradient(loss, self.student.trainable_variables)
        # ... apply_gradients
        
        return {"loss": loss}
```

### 4.3 Distillation pour TinyML (student extrêmement petit)

```python
# Tiny Student : modèle avec < 50K paramètres
# Le teacher peut être un modèle large ou un ensemble de modèles

def creer_tiny_student(n_classes: int = 10) -> tf.keras.Model:
    """Créer un modèle student ultra-léger pour TinyML."""
    
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(32, 32, 1)),
        tf.keras.layers.Conv2D(4, 3, padding="same", strides=2),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        tf.keras.layers.DepthwiseConv2D(3, padding="same"),
        tf.keras.layers.Conv2D(8, 1, padding="same"),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(n_classes),
    ])
    
    print(f"Paramètres student : {model.count_params():,}")
    # ~5,000-20,000 paramètres → 5-20 KB en INT8
    return model

# Teacher plus large
teacher = creer_teacher_modele()  # ~500K params

# Distillation
distiller = Distiller(
    student=creer_tiny_student(),
    teacher=teacher,
    temperature=8.0,  # T plus haut pour tiny student
    alpha=0.7,        # Plus de distillation que de perte réelle
)
```

---

## 5. NAS — Neural Architecture Search

### 5.1 NAS pour modèles Edge

```python
# NAS : recherche automatique de l'architecture optimale
# Contraintes : taille, latence, consommation

# Approches NAS pour Edge :
# 1. Once-for-All (OFA) — entraine un super-réseau, puis le sub-sample
# 2. MNASNet — recherche avec contrainte de latence
# 3. FBNet — NAS différenciable avec budget FLOPs
# 4. ProxylessNAS — architecture directe sans proxy

# Utilisation pratique : architectures déjà optimisées par NAS
# - MobileNetV3 : NAS + NetAdapt
# - EfficientNet-Lite : NAS + scaling compound
# - MixNet : NAS avec mix de convolutions

from tensorflow.keras.applications import MobileNetV3Small

# MobileNetV3Small est déjà le résultat d'un NAS
# avec contrainte de latence pour mobile/edge

model = MobileNetV3Small(
    input_shape=(224, 224, 3),
    alpha=0.75,       # width multiplier (0.35, 0.5, 0.75, 1.0)
    include_top=True,
    weights="imagenet",
    classes=1000,
)

print(f"Paramètres : {model.count_params():,}")
# alpha=0.75 → ~2.5M params (9 MB en FP16)
# alpha=0.35 → ~1.0M params (4 MB en FP16)
```

### 5.2 Recherche d'architecture manuelle (NAS-like)

```python
# Recherche manuelle des hyperparamètres architecturaux
# Objectif : trouver le meilleur rapport précision/taille

def rechercher_architecture_optimum(
    x_train, y_train, x_val, y_val,
    budgets=[(5000, 0.90), (20000, 0.95), (50000, 0.98)]  # (params, accuracy)
) -> tf.keras.Model:
    """Recherche d'architecture avec contrainte de taille."""
    
    for max_params, accuracy_target in budgets:
        print(f"\nRecherche: max {max_params:,} params, target {accuracy_target:.0%}")
        
        # Essayer différentes architectures
        architectures = [
            # (conv_filters, depthwise_filters, n_layers)
            (8, 16, 2),
            (16, 32, 3),
            (8, 32, 2),
            (16, 16, 4),
            (16, 32, 2),
            (32, 64, 2),
        ]
        
        best_acc = 0
        best_config = None
        
        for conv_f, dw_f, n_l in architectures:
            model = creer_modele_personnalise(
                conv_filtres=conv_f,
                dw_filtres=dw_f,
                n_couches=n_l,
            )
            
            if model.count_params() > max_params:
                print(f"  Skip: {model.count_params():,} > {max_params:,}")
                continue
            
            model.compile(
                optimizer="adam",
                loss="sparse_categorical_crossentropy",
                metrics=["accuracy"],
            )
            
            history = model.fit(
                x_train, y_train[:1000],
                epochs=10, validation_data=(x_val[:200], y_val[:200]),
                verbose=0,
            )
            
            val_acc = max(history.history["val_accuracy"])
            
            if val_acc > best_acc:
                best_acc = val_acc
                best_config = (conv_f, dw_f, n_l)
            
            print(f"  Conv={conv_f}, DW={dw_f}, Layers={n_l}: {val_acc:.2%}, {model.count_params():,} params")
        
        print(f"  Meilleur: {best_config} à {best_acc:.2%}")
    
    return best_config
```

---

## 6. Pipeline d'Optimisation Complet

### 6.1 Workflow production Edge

```python
def pipeline_optimisation_complet(model: tf.keras.Model, 
                                  x_train, y_train, x_val, y_val,
                                  sparsity_target: float = 0.6,
                                  n_clusters: int = 16) -> bytes:
    """Pipeline complet : Pruning → Clustering → QAT → TFLite."""
    
    # Phase 1 : Pruning
    print("Phase 1: Pruning...")
    model_pruned = pruning_avec_finetuning(
        model, x_train, y_train, x_val, y_val,
        sparsity_cible=sparsity_target,
    )
    
    # Phase 2 : Clustering
    print("Phase 2: Clustering...")
    clustering_params = {"number_of_clusters": n_clusters}
    model_clustered = tfmot.clustering.keras.cluster_weights(
        model_pruned, **clustering_params
    )
    model_clustered.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    model_clustered.fit(
        x_train, y_train,
        batch_size=32, epochs=5,
        validation_data=(x_val, y_val),
        verbose=0,
    )
    model_clustered = tfmot.clustering.keras.strip_clustering(model_clustered)
    
    # Phase 3 : QAT
    print("Phase 3: QAT...")
    qat_model = tfmot.quantization.keras.quantize_model(model_clustered)
    qat_model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.00005),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    qat_model.fit(
        x_train, y_train,
        batch_size=32, epochs=10,
        validation_data=(x_val, y_val),
        verbose=0,
    )
    
    # Phase 4 : Conversion TFLite
    print("Phase 4: Conversion...")
    converter = tf.lite.TFLiteConverter.from_keras_model(qat_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8
    converter.representative_dataset = lambda: [
        [x_val[i:i+1].astype(np.float32)] for i in range(min(100, len(x_val)))
    ]
    
    tflite_model = converter.convert()
    
    # Rapport
    taille_init = sum(
        np.prod(w.shape) * 4 for w in model.get_weights()
    ) / (1024 * 1024)
    taille_final = len(tflite_model) / (1024 * 1024)
    
    _, acc_init = model.evaluate(x_val, y_val, verbose=0)
    
    interpreter = tf.lite.Interpreter(model_content=tflite_model)
    interpreter.allocate_tensors()
    # Évaluer la précision TFLite
    acc_final = evaluer_tflite(interpreter, x_val, y_val)
    
    print(f"\n=== RÉSULTATS ===")
    print(f"Taille initiale: {taille_init:.2f} MB")
    print(f"Taille finale: {taille_final:.2f} MB")
    print(f"Réduction: {(1 - taille_final/taille_init) * 100:.1f}%")
    print(f"Précision initiale: {acc_init:.2%}")
    print(f"Précision finale: {acc_final:.2%}")
    
    return tflite_model
```

---

## Pièges Courants

1. **Pruning + QAT dans le mauvais ordre** : toujours pruning → QAT, jamais l'inverse. QAT d'un modèle déjà pruné est plus stable.

2. **Température de distillation trop basse** : T < 2 donne des soft labels trop durs (équivalent aux hard labels). T > 8 dilue trop l'information. T=4 est un bon point de départ.

3. **Clustering avec trop peu de clusters** : 2-4 clusters ne capturent pas la diversité des poids (perte > 10%). 16-32 clusters est un bon compromis.

4. **QAT sans fine-tuning suffisant** : QAT avec < 5 epochs peut ne pas converger. 10-20 epochs est recommandé, avec un LR 10× plus faible.

5. **Student trop petit pour la distillation** : si le student a < 1% des paramètres du teacher, la distillation seule ne suffit pas. Ajouter hint learning.

6. **NAS coûteux en compute** : NAS peut nécessiter 100-1000 entraînements. Utiliser des super-réseaux (Once-for-All) ou des modèles déjà NAS-optimisés.

7. **Métriques trompeuses** : la réduction de taille ne reflète pas la réduction de latence. Le pruning non-structuré réduit la taille mais pas la latence (sans hardware sparse). Toujours mesurer les deux.

---

## Références

- **TF Model Optimization** : https://www.tensorflow.org/model_optimization
- **Pruning (Han et al., 2015)** : https://arxiv.org/abs/1506.02626
- **QAT (Jacob et al., 2018)** : https://arxiv.org/abs/1712.05877
- **Distillation (Hinton et al., 2015)** : https://arxiv.org/abs/1503.02531
- **Clustering (Deep Compression)** : https://arxiv.org/abs/1510.00149
- **Once-for-All (OFA)** : https://arxiv.org/abs/1908.05770
- **MobileNetV3** : https://arxiv.org/abs/1905.02244
- **EfficientNet-Lite** : https://arxiv.org/abs/1905.11946
- **MCUNet (TinyML NAS)** : https://arxiv.org/abs/2007.10319
