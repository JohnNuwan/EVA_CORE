---
name: onnx-edge-deployment
description: "Déploiement Edge avec ONNX Runtime — conversion PyTorch/TF/Sklearn → ONNX, exécution cross-platform (CPU/GPU/TensorRT/OpenVINO/CoreML), optimisation de graphe, profilage et quantification avancée."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags:
      - onnx
      - onnx-runtime
      - tensorrt
      - openvino
      - coreml
      - quantization
      - model-optimization
      - edge-ai
      - cross-platform
    related_skills:
      - tensorflow-lite-deep-dive
      - nvidia-jetson-deployment
      - model-optimization-edge
      - tinyml-fundamentals
---

# ONNX Edge Deployment

## Vue d'ensemble

ONNX (Open Neural Network Exchange) est le format d'échange universel entre frameworks ML. ONNX Runtime est le moteur d'inférence cross-platform qui exécute ces modèles sur CPU (x86/ARM), GPU (CUDA/TensorRT), NPU (OpenVINO) et Apple Silicon (CoreML).

### Architecture ONNX Runtime Edge

```
┌─────────────────────────────────────────────────────┐
│         Modèle source (PyTorch / TF / Sklearn)       │
├─────────────────────────────────────────────────────┤
│              Conversion ONNX (torch.onnx / tf2onnx)  │
├─────────────────────────────────────────────────────┤
│              ONNX Runtime (cross-platform)            │
├──────┬──────┬──────┬──────┬──────┬──────┬──────────┤
│ CPU  │CUDA  │TRT   │OVINO │CoreML│XNNPACK│ DirectML│
│(MLAS)│(NVIDIA)│(Jetson)│(Intel)│(Apple)│ (ARM) │ (AMD)  │
└──────┴──────┴──────┴──────┴──────┴──────┴──────────┘
```

---

## 1. Conversion vers ONNX

### 1.1 Depuis PyTorch

```python
import torch
import torch.onnx

class ModeleAudio(torch.nn.Module):
    def __init__(self, n_classes: int = 10):
        super().__init__()
        self.conv1 = torch.nn.Conv2d(1, 8, 3, padding=1)
        self.bn1 = torch.nn.BatchNorm2d(8)
        self.conv2 = torch.nn.Conv2d(8, 16, 3, padding=1, stride=2)
        self.bn2 = torch.nn.BatchNorm2d(16)
        self.pool = torch.nn.AdaptiveAvgPool2d(1)
        self.fc = torch.nn.Linear(16, n_classes)
    
    def forward(self, x):
        x = torch.relu(self.bn1(self.conv1(x)))
        x = torch.relu(self.bn2(self.conv2(x)))
        x = self.pool(x).flatten(1)
        return self.fc(x)

model = ModeleAudio()
model.eval()

# Entrée factice
dummy_input = torch.randn(1, 1, 32, 32)

# Export ONNX
torch.onnx.export(
    model,
    dummy_input,
    "audio_model.onnx",
    input_names=["audio_input"],      # noms symboliques
    output_names=["logits"],
    dynamic_axes={                     # axes dynamiques (batch)
        "audio_input": {0: "batch_size"},
        "logits": {0: "batch_size"},
    },
    opset_version=18,                 # ONNX opset 18+ pour meilleur support
    do_constant_folding=True,          # pliage des constantes
    export_params=True,                # exporter les poids
)

# Validation
import onnx
onnx_model = onnx.load("audio_model.onnx")
onnx.checker.check_model(onnx_model)
print(f"ONNX valide : {onnx.helper.printable_graph(onnx_model.graph)}")
```

### 1.2 Depuis TensorFlow / Keras

```bash
# Méthode 1 : tf2onnx (recommandé)
pip install tf2onnx

python3 -m tf2onnx.convert \
    --saved-model ./saved_model \
    --output model.onnx \
    --opset 18 \
    --inputs-as-nchw "input:0" \  # Format NCHW pour GPU
    --fold_const
```

