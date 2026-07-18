---
name: computational-biology-genomics
description: "Compétence en recherche en biologie computationnelle et génomique suivie sur arXiv sous q-bio.GN, q-bio.BM et domaines connexes. Couvre la génomique comparative, l'assemblage de génomes, la transcriptomique, l'épigénomique, la métagénomique, la phylogénie computationnelle, et les modèles de langage pour la génomique."
category: research
arxiv_categories:
  - q-bio.GN
  - q-bio.BM
  - cs.LG
  - cs.AI
---

# Compétence : Biologie Computationnelle et Génomique

## Présentation

Cette compétence couvre la recherche en biologie computationnelle et génomique : génomique comparative, assemblage de génomes, transcriptomique, épigénomique, métagénomique, phylogénie computationnelle et modèles de langage pour la génomique. Suivi principal sur arXiv sous **q-bio.GN** (Genomics) et **q-bio.BM** (Biomolecules), avec des extensions vers cs.LG et cs.AI pour les approches d'apprentissage automatique.

---

## 1. Génomique Computationnelle

### Assemblage de génomes
- Assembleurs De Bruijn graph (Velvet, SPAdes, MEGAHIT)
- Assembleurs overlap-layout-consensus (Canu, Flye)
- Assemblage long-reads (PacBio, ONT) vs short-reads (Illumina)
- Assemblage métagénomique et multi-échantillons
- Évaluation de la qualité : N50, L50, complétude (BUSCO)

### Alignement de séquences
- Alignement par paires : Needleman-Wunsch, Smith-Waterman
- Alignement multiple : Clustal, MAFFT, MUSCLE
- Alignement de lectures : BWA, Bowtie2, STAR, minimap2
- Alignement génomique : MUMmer, LASTZ

### Détection de variants
- SNV/SNP calling : GATK, Samtools, FreeBayes
- Indel calling et structural variant calling
- CNV (Copy Number Variation) detection
- Variants rares et germline vs somatic

### Annotation de génomes
- Prédiction de gènes : AUGUSTUS, BRAKER, GeneMark
- Annotation fonctionnelle : InterProScan, eggNOG, BLAST2GO
- Éléments répétés, transposons, non-coding RNAs
- Annotation comparative : orthologie, synténie

---

## 2. Transcriptomique et Expression Génique

### RNA-seq
- Quantification d'expression : RSEM, Salmon, kallisto
- Analyse différentielle : DESeq2, edgeR, limma
- Analyse de splicing : rMATS, MISO, SUPPA
- Fusion de gènes et transcrits de novo

### Single-cell RNA-seq (scRNA-seq)
- Normalisation et imputation : SCTransform, sctransform
- Clustering : Seurat, Scanpy, Leiden clustering
- Trajectoire et pseudotemps : Monocle, Slingshot, URD
- Annotation cellulaire : SingleR, CellTypist, scmap
- Intégration multi-échantillons : Harmony, scVI, Scanorama

### Spatial Transcriptomics
- Méthodes basées sur image : MERFISH, seqFISH, STARmap
- Méthodes basées sur capture spatiale : Visium, Slide-seq, Slide-tags
- Intégration transcriptomique spatiale avec scRNA-seq
- Déconvolution spatiale et analyse de niches

### Analyse différentielle et réseaux
- Régression et modèles linéaires pour l'expression
- Réseaux de co-expression (WGCNA)
- Inférence de réseaux de régulation génique
- Enrichissement fonctionnel : GO, KEGG, GSEA

---

## 3. Épigénomique

### ChIP-seq
- Peak calling : MACS2, SPP, Genrich
- Analyse différentielle de la liaison (diffbind)
- Motif discovery : MEME, HOMER, STREME
- ChIP-seq vs ChIPmentation vs CUT&Tag

### ATAC-seq
- Open chromatin detection et peak calling
- Analyse de l'accessibilité différentielle
- Footprinting transcriptionnel (TOBIAS, Wellington)
- Intégration ATAC-seq + RNA-seq

### Méthylation de l'ADN
- Bisulfite sequencing (WGBS, RRBS)
- Analyse différentielle de méthylation
- Méthylation et régulation génique
- Méthylation dans le développement et les maladies

### Modifications histones
- Analyse des marques histones (H3K4me3, H3K27ac, H3K27me3)
- Chromatin states et segmentation (ChromHMM, Segway)
- Hi-C et conformation chromatinienne (hiclib, cooltools)
- Compartiments A/B et TADs (Topologically Associating Domains)

---

## 4. Phylogénie et Évolution

### Arbres phylogénétiques
- Maximum de parcimonie (MP)
- Maximum de vraisemblance (ML) : RAxML, IQ-TREE, PhyML
- Inférence bayésienne : MrBayes, BEAST, RevBayes
- Distance-based : Neighbor-Joining, FastME

### Horloge moléculaire
- Horloge stricte vs relâchée
- Datation moléculaire et temps de divergence
- Estimation des taux de mutation et de substitution

### Détection de sélection
- dN/dS ratio (Ka/Ks)
- Tests de sélection positive (PAML, HyPhy)
- Sélection balancée, sélection neutre, balayages sélectifs

### Génomique évolutive
- Génomique des populations (θ, Tajima's D, Fst, π)
- Phylogénomique : arbres d'espèces vs arbres de gènes
- Évolution des génomes : duplications, réarrangements, pertes
- GWAS et cartographie génétique (QTL, association studies)

---

## 5. Métagénomique et Microbiome

### Taxonomie
- Amplicon 16S/ITS : QIIME2, DADA2, mothur
- Shotgun métagénomique : Kraken2, Bracken, MetaPhlAn
- Profilage taxonomique et abondance relative
- Nouveaux génomes et espèces (SGB, MAGs)

### Analyse fonctionnelle
- Annotation fonctionnelle métagénomique : HUMAnN3, PICRUSt
- Voies métaboliques et enzymes : KEGG, MetaCyc
- Résistome : MEGARes, CARD, ResFinder
- Gènes de virulence et facteurs de pathogénicité

### Métagénomique quantitative
- Assemblage et binning : MetaBAT2, MaxBin2, CONCOCT
- MAGs (Metagenome-Assembled Genomes) : DAS Tool, metaWRAP
- Métagénomique comparative
- Études longitudinales et time-series du microbiome

---

## 6. Modèles de Langage pour la Génomique

### Modèles fondation
- **DNABERT** : BERT adapté aux séquences ADN
- **Nucleotide Transformer** : Transformer pré-entraîné sur génomes
- **DNAGPT** : GPT pour séquences génomiques
- **Evo** : modèles de fondation génomique à grande échelle

### Applications des modèles de langage génomique
- Prédiction de régulation (promoteurs, enhancers, épissage)
- Classification de séquences (codantes, non-codantes, régulatrices)
- Détection de variants pathogènes (effet des mutations)
- Conception de séquences (protein engineering, synthetic biology)

### Autres approches ML en génomique
- Deep learning pour le splicing prediction (SpliceAI)
- Réseaux de neurones convolutionnels pour ChIP-seq/TF binding
- Graph neural networks pour les réseaux de régulation
- Apprentissage auto-supervisé en biologie moléculaire

---

## Catégories arXiv

- **q-bio.GN** — Genomics (génomique, séquençage, variants)
- **q-bio.BM** — Biomolecules (structures, ARN, protéines)
- **cs.LG** — Machine Learning (modèles de langage génomique, deep learning)
- **cs.AI** — Artificial Intelligence (applications IA en biologie)

## Articles Notables

- DNABERT, Nucleotide Transformer, Evo — modèles de fondation génomique
- SpliceAI — prédiction d'épissage par deep learning
- Single-cell foundation models — scGPT, Geneformer
- Spatial transcriptomics methods — récents développements

## Stratégies de veille

1. Surveiller les nouvelles soumissions sur **q-bio.GN** (quotidien)
2. Suivre **q-bio.BM** pour les biomolécules et structures
3. Conférences clés : RECOMB, ISMB, ECCB, BIBM, PSB
4. Journaux : Bioinformatics, Genome Biology, PLOS Computational Biology, Nature Methods
5. Mots-clés : genomics, transcriptomics, epigenomics, metagenomics, single-cell, DNA language model, phylogenomics