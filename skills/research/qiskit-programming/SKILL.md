---
name: qiskit-programming
description: "Programmation quantique avec IBM Qiskit : installation, circuits, transpilation, exécution sur backends réels et simulateurs, Qiskit Runtime, Primitive API et optimisation."
version: 1.0.0
author: EVA
license: Privée EVA
metadata:
  EVA:
    tags: [qiskit, quantum, ibm, circuit, transpilation, quantum-runtime, primitive, qasm]
    related_skills: [quantum-gates, quantum-computing-fundamentals, quantum-error-correction]
platforms: [linux, macos, windows]
---

# Programmation Quantique avec IBM Qiskit

## Vue d'ensemble

**Qiskit** est le framework open-source d'IBM pour la programmation quantique. Cette compétence couvre l'installation, la construction de circuits, la transpilation, l'exécution sur simulateurs et processeurs réels (via IBM Quantum), Qiskit Runtime, les Primitives (Estimator, Sampler), l'optimisation de circuits et l'intégration avec d'autres frameworks (PennyLane, Q#). Niveau ingénieur.

## Quand l'utiliser

- Construire et exécuter un circuit quantique avec Qiskit.
- Transpiler un circuit pour un backend IBM spécifique (topologie, jeu de portes).
- Utiliser Qiskit Runtime et les Primitives (Estimator, Sampler) pour des workloads hybrides.
- Implémenter un VQE (Variational Quantum Eigensolver) ou un QAOA.
- Analyser les résultats d'exécution et la fidélité.

---

## 1. Installation et Configuration

### 1.1 Installation

```bash
# Dernière version stable (Qiskit 1.x)
pip install qiskit

# Modules additionnels
pip install qiskit-ibm-runtime    # IBM Quantum Runtime
pip install qiskit-aer            # Simulateur haute performance
pip install qiskit-dynamics       # Simulation Hamiltonienne
pip install qiskit-transpiler-service  # Transpilation cloud

# Visualisation
pip install qiskit[visualization]
```

### 1.2 Configuration IBM Quantum

```python
from qiskit_ibm_runtime import QiskitRuntimeService

# Connexion avec token API
service = QiskitRuntimeService(
    channel='ibm_quantum',
    token='votre_token_ibm',
    instance='ibm-q/open/main'
)

# Lister les backends disponibles
service.backends()

# Backend spécifique
backend = service.backend('ibm_brisbane')
print(f"Qubits: {backend.num_qubits}")
print(f"Topologie: {backend.coupling_map}")
print(f"Jeu de portes de base: {backend.basis_gates}")
```

---

## 2. Construction de Circuits

### 2.1 API de base

```python
from qiskit import QuantumCircuit

# Circuit à 3 qubits, 3 bits classiques
qc = QuantumCircuit(3, 3)

# Portes
qc.h(0)              # Hadamard sur q0
qc.cx(0, 1)          # CNOT q0→q1
qc.rz(0.5, 1)        # R_z(0.5) sur q1
qc.measure(0, 0)     # Mesure q0→c0
qc.measure_all()     # Mesure tous les qubits

print(qc.draw())
```

### 2.2 Opérations paramétrées

```python
from qiskit.circuit import Parameter

theta = Parameter('θ')
phi = Parameter('φ')

qc = QuantumCircuit(2)
qc.ry(theta, 0)
qc.rz(phi, 1)
qc.cx(0, 1)

# Binding de paramètres
bound_qc = qc.assign_parameters({theta: 0.5, phi: 1.2})
```

### 2.3 Circuits composites et instructions

```python
from qiskit.circuit import QuantumCircuit, Gate, Instruction

# Définir une sous-routine comme porte personnalisée
sub_qc = QuantumCircuit(2, name='ma_porte')
sub_qc.h(0)
sub_qc.cx(0, 1)
my_gate = sub_qc.to_gate()

# Utilisation
qc = QuantumCircuit(3, 3)
qc.append(my_gate, [0, 1])
qc.append(my_gate.control(), [2, 0, 1])  # Version contrôlée
```

### 2.4 Circuits de base

```python
def ghz_circuit(n: int) -> QuantumCircuit:
    """Prépare |GHZₙ⟩ = (|0⟩⊗ⁿ + |1⟩⊗ⁿ)/√2."""
    qc = QuantumCircuit(n, n)
    qc.h(0)
    for i in range(n-1):
        qc.cx(i, i+1)
    qc.measure(range(n), range(n))
    return qc

def qft_circuit(n: int) -> QuantumCircuit:
    """Transformée de Fourier quantique sur n qubits."""
    qc = QuantumCircuit(n)
    for j in range(n):
        qc.h(j)
        for k in range(j+1, n):
            theta = np.pi / 2**(k - j)
            qc.cp(theta, k, j)
    # Swap finale pour inversion d'ordre
    for i in range(n // 2):
        qc.swap(i, n-i-1)
    return qc
```

---

## 3. Transpilation

### 3.1 Transpileur de base

```python
from qiskit.transpiler import PassManager, PassManagerConfig
from qiskit.transpiler.passes import (
    TrivialLayout, FullAncillaAllocation, 
    EnlargeWithAncilla, Optimize1qGatesDecomposition,
    CXCancellation, CommutationAnalysis, CommutativeCancellation
)
from qiskit import transpile

# Transpilation simple
qc_transpiled = transpile(
    qc,
    backend=backend,
    optimization_level=3,  # 0-3, plus élevé = plus optimisé
    initial_layout=[0, 1, 2],
    seed_transpiler=42,
    scheduling_method='asap'  # 'asap' ou 'alap' pour l'ordonnancement
)

# Pipeline personnalisé
pass_manager = PassManager([
    TrivialLayout(),
    FullAncillaAllocation(),
    EnlargeWithAncilla(),
    Optimize1qGatesDecomposition(basis=['rz', 'sx', 'x']),
    CXCancellation(),
    CommutationAnalysis(),
    CommutativeCancellation(),
])

qc_optimized = pass_manager.run(qc)
```

### 3.2 Analyse post-transpilation

```python
def analyze_transpilation(qc_orig, qc_transpiled):
    """Compare les métriques avant/après transpilation."""
    ops_orig = qc_orig.count_ops()
    ops_trans = qc_transpiled.count_ops()
    return {
        'depth_orig': qc_orig.depth(),
        'depth_trans': qc_transpiled.depth(),
        'gates_orig': qc_orig.size(),
        'gates_trans': qc_transpiled.size(),
        'operations_orig': ops_orig,
        'operations_trans': ops_trans,
        'swaps': ops_trans.get('swap', 0)
    }
```

---

## 4. Exécution et Primitives (Qiskit Runtime)

### 4.1 Sampler (échantillonnage)

```python
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# Transpilation pour le backend
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
isa_circuit = pm.run(qc)

# Exécution
with Session(service=service, backend=backend) as session:
    sampler = Sampler(session=session)
    job = sampler.run([isa_circuit], shots=4096)
    result = job.result()

# Analyse
pub_result = result[0]
counts = pub_result.data.meas.get_counts()
print(f"Counts : {counts}")
```

### 4.2 Estimator (valeur d'espérance)

```python
from qiskit_ibm_runtime import EstimatorV2 as Estimator
from qiskit.quantum_info import SparsePauliOp

# Observable : ZZ sur qubits 0 et 1
observable = SparsePauliOp.from_list([("ZZ", 1.0)])

# Circuit d'essai
qc = QuantumCircuit(2)
qc.ry(0.5, 0)
qc.rx(0.3, 1)
qc.cx(0, 1)

isa_circuit = pm.run(qc)

with Session(service=service, backend=backend) as session:
    estimator = Estimator(session=session)
    job = estimator.run([(isa_circuit, [observable])])
    result = job.result()

print(f"⟨ZZ⟩ = {result[0].data.evs[0]:.6f} ± {result[0].data.stds[0]:.6f}")
```

### 4.3 Sessions et exécution itérative

```python
from qiskit_ibm_runtime import Session, EstimatorV2 as Estimator

# Session : réserve le backend, permet iteration rapide
with Session(service=service, backend='ibm_brisbane') as session:
    estimator = Estimator(session=session)
    
    for theta in np.linspace(0, 2*np.pi, 100):
        bound_qc = circuit.assign_parameters({param: theta})
        isa_qc = pm.run(bound_qc)
        job = estimator.run([(isa_qc, [observable])])
        # Session garde la connexion → execution plus rapide
```

---

## 5. VQE (Variational Quantum Eigensolver)

```python
import numpy as np
from qiskit.circuit.library import EfficientSU2, RealAmplitudes
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime import EstimatorV2 as Estimator, Session
from scipy.optimize import minimize

# Hamiltonien : H₂ moléculaire simplifié
H = SparsePauliOp.from_list([
    ("II", -1.05237),
    ("IZ", 0.39794),
    ("ZI", 0.39794),
    ("ZZ", -0.01128),
    ("XX", 0.18093),
])

# Ansatz variationnel
ansatz = EfficientSU2(2, reps=3, entanglement='linear')
ansatz.measure_all()
params = np.random.rand(ansatz.num_parameters)

def cost_function(params, ansatz, H, backend):
    """Fonction de coût pour VQE."""
    bound_qc = ansatz.assign_parameters(params)
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_qc = pm.run(bound_qc)
    
    with Session(backend=backend) as session:
        estimator = Estimator(session=session)
        job = estimator.run([(isa_qc, [H])])
        result = job.result()
    return result[0].data.evs[0]

# Optimisation
result = minimize(
    cost_function, params,
    args=(ansatz, H, backend),
    method='COBYLA',
    options={'maxiter': 500, 'rhobeg': 0.1}
)
print(f"Énergie optimale : {result.fun:.6f} Ha")
```

---

## 6. Simulateurs Haute Performance

### 6.1 Aer Simulator

```python
from qiskit_aer import AerSimulator

# Simulateur local (supporte le bruit)
simulator = AerSimulator(method='statevector')  # 'density_matrix', 'stabilizer'
result = simulator.run(qc, shots=10000).result()
counts = result.get_counts()

# Simulation bruitée
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime import IBMQ

noise_model = NoiseModel.from_backend(
    service.backend('ibm_brisbane')
)
sim_noise = AerSimulator(noise_model=noise_model)
```

### 6.2 Simulation GPU

```python
# Méthode statevector avec GPU CUDA
sim = AerSimulator(
    method='statevector',
    device='GPU',
    cuStateVec_enable=True,  # NVIDIA cuQuantum
)
```

---

## 7. Optimisation de Circuits

### 7.1 Approximations et pruning

| Technique | Description | Gain typique |
|:---|:---|:---|
| **Commutation** | Réordonnancement pour fusionner des portes adjacentes | 10-20% |
| **Template matching** | Remplacement de patterns par des équivalents plus courts | 15-30% |
| **KAK decomposition** | Décomposition optimale des portes 2-qubits | 40-50% |
| **Gate cancellation** | Annulation de paires inverses (XX, HH, etc.) | 5-15% |

### 7.2 Optimisation du T-count (pour FTQC)

```python
# Le T-count optimal pour un circuit Clifford+T peut être approché
# par des algorithmes de synthèse de circuits utilisant 
# la représentation ZX-calcul ou la phase polynomiale

def optimal_t_count(circuit: QuantumCircuit) -> int:
    """Estimation du T-count minimal possible."""
    # Approche : compter les angles de phase non-Clifford
    params = circuit.parameters
    t_count = 0
    for instruction in circuit.data:
        if instruction.operation.name in ('t', 'tdg'):
            t_count += 1
        elif instruction.operation.name == 'cp':
            angle = float(instruction.operation.params[0])
            if angle % (np.pi/2) != 0:
                t_count += 1
    return t_count
```

---

## 8. Intégration avec PennyLane

```python
import pennylane as qml

# Utiliser PennyLane avec Qiskit comme backend
dev = qml.device('qiskit.aer', wires=2, shots=1000)

@qml.qnode(dev)
def circuit(params):
    qml.RY(params[0], wires=0)
    qml.RX(params[1], wires=1)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))
```

---

## 9. Pièges et Limitations

1. **Version Qiskit :** Qiskit 1.x a changé l'API (notamment Runtime V2). Les tutoriels pré-2024 utilisent souvent l'ancienne API (`qiskit-ibmq-provider` déprécié).
2. **Limites IBM :** 10 minutes de circuit gratuites/mois. Pour des workloads sérieux, un plan payant est nécessaire (Open Plan ≈ 50€/mois).
3. **Goulot d'étranglement transpilation :** La transpilation sur des circuits de 100+ qubits peut prendre des heures sur un ordinateur classique.
4. **Shots insuffisants :** Pour estimer ⟨P⟩ avec précision ε, il faut O(1/ε²) shots. Un observatoire avec variance σ² nécessite shots = σ²/ε².
5. **Qubits factices :** Les backends IBM ont des qubits inactifs ou de qualité médiocre — utilisez `backend.qubit_properties()` pour sélectionner les meilleurs.

---

## Liste de vérification

- [ ] Qiskit 1.x installé avec les modules nécessaires (ibm-runtime, aer).
- [ ] La construction de circuits (QuantumCircuit, gates, parameters) est maîtrisée.
- [ ] La transpilation avec optimisation level 3 est configurée.
- [ ] Les Primitives V2 (Sampler, Estimator) sont utilisées, pas l'ancienne API.
- [ ] Les sessions Runtime sont ouvertes pour les workloads itératifs.
- [ ] Les simulateurs Aer (statevector, noise, GPU) sont disponibles.
- [ ] L'optimisation de circuits (T-count, depth) est appliquée systématiquement.
- [ ] Les limites du plan IBM (10 min/mois) sont respectées.