```python
# Méthode 2 : API Python tf2onnx
import tf2onnx
import tensorflow as tf

model = tf.keras.models.load_model("model.h5")
spec = (tf.TensorSpec((None, 32, 32, 1), tf.float32, name="input"))

output, _ = tf2onnx.convert.from_keras(
    model, 
    input_signature=[spec],
    opset=18,
)
with open("model.onnx", "wb") as f:
    f.write(output.SerializeToString())
```

### 1.3 Depuis Scikit-learn (modèles classiques)

```python
# Conversion SVM, Random Forest, etc.
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators=100)
rf.fit(X_train, y_train)

initial_type = [("float_input", FloatTensorType([None, X_train.shape[1]]))]
onx = convert_sklearn(rf, initial_types=initial_type)

with open("rf_model.onnx", "wb") as f:
    f.write(onx.SerializeToString())
```

### 1.4 Bonnes pratiques de conversion

```python
# 1. Forcer le format NCHW (meilleur perf GPU)
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    opset_version=18,
)

# 2. Simplifier le graphe ONNX
# pip install onnx-simplifier
import onnxsim
model_simp, check = onnxsim.simplify("model.onnx")
assert check, "Échec de la simplification"
onnx.save(model_simp, "model_simplified.onnx")
print("Modèle simplifié avec succès")

# 3. Supprimer les noeuds Identity (inutiles)
import onnx
from onnx import optimizer
optimized = optimizer.optimize(
    onnx.load("model.onnx"),
    ["eliminate_deadend", "eliminate_identity", "fuse_consecutive_reshape"]
)
```

---

## 2. ONNX Runtime — Exécution

### 2.1 Sessions pour différentes plateformes

```python
import onnxruntime as ort
import numpy as np

class SessionONNX:
    """Gestionnaire de sessions ONNX Runtime cross-platform."""
    
    def __init__(self, model_path: str, provider: str = "cpu"):
        self.model_path = model_path
        self.provider = provider
        self.session = self._creer_session()
        self._analyser_entrees_sorties()
    
    def _creer_session(self) -> ort.InferenceSession:
        """Crée une session avec le provider spécifié."""
        providers = self._mapper_providers()
        options = ort.SessionOptions()
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        options.enable_pattern_optimization = True
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        options.intra_op_num_threads = 4
        options.inter_op_num_threads = 2
        
        return ort.InferenceSession(self.model_path, options, providers=providers)
    
    def _mapper_providers(self) -> list:
        """Mapper du nom de provider vers la configuration ONNX."""
        mapping = {
            "cpu": ["CPUExecutionProvider"],
            "cuda": [
                ("CUDAExecutionProvider", {
                    "device_id": 0,
                    "arena_extend_strategy": "kNextPowerOfTwo",
                    "cuda_mem_limit": 4 * 1024 * 1024 * 1024,  # 4 GB
                    "do_copy_in_default_stream": True,
                }),
                "CPUExecutionProvider",  # fallback
            ],
            "tensorrt": [
                ("TensorrtExecutionProvider", {
                    "device_id": 0,
                    "trt_max_workspace_size": 1 * 1024 * 1024 * 1024,  # 1 GB
                    "trt_fp16_enable": True,
                    "trt_int8_enable": False,
                    "trt_engine_cache_enable": True,
                    "trt_engine_cache_path": "/tmp/trt_cache",
                }),
                "CUDAExecutionProvider",
                "CPUExecutionProvider",
            ],
            "openvino": [
                ("OpenVINOExecutionProvider", {
                    "device_type": "CPU_FP32",  # ou GPU, MYRIAD
                }),
                "CPUExecutionProvider",
            ],
            "coreml": [
                ("CoreMLExecutionProvider", {
                    "compute_precision": "float16",
                }),
            ],
            "xnnpack": [
                ("XnnpackExecutionProvider", {}),
                "CPUExecutionProvider",
            ],
            "directml": [
                ("DmlExecutionProvider", {
                    "device_id": 0,
                    "disable_metacommands": False,
                }),
            ],
        }
        return mapping.get(self.provider, mapping["cpu"])
    
    def _analyser_entrees_sorties(self):
        """Analyse les entrées/sorties du modèle."""
        self.inputs = {
            i.name: {
                "shape": i.shape,
                "type": i.type,
            }
            for i in self.session.get_inputs()
        }
        self.outputs = {
            o.name: {
                "shape": o.shape,
                "type": o.type,
            }
            for o in self.session.get_outputs()
        }
    
    def inferer(self, inputs: dict) -> dict:
        """Exécute l'inférence."""
        # Validation des entrées
        for name, tensor in inputs.items():
            assert name in self.inputs, f"Entrée inconnue : {name}"
            if isinstance(tensor, np.ndarray):
                inputs[name] = tensor.astype(np.float32)
        
        # Inférence
        outputs = self.session.run(
            list(self.outputs.keys()),
            inputs,
        )
        return dict(zip(self.outputs.keys(), outputs))
    
    def benchmark(self, iterations: int = 100, warmup: int = 10) -> dict:
        """Benchmark de l'inférence."""
        import time
        
        # Entrée factice
        dummy = {
            name: np.random.randn(*info["shape"]).astype(np.float32)
            for name, info in self.inputs.items()
        }
        
        # Warmup
        for _ in range(warmup):
            self.session.run(list(self.outputs.keys()), dummy)
        
        # Mesure
        latences = []
        for _ in range(iterations):
            start = time.perf_counter()
            self.session.run(list(self.outputs.keys()), dummy)
            latences.append((time.perf_counter() - start) * 1000)
        
        return {
            "provider": self.provider,
            "latence_moyenne_ms": float(np.mean(latences)),
            "latence_p50_ms": float(np.percentile(latences, 50)),
            "latence_p99_ms": float(np.percentile(latences, 99)),
            "fps": 1000 / float(np.mean(latences)),
        }


# Utilisation :
session = SessionONNX("model.onnx", provider="cuda")
resultats = session.inferer({"audio_input": np.random.randn(1, 1, 32, 32)})
bench = session.benchmark(iterations=150)
print(f"FPS ({session.provider}) : {bench['fps']:.1f}")
```

