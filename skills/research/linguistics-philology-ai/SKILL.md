---
name: linguistics-philology-ai
description: "Compétence niveau ingénieur/docteur en linguistique et philologie computationnelles. Couvre linguistique formelle, phonétique computationnelle, morphologie, syntaxe, sémantique, pragmatique, analyse de discours, philologie numérique, épigraphie ML, manuscrits, langues anciennes, documentation des langues, et linguistique de terrain assistée par IA."
category: research
tags: [linguistics, philology, computational-linguistics, nlp, ancient-languages, digital-humanities, semantics, phonetics, discourse-analysis]
arxiv_categories: [cs.CL, cs.CY, cs.AI, cs.DL]
---

# Compétence : Linguistique et Philologie Computationnelles (Computational Linguistics & Philology)

## Présentation

Cette compétence de niveau ingénieur/docteur couvre l'intersection de la linguistique théorique et formelle, de la philologie numérique, et de l'intelligence artificielle. Elle intègre la modélisation computationnelle de la phonétique, phonologie, morphologie, syntaxe, sémantique et pragmatique, ainsi que les méthodes de philologie numérique pour l'étude des manuscrits, des langues anciennes et menacées, et l'analyse de discours informatisée. Le practitioner maîtrise à la fois les formalismes linguistiques classiques et les techniques modernes de deep learning pour le traitement du langage.

---

## 1. Linguistique Formelle Computationnelle (Formal Computational Linguistics)

### Grammaires Formelles
- **Grammaires context-free (CFG)** : Chomsky hierarchy, CYK parsing, Earley algorithm, ambiguïté structurelle.
- **Grammaires catégorielles (CCG)** : combinatory categorial grammar, application/composition, type-raising, parsing CCG, CCGbank.
- **Tree-Adjoining Grammars (TAG)** : arbres élémentaires, substitution, adjonction, TAG parsing, XTAG, English TAG.
- **HPSG (Head-Driven Phrase Structure Grammar)** : types, feature structures, unification, ALE, LKB, TRALE.
- **LFG (Lexical Functional Grammar)** : c-structure (constituency) vs f-structure (functional), mapping, parsing LFG, ParGram.

### Parsing Syntaxique
- **Constituency Parsing** : PCFG, Treebank, Berkeley parser, neural constituency parsing (Self-Attentive, CRF).
- **Dependency Parsing** : transition-based (arc-standard, arc-eager, arc-hybrid), graph-based (MST, deep biaffine), pointer networks.
- **Universal Dependencies (UD)** : 300+ treebanks, 160+ langues, POS (UPOS), dependency relations, enhanced dependencies, CoNLL-U format.

### Morphologie Computationnelle
- **Finite-State Morphology** : HFST, Foma, Xerox xfst/lexc, two-level morphology, morphotactics, morphophonology.
- **Morphological Segmentation** : Morfessor, neural segmentation (byte-pair encoding, unigram LM), unsupervised.
- **Morphological Tagging** : génération et analyse, paradigm completion, canonical segmentation, SIGMORPHON shared tasks.

---

## 2. Phonétique et Phonologie ML (Phonetics & Phonology ML)

### ASR Multilingue
- **Architectures** : CTC (Connectionist Temporal Classification), RNN-T (Transducer), LAS (Listen-Attend-Spell), Wav2Vec 2.0, HuBERT, Whisper (OpenAI).
- **Multilingual ASR** : 100+ langues, low-resource fine-tuning, language identification, code-switching.
- **Applications** : transcription de terrain, documentation de langues menacées, dialectologie automatique.

### Reconnaissance Phonème
- **Phoneme Recognition** : TIMIT, LibriSpeech alignments, IPA-based systems, multilingual phoneme sets.
- **IPA (International Phonetic Alphabet)** : tables IPA, diacritics, suprasegmentals, IPA Chart, Unicode/OpenType IPA.
- **Phoneme-to-Audio** : text-to-speech (Tacotron 2, FastSpeech, VITS), voice cloning, expressive TTS.

