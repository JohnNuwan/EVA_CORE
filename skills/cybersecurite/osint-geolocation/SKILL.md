---
name: osint-geolocation
description: Géolocalisation OSINT — analyse d'images, cartographie, repérage satellite, géotags et techniques de localisation avancées.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, geolocation, gps, cartographie, satellite, exif]
---

# Techniques de Géolocalisation OSINT

## 🎯 Description

Techniques de géolocalisation avancées pour déterminer la position géographique d'une cible à partir de photos, vidéos, données EXIF, points de repère, métadonnées et sources ouvertes. Couvre l'analyse d'images satellite, la cartographie interactive et la corrélation de données spatiales.

---

## 📋 Outils Essentiels

### Cartographie et Imagerie Satellite
| Outil | URL | Usage |
|-------|-----|-------|
| Google Earth | https://earth.google.com | Visualisation satellite 3D |
| Google Earth Pro | https://www.google.com/earth/versions/#earth-pro | Version pro gratuite |
| Google Maps | https://maps.google.com | Cartographie standard |
| OpenStreetMap | https://www.openstreetmap.org | Cartographie collaborative |
| Sentinel Hub | https://www.sentinel-hub.com/explore/sentinelplayground/ | Images satellite ESA |
| USGS EarthExplorer | https://earthexplorer.usgs.gov/ | Images satellite USGS |
| Zoom Earth | https://zoom.earth/ | Images satellite temps réel |
| Windy | https://www.windy.com | Météo et cartographie |
| ArcGIS | https://livingatlas.arcgis.com/en/browse/ | Atlas vivant ESRI |
| Bing Maps | https://www.bing.com/maps | Cartographie Microsoft |
| HERE Maps | https://here.com | Cartographie HERE |
| Wikimapia | https://wikimapia.org | Wiki cartographique |
| Mapillary | https://www.mapillary.com/app/ | Photos de rue crowdsourcées |
| KartaView | https://kartaview.org/map/ | Photos de rue alternatives |
| SAS Planet | https://www.sasgis.org/sasplaneta/ | Visualisation multi-satellite |

### Street View et Photos de Rue
| Outil | URL | Usage |
|-------|-----|-------|
| Instant Street View | https://www.instantstreetview.com | Street View rapide |
| Mapillary | https://www.mapillary.com/app/ | Photos de rue collaboratives |
| KartaView | https://kartaview.org/map/ | Photos de rue alternatives |

### Analyse EXIF et Métadonnées
| Outil | URL | Usage |
|-------|-----|-------|
| ExifTool | https://exiftool.org | Analyse EXIF complète |
| Jeffreys Viewer | https://exif.regex.info/ | Visualisation EXIF |
| JIMPL | https://jimpl.com/ | Lecteur EXIF en ligne |
| Pic2Map | https://www.pic2map.com/ | Géolocalisation depuis photo |
| TracePoint | https://kluter.github.io/TracePoint/ | Géolocalisation par rayons |

### Géolocalisation par IA
| Outil | URL | Usage |
|-------|-----|-------|
| GeoSpy | https://geospy.web.app/ | Géolocalisation par IA |
| GeoInfer | https://geoinfer.com | Géolocalisation sans EXIF |
| ReverseImageLocation | https://reverseimagelocation.com | Géolocalisation par IA |

---

## 🔧 Méthodologie

### Phase 1 : Extraction des Métadonnées
```bash
# ExifTool - extraction complète
exiftool photo.jpg

# Extraction GPS spécifique
exiftool -GPSLatitude -GPSLongitude -GPSAltitude photo.jpg

# ExifLooter (CLI)
pip install exiflooter
exiflooter -i photo.jpg
```

### Phase 2 : Analyse de l'Image

**Éléments à analyser dans une photo :**
- **Panneaux** : Langue, design, couleurs, logos
- **Végétation** : Espèces, densité, climat
- **Architecture** : Style, matériaux, période
- **Véhicules** : Plaques d'immatriculation, modèles
- **Éclairage** : Position du soleil, ombres, heure
- **Enseignes** : Noms de magasins, logos, langues
- **Drapeaux** : Nationalité, organisation
- **Montagnes** : Forme, neige, orientation
- **Routes** : Marquages, panneaux, signalisation
- **Prises électriques** : Type de prises (pays)