### 2.2 Benchmark multi-provider

```python
def benchmark_tous_providers(model_path: str) -> dict:
    """Compare les performances de tous les providers disponibles."""
    import onnxruntime as ort
    
    providers_disponibles = ort.get_available_providers()
    print(f"Providers disponibles : {providers_disponibles}")
    
    resultats = {}
    for provider in providers_disponibles:
        try:
            session = SessionONNX(model_path, provider=provider.replace("ExecutionProvider", "").lower())
            bench = session.benchmark(iterations=50)
            resultats[provider] = bench
        except Exception as e:
            resultats[provider] = {"erreur": str(e)}
    
    return resultats
```

### 2.3 Optimisation des sessions

```python
# SessionOptions avancées
options = ort.SessionOptions()

# Niveau d'optimisation
options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED

# Optimisation spécifique
options.optimized_model_filepath = "model_optimized.onnx"

# Configuration mémoire
options.enable_cpu_mem_arena = True
options.enable_mem_reuse = True

# Parallélisme
options.intra_op_num_threads = 4    # threads par op
options.inter_op_num_threads = 2    # ops parallèles
options.execution_mode = ort.ExecutionMode.ORT_PARALLEL

# Logging
options.log_severity_level = 1  # 0=INFO, 1=WARN, 2=ERROR
options.log_verbosity_level = 0
```

---

## 3. Optimisation de Modèle ONNX

### 3.1 Simplification de graphe

```bash
# onnx-simplifier : élimine les noeuds superflus
pip install onnx-simplifier

python3 -m onnxsim input.onnx output_simplified.onnx \
    --skip-optimization \
    --check-n 3  # vérifier sur 3 échantillons
```

```python
# Simplification avancée
import onnx
from onnx import optimizer, shape_inference

# Inférence de formes (resolve les shapes dynamiques)
model = onnx.load("model.onnx")
model_inferred = shape_inference.infer_shapes(model)

# Optimisation du graphe
passes = [
    "eliminate_identity",
    "eliminate_deadend",
    "eliminate_nop_dropout",
    "eliminate_nop_cast",
    "eliminate_nop_pad",
    "extract_constant_to_initializer",
    "fuse_consecutive_reshape",
    "fuse_consecutive_concats",
    "fuse_consecutive_squeezes",
    "fuse_matmul_add_bias_into_gemm",
    "fuse_pad_into_conv",
    "fuse_relu_into_conv",
]
optimized = optimizer.optimize(model_inferred, passes)
onnx.save(optimized, "model_optimized.onnx")
```

