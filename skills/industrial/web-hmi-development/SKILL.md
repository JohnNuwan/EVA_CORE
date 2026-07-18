---
name: web-hmi-development
description: "Développer des IHMs web industrielles en HTML, CSS et JS."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [windows, linux]
metadata:
  tags: [web-hmi, html5, css3, javascript, ignition-perspective, wincc-unified, svg, webvisu, websocket]
  related_skills: [scada-hmi-programming-languages, ot-it-integration-languages]
---

# Développement d'IHM Web Modernes pour les Systèmes SCADA et de Supervision

Cette compétence encadre le développement d'interfaces homme-machine (IHM) basées sur les standards du web (HTML5, CSS3, JavaScript) pour les plateformes de supervision modernes comme **Ignition Perspective**, **Siemens WinCC Unified** ou **CODESYS WebVisu**.

---

## 1. Scripting et Subscription d'Événements avec l'API WinCC Unified

WinCC Unified n'utilise plus les scripts C/VBS legacy. Les animations et traitements asynchrones s'appuient sur un runtime JavaScript moderne. Le script ci-dessous montre comment s'abonner de manière optimale à un groupe de variables PLC (Tags) pour mettre à jour l'interface sans latence.

```javascript
// Connexion et abonnement asynchrone à un groupe de Tags dans WinCC Unified
let tagGroup = HMIRuntime.Tags.CreateTagSet();

// Ajout des variables a surveiller
tagGroup.Add("Tag_Mesure_Debit");
tagGroup.Add("Tag_Vanne_Statut");
tagGroup.Add("Tag_Alerte_Niveau");

// Lecture asynchrone avec callback
tagGroup.ReadAsync(function(errorCode, tagValues) {
    if (errorCode === 0) {
        // Traitement initial
        UpdateHmiDisplay(tagValues);
    } else {
        HMIRuntime.Trace("Erreur lors de la lecture asynchrone du groupe de Tags : " + errorCode);
    }
});

function UpdateHmiDisplay(tagValues) {
    // 1. Mise a jour de la mesure de debit
    let debitItem = Screen.Items("Text_Debit");
    debitItem.Text = tagValues("Tag_Mesure_Debit").Value.toFixed(2) + " m3/h";

    // 2. Gestion de l'affichage de la vanne (couleur dynamique)
    let vanneWidget = Screen.Items("Vanne_Widget");
    let statut = tagValues("Tag_Vanne_Statut").Value;
    
    switch(statut) {
        case 0: // Fermee
            vanneWidget.BackColor = 0xFF808080; // Gris
            break;
        case 1: // Ouverte
            vanneWidget.BackColor = 0xFF00FF00; // Vert
            break;
        case 2: // En mouvement
            vanneWidget.BackColor = 0xFFFFCC00; // Orange/Jaune
            break;
        default: // Defaut
            vanneWidget.BackColor = 0xFFFF0000; // Rouge clignotant
    }
}
```

---

## 2. Graphiques Vectoriels SVG Dynamiques et Animes

Les graphiques industriels (synoptiques) doivent être vectoriels (SVG) pour s'adapter à toutes les résolutions d'écran sans perte de qualité.

### Widget SVG Dynamique de Pompe Industrielle
Voici le code XML/SVG d'une pompe animée en fonction de son état (rotation continue si active, rouge clignotant si défaut).

```xml
<svg width="150" height="150" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" id="pompe-widget">
  <style>
    /* Definition des animations CSS */
    @keyframes rotation-helice {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    @keyframes clignotement-defaut {
      0% { fill: #ff0000; }
      50% { fill: #800000; }
      100% { fill: #ff0000; }
    }

    /* Classes d'etats appliquees par JavaScript */
    .pompe-corps {
      fill: #2c3e50;
      stroke: #34495e;
      stroke-width: 2;
    }
    .helice-active {
      transform-origin: 50px 50px;
      animation: rotation-helice 1s linear infinite;
    }
    .defaut-actif {
      animation: clignotement-defaut 0.8s infinite;
    }
  </style>

  <!-- Corps de la pompe -->
  <circle cx="50" cy="50" r="40" class="pompe-corps" />
  <rect x="75" y="40" width="20" height="20" fill="#7f8c8d" />

  <!-- Indicateur d'etat (defaut) -->
  <circle cx="50" cy="25" r="5" id="indicateur-defaut" fill="#95a5a6" />

  <!-- Hélice mobile de la pompe -->
  <g id="helice" class="helice-active">
    <line x1="50" y1="50" x2="50" y2="20" stroke="#ecf0f1" stroke-width="4" stroke-linecap="round" />
    <line x1="50" y1="50" x2="50" y2="80" stroke="#ecf0f1" stroke-width="4" stroke-linecap="round" />
    <line x1="50" y1="50" x2="20" y2="50" stroke="#ecf0f1" stroke-width="4" stroke-linecap="round" />
    <line x1="50" y1="50" x2="80" y2="50" stroke="#ecf0f1" stroke-width="4" stroke-linecap="round" />
  </g>
</svg>
```

Pour activer le mode défaut via JavaScript :
```javascript
// Activer l'affichage du defaut
document.getElementById("indicateur-defaut").classList.add("defaut-actif");
// Arreter la rotation de l'helice
document.getElementById("helice").classList.remove("helice-active");
```

---

## 3. Conception Responsive et Tactile (Grille CSS)

Les dalles tactiles d'atelier exigent des layouts fluides mais fixes pour éviter la gigue d'affichage lorsque l'opérateur clique.

### Feuille de Style CSS standard pour Pupitres Industriels
```css
/* Container de synoptique principal */
.dashboard-container {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-template-rows: 60px 1fr 40px;
  height: 100vh;
  gap: 10px;
  background-color: #1a1a24;
  color: #e2e8f0;
  font-family: 'Roboto', sans-serif;
  box-sizing: border-box;
  padding: 10px;
}

/* En-tete avec les informations de l'usine */
.header-bar {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #2d3748;
  border-bottom: 2px solid #4a5568;
  padding: 0 15px;
}

/* Grille de cartes de mesures */
.mesures-grid {
  grid-column: 1 / 4; /* Colonne gauche pour la telemesure */
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* Carte de mesure individuelle */
.sensor-card {
  background-color: #2d3748;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

/* Boutons de commande d'atelier tactiles */
.btn-command-tactile {
  min-width: 80px;
  min-height: 55px; /* Optimise pour l'appui par gants */
  padding: 10px 20px;
  font-size: 16px;
  font-weight: bold;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  margin: 5px;
  transition: background-color 0.2s;
}

.btn-start {
  background-color: #2f855a;
  color: #fff;
}
.btn-start:active {
  background-color: #22543d; /* Effet d'enfoncement tactile immediat */
}
```
