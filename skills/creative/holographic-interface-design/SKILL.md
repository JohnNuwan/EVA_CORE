---
title: "Design d'Interfaces Holographiques"
description: "Guide pour concevoir des interfaces holographiques pour jeux vidéo et applications — inspiré de Cortana (Halo), Iron Man, Horizon, et autres références. Shaders, particules, typographie, interactions gestuelles."
category: creative
tags: [holographic-ui, hologram, interface, sci-fi-ui, shader]
---

# Design d'Interfaces Holographiques

## Références Jeu Vidéo

### Cortana (Halo — 343 Industries)
- **Style**: Bleu cyan translucide, grille de données, projections 3D
- **Techniques**:
  - Shader de diffraction avec aberration chromatique
  - Particules lumineuses flottantes
  - Scanlines horizontales subtiles
  - Fondu entrée/sortie avec distortion
  - Palette: cyan (#00BFFF), blanc (#FFFFFF), orange alerte (#FF8C00)

### Aloy Focus (Horizon — Guerrilla Games)
- **Style**: Hologrammes verts/bleus, scan, analyse de données
- **Techniques**:
  - Projection de modèle 3D avec rotation lente
  - Lignes de connexion entre points d'intérêt
  - Cercles concentriques de scan
  - Données superposées en temps réel
  - Palette: vert (#00FF88), bleu (#0088FF), ambre (#FF8800)

### Iron Man / Tony Stark (Marvel's Avengers, Iron Man VR)
- **Style**: Rouge/or, interfaces de combat, AR temps réel
- **Techniques**:
  - Menus holographiques rotatifs
  - Données de vol superposées
  - Cibles et verrouillage avec lignes de tiret
  - État du réacteur ARC visible
  - Palette: rouge (#FF3300), or (#FFD700), bleu (#00AAFF)

### Dead Space (EA Motive)
- **Style**: Interface diégétique, hologrammes médicaux/militaires
- **Techniques**:
  - Barre de vie intégrée au costume (RIG)
  - Projections de carte 3D
  - Effets de distortion holographique
  - Palette: bleu froid, orange, blanc

## Shaders Holographiques

### Shader de Base (HLSL/GLSL)
```glsl
// Shader holographique de base
float4 HologramShader(float3 position, float3 normal, float2 uv)
{
    // Scanlines
    float scanline = sin(uv.y * _ScanlineCount + _Time.y * _ScanlineSpeed) * 0.5 + 0.5;
    
    // Fresnel effect (bords plus brillants)
    float fresnel = pow(1.0 - dot(normal, viewDir), _FresnelPower);
    
    // Distortion
    float2 distortion = float2(
        sin(uv.y * 10 + _Time.y * 2) * 0.01,
        cos(uv.x * 10 + _Time.y * 2) * 0.01
    );
    
    // Aberration chromatique
    float r = tex2D(_MainTex, uv + distortion).r;
    float g = tex2D(_MainTex, uv).g;
    float b = tex2D(_MainTex, uv - distortion).b;
    
    // Alpha flicker
    float flicker = sin(_Time.y * _FlickerSpeed) * 0.1 + 0.9;
    
    float4 color;
    color.rgb = float3(r, g, b) * _HologramColor * fresnel;
    color.a = scanline * fresnel * flicker * _Opacity;
    return color;
}
```

### Effets de Particules
- **Points lumineux**: Particules flottantes aléatoires
- **Lignes de connexion**: Lines entre points d'intérêt
- **Cercles de scan**: Anneaux qui s'expansent
- **Poussière numérique**: Petits carrés lumineux
- **Traînées**: Particules qui suivent le mouvement

## Patterns d'Interaction

### Navigation Gestuelle
| Geste | Action | Feedback |
|-------|--------|----------|
| Pincer | Sélectionner | Élément se soulève, glow |
| Glisser | Naviguer | Éléments suivent le doigt |
| Tourner | Rotation 3D | Objet pivote |
| Tape | Confirmer | Pulse, particules |
| Swipe haut | Fermer | Éléments disparaissent vers le haut |
| Spread | Zoom avant | Échelle augmente |

### Chronologie d'Interaction
```
1. Détection du geste (0ms)
2. Feedback visuel (50ms) — glow, highlight
3. Confirmation haptique (100ms) — vibration
4. Animation de transition (200-400ms) — élément se déplace
5. État final (500ms) — élément en place
```

## Design System Holographique

### Typographie
- **Police**: Sans-serif, futuriste (Exo 2, Orbitron, Rajdhani)
- **Taille**: 14-48px selon l'importance
- **Effets**: Glow, edge glow, scanline sur le texte
- **Anti-aliasing**: Activer le luma chroma subpixel pour la lisibilité

### Palette de Couleurs

| Usage | Couleur | Hex | Opacité |
|-------|---------|-----|---------|
| Primary | Cyan | #00BFFF | 80% |
| Secondary | Bleu | #0088FF | 60% |
| Accent | Orange | #FF8800 | 70% |
| Danger | Rouge | #FF3333 | 80% |
| Succès | Vert | #00FF88 | 70% |
| Texte | Blanc | #FFFFFF | 90% |
| Grille | Cyan foncé | #004466 | 30% |

### Grille de Base
- Lignes horizontales et verticales espacées de 32px
- Points d'intersection avec glow
- Rotation optionnelle en 3D
- Animation lente de défilement

## Implémentation Technique

### Unity (Shader Graph)
```
HologramShader:
├── PBR Master → Transparency
├── Time → Scanline UV
├── Fresnel Effect → Emission
├── Voronoi → Distortion
├── Chromatic Aberration → RGB Split
└── Flicker → Alpha Channel
```

### Unreal Engine (Material Editor)
```
HologramMaterial:
├── Material Domain → Surface
├── Blend Mode → Translucent
├── Lighting Model → Unlit
├── World Position Offset → Wobble
├── Pixel Depth Offset → Scanlines
└── Emissive Color → Fresnel + Pulse
```

### WebGL (Three.js)
```javascript
const hologramMaterial = new THREE.ShaderMaterial({
    uniforms: {
        time: { value: 0 },
        color: { value: new THREE.Color(0x00BFFF) },
        opacity: { value: 0.8 },
        scanlineCount: { value: 50 },
        flickerSpeed: { value: 2.0 }
    },
    vertexShader: vertexShader,
    fragmentShader: fragmentShader,
    transparent: true,
    side: THREE.DoubleSide
});
```

## Pitfalls

- **Trop transparent** → illisible
- **Trop d'effets** → perte de performance
- **Aberration chromatique excessive** → maux de tête
- **Pas de hiérarchie** → l'utilisateur ne sait pas où regarder
- **Animation trop rapide** → impossible à suivre
- **Ignorer l'accessibilité** → daltoniens ne voient pas les couleurs

## Voir Aussi

- [game-ai-character-design](../game-ai-character-design/SKILL.md)
- [animation-patterns-for-ui](../animation-patterns-for-ui/SKILL.md)
- [video-game-award-winning-ui](../video-game-award-winning-ui/SKILL.md)