### 3.2 Quantification ONNX

```python
# ONNX Runtime propose la quantification post-entraînement
from onnxruntime.quantization import quantize_dynamic, quantize_static
from onnxruntime.quantization import QuantType, CalibrationMethod

# Quantification dynamique (poids INT8, activations FP32)
quantize_dynamic(
    "model.onnx",
    "model_quant_dynamic.onnx",
    weight_type=QuantType.QInt8,  # ou QUInt8
    op_types_to_quantize=["MatMul", "Add", "Conv"],
    per_channel=True,
)

# Quantification statique (poids + activations INT8)
# Nécessite un dataset de calibration
from onnxruntime.quantization.calibrate import create_calibrator
from onnxruntime.quantization import CalibrationDataReader

class CalibrationReader(CalibrationDataReader):
    def __init__(self, data: np.ndarray, n_samples: int = 100):
        self.data = data
        self.n_samples = n_samples
        self.iterator = 0
    
    def get_next(self) -> dict:
        if self.iterator >= self.n_samples:
            return None
        batch = self.data[self.iterator:self.iterator + 1]
        self.iterator += 1
        return {"audio_input": batch.astype(np.float32)}

calib_data = CalibrationReader(x_val, n_samples=100)

quantize_static(
    "model.onnx",
    "model_quant_static.onnx",
    calibration_data_reader=calib_data,
    quant_format=QuantType.QInt8,
    per_channel=True,
    activation_type=QuantType.QUInt8,
    weight_type=QuantType.QInt8,
    calibrate_method=CalibrationMethod.MinMax,
    extra_options={
        "ActivationSymmetric": True,
        "WeightSymmetric": True,
        "EnableSubgraph": True,
    },
)
```

### 3.3 Operations fusions spécifiques

```python
# Fusions manuelles possibles dans ONNX Runtime :
# Conv + BatchNorm → Conv (fusionnée)
# Conv + Add + Relu → Conv (fusionnée)
# MatMul + Add → Gemm
# Reshape + Softmax → Softmax (reshape intégré)
# LayerNorm → SimplifyLayerNorm

# Vérifier les fusions appliquées :
session = ort.InferenceSession("model.onnx")
print(f"Nombre de noeuds : {len(session._sess.graph.nodes())}")
```

---

## 4. Déploiement sur Cibles Edge

### 4.1 NVIDIA Jetson (TensorRT)

```python
# TensorRT via ONNX Runtime
session = SessionONNX("model.onnx", provider="tensorrt")

# Ou conversion TensorRT native
import tensorrt as trt

TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

def build_trt_engine(onnx_path: str, engine_path: str, 
                     fp16: bool = True) -> trt.ICudaEngine:
    """Construit un moteur TensorRT depuis ONNX."""
    with trt.Builder(TRT_LOGGER) as builder:
        network_flags = 1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
        
        with builder.create_network(network_flags) as network, \
             trt.OnnxParser(network, TRT_LOGGER) as parser:
            
            # Parser le modèle ONNX
            with open(onnx_path, "rb") as f:
                if not parser.parse(f.read()):
                    for err in range(parser.num_errors):
                        print(parser.get_error(err))
                    raise RuntimeError("Échec du parsing ONNX")
            
            config = builder.create_builder_config()
            config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 30)  # 1 GB
            
            if fp16 and builder.platform_has_fast_fp16:
                config.set_flag(trt.BuilderFlag.FP16)
                print("FP16 activé")
            
            # Optimisation par défaut
            profile = builder.create_optimization_profile()
            input_name = network.get_input(0).name
            input_shape = network.get_input(0).shape
            
            # Réserver un range pour les shapes dynamiques
            profile.set_shape(input_name, 
                            min=(1, *input_shape[1:]),
                            opt=(8, *input_shape[1:]),
                            max=(32, *input_shape[1:]))
            config.add_optimization_profile(profile)
            
            # Build engine
            engine = builder.build_serialized_network(network, config)
            if engine is None:
                raise RuntimeError("Échec du build engine")
            
            with open(engine_path, "wb") as f:
                f.write(engine)
            
            print(f"Engine TensorRT sauvegardé : {engine_path}")
            return engine

# Utilisation
# build_trt_engine("model.onnx", "model.trt", fp16=True)
```

