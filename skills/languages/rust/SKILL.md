---
name: rust
description: Guide complet du langage Rust — ownership, borrowing, lifetimes, traits, async, unsafe, cargo, patterns et écosystème. En français.
---

# Rust — Guide Complet (Français)

Langage système sans garbage collector, mémoire sûre, performances natives. Édition 2021+.

---

## 1. Installation et Outils

```bash
# Installation via rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Outils essentiels
rustc --version     # Compilateur
cargo --version     # Gestionnaire de paquets
rustup update       # Mise à jour
rustup component add clippy rustfmt  # Linter + formateur
cargo new mon_projet
cargo build --release
cargo run
cargo test
cargo doc --open
cargo fmt
cargo clippy
```

---

## 2. Types et Variables

```rust
// Scalaires
let x: i32 = 42;           // Entier signé 32 bits
let y: u64 = 100;          // Non signé 64 bits
let z: f64 = 3.14159;      // Flottant
let actif: bool = true;    // Booléen
let c: char = '🦀';        // Unicode (4 octets)

// Entiers : i8, i16, i32, i64, i128, isize
// Non signés : u8, u16, u32, u64, u128, usize
// Flottants : f32, f64

// Inférence de type
let a = 42;                // i32 par défaut
let b = 3.14;              // f64 par défaut

// Mutabilité
let mut compteur = 0;      // Modifiable
compteur += 1;

// Constantes (toujours typées)
const MAX_POINTS: u32 = 100_000;

// Tuples
let tup: (i32, f64, u8) = (500, 6.4, 1);
let (x, y, z) = tup;       // Déstructuration
let premier = tup.0;       // Accès par index

// Tableaux (taille fixe, sur la pile)
let arr: [i32; 5] = [1, 2, 3, 4, 5];
let zeros = [0; 100];      // [0, 0, ..., 0] (100 fois)
let premier = arr[0];

// Vecteurs (taille dynamique, sur le tas)
let mut vec: Vec<i32> = Vec::new();
vec.push(1);
vec.push(2);

let vec2 = vec![1, 2, 3, 4, 5];  // Macro vec!
let troisieme = vec2[2];

// Slices (références vers une portion)
let slice: &[i32] = &vec2[1..4];  // Éléments 1, 2, 3

// Chaînes
let s: &str = "Hello";           // Slice de chaîne (emprunté)
let mut s2: String = String::from("Hello");  // Chaîne possédée
s2.push_str(" World");
let s3 = format!("{} {}", s, "Rust");

// HashMap
use std::collections::HashMap;
let mut scores = HashMap::new();
scores.insert(String::from("Bleu"), 10);
scores.insert(String::from("Rouge"), 50);
let score = scores.get("Bleu").copied().unwrap_or(0);
```

---

## 3. Ownership, Borrowing, Lifetimes

```rust
// OWNERSHIP : chaque valeur a un unique propriétaire
let s1 = String::from("hello");
let s2 = s1;               // s1 est DÉPLACÉ, plus utilisable
// println!("{}", s1);     // Erreur de compilation !

let s3 = s2.clone();       // Copie profonde (coûteuse)

// Copy trait (types simples copiés automatiquement)
let x = 5;
let y = x;                 // x toujours valide (i32 est Copy)
println!("{}", x);         // OK

// BORROWING : références sans prendre ownership
fn calculer_longueur(s: &String) -> usize {
    s.len()
}  // s n'est pas libéré, juste emprunté

let s = String::from("hello");
let len = calculer_longueur(&s);
println!("{}", s);         // s toujours valide !

// Borrowing mutable (une seule ref mutable à la fois)
fn ajouter(s: &mut String) {
    s.push_str(" world");
}

let mut s = String::from("hello");
ajouter(&mut s);

// Règle d'or :
// - Une seule référence mutable OU
// - Plusieurs références immuables
// - Jamais les deux simultanément

// LIFETIMES : annotations explicites quand nécessaire
fn plus_long<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

// Lifetime dans les structs
struct Extrait<'a> {
    partie: &'a str,
}
```

---

## 4. Fonctions et Closures

```rust
// Fonction classique
fn additionner(a: i32, b: i32) -> i32 {
    return a + b;          // return explicite
}

fn multiplier(a: i32, b: i32) -> i32 {
    a * b                  // Expression finale = return implicite
}

// Fonction sans retour (type unit)
fn afficher(message: &str) {
    println!("{}", message);
}

// Closures (fonctions anonymes capturant l'environnement)
let doubler = |x: i32| -> i32 { x * 2 };
let ajouter = |a, b| a + b;  // Types inférés

let mut compteur = 0;
let mut incrementer = || {
    compteur += 1;         // Capture mutable
    compteur
};

// Closures comme paramètres (traits Fn, FnMut, FnOnce)
fn appliquer<F>(f: F, x: i32) -> i32
where
    F: Fn(i32) -> i32,
{
    f(x)
}

let resultat = appliquer(|x| x + 1, 5);  // 6
```

---

## 5. Structs, Enums, Traits

