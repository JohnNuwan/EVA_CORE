---
name: go
description: Guide complet du langage Go — syntaxe, goroutines, channels, interfaces, tests, modules, patterns concurrents et écosystème. En français.
---

# Go (Golang) — Guide Complet (Français)

Langage compilé, concurrent, à garbage collector. Go 1.22+.

---

## 1. Installation et Outils

```bash
# Installation
wget https://go.dev/dl/go1.22.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.22.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

go version
go mod init mon-projet
go build
go run main.go
go test ./...
go fmt ./...
go vet ./...
```

---

## 2. Syntaxe de Base

```go
package main

import "fmt"

func main() {
    // Variables
    var x int = 42
    var y float64 = 3.14
    var nom string = "Go"
    var actif bool = true
    
    // Inférence (déclaration courte)
    z := 100
    message := "Bonjour"
    
    // Constantes
    const Pi = 3.14159
    const MaxRetries = 3
    
    // Types de base
    // int, int8, int16, int32, int64
    // uint, uint8, uint16, uint32, uint64
    // float32, float64
    // complex64, complex128
    // byte (alias uint8), rune (alias int32)
    // string, bool
    
    // Tableaux (taille fixe)
    var arr [5]int
    arr[0] = 1
    arr2 := [3]string{"a", "b", "c"}
    
    // Slices (taille dynamique)
    slice := []int{1, 2, 3, 4, 5}
    slice = append(slice, 6)
    sousEnsemble := slice[1:4]  // [2, 3, 4]
    fmt.Println(len(slice), cap(slice))
    
    // Maps
    scores := map[string]int{
        "Alice": 95,
        "Bob":   87,
    }
    scores["Charlie"] = 92
    delete(scores, "Bob")
    valeur, existe := scores["Bob"]
    
    // Structs
    type Personne struct {
        Nom    string
        Age    int
        Email  string
    }
    
    alice := Personne{Nom: "Alice", Age: 30, Email: "alice@mail.com"}
    fmt.Println(alice.Nom)
}
```

---

## 3. Structures de Contrôle

```go
// if/else
if x > 0 {
    fmt.Println("Positif")
} else if x < 0 {
    fmt.Println("Négatif")
} else {
    fmt.Println("Zéro")
}

// if avec déclaration
if err := faireQuelqueChose(); err != nil {
    fmt.Println("Erreur :", err)
}

// for (unique boucle en Go)
for i := 0; i < 10; i++ {
    fmt.Println(i)
}

// while-like
for condition {
    // ...
}

// boucle infinie
for {
    break
}

// range
for i, v := range slice {
    fmt.Printf("Index %d : %v\n", i, v)
}

for cle, valeur := range scores {
    fmt.Printf("%s → %d\n", cle, valeur)
}

// switch (pas de break nécessaire)
switch jour {
case "lundi", "mardi":
    fmt.Println("Début de semaine")
case "vendredi":
    fmt.Println("Bientôt le weekend")
default:
    fmt.Println("Milieu de semaine")
}

// switch sans expression (if/else chain)
switch {
case x < 0:
    fmt.Println("Négatif")
case x == 0:
    fmt.Println("Zéro")
default:
    fmt.Println("Positif")
}
```

---

## 4. Fonctions

```go
func Additionner(a, b int) int {
    return a + b
}

// Retours multiples
func Diviser(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("division par zéro")
    }
    return a / b, nil
}

// Retours nommés
func Calculer(a, b int) (somme int, produit int) {
    somme = a + b
    produit = a * b
    return  // retour nu (utilise les noms)
}

// Fonction variadique
func Somme(nombres ...int) int {
    total := 0
    for _, n := range nombres {
        total += n
    }
    return total
}

// Fonctions comme valeurs
operation := func(a, b int) int { return a * b }
fmt.Println(operation(3, 4))

// Méthodes sur types
type Compte struct {
    Solde float64
}

func (c *Compte) Deposer(montant float64) {
    c.Solde += montant
}

func (c Compte) Afficher() string {
    return fmt.Sprintf("%.2f €", c.Solde)
}
```

---

## 5. Gestion d'Erreurs

```go
// Pattern standard : retour (valeur, error)
func LireFichier(chemin string) ([]byte, error) {
    data, err := os.ReadFile(chemin)
    if err != nil {
        return nil, fmt.Errorf("lecture de %s : %w", chemin, err)
    }
    return data, nil
}

// defer (exécution à la sortie, style finally)
func TraiterFichier(chemin string) error {
    f, err := os.Open(chemin)
    if err != nil {
        return err
    }
    defer f.Close()  // Exécuté à la fin
    
    // Traitement...
    return nil
}

// panic/recover (usage exceptionnel)
func FonctionProtegee() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("Récupéré de :", r)
        }
    }()
    panic("quelque chose de grave")
}
```

---

## 6. Interfaces

