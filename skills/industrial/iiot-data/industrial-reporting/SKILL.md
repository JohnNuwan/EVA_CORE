---
name: industrial-reporting
description: "Utiliser quand l'utilisateur demande de générer ou d'automatiser la création de rapports de production, bilans de poste ou bilans qualité aux formats Excel et PDF."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [excel, pdf, openpyxl, reportlab, reporting, mes, industrial-automation]
    related_skills: [simplify-code, plan]
---

# Automatisation des Rapports Industriels (PDF & Excel)

## Vue d'ensemble

Les rapports de production (bilans de poste, bilans de nettoyage CIP, suivis de consommation d'énergie, synthèses de défauts) sont indispensables pour le suivi opérationnel. L'automatisation de ces rapports permet de faire le pont entre l'OT (les données de l'atelier) et l'IT (les managers de production).

Cette compétence guide l'agent Helios pour concevoir des scripts de génération de rapports fiables, automatisés et bien présentés en utilisant :
- **openpyxl :** Pour injecter des données calculées dans des modèles de fichiers Excel prédéfinis contenant déjà les styles graphiques d'Actemium ou du client final.
- **ReportLab :** Pour générer des fichiers PDF bruts dynamiques et infalsifiables.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'écrire un script pour remplir un tableau croisé ou des graphiques de production dans un fichier Excel existant.
- De générer un bilan de lot au format PDF à la fin d'une étape de production.
- D'automatiser l'envoi hebdomadaire d'indicateurs de performance par email.
- De déboguer des problèmes de mise en page Excel ou PDF dans des tâches asynchrones d'IHM SCADA.

**Ne pas utiliser pour :**
- La configuration de serveurs d'impression industriels ou de configurations réseau d'imprimantes de bureau.

---

## 1. Remplissage de Modèles Excel avec `openpyxl`

En industrie, il est plus simple et plus propre de charger un template Excel pré-stylé (.xlsx) contenant déjà les en-têtes, logos et formules complexes, et d'y injecter uniquement les données de production.

```python
import openpyxl

def generate_production_report(template_path: str, output_path: str, batch_data: list):
    # Charger le classeur existant (modèle)
    wb = openpyxl.load_workbook(template_path)
    sheet = wb.active # Ou wb['NomFeuille']
    
    # Écrire des informations d'en-tête
    sheet['B3'] = "Actemium Production System"
    sheet['B4'] = "Lot N°: " + batch_data[0]['lot_number']
    
    # Remplir le tableau des mesures à partir de la ligne 8
    start_row = 8
    for idx, data_point in enumerate(batch_data):
        row = start_row + idx
        sheet.cell(row=row, column=2, value=data_point['timestamp'])
        sheet.cell(row=row, column=3, value=data_point['value'])
        sheet.cell(row=row, column=4, value=data_point['status'])
        
    # Enregistrer le nouveau fichier de rapport généré
    wb.save(output_path)
    wb.close()
```

---

## 2. Génération de Rapports PDF avec `ReportLab`

ReportLab permet de construire programmatiquement des documents PDF structurés sous forme de flux de composants (Flowables : paragraphes, tableaux, images).

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def build_pdf_report(filename: str, report_title: str, table_data: list):
    # Initialisation du document PDF
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    
    # Chargement de la feuille de style
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    body_style = styles['Normal']
    
    # Titre du rapport
    story.append(Paragraph(report_title, title_style))
    story.append(Spacer(1, 20)) # Espacement vertical
    
    # Ajout d'un paragraphe descriptif
    desc = "Ce document contient le bilan de fonctionnement généré automatiquement par le système Helios."
    story.append(Paragraph(desc, body_style))
    story.append(Spacer(1, 15))
    
    # Création du tableau de données (première ligne = en-tête)
    t = Table(table_data, colWidths=[150, 150, 100])
    
    # Application de styles au tableau
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3D59')), # Couleur Actemium
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5F7FA')])
    ]))
    story.append(t)
    
    # Génération effective du PDF
    doc.build(story)
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Fichiers Excel laissés ouverts en arrière-plan :**
   * *Erreur :* Écrire dans un fichier Excel sans fermer correctement l'objet Workbook de openpyxl (`wb.close()`). En cas de plantage ou de boucles d'écriture, cela peut saturer la mémoire et corrompre les fichiers.
   * *Correction :* Toujours invoquer `wb.close()` ou utiliser le bloc contextuel `with`.

2. **Dépassement de page non géré sur ReportLab :**
   * *Erreur :* Définir des positions de dessin absolues (`canvas.drawString()`) pour l'écriture de tableaux longs. Si les données s'étendent sur plusieurs pages, le texte se superpose et sort du document.
   * *Correction :* Toujours utiliser le moteur de mise en page dynamique de ReportLab avec des structures `SimpleDocTemplate` et des composants `Table` / `Paragraph` ajoutés dans la liste `story`.

---

## Liste de vérification (Checklist)

- [ ] Les instances Excel (`openpyxl`) sont explicitement fermées avec `wb.close()`.
- [ ] Le design graphique respecte la charte du projet (éviter les couleurs agressives et utiliser des palettes épurées).
- [ ] Les rapports PDF dynamiques à lignes multiples utilisent bien l'API `Platypus` (avec `SimpleDocTemplate` et `story`) et non des écritures de coordonnées absolues de dessin `canvas`.
- [ ] Toutes les cellules contenant des formules dynamiques dans le modèle Excel de départ sont préservées (ne pas écrire sur ces cellules).