### Dialectologie
- **Dialectometry** : distances linguistiques (Levenshtein acoustique, Levenshtein phonétique), clustering dialectal, dialect maps.
- **Automatic Dialect Identification** : classification de dialectes/accents, features prosodiques, phone recognition + ML.
- **Sound Change Modelling** : ML pour modélisation de changements phonétiques, diffusion lexicale, regular sound laws.

---

## 3. Sémantique et Pragmatique (Semantics & Pragmatics)

### Semantic Role Labeling (SRL)
- **PropBank / FrameNet / VerbNet** : roles sémantiques, frames, semantic arguments, verb-specific vs thematic roles.
- **SRL Neural** : BIO tagging, BERT-based, span-based, graph-based SRL, joint SRL + coreference.
- **Deep SRL** : implicit arguments, non-canonical constructions, cross-lingual SRL.

### Abstract Meaning Representation (AMR)
- **AMR Structure** : graphe acyclique dirigé, racine concept, relations (ARGO–ARG5, sémantique), reification.
- **AMR Parsing** : transition-based, graph-based, seq2seq, multi-task (AMR + SRL + NER).
- **AMR Generation** : text-to-AMR, AMR-to-text, AMR meaning similarity (Smatch, fine-grained).

### Discourse Parsing
- **Rhetorical Structure Theory (RST)** : relations de discours (noyau-satellite, multi-noyau), RST-DT, discours trees.
- **Penn Discourse TreeBank (PDTB)** : connecteurs, arguments, sens, relation types (Contingency, Comparison, Expansion, Temporal).
- **Discourse Parsing Neural** : discourse-aware Transformers, span-based, end-to-end, implicit discourse relation recognition.

### Implicature et DRT (Discourse Representation Theory)
- **Implicature computationnelle** : scalar implicature, pragmatic inference, rational speech act (RSA) models, Bayesian pragmatics.
- **DRT (Discourse Representation Theory)** : DRS construction, anaphora resolution, presupposition, binding, donkey sentences.
- **Inference Textuelle** : NLI (Natural Language Inference), RTE (Recognizing Textual Entailment), SNLI, MultiNLI, adversarial NLI.

---

## 4. Philologie Numérique (Digital Philology)

### Manuscrits et OCR
- **HOCR/ALTO/PageXML** : formats de transcription, segmentation en zones, lignes, mots.
- **OCR classique** : Tesseract (LSTM OCR), Kraken (OCR pour manuscrits), eScriptorium, Transkribus (HTR/Handwritten Text Recognition).
- **HTR (Handwritten Text Recognition)** : CTC, attention-based, Transformer-OCR, fine-tuning sur mains spécifiques.
- **OCR post-correction** : language models, BERT for OCR errors, edit distance, context-aware correction.

### Paléographie ML
- **Writer Identification** : scribe identification, deep learning pour caractéristiques d'écriture (Histogram of Oriented Gradients, SIFT, CNN).
- **Dating & Localization** : datation automatique de manuscrits, localisation géographique, classification de mains.
- **Character Recognition** : transcription diplomatique, ligature analysis, abbreviation expansion, paleographic XML.

### Stemmatology
- **SteMMA / Stemmatology** : stemma codicum, phylogenetic analysis, Lachmann method, cladistics, computer-assisted stemmatology.
- **Algorithmes** : Neighbor-Joining, UPGMA, Maximum Parsimony, Bayesian inference, RHM (Rhetorical History Model).
- **Text Reuse Detection** : intertextualité, parallels, quotation detection, text alignment (BLAST, Passim, TRACER, LASER).

### Édition Numérique
- **TEI (Text Encoding Initiative)** : XML TEI, guidelines, <teiHeader>, <msDesc>, <text>, critical apparatus, diplomatic edition.
- **Digital Scholarly Editions** : Ecdotique, édition synchronique/diachronique, génétique textuelle, EVT (Edition Visualization Technology).
- **Versioning** : collation, CollateX, Juxta, stemma-based, text alignment, diff structurel.

