---
name: tensorflow
description: Guide complet de TensorFlow 2.x / Keras — couches, modèles, callbacks, TF Datasets, GPU, sauvegarde, TF Serving, TF Lite, et bonnes pratiques. En français.

---

# TensorFlow / Keras — Guide Complet (Français)

Framework de deep learning par Google. API Keras intégrée.

---

## 1. Installation

```bash
pip install tensorflow          # CPU
pip install tensorflow[and-cuda] # GPU
```

---

## 2. Tenseurs et Opérations

```python
import tensorflow as tf
import numpy as np

# Création
x = tf.constant([1.0, 2.0, 3.0])
y = tf.zeros((3, 4))
z = tf.ones((2, 3))
a = tf.random.normal((100, 10))
b = tf.range(10)

# Conversion NumPy ↔ TF
np_array = x.numpy()
tf_tensor = tf.convert_to_tensor(np_array)

# Opérations
c = tf.add(a, b)
c = a + b                     # Surcharge Python
d = tf.matmul(a, b)
e = tf.reduce_sum(a)
f = tf.nn.relu(a)

# GPU
with tf.device('/GPU:0'):
    x = tf.random.normal((1000, 1000))

print(tf.config.list_physical_devices('GPU'))
```

---

## 3. Modèle Séquentiel (Keras)

```python
from tensorflow import keras
from tensorflow.keras import layers

# API Séquentielle
model = keras.Sequential([
    layers.Dense(128, activation='relu', input_shape=(784,)),
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(10, activation='softmax'),
])

# Compilation
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-3),
    loss=keras.losses.SparseCategoricalCrossentropy(),
    metrics=['accuracy'],
)

# Résumé
model.summary()

# Entraînement
history = model.fit(
    x_train, y_train,
    batch_size=64,
    epochs=20,
    validation_data=(x_val, y_val),
    callbacks=[
        keras.callbacks.EarlyStopping(patience=5),
        keras.callbacks.ModelCheckpoint('best_model.keras'),
        keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3),
    ],
)

# Évaluation
test_loss, test_acc = model.evaluate(x_test, y_test)

# Prédiction
predictions = model.predict(x_test)
```

---

## 4. API Fonctionnelle

```python
# Modèle multi-entrées / multi-sorties
entree_texte = keras.Input(shape=(100,), name='texte')
entree_image = keras.Input(shape=(64, 64, 3), name='image')

# Branche texte
x1 = layers.Dense(128, activation='relu')(entree_texte)
x1 = layers.Dense(64, activation='relu')(x1)

# Branche image
x2 = layers.Conv2D(32, 3, activation='relu')(entree_image)
x2 = layers.GlobalAveragePooling2D()(x2)
x2 = layers.Dense(64, activation='relu')(x2)

# Fusion
concat = layers.Concatenate()([x1, x2])
sortie = layers.Dense(1, activation='sigmoid')(concat)

model = keras.Model(
    inputs=[entree_texte, entree_image],
    outputs=sortie,
)

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy'],
)

# Entraînement avec entrées multiples
model.fit(
    {'texte': x_texte, 'image': x_image},
    y_train,
    epochs=10,
)
```

---

## 5. Sous-classement (API avancée)

```python
class MonModele(keras.Model):
    """Modèle personnalisé avec boucle d'entraînement."""
    
    def __init__(self, dim_cachee: int = 64) -> None:
        super().__init__()
        self.dense1 = layers.Dense(dim_cachee, activation='relu')
        self.dropout = layers.Dropout(0.3)
        self.dense2 = layers.Dense(10)
    
    def call(self, x: tf.Tensor, training: bool = False) -> tf.Tensor:
        x = self.dense1(x)
        x = self.dropout(x, training=training)
        return self.dense2(x)

# Boucle d'entraînement personnalisée
model = MonModele()
optimizer = keras.optimizers.Adam(1e-3)
loss_fn = keras.losses.SparseCategoricalCrossentropy(from_logits=True)

@tf.function
def train_step(x, y):
    with tf.GradientTape() as tape:
        logits = model(x, training=True)
        loss = loss_fn(y, logits)
    grads = tape.gradient(loss, model.trainable_weights)
    optimizer.apply_gradients(zip(grads, model.trainable_weights))
    return loss

for epoch in range(epochs):
    for x_batch, y_batch in train_dataset:
        loss = train_step(x_batch, y_batch)
```

---

## 6. tf.data (Datasets performants)

```python
# Depuis des tenseurs
dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))

# Pipeline optimisée
dataset = (
    tf.data.Dataset.from_tensor_slices((x_train, y_train))
    .shuffle(buffer_size=10000)
    .batch(64)
    .prefetch(tf.data.AUTOTUNE)
    .cache()                        # Cache en mémoire
)

# Depuis des fichiers
dataset = tf.data.TFRecordDataset(files)
dataset = tf.data.TextLineDataset('fichier.txt')

# Augmentation de données
def augmenter(image, label):
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_brightness(image, 0.2)
    return image, label

dataset = dataset.map(augmenter, num_parallel_calls=tf.data.AUTOTUNE)
```

---

## 7. Callbacks Essentiels

```python
callbacks = [
    # Arrêt anticipé
    keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
    ),
    # Sauvegarde du meilleur modèle
    keras.callbacks.ModelCheckpoint(
        'best.keras',
        monitor='val_accuracy',
        save_best_only=True,
    ),
    # Réduction du LR
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
    ),
    # TensorBoard
    keras.callbacks.TensorBoard(
        log_dir='./logs',
        histogram_freq=1,
    ),
    # CSV logger
    keras.callbacks.CSVLogger('historique.csv'),
]
```

---

## 8. Sauvegarde et Transfert Learning

```python
# Sauvegarde (format natif .keras)
model.save('modele.keras')
model_charge = keras.models.load_model('modele.keras')

# Sauvegarde des poids seulement
model.save_weights('poids.h5')
model.load_weights('poids.h5')

# Transfert learning
base_model = keras.applications.ResNet50(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3),
)
base_model.trainable = False  # Geler les couches

inputs = keras.Input(shape=(224, 224, 3))
x = base_model(inputs, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dense(256, activation='relu')(x)
outputs = layers.Dense(10, activation='softmax')(x)
model = keras.Model(inputs, outputs)

model.compile(optimizer='adam', loss='categorical_crossentropy')
model.fit(train_data, epochs=10)

# Dégeler pour fine-tuning
base_model.trainable = True
model.compile(optimizer=keras.optimizers.Adam(1e-5), loss='...')
model.fit(train_data, epochs=5)
```

---

## 9. Activation de GPU / TPU / Distribué

```python
# Vérifier GPU
tf.config.list_physical_devices('GPU')

# Stratégie multi-GPU
strategy = tf.distribute.MirroredStrategy()

with strategy.scope():
    model = create_model()
    model.compile(...)

# TPU
tpu = tf.distribute.cluster_resolver.TPUClusterResolver()
tf.config.experimental_connect_to_cluster(tpu)
tf.tpu.experimental.initialize_tpu_system(tpu)
strategy = tf.distribute.TPUStrategy(tpu)
```

---

## 10. TensorFlow Serving et Lite

```python
# Export pour TF Serving
model.save('modele/1/')

# TensorFlow Lite (mobile/embedded)
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()
with open('modele.tflite', 'wb') as f:
    f.write(tflite_model)

# TensorFlow.js
# pip install tensorflowjs
# tensorflowjs_converter --input_format keras modele.keras modele_tfjs/
```

---

## Références
- TF Docs : https://www.tensorflow.org/api_docs
- Keras : https://keras.io/
- TFX : https://www.tensorflow.org/tfx