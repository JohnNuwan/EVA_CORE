# Référence Scientifique : NoPA: Non-Parametric Online 3D Scene Graph Generation

*   **Auteurs** : Qi Xun Yeo, Seungjun Lee, Yan Li, Gim Hee Lee
*   **Identifiant arXiv** : 2607.00529
*   **Lien arXiv** : https://arxiv.org/abs/2607.00529

---

## Résumé Original de l'Article
Classic 3D scene graph generation approaches fail to work in real-time due to the heavy computational cost of environment mapping and the need to generate intermediate point-cloud representations. To alleviate this issue, a recent work eschews point clouds in favor of a lightweight Gaussian distribution for each object. This approximation drastically speeds up inference and enables real-time 3D scene graph generation. However, the representation has two key weaknesses. 1) Each object is approximated by a single 3D Gaussian, which causes a severe loss of 3D geometric detail. 2) The discrepancy between this approximation and the true object geometry exacerbates the inaccurate merging of object candidates during online inference. To address these issues, we propose NoPA, which represents each object as a separate non-parametric distribution. This formulation retains 3D geometric information while preserving real-time inference of the parametric Gaussian formulation. To build upon our novel object representation, we propose a tailored merging strategy to recover coherent object instances. Specifically, we leverage maximum mean discrepancy on kernel density estimates to enable robust merging of object candidates during online exploration while minimizing added computational complexity. The key is to maintain a fixed particle set per object. Furthermore, to rectify the relation loss caused by misclassified objects, NoPA propagates relationships between objects with high affinity. Experiments show that NoPA substantially outperforms current methods without sacrificing real-time inference speed.

---

## Synthèse et Analyse
L'intégration de cette recherche au sein de l'agent EVA permet de tirer parti des avancées en matière de structures agentiques et d'optimisations des LLM pour améliorer l'efficacité des workflows.