---

## 5. Langues Anciennes et Menacées (Ancient & Endangered Languages)

### Latin et Grec Ancien
- **Latin NLP** : lemmatisation (Latin lemmatizer, Collatinus, Whitaker's Words), POS tagging, dependency parsing Latin.
- **Ancient Greek NLP** : GREEK, Diorisis, Perseus Digital Library, treebanks (UD), Ancient Greek BERT.
- **Computational Classical Philology** : text mining classique, stylometry, authorship attribution, chronologie, toponymie.

### Sumérien, Maya, Hiéroglyphes
- **Sumerian (Cuneiform)** : translittération, grapheme-to-phoneme, RINAP, CDLI (Cuneiform Digital Library Initiative), ORACC.
- **Maya Hieroglyphs** : déchiffrement assisté, syllabaire, logogrammes, corpus Maya (Maya Hieroglyphic Database, THSM).
- **Egyptian Hieroglyphs** : Manuel de Codage, JSesh, Thesaurus Linguae Aegyptiae, automatic transcription.

### Documentation Automatique
- **Field Recording & Processing** : ELAN, Praat, FieldWorks, FLEx, survey tools, audio alignment (WebMAUS, Montreal Forced Aligner).
- **Automatic Transcription** : Whisper fine-tuning for low-resource, low-resource TTS, dictionary induction.
- **Data Collection** : elicitation, word lists (Swadesh, Leipzig-Jakarta), paradigms, Interlinear Glossed Text (IGT).

### Revitalisation
- **Language Learning AI** : systèmes tutoriels, chatbot pour langues menacées, gamification, AR/VR immersion.
- **Digital Archives** : preservation, online dictionaries, Treebank building, oral tradition transcription.
- **Community-based NLP** : participatory design, language data sovereignty, OCAP principles, NLP for language empowerment.

---

## 6. Analyse de Discours et Stylométrie (Discourse Analysis & Stylometry)

### Authorship Attribution
- **Méthodes** : fonction de style (n-grammes char, POS, mots fonction), machine learning (SVM, random forest, neural).
- **Deep Learning** : CNN, LSTM, BERT, Siamese networks pour attribution, cross-genre attribution.
- **Benchmarks** : PAN (CLEF), CCAT, IMDB62, Blog Authorship Corpus.

### Stylochronometry
- **Définition** : évolution du style d'un auteur au fil du temps, quantification du changement stylistique.
- **Méthodes** : rolling delta, sliding window, Burrows' Delta, Zeta, Iota, multivariate analysis.
- **Applications** : datation de textes non datés, analyse de carrière, évolution lexicale, syntactic change.

### Register Analysis
- **Text Types & Registers** : Biber's multi-dimensional analysis, dimensions (Narrative, Informational, etc.).
- **Corpus-based** : comptage de features (nouns, verbs, clauses, passives), factor analysis, PCA.
- **Register Classification** : ML pour classification de registre, genre, domain, NLP for Register Analysis (NRA).

---

## Références et Lectures

- **ArXiv** : cs.CL (Computation & Language), cs.CY (Computers & Society), cs.AI, cs.DL (Digital Libraries).
- **ACL / NAACL / EACL / COLING** : conférences majeures en linguistique computationnelle.
- **LREC (Language Resources and Evaluation Conference)** : ressources, corpus, standards.
- **SIGMORPHON / SIGDIAL / SEMEVAL** : workshops spécialisés morphologie, discours, évaluation.
- **Digital Humanities Conference (DH / ADHO)** : philologie numérique, TEI, coding.
- **Perseus Digital Library / TLG / PHI / CETEDOC** : corpus classiques numériques.
- **Linguistic Society of America (LSA) / SLE** : linguistique générale et computationnelle.
- **Réseau** : CLARIN (Common Language Resources and Technology Infrastructure), DARIAH.