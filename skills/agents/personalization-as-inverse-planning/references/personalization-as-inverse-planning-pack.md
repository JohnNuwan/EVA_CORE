# Référence Scientifique : Personalization as Inverse Planning: Learning Latent Design Intents for Agentic Slide Generation via Structural Denoising

*   **Auteurs** : Tianci Liu, Zihan Dong, Linjun Zhang, Haoyu Wang, jing Gao, Emre Kiciman, Ranveer Chandra, Wei-Ting Chen
*   **Identifiant arXiv** : 2607.00407
*   **Lien arXiv** : https://arxiv.org/abs/2607.00407

---

## Résumé Original de l'Article
Slide design requires personalizing both deck themes and page layouts. Yet, current AI agent-based methods struggle with fine-grained, page-level design. Solely relying on prespecified templates or user verbose instructions, they fail to capture latent design intents, leaving Page-level Slide Personalization (PSP) unresolved. To close this gap, this work formulates PSP as an inverse planning problem. We propose to learn a design intent without assuming any knowledge of the specific executing tools (e.g., PowerPoint, Beamer) being used. However, relinquishing control over these tools makes the problem intractable to optimize end-to-end. To overcome this, we propose SPIRE, a principled framework to solve PSP approximately. By intentionally corrupting the visual structures of clean slides, SPIRE creates a verifiable task to denoise the corruption, whereby two agents learn to collaboratively refine executable designs via reinforcement learning (RL). We present a proof that structural denoising is a consistent surrogate for PSP, and that the multi-agent formulation strictly reduces policy gradient variance in RL. Extensive experiments demonstrate the superiority of SPIRE.

---

## Synthèse et Analyse
L'intégration de cette recherche au sein de l'agent Helios permet de tirer parti des avancées en matière de structures agentiques et d'optimisations des LLM pour améliorer l'efficacité des workflows.