### 4.2 Intel OpenVINO

```python
# OpenVINO : idéal pour CPU Intel et Myriad X (NCS2)

# Conversion vers OpenVINO IR
# pip install openvino-dev
!mo --input_model model.onnx --output_dir ./openvino_ir/ --data_type FP16

# Inférence avec OpenVINO
from openvino.runtime import Core

core = Core()
model = core.read_model("openvino_ir/model.xml")
compiled = core.compile_model(model, "CPU")  # ou GPU, MYRIAD

# Inférence
output = compiled([np.random.randn(1, 1, 32, 32)])
```

### 4.3 Apple CoreML

```python
# CoreML pour Apple Neural Engine (iPhone, Mac M-series)

# Conversion via coremltools
import coremltools as ct

# Depuis ONNX
mlmodel = ct.converters.onnx.convert(
    model="model.onnx",
    minimum_ios_target="16",
    compute_precision=ct.transform.Float16ComputePrecision(),
)

# Depuis PyTorch directement
model = ModeleAudio()
model.eval()
traced = torch.jit.trace(model, torch.randn(1, 1, 32, 32))
mlmodel = ct.convert(
    traced,
    inputs=[ct.TensorType(shape=(1, 1, 32, 32))],
)

mlmodel.save("AudioModel.mlpackage")
```

### 4.4 Qualcomm SNPE / QNN

```bash
# Qualcomm Neural Processing SDK
snpe-onnx-to-dlc --input_model model.onnx --output_model model.dlc

# Conversion pour Adreno GPU
snpe-dlc-quantize --input_dlc model.dlc --input_list calibration_list.txt

# Inférence sur DSP/GPU
snpe-net-run --container model.dlc --input_list input_list.txt --use_dsp
```

---

## 5. Débogage et Validation

### 5.1 Vérification de la conformité ONNX

```python
def valider_modele_onnx(model_path: str) -> dict:
    """Validation approfondie d'un modèle ONNX."""
    import onnx
    import onnxruntime as ort
    
    resultats = {"valide": True, "erreurs": [], "avertissements": []}
    
    # 1. Vérification structurelle
    try:
        model = onnx.load(model_path)
        onnx.checker.check_model(model)
        resultats["valide_structure"] = True
    except Exception as e:
        resultats["valide_structure"] = False
        resultats["erreurs"].append(f"Structure invalide : {e}")
        return resultats
    
    # 2. Version opset
    resultats["opset_version"] = model.opset_import[0].version
    
    # 3. Exécution test
    try:
        session = ort.InferenceSession(model_path)
        input_name = session.get_inputs()[0].name
        dummy = {input_name: np.random.randn(*session.get_inputs()[0].shape).astype(np.float32)}
        session.run(None, dummy)
        resultats["execution_test"] = True
    except Exception as e:
        resultats["execution_test"] = False
        resultats["erreurs"].append(f"Échec exécution : {e}")
    
    # 4. Graphe
    resultats["n_noeuds"] = len(model.graph.node)
    resultats["n_entrees"] = len(model.graph.input)
    resultats["n_sorties"] = len(model.graph.output)
    resultats["poids_totaux_mb"] = sum(
        sum(t.dims) * 4 for t in model.graph.initializer
    ) / (1024 * 1024)
    
    return resultats
```

### 5.2 Comparaison de précision

