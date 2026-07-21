---
title: Théorie des Couleurs — Design UI/UX
description: Théorie des couleurs pour le design — harmonies, contrastes, psychologie, accessibilité, espaces colorimétriques HSL/OKLCH, palettes, thèmes dark/light
category: creative
author: E.V.A
tags: [couleur, color-theory, palette, accessibilite, hsl, oklch, harmonie, theme]
version: 1.0
---

# Théorie des Couleurs — Design UI/UX

## Fondamentaux de la Couleur

### Le Cercle Chromatique
```
          Rouge (0°)
             |
   Orange ————|———— Magenta
      |       |       |
  Jaune ------+------ Violet
      |       |       |
   Chartreuse———|———— Bleu
             |
          Cyan (180°)
```

### Propriétés de la couleur
| Propriété | Description | CSS |
|-----------|-------------|-----|
| **Teinte (Hue)** | Position sur le cercle 0-360° | `hsl(200, 50%, 50%)` |
| **Saturation** | Intensité (0% = gris, 100% = pur) | `hsl(200, 100%, 50%)` |
| **Luminosité (Lightness)** | Claireté (0% = noir, 100% = blanc) | `hsl(200, 50%, 70%)` |
| **Chroma** | Pureté colorimétrique (OKLCH) | `oklch(70% 0.15 200)` |
| **Valeur (Value)** | Luminosité perçue (HSB) | `hsb(200, 50%, 80%)` |

### Espaces colorimétriques modernes

```css
/* HSL — standard, large support */
color: hsl(200, 70%, 50%);

/* OKLCH — perception humaine uniforme, recommandé */
color: oklch(65% 0.18 200);

/* LAB — scientifique */
color: lab(65% -20 -30);

/* P3 — gamut étendu (écrans modernes) */
color: color(display-p3 0.2 0.5 0.8);
```

**Pourquoi OKLCH est supérieur :**
- Perception uniforme : 10° de différence visuelle est constant sur tout le cercle
- Palette cohérente : varier L et C à H fixe donne des teintes visuellement harmonieuses
- Dégradés naturels : interpolation en OKLCH évite les zones grises sales

## Harmonies Chromatiques

### 1. Monochrome
```yaml
Une seule teinte, saturation/luminosité variables
Exemple: Bleu #0066FF → #4D94FF → #99C2FF → #CCE5FF
Usage: Minimaliste, professionnel, sobre
Verdict: Sûr, élégant, mais peut manquer de contraste
```

### 2. Analogique
```yaml
Couleurs adjacentes sur le cercle (30°)
Exemple: Bleu (200°) + Cyan (180°) + Bleu-violet (220°)
Usage: Harmonieux, cohérent, agréable
Verdict: Naturel, facile à vivre
```

### 3. Complémentaire
```yaml
Couleurs opposées (180°)
Exemple: Bleu (200°) + Orange (20°)
Usage: Contraste fort, énergique, accrocheur
Verdict: Puissant, mais doser avec soin (80/20)
```

### 4. Triadique
```yaml
Trois couleurs à 120° d'intervalle
Exemple: Rouge (0°) + Vert (120°) + Bleu (240°)
Usage: Dynamique, riche, équilibré
Verdict: Difficile, utiliser une couleur dominante
```

### 5. Tétradique (Double Complémentaire)
```yaml
Deux paires complémentaires
Exemple: Bleu+Orange + Violet+Jaune
Usage: Complexe, riche, vibrant
Verdict: Réservé aux experts, équilibrage délicat
```

### 6. Split-Complémentaire
```yaml
Une couleur + les deux adjacentes à sa complémentaire
Exemple: Bleu + Jaune-orange + Orange-rouge
Usage: Contraste sans agressivité
Verdict: Excellent compromis, très utilisé
```

## Systèmes de Palettes

### Palette UI (Système 50-950)
```yaml
Neutres (Gris):
  50:  #FAFAFA  (fond clair)
  100: #F5F5F5  (fond section)
  200: #E5E5E5  (bordure légère)
  300: #D4D4D4  (bordure)
  400: #A3A3A3  (placeholder)
  500: #737373  (texte secondaire)
  600: #525252  (texte primaire)
  700: #404040  (titre)
  800: #262626  (fond dark)
  900: #171717  (fond dark profond)
  950: #0A0A0A  (fond dark extrême)

Primaire (Bleu):
  50:  #EFF6FF  (fond light)
  100: #DBEAFE  (hover léger)
  200: #BFDBFE  (sélection)
  300: #93C5FD  (bordure)
  400: #60A5FA  (hover)
  500: #3B82F6  (PRIMARY)
  600: #2563EB  (hover)
  700: #1D4ED8  (texte sur light)
  800: #1E40AF  (fond dark)
  900: #1E3A8A  (dark hover)
  950: #172554  (dark accent)
```

### Palette Sémantique
```yaml
Success:  Vert   (#22C55E, #16A34A)
Warning:  Jaune  (#EAB308, #CA8A04)
Error:    Rouge  (#EF4444, #DC2626)
Info:     Bleu   (#3B82F6, #2563EB)
```

### Génération de palette depuis une couleur primaire
```javascript
function generatePalette(hex, steps = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]) {
  // Convertir en OKLCH pour interpolation uniforme
  const { l, c, h } = hexToOklch(hex);
  const palette = {};
  steps.forEach(step => {
    const lightness = 0.95 - (step / 1000) * 0.85; // 50→0.95, 950→0.10
    palette[step] = oklchToHex({ l: lightness, c: c * (1 - step/1000 * 0.5), h });
  });
  return palette;
}
```

