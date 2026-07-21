# Livrables techniques freelance — architecture, commandes, limites

Détail opérationnel des livrables paramétrables produits et testés. Localisation
type : `~/revenus-alternatifs/livrables/` avec un venv dédié `livrables-venv/`.

## Environnement
- venv dédié : `python3 -m venv livrables-venv` puis
  `pip install openpyxl pymupdf pdfplumber pytesseract Pillow requests`
- OCR système : `sudo apt-get install tesseract-ocr tesseract-ocr-fra poppler-utils`
- Invoquer avec : `./livrables-venv/bin/python <script>.py`

## 1. Extracteur PDF → Excel (service d'appel)
- Approche : tenter l'extraction native (PyMuPDF `page.get_text()`), mesurer la
  densité de texte/page ; si < seuil (~50 car/page) → bascule OCR (Tesseract
  `image_to_string` lang `fra+eng`, rendu page à 300 dpi via PyMuPDF pixmap).
- Champs : liste `CHAMPS = [(nom_colonne, regex_avec_1_groupe)]` — ADAPTER à chaque
  format client (facture ≠ bon de commande). Prévoir ~30 min d'ajustement.
- Sortie Excel (openpyxl) : 3 feuilles — "Données" (1 ligne/PDF), "Contrôle"
  (docs à vérifier : 0 champ rempli ou OCR pauvre), "Texte brut".
- Montants normalisés (`1 234,56` → `1234.56`) pour tri/calcul.
- Pièges regex rencontrés : un motif "total" trop large capture aussi "total ht" ;
  utiliser des alternatives précises (`total ttc|ttc|net à payer`) et `\bht\b` pour HT.
- Commande : `python extracteur_pdf_excel.py dossier_pdf/ sortie.xlsx [--ocr-force]`

## 2. Automation fusion + rapport
- Lit .xlsx (openpyxl read_only) et .csv (multi-encodage utf-8/latin-1/cp1252),
  fusionne, normalise les espaces, dédoublonne (clé configurable ou ligne entière),
  filtre colonnes, écrit Excel + rapport .txt.
- Pour toute AUTRE automatisation (mail, planification, API) : coder la spécifique
  à la demande du client — c'est là que la marge se fait (options payantes).
- Commande : `python automatisation_fusion_rapport.py dossier/ sortie.xlsx --rapport r.txt`

## 3. Chatbot RAG (données privées)
- Contrainte clé : AUCUNE grosse dépendance ML (pas de sentence-transformers/torch,
  trop lourd et souvent bloqué). TF-IDF fait main en pur stdlib.
- Recherche : tokenisation + stop-words FR, TF-IDF (idf lissé), score cosinus-like.
  SEUIL DE PERTINENCE à calibrer : 0.05 trop permissif (répond au hors-sujet),
  0.2 trop strict (perd les synonymes) ; 0.1 est un bon départ. Limite connue :
  TF-IDF matche les mots exacts, pas les synonymes → le mode LLM compense.
- 2 modes de génération : (a) vLLM local dispo (GET /v1/models OK) → appel API
  compatible OpenAI (`/v1/chat/completions`) pour une réponse naturelle sourcée ;
  (b) sinon → mode extractif (affiche le passage exact + source). Le livrable
  fonctionne donc TOUJOURS, même sans LLM.
- Interface web : `http.server` stdlib (pas de FastAPI requis) — page HTML + fetch
  POST /ask. Testable en mémoire (monter HTTPServer sur un thread, requêter, shutdown)
  sans laisser tourner de processus.
- Commande : `python chatbot_rag.py --docs dossier/ --port 8080` ou `--question "..."`

## Temps par mission (réel)
- Extracteur : ~30 min une fois rodé (le script fait le gros) → marge élevée sur 20 €.
- Automation standard : 1–2 h selon complexité ; les options (intégration, planification)
  sont la vraie marge.
- Chatbot RAG : 2–4 h (indexation + ajustement seuil + docs client). Mode LLM en offre
  Standard/Premium.