```python
def comparer_precision(model_onnx_path: str, model_source, 
                       data_test: np.ndarray, n_echantillons: int = 100) -> dict:
    """Compare la précision du modèle ONNX vs modèle source."""
    
    from scipy.special import softmax
    
    session = SessionONNX(model_onnx_path, provider="cpu")
    erreurs = []
    
    for i in range(min(n_echantillons, len(data_test))):
        # Entrée source
        x = data_test[i:i+1]
        
        # Prédiction source
        if hasattr(model_source, 'predict'):
            pred_source = model_source.predict(x)
        else:
            model_source.eval()
            with torch.no_grad():
                pred_source = model_source(torch.from_numpy(x)).numpy()
        
        # Prédiction ONNX
        pred_onnx = session.inferer({"input": x.astype(np.float32)})
        pred_onnx = list(pred_onnx.values())[0]
        
        # Erreur relative
        diff = np.abs(pred_source - pred_onnx)
        erreurs.append(np.mean(diff))
    
    return {
        "erreur_moyenne": float(np.mean(erreurs)),
        "erreur_max": float(np.max(erreurs)),
        "erreur_std": float(np.std(erreurs)),
        "n_echantillons": min(n_echantillons, len(data_test)),
    }
```

---

## 6. Surveillance et Métriques

### 6.1 Métriques de service

```python
class MoniteurONNX:
    """Surveillance des performances d'inférence ONNX."""
    
    def __init__(self):
        self.metrics = {
            "latences": [],
            "debits": [],
            "erreurs": 0,
            "total": 0,
        }
    
    def mesurer(self, session: SessionONNX, entree: dict) -> dict:
        """Mesure avec monitoring."""
        import time
        
        self.metrics["total"] += 1
        start = time.perf_counter()
        
        try:
            sortie = session.inferer(entree)
            latence_ms = (time.perf_counter() - start) * 1000
            self.metrics["latences"].append(latence_ms)
            sortie["latence_ms"] = latence_ms
            return sortie
        except Exception as e:
            self.metrics["erreurs"] += 1
            raise
    
    def rapport(self) -> dict:
        """Rapport des métriques."""
        if not self.metrics["latences"]:
            return {"status": "pas_de_donnees"}
        
        l = self.metrics["latences"]
        return {
            "total_requetes": self.metrics["total"],
            "taux_erreur": self.metrics["erreurs"] / max(1, self.metrics["total"]) * 100,
            "latence_moyenne_ms": float(np.mean(l)),
            "p50_ms": float(np.percentile(l, 50)),
            "p90_ms": float(np.percentile(l, 90)),
            "p99_ms": float(np.percentile(l, 99)),
            "debit_requetes_sec": 1000 / float(np.mean(l)),
        }
```

---

## Pièges Courants

1. **Dynamic axes sans profile TensorRT** : si le modèle a des axes dynamiques, TensorRT nécessite un optimization profile. Définir min/opt/max pour chaque dimension variable.

2. **Opset version trop ancien** : opset < 15 manque de support pour certaines ops modernes (LayerNorm, Softmax avec axes). Utiliser opset 18+.

3. **Provider fallback silencieux** : si le provider sélectionné n'est pas disponible, ONNX Runtime tombe sur CPU sans avertissement clair. Vérifier avec `ort.get_available_providers()`.

4. **Fusion BatchNorm manquée** : BatchNorm ne se fusionne pas avec Conv si l'opérateur est défini indépendamment dans le graphe. Activer `do_constant_folding=True` à l'export.

5. **Quantification statique sans calibration** : la quantification statique sans calibration adaptée dégrade la précision de 5-15%. Utiliser un dataset de calibration représentatif.

6. **TensorRT engine caching** : la mise en cache des engines TensorRT est essentielle (le build prend 5-30 min). Activer `trt_engine_cache_enable=True`.

---

## Références

- **ONNX Runtime** : https://onnxruntime.ai/
- **ONNX Converter** : https://github.com/onnx/onnx
- **tf2onnx** : https://github.com/onnx/tensorflow-onnx
- **skl2onnx** : https://github.com/onnx/sklearn-onnx
- **onnx-simplifier** : https://github.com/daquexian/onnx-simplifier
- **TensorRT** : https://developer.nvidia.com/tensorrt
- **OpenVINO** : https://docs.openvino.ai/
- **CoreML** : https://coremltools.readme.io/
- **OnnxRuntime Quantization** : https://onnxruntime.ai/docs/performance/quantization.html