## Psychologie des Couleurs

### Associations culturelles
| Couleur | Occident | Asie | Afrique |
|---------|----------|------|---------|
| **Rouge** | Danger, passion, énergie | Chance, prospérité | Vie, santé |
| **Bleu** | Confiance, calme, pro | Immortalité, ciel | Ciel, spiritualité |
| **Vert** | Nature, santé, argent | Harmonie, jeunesse | Nature, fertilité |
| **Jaune** | Joie, optimisme, attention | Sacré, pouvoir | Richesse, soleil |
| **Orange** | Créativité, enthousiasme | Courage, transformation | - |
| **Violet** | Luxe, spiritualité | Noblesse, mystère | Royauté, spiritualité |
| **Noir** | Élégance, pouvoir, mort | Masculinité, puissance | Âge, maturité |
| **Blanc** | Pureté, propreté | Deuil, pureté | Paix, pureté |

### Usage en UI
```yaml
Bleu: Banques, tech, santé, SaaS
  → Confiance, professionnalisme, calme
Vert: Écologie, finance, santé
  → Nature, croissance, stabilité
Rouge: Urgence, food, e-commerce
  → Urgence, passion, appétit
Noir: Luxe, tech premium, mode
  → Élégance, puissance, sophistication
Orange: Créativité, entertainment
  → Énergie, fun, accessible
Violet: Beauty, spiritualité, premium
  → Luxe, créativité, mystère
```

## Thèmes Dark & Light

### Stratégie de palette
```yaml
Light mode:
  Fond: #FFFFFF → #F9FAFB
  Surface: #F3F4F6
  Bordure: #E5E7EB
  Text primaire: #111827
  Text secondaire: #6B7280

Dark mode:
  Fond: #0F172A → #1E293B
  Surface: #1E293B
  Bordure: #334155
  Text primaire: #F1F5F9
  Text secondaire: #94A3B8
```

### Inversion des couleurs
```css
/* ✅ Approche CSS custom properties */
:root {
  --bg-primary: #FFFFFF;
  --text-primary: #1A1A1A;
  --color-primary: #0066FF;
}

[data-theme="dark"] {
  --bg-primary: #1A1A1A;
  --text-primary: #F5F5F5;
  --color-primary: #4D94FF;  /* Plus clair sur fond sombre */
}
```

### Ajustements OKLCH pour dark mode
```yaml
Light mode:  oklch(45% 0.15 260)  → bleu moyen
Dark mode:   oklch(65% 0.12 260)  → bleu plus clair, moins saturé
→ Augmenter L de 15-25%, réduire C de 10-20%
```

## Accessibilité & Contraste

### Ratios minimums
```yaml
Text normal (<18px):      4.5:1 (AA), 7:1 (AAA)
Text large (≥18px bold):  3:1 (AA), 4.5:1 (AAA)
UI components:            3:1
```

### Outils de vérification
```bash
# CLI avec Node.js
npx color-contrast-checker #FF0000 #FFFFFF  # → ratio 4.0:1 ❌
npx color-contrast-checker #1A1A1A #FFFFFF  # → ratio 15.3:1 ✅
```

### Daltonisme
```yaml
Types:
  Deutéranopie (vert): 6% hommes, 0.4% femmes
  Protanopie (rouge): 2% hommes, 0.02% femmes
  Tritanopie (bleu): 0.005%
  Achromatopsie (total): 0.003%

Règles:
  - Ne jamais utiliser la couleur seule pour l'info
  - Ajouter icônes, patterns, labels
  - Tester en niveaux de gris
  - Éviter les combinaisons: rouge/vert, bleu/violet, vert/gris
```

## Dégradés & Effets

### Dégradés harmonieux
```css
/* Dégradé en OKLCH — naturel, sans zone grise */
background: oklch(65% 0.15 200) → oklch(65% 0.15 260);

/* Dégradé HSL — peut créer des gris sales */
background: hsl(200, 70%, 50%) → hsl(260, 70%, 50%);  /* ⚠️ */

/* ✅ Même luminosité = dégradé propre */
background: oklch(65% 0.15 200) → oklch(65% 0.15 20);
```

### Ombre portée
```css
/* Ombres avec la couleur primaire */
box-shadow: 
  0 4px 6px color-mix(in srgb, var(--color-primary) 10%, transparent),
  0 10px 15px color-mix(in srgb, var(--color-primary) 15%, transparent);
```

## Pièges
- ⚠️ Contraste insuffisant sur textes longs (fatigue visuelle)
- ⚠️ Palettes trop saturées → agressives, illisibles
- ⚠️ Ignorer les préférences système `prefers-color-scheme`
- ⚠️ Dégradés HSL → zones grises dans l'interpolation
- ⚠️ 50 nuances de gris → sans variations de teinte, paraît froid
- ⚠️ Ne pas tester en niveaux de gris → info perdue pour daltoniens
- ⚠️ Trop de couleurs → pas de hiérarchie, confusion
- ⚠️ Utiliser le noir `#000000` → fatigue, halos (préférer `#1A1A1A`)
- ⚠️ Ne pas tester sur projecteur → couleurs différentes
- ⚠️ Choisir une palette sans contexte culturel → mal interprété