```go
// Interface (contrat implicite)
type Formateur interface {
    Formater() string
}

type Personne struct {
    Nom string
    Age int
}

// Implémentation implicite (pas de "implements")
func (p Personne) Formater() string {
    return fmt.Sprintf("%s (%d ans)", p.Nom, p.Age)
}

// Interface comme paramètre
func Afficher(f Formateur) {
    fmt.Println(f.Formater())
}

// Interface vide (accepte tout)
func Decrire(v interface{}) {
    fmt.Printf("Type: %T, Valeur: %v\n", v, v)
}

// Type assertion
var f Formateur = Personne{"Bob", 25}
p, ok := f.(Personne)
if ok {
    fmt.Println(p.Nom)
}

// Type switch
switch v := f.(type) {
case Personne:
    fmt.Println("Personne :", v.Nom)
case string:
    fmt.Println("Chaîne :", v)
default:
    fmt.Printf("Inconnu : %T\n", v)
}
```

---

## 7. Concurrence (Goroutines et Channels)

```go
// Goroutine
go func() {
    fmt.Println("Concurrent")
}()

// WaitGroup
var wg sync.WaitGroup
for i := 0; i < 5; i++ {
    wg.Add(1)
    go func(id int) {
        defer wg.Done()
        fmt.Printf("Goroutine %d\n", id)
    }(i)
}
wg.Wait()

// Channels (buffered et unbuffered)
ch := make(chan int)         // Unbuffered (synchrone)
ch := make(chan int, 10)     // Buffered (capacité 10)

// Envoi et réception
ch <- 42                     // Envoyer
valeur := <-ch               // Recevoir

// Channel directionnel
func Envoyer(ch chan<- int, v int) { ch <- v }
func Recevoir(ch <-chan int) int { return <-ch }

// Select (multiplexer les channels)
select {
case msg1 := <-ch1:
    fmt.Println("Reçu de ch1 :", msg1)
case msg2 := <-ch2:
    fmt.Println("Reçu de ch2 :", msg2)
case <-time.After(1 * time.Second):
    fmt.Println("Timeout !")
case ch3 <- 42:
    fmt.Println("Envoyé vers ch3")
default:
    fmt.Println("Pas de communication prête")
}

// Range sur channel
for valeur := range ch {
    fmt.Println(valeur)
}

// Close (fermer un channel)
close(ch)

// Mutex
var mu sync.Mutex
var compteur int

for i := 0; i < 1000; i++ {
    go func() {
        mu.Lock()
        compteur++
        mu.Unlock()
    }()
}
```

---

## 8. Generics (Go 1.18+)

```go
// Fonction générique
func Premier[T any](slice []T) (T, bool) {
    if len(slice) == 0 {
        var zero T
        return zero, false
    }
    return slice[0], true
}

// Contrainte
type Numerique interface {
    ~int | ~int64 | ~float64
}

func Somme[T Numerique](nombres []T) T {
    var total T
    for _, n := range nombres {
        total += n
    }
    return total
}

// Type générique
type Pile[T any] struct {
    elements []T
}

func (p *Pile[T]) Push(v T) {
    p.elements = append(p.elements, v)
}

func (p *Pile[T]) Pop() (T, bool) {
    if len(p.elements) == 0 {
        var zero T
        return zero, false
    }
    v := p.elements[len(p.elements)-1]
    p.elements = p.elements[:len(p.elements)-1]
    return v, true
}
```

---

## 9. Tests et Benchmarks

```go
// mon_module_test.go
package monmodule

import "testing"

func TestAddition(t *testing.T) {
    resultat := Additionner(2, 3)
    if resultat != 5 {
        t.Errorf("Additionner(2, 3) = %d; attendu 5", resultat)
    }
}

// Table-driven tests
func TestAdditionner(t *testing.T) {
    tests := []struct {
        nom     string
        a, b    int
        attendu int
    }{
        {"positifs", 2, 3, 5},
        {"negatifs", -1, -1, -2},
        {"zero", 0, 5, 5},
    }
    
    for _, tt := range tests {
        t.Run(tt.nom, func(t *testing.T) {
            if got := Additionner(tt.a, tt.b); got != tt.attendu {
                t.Errorf("=%d; attendu %d", got, tt.attendu)
            }
        })
    }
}

// Benchmarks
func BenchmarkAdditionner(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Additionner(1, 2)
    }
}

// Exécution :
// go test -v -bench=. -benchmem
```

---

## 10. Modules et Packages

```go
// go.mod
module github.com/utilisateur/monprojet

go 1.22

require (
    github.com/gin-gonic/gin v1.9.1
)

// Exporter (majuscule = public, minuscule = privé)
package utils

func Publique() {}   // Exportée
func privee() {}     // Non exportée

type MonType struct {
    Public string    // Exporté
    prive  int       // Non exporté
}
```

---

## 11. Écosystème Web (Gin)

```go
package main

import "github.com/gin-gonic/gin"

func main() {
    r := gin.Default()
    
    r.GET("/ping", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "pong"})
    })
    
    r.POST("/utilisateurs", func(c *gin.Context) {
        var utilisateur struct {
            Nom  string `json:"nom"`
            Email string `json:"email"`
        }
        if err := c.ShouldBindJSON(&utilisateur); err != nil {
            c.JSON(400, gin.H{"erreur": err.Error()})
            return
        }
        c.JSON(201, utilisateur)
    })
    
    r.Run(":8080")
}
```

---

## Références
- Go Tour : https://go.dev/tour/
- Effective Go : https://go.dev/doc/effective_go
- Go by Example : https://gobyexample.com/
- Standard Library : https://pkg.go.dev/std