### Phase 3 : Analyse solaire et ombres
```bash
# SunCalc - position du soleil
# Naviguer vers https://www.suncalc.org/

# ShadowFinder - analyse d'ombres (Bellingcat)
# Naviguer vers https://kluter.github.io/ShadowFinder-Web
```

### Phase 4 : Cartographie et Corrélation
```bash
# Créer une carte de chaleur
# - Google My Maps (https://www.google.com/maps/about/mymaps/)
# - Batchgeo (https://batchgeo.com)
# - QGIS (https://qgis.org) - Open source

# Analyse de données GPS
# - GPSVisualizer (https://www.gpsvisualizer.com)
# - GeoJSON.io (https://geojson.io)
```

---

## 📊 Techniques Avancées

### Recherche par Coordonnées
```bash
# Convertir des coordonnées
# Degrés décimaux → DMS
# 48.8584, 2.2945 → 48°51'30"N, 2°17'40"E

# Google Maps
# Naviguer vers https://maps.google.com/?q=48.8584,2.2945

# What3Words
# Naviguer vers https://what3words.com
```

### Analyse de Réseaux WiFi
```bash
# WiGLE - wardriving database
# Naviguer vers https://wigle.net/

# Recherche par BSSID/MAC
# Naviguer vers https://wigle.net/search
```

### Géolocalisation YouTube
```bash
# YouTube Geofind
# Naviguer vers https://mattw.io/youtube-geofind/
```

### Géolocalisation Twitter
```bash
# OneMillionTweetMap
# Naviguer vers https://onemilliontweetmap.com
```

---

## 🛠️ Outils de Cartographie

### Open Source
| Outil | URL | Usage |
|-------|-----|-------|
| QGIS | https://qgis.org | SIG complet |
| Leaflet | https://leafletjs.com | Cartographie web |
| OpenLayers | https://openlayers.org | Cartographie avancée |
| GRASS GIS | https://grass.osgeo.org | Analyse spatiale |
| GeoGig | https://geogig.org | Gestion de versions géospatiales |

### Web
| Outil | URL | Usage |
|-------|-----|-------|
| Batchgeo | https://batchgeo.com | Géocodage par lots |
| Mapchart.net | https://mapchart.net | Cartes personnalisées |
| Scribble Maps | https://scribblemaps.com | Cartographie annotée |
| Zeemaps | https://www.zeemaps.com | Cartes collaboratives |
| MapHub | https://maphub.net | Cartes interactives |

---

## 📝 Exemple : Analyse d'une Photo

1. **Récupérer l'EXIF** : `exiftool photo.jpg`
2. **Vérifier les coordonnées GPS** dans les métadonnées
3. **Si pas de GPS** : Analyser visuellement :
   - Identifier les panneaux (langue, design)
   - Analyser la végétation (climat, région)
   - Noter l'architecture (style, période)
   - Observer le trafic (sens de conduite, plaques)
4. **Utiliser SunCalc** pour déterminer l'heure et la date
5. **Chercher sur Google Maps/Street View** les points de repère
6. **Confirmer avec Mapillary ou KartaView** pour plus de perspectives

---

## ⚠️ Pièges et Bonnes Pratiques

- **EXIF stripping** : Beaucoup de plateformes suppriment les EXIF (Twitter, Facebook). Vérifier les métadonnées avant partage.
- **Fausses coordonnées** : Les données GPS peuvent être falsifiées. Toujours recouper avec l'analyse visuelle.
- **Image satellite** : Les images peuvent être obsolètes de plusieurs mois/années. Vérifier la date de capture.
- **Ombre** : L'analyse d'ombres nécessite une date précise. Utiliser des almanachs solaires.
- **Légalité** : La géolocalisation sans consentement peut être illégale dans certaines juridictions.

---

## 🔗 Références

- https://www.bellingcat.com/category/resources/how-tos/ - Tutoriels Bellingcat
- https://github.com/jivoi/awesome-osint#geospatial-research-and-mapping-tools
- https://geospy.web.app/
- https://wigle.net/