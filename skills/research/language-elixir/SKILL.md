---
name: language-elixir
title: "Doctorat — Langage Elixir"
description: "Compétence niveau docteur en Elixir. Couvre BEAM VM, OTP, GenServer, Supervision trees, ETS, Mnesia, Phoenix, Nx, LiveView, concurrency, fault-tolerance, distributed Erlang, et la métaprogrammation Elixir."
category: research
lang: fr
---

# Doctorat : Langage Elixir

## Présentation
Elixir est un langage de programmation fonctionnel, concurrent et tolérant aux pannes, créé par José Valim (2011-2014). Il tourne sur la BEAM (Bogdan/Björn's Erlang Abstract Machine), la machine virtuelle d'Erlang, héritant de ses super-pouvoirs : concurrence massive (des millions de processus légers), tolérance aux pannes (supervision trees), distribution native, et mise à jour à chaud du code. Elixir ajoute une syntaxe moderne (inspirée de Ruby), la métaprogrammation via macros, les protocoles, les pipes, et un écosystème riche (Phoenix, Nx, LiveView).

## Histoire et Contexte
- 2011 : José Valim (Plataformatec) commence Elixir
- 2012 : Première version publique
- 2014 : Elixir 1.0 — stabilité
- 2016-2018 : Elixir 1.4-1.6 — Phoenix 1.3, écosystème Nx
- 2021 : Elixir 1.12 — améliorations mix, ExUnit
- 2022-2023 : Elixir 1.14-1.16 — SET transform, Nx mature, Phoenix 1.7

## Architecture du Langage
- **BEAM VM** : Machine virtuelle register-based pour concurrence et tolérance aux pannes
- **Processus BEAM** : Processus légers (~2KB, millions simultanément)
- **Scheduler** : 1 scheduler par cœur CPU — répartit les processus
- **Préemption** : Toutes les ~1000 reductions (appels de fonction)
- **Memory per process** : Chaque processus a son propre heap
- **OTP** : Framework, bibliothèques, patterns standard
- **Hot code swapping** : Mise à jour sans arrêter le système

## Système de Types
- **Types dynamiques** : Héritage Erlang
- **Types de base** : Integers (big ints), Floats, Atoms, Strings (UTF-8 binaries), Lists, Tuples, Maps, Structs
- **Structs** : Maps nommés avec validation
- **Protocols** : Polymorphisme ad-hoc (defprotocol, defimpl)
- **Type specs** : spec, type, opaque — documentation et analyse
- **Dialyzer** : Analyse statique (success typing)
- **Guards** : when is_integer(x)
- **Union types** : atom() | integer()

## Compilation et Interprétation
- **Compilation** : elixirc compile en bytecode BEAM
- **IEx** : REPL interactif avec autocomplétion
- **Mix** : Build tool, test runner, dependency manager
- **Bytecode BEAM** : Fichiers .beam chargés par la BEAM
- **Core Erlang** : Elixir compile vers Core Erlang, puis BEAM bytecode
- **Hot reload** : r Module dans IEx
- **NIF** : C extensions (dangereux — peut crasher la VM)

## Mémoire et Performances
- **GC par processus** : Chaque processus a son propre heap
- **Copying GC** : GC générationnel, copying collector
- **Binary heap** : Grands binaires (>64 bytes) partagés avec comptage
- **ETS** : Erlang Term Storage — table en mémoire partagée
- **List (linked list)** : O(n) accès, O(1) ajout en tête
- **Maps** : Arbres Hamt pour mises à jour immuables
- **Hibernation** : erlang.hibernate pour réduire mémoire

## Écosystème et Outils
- **Mix** : Build tool, test runner, hex
- **Hex** : hex.pm — gestionnaire de paquets
- **Phoenix** : Framework web (MVC, channels, LiveView)
- **Ecto** : ORM/DSL pour bases de données
- **Nx** : Numerical Elixir — tenseurs, différentiation
- **LiveView** : Applications web temps réel sans JS
- **ExUnit** : Framework de test intégré
- **ExDoc** : Générateur de documentation
- **Credo** : Linter et guide de style
- **Observer** : Interface graphique BEAM

## Concurrence et Parallélisme
- **Processus BEAM** : Acteurs isolés communiquant par messages
- **Send/Receive** : send(pid, msg), receive do ... end
- **GenServer** : Client-serveur générique (call/cast/info)
- **Supervisor** : Arbres de supervision — redémarrage automatique
- **Tasks** : Tâches asynchrones (Task.async, Task.await)
- **Agents** : Encapsulation d'état mutable
- **ETS** : Table de données partagée concurrente
- **Mnesia** : Base de données temps réel distribuée
- **GenStage / Flow** : Pipelines avec backpressure
- **Distribution** : Communication entre nœuds

## Patterns Avancés
- **OTP Design Principles** : GenServer, Supervisor, Application
- **GenServer callbacks** : init, handle_call, handle_cast, handle_info
- **GenStateMachine** : Machine à états OTP
- **Horde** : Registry et Supervisor distribués
- **Phoenix Channels** : WebSocket pub/sub
- **Phoenix LiveView** : Rendu serveur temps réel
- **ETS pattern matching** : ets.match, ets.match_object
- **Mnesia transactions** : Transactions ACID distribuées
- **Macros** : quote, unquote — métaprogrammation

## Optimisation
- **Profiling** : fprof, eprof, recon_trace
- **Observer** : Visualisation des processus, mémoire, ETS
- **ETS optimization** : Choix du type de table
- **IO lists** : Construction de chaînes sans copie
- **Binary matching** : Pattern matching sur binaires
- **Streams** : Évaluation paresseuse sans intermédiaires
- **Process hibernation** : Réduction mémoire

## Interopérabilité
- **Erlang interop** : Appel direct de modules Erlang
- **NIF** : C extensions (prudence)
- **Ports** : Processus externes connectés à la BEAM
- **CNode** : Nœud C distant
- **Rustler** : NIFs en Rust (plus sûr que C)
- **Python** : Pythonx — appel de code Python

## Applications Industrielles
- **Discord** : 5+ millions de connexions simultanées
- **Pinterest** : Feed en temps réel
- **WhatsApp** (v1) : 1 milliard d'utilisateurs
- **Financial Times** : Plateforme de contenu
- **Heroku** : Routing layer
- **Toyota Connected** : Systèmes connectés
- **Supabase** : Realtime

## Sécurité
- **Process isolation** : Pas d'accès à la mémoire d'autres processus
- **Message passing** : Messages immuables
- **Fault tolerance** : Let it crash — superviseurs redémarrent
- **No shared state** : Pas de variables globales mutables
- **Hot code swap** : Mise à jour sécurisée
- **SSL/TLS** : Module :ssl natif

## Veille Technologique
- **Elixir Lang Blog** : elixir-lang.org/blog
- **GitHub** : elixir-lang/elixir
- **Hex** : hex.pm
- **Elixir Forum** : elixirforum.com
- **Elixir Radar** : Newsletter
- **Conférences** : ElixirConf, CodeBEAM