```rust
// Struct classique
struct Utilisateur {
    nom: String,
    email: String,
    age: u32,
    actif: bool,
}

let alice = Utilisateur {
    email: String::from("alice@exemple.com"),
    nom: String::from("Alice"),
    age: 30,
    actif: true,
};

// Struct tuple
struct Couleur(i32, i32, i32);
let noir = Couleur(0, 0, 0);

// Struct unit (sans champs)
struct Marqueur;

// Méthodes avec impl
impl Utilisateur {
    // Constructeur
    fn nouveau(nom: String, email: String) -> Self {
        Self { nom, email, age: 0, actif: true }
    }
    
    // Méthode avec &self
    fn saluer(&self) -> String {
        format!("Bonjour, je suis {}", self.nom)
    }
    
    // Méthode avec &mut self
    fn vieillir(&mut self) {
        self.age += 1;
    }
    
    // Fonction associée (sans self)
    fn espece() -> String {
        String::from("Homo sapiens")
    }
}

// ENUMS (types somme algébriques)
enum Resultat<T, E> {
    Ok(T),
    Err(E),
}

enum Option<T> {
    Some(T),
    None,
}

enum Message {
    Quitter,
    Deplacer { x: i32, y: i32 },
    Ecrire(String),
    ChangerCouleur(i32, i32, i32),
}

// Pattern matching
fn traiter_message(msg: Message) {
    match msg {
        Message::Quitter => println!("Au revoir !"),
        Message::Deplacer { x, y } => println!("Déplacement vers ({}, {})", x, y),
        Message::Ecrire(texte) => println!("Message : {}", texte),
        Message::ChangerCouleur(r, g, b) => {
            println!("Nouvelle couleur : ({}, {}, {})", r, g, b)
        }
    }
}

// if let
if let Message::Ecrire(texte) = msg {
    println!("Texte : {}", texte);
}

// TRAITS (interfaces)
trait Resumable {
    fn resumer(&self) -> String;
    
    // Méthode par défaut
    fn resumer_defaut(&self) -> String {
        String::from("(En savoir plus...)")
    }
}

impl Resumable for Utilisateur {
    fn resumer(&self) -> String {
        format!("{} ({})", self.nom, self.email)
    }
}

// Trait bounds
fn afficher_resume<T: Resumable>(item: &T) {
    println!("{}", item.resumer());
}

// Trait objects (dispatch dynamique)
fn afficher_dyn(item: &dyn Resumable) {
    println!("{}", item.resumer());
}

// Traits dérivés
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct Point {
    x: i32,
    y: i32,
}
```

---

## 6. Gestion d'Erreurs

```rust
// Result<T, E>
use std::fs::File;
use std::io::{self, Read};

fn lire_fichier(chemin: &str) -> Result<String, io::Error> {
    let mut fichier = File::open(chemin)?;  // ? = propagation d'erreur
    let mut contenu = String::new();
    fichier.read_to_string(&mut contenu)?;
    Ok(contenu)
}

// match sur Result
match lire_fichier("test.txt") {
    Ok(contenu) => println!("{}", contenu),
    Err(e) => eprintln!("Erreur : {}", e),
}

// unwrap / expect (panique si erreur)
let contenu = lire_fichier("test.txt").unwrap();
let contenu = lire_fichier("test.txt").expect("Fichier introuvable");

// Option<T>
fn trouver_element(liste: &[i32], cible: i32) -> Option<usize> {
    liste.iter().position(|&x| x == cible)
}

match trouver_element(&[1, 2, 3], 2) {
    Some(index) => println!("Trouvé à l'index {}", index),
    None => println!("Non trouvé"),
}
```

---

## 7. Itérateurs et Closures

```rust
// Itérateurs
let nombres = vec![1, 2, 3, 4, 5];

// Map
let carres: Vec<i32> = nombres.iter().map(|x| x * x).collect();

// Filter
let pairs: Vec<&i32> = nombres.iter().filter(|&&x| x % 2 == 0).collect();

// Fold
let somme = nombres.iter().fold(0, |acc, x| acc + x);

// Chaînage
let resultat: Vec<i32> = (1..=100)
    .filter(|x| x % 3 == 0)
    .map(|x| x * 2)
    .take(5)
    .collect();

// Consommation paresseuse (itérateurs non évalués avant collect/for)
let iter = (0..).map(|x| x * x).filter(|x| x % 2 == 0);
for x in iter.take(5) {
    println!("{}", x);  // 0, 4, 16, 36, 64
}
```

---

## 8. Smart Pointers

```rust
// Box<T> : allocation sur le tas
let b = Box::new(5);
println!("b = {}", b);

// Rc<T> : comptage de références (mono-thread)
use std::rc::Rc;
let a = Rc::new(String::from("hello"));
let b = Rc::clone(&a);   // Incrémente le compteur
let c = Rc::clone(&a);
println!("Références : {}", Rc::strong_count(&a));  // 3

// Arc<T> : Rc thread-safe (atomique)
use std::sync::Arc;
use std::thread;
let a = Arc::new(vec![1, 2, 3]);
let a_clone = Arc::clone(&a);
thread::spawn(move || {
    println!("{:?}", a_clone);
});

// RefCell<T> : mutabilité intérieure
use std::cell::RefCell;
let x = RefCell::new(42);
*x.borrow_mut() += 1;
println!("{}", x.borrow());

// Combinaison Rc<RefCell<T>> (données partagées et mutables)
let donnees = Rc::new(RefCell::new(0));
```

---

## 9. Concurrence

```rust
use std::thread;
use std::sync::{Arc, Mutex, mpsc};
use std::time::Duration;

// Threads basiques
let handle = thread::spawn(|| {
    for i in 1..=5 {
        println!("Thread : {}", i);
        thread::sleep(Duration::from_millis(10));
    }
});

for i in 1..=3 {
    println!("Principal : {}", i);
    thread::sleep(Duration::from_millis(10));
}

handle.join().unwrap();

// Mutex pour données partagées
let compteur = Arc::new(Mutex::new(0));
let mut handles = vec![];

for _ in 0..10 {
    let compteur = Arc::clone(&compteur);
    let handle = thread::spawn(move || {
        let mut num = compteur.lock().unwrap();
        *num += 1;
    });
    handles.push(handle);
}

for handle in handles {
    handle.join().unwrap();
}
println!("Résultat : {}", *compteur.lock().unwrap());  // 10

// Channels (mpsc = multiple producer, single consumer)
let (tx, rx) = mpsc::channel();

thread::spawn(move || {
    tx.send("Message 1").unwrap();
    tx.send("Message 2").unwrap();
});

for recu in rx {
    println!("Reçu : {}", recu);
}
```

---

## 10. Async/Await avec Tokio

```rust
// Cargo.toml : tokio = { version = "1", features = ["full"] }

use tokio;

#[tokio::main]
async fn main() {
    // Exécution concurrente
    let (r1, r2) = tokio::join!(
        tache_1(),
        tache_2(),
    );
    
    // Select (premier terminé)
    tokio::select! {
        resultat = tache_longue() => println!("Tâche longue : {}", resultat),
        _ = tokio::time::sleep(Duration::from_secs(5)) => println!("Timeout !"),
    }
}

async fn tache_1() -> String {
    tokio::time::sleep(Duration::from_secs(1)).await;
    String::from("Tâche 1 terminée")
}

async fn tache_2() -> String {
    String::from("Tâche 2 immédiate")
}

// Client HTTP avec reqwest
async fn requete_http() -> Result<(), reqwest::Error> {
    let client = reqwest::Client::new();
    let reponse = client
        .get("https://api.exemple.com/data")
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;
    println!("{:#?}", reponse);
    Ok(())
}
```

---

## 11. Tests

```rust
// Tests unitaires (dans le même fichier)
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_additionner() {
        assert_eq!(additionner(2, 2), 4);
        assert_ne!(additionner(2, 2), 5);
    }
    
    #[test]
    #[should_panic(expected = "division par zéro")]
    fn test_division_zero() {
        diviser(10, 0);
    }
    
    #[test]
    #[ignore]  // Ignorer ce test
    fn test_lent() {
        // ...
    }
}
```

---

## 12. Unsafe Rust

```rust
// Pointeurs bruts
let mut x = 5;
let r1 = &x as *const i32;   // Pointeur immuable
let r2 = &mut x as *mut i32;  // Pointeur mutable

unsafe {
    println!("r1: {}", *r1);
    *r2 += 1;
}

// Fonction unsafe
unsafe fn dangereux() {
    // Opérations qui contournent le vérificateur
}

// Appel à une fonction C
extern "C" {
    fn abs(input: i32) -> i32;
}

unsafe {
    println!("Valeur absolue de -3 : {}", abs(-3));
}

// Exposer une fonction Rust au C
#[no_mangle]
pub extern "C" fn appel_depuis_c() {
    println!("Appelé depuis C !");
}
```

---

## 13. Écosystème Essentiel

```toml
[dependencies]
serde = { version = "1", features = ["derive"] }  # Sérialisation
serde_json = "1"                                    # JSON
tokio = { version = "1", features = ["full"] }      # Async runtime
reqwest = { version = "0.12", features = ["json"] }# HTTP client
axum = "0.7"                                        # Web framework
sqlx = { version = "0.7", features = ["sqlite"] }   # Base de données
clap = { version = "4", features = ["derive"] }     # CLI parser
rayon = "1"                                         # Parallélisme
anyhow = "1"                                        # Gestion d'erreurs
thiserror = "1"                                     # Erreurs dérivées
tracing = "0.1"                                     # Journalisation
rand = "0.8"                                        # Aléa
```

---

## Références
- Rust Book : https://doc.rust-lang.org/book/
- Rust by Example : https://doc.rust-lang.org/rust-by-example/
- Cargo Book : https://doc.rust-lang.org/cargo/
- Tokio : https://tokio.rs/