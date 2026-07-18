# Référence Scientifique : Crafter: A Multi-Agent Harness for Editable Scientific Figure Generation from Diverse Inputs

*   **Auteurs** : Haozhe Zhao, Shuzheng Si, Zhenhailong Wang, Zheng Wang, Liang Chen, Xiaotong Li, Zhixiang Liang, Maosong Sun, Minjia Zhang
*   **Identifiant arXiv** : 2605.30611
*   **Lien arXiv** : https://arxiv.org/abs/2605.30611

---

## Résumé Original de l'Article
Scientific figures are among the most effective means of communicating complex research ideas, yet producing publication-quality illustrations remains one of the most labor-intensive parts of paper preparation. Existing automated systems each target a single figure type under text-only input, leaving the diversity of types and conditions researchers actually use unaddressed; their raster outputs further cannot be locally revised. Because scientific figures are structured compositions of discrete semantic components, the localized errors generators produce on such layouts demand not a stronger backbone but a harness. We instantiate this harness in two complementary systems: Crafter, a multi-agent harness for figure generation that generalizes across figure types and input conditions without architectural changes, and CraftEditor, which applies the same pattern to convert raster outputs into editable SVGs. Moreover, we introduce CraftBench, a benchmark spanning three figure types and four input conditions with human quality annotation. Experiments show that Crafter substantially outperforms both standalone generators and the agentic baseline on PaperBanana-Bench and CraftBench, with ablations confirming each component's independent contribution; CraftEditor faithfully converts outputs into editable SVGs that surpass all baselines. Our code and benchmark are available at https://github.com/HaozheZhao/Crafter.

---

## Synthèse et Analyse
L'intégration de cette recherche au sein de l'agent EVA permet de tirer parti des avancées en matière de structures agentiques et d'optimisations des LLM pour améliorer l'efficacité des workflows.
