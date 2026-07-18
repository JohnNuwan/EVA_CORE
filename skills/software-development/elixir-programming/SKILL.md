---
name: elixir-programming
description: "Programmer en Elixir, utiliser OTP et les outils Mix."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [elixir, otp, mix, nerves, functional-programming, iot, industrial-protocols]
  related_skills: [siemens-scl-generation, rockwell-l5x-generation]
---

# Programmation Elixir et Ingénierie OTP pour l'IoT Industriel

Cette compétence régit l'écriture de code Elixir, la conception d'architectures concurrentes et tolérantes aux pannes avec OTP, et l'intégration d'applications industrielles embarquées via le framework Nerves.

## Quand utiliser cette compétence

Activez cette compétence lorsque l'utilisateur demande :
* De l'aide pour concevoir, implémenter ou déboguer du code Elixir.
* Des explications sur les concepts de programmation fonctionnelle (pattern matching, immutabilité, recursion).
* Des conseils sur l'architecture OTP (GenServer, Supervisor, arbres de supervision).
* L'intégration d'équipements industriels ou de passerelles IoT en Elixir (Modbus/TCP, OPC UA, Nerves).

---

## 1. Fondations Typographiques et Syntaxiques d'Elixir

Elixir est un langage fonctionnel dynamique conçu pour créer des applications scalables et maintenables.

### Concepts clés
* **Immutabilité** : Les données ne peuvent pas être modifiées sur place. Toute transformation produit une nouvelle structure de données.
* **Pattern Matching (Opérateur `=`)** : L'opérateur `=` n'est pas une simple affectation, mais une assertion d'égalité de motifs.
  ```elixir
  {status, result} = {:ok, "Donnée capteur"}
  ```
* **Opérateur Pipe (`|>`)** : Enchaîne les appels de fonctions en passant le résultat de la fonction précédente comme premier argument de la suivante.
  ```elixir
  capteur_id
  |> lire_mesure()
  |> filtrer_bruit()
  |> normaliser_echelle()
  ```
* **Récursion** : Remplace les boucles traditionnelles. Utilisez la récursion terminale (tail-recursion) pour éviter la saturation de la pile.

---

## 2. Outillage standard avec Mix et IEx

Mix est l'outil d'automatisation de build d'Elixir. Il gère la création de projets, la compilation, les tests et la gestion des dépendances.

* **Créer un nouveau projet** :
  ```bash
  mix new mon_app --sup
  ```
  Le drapeau `--sup` configure automatiquement un arbre de supervision de base.
* **Console interactive (IEx)** :
  ```bash
  iex -S mix
  ```
  Permet d'exécuter l'application interactivement et de recharger les modules à la volée avec `recompile()`.
* **Tests unitaires (ExUnit)** :
  ```bash
  mix test
  ```
* **Gestion des dépendances** : Déclarées dans `mix.exs` sous la fonction `deps/0`, et récupérées avec :
  ```bash
  mix deps.get
  ```

---

## 3. Architecture Concurrente avec OTP (Open Telecom Platform)

L'atout majeur d'Elixir réside dans son modèle d'acteurs de processus légers (indépendants des threads de l'OS) managés par la machine virtuelle BEAM.

### GenServer (Generic Server)
Composant standard pour encapsuler l'état d'un processus et gérer des requêtes synchrones (`call`) ou asynchrones (`cast`).
```elixir
defmodule Actemium.TelemetryWorker do
  use GenServer

  # API Client
  def start_link(opts) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  def get_last_measure() do
    GenServer.call(__MODULE__, :get_last)
  end

  # Rappels (Callbacks) Server
  @impl true
  def init(_opts) do
    # Initialise l'état du capteur
    {:ok, %{last_value: 0.0}}
  end

  @impl true
  def handle_call(:get_last, _from, state) do
    {:reply, state.last_value, state}
  end
end
```

### Supervisor et Tolérance aux Pannes
Les superviseurs surveillent d'autres processus (leurs enfants) et les redémarrent automatiquement en cas de crash suivant des stratégies précises (`one_for_one`, `one_for_all`, `rest_for_one`).
```elixir
defmodule Actemium.Supervisor do
  use Supervisor

  def start_link(opts) do
    Supervisor.start_link(__MODULE__, opts, name: __MODULE__)
  end

  @impl true
  def init(_opts) do
    children = [
      {Actemium.TelemetryWorker, []}
    ]

    Supervisor.init(children, strategy: :one_for_one)
  end
end
```

---

## 4. Intégration Industrielle (IoT & Nerves) chez Actemium

### Le Framework Nerves
Nerves permet de compiler du code Elixir directement en une image système minimale (firmware) démarrant instantanément sur du matériel embarqué (Raspberry Pi, BeagleBone, PC industriels).
* Le cycle de développement typique utilise Mix :
  ```bash
  export MIX_TARGET=rpi4
  mix deps.get
  mix firmware
  mix firmware.burn
  ```

### Protocoles Industriels en Elixir
Elixir excelle dans le décodage binaire grâce au pattern matching sur les binaires.
* **Modbus/TCP** :
  ```elixir
  # Exemple de parsing d'une trame Modbus/TCP en Elixir
  def parse_modbus_response(<<transaction_id::16, protocol_id::16, length::16, unit_id::8, function_code::8, data::binary>>) do
    %{
      transaction_id: transaction_id,
      unit_id: unit_id,
      function: function_code,
      payload: data
    }
  end
  ```
* **OPC UA / MQTT** : Utilisez des processus GenServer supervisés pour maintenir les connexions TCP persistantes vers les automates de l'usine (ex. Siemens S7, Rockwell Automation) et gérer les reconnexions transparentes en cas de coupure réseau sans faire crasher l'application globale.

---

## 5. Pièges Connus et Bonnes Pratiques en Elixir

* **Ne pas utiliser de structures de contrôle complexes** : Préférez le pattern matching dans les signatures de fonctions ou l'expression `with` plutôt que de multiples blocs `if` ou `case` imbriqués.
* **Éviter le partage d'état mutable** : Ne tentez pas de simuler des variables globales. L'état doit vivre exclusivement dans un GenServer ou un Agent.
* **Surveiller la boîte aux lettres des processus** : Si un processus reçoit des messages asynchrones plus rapidement qu'il ne peut les traiter, sa boîte aux lettres va gonfler et saturer la mémoire. Utilisez des mécanismes de contre-pression (backpressure) ou de pooling (ex. avec `Poolboy`).
* **Dialyzer (Types de données)** : Déclarez les types de vos fonctions avec `@spec` et utilisez `Dialyxir` pour valider la correction statique des types lors des analyses CI.
