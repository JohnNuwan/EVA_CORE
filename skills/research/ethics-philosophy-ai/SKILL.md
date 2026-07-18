---
name: ethics-philosophy-ai
description: "Compétence niveau ingénieur/docteur en éthique et philosophie de l'IA. Couvre l'éthique algorithmique, la philosophie de l'esprit, la conscience artificielle, les théories de l'équité, la responsabilité morale des machines, la philosophie des sciences cognitives, l'épistémologie de l'IA, et le governance framework."
category: research
tags: [ethics, philosophy, ai-ethics, philosophy-of-mind, fairness, moral-philosophy, epistemology, governance, ai-safety]
arxiv_categories: [cs.CY, cs.AI, cs.HC, cs.LG, econ.GN, physics.soc-ph]
---

# Compétence : Éthique et Philosophie de l'IA (Ethics & Philosophy of AI)

## Présentation

Cette compétence de niveau ingénieur/docteur couvre les fondements philosophiques et les cadres éthiques de l'intelligence artificielle. Elle intègre l'éthique algorithmique (biais, équité, transparence), la philosophie de l'esprit et la question de la conscience artificielle, les théories de la justice distributive appliquées à l'IA, la responsabilité morale des systèmes autonomes, la philosophie des sciences cognitives, l'épistémologie de la connaissance computationnelle, et les cadres de gouvernance de l'IA (AI Safety, régulation, interprétabilité). Le practitioner est capable d'analyser, critiquer et concevoir des systèmes d'IA alignés sur des valeurs éthiques et philosophiques fondamentales.

---

## 1. Éthique Algorithmique (Algorithmic Ethics)

### Fairness Metrics (Métriques d'Équité)
- **Group Fairness** : demographic parity (statistical parity difference), equalized odds (equal opportunity), predictive parity (positive predictive value parity), calibration parity.
- **Individual Fairness** : similar individuals treated similarly — distance metrics (Euclidean, Mahalanobis), fairness through awareness/unawareness.
- **Causal Fairness** : total effect, direct/indirect discrimination, counterfactual fairness, path-specific effects, fairness via causal DAGs.
- **Limitations & Trade-offs** : impossibility theorem (Chouldechova, Kleinberg), incompatibilité entre métriques, fairness-accuracy Pareto frontier.

### Bias Detection (Détection de Biais)
- **Types de biais** : data bias (historical, representation, measurement), algorithmic bias (optimization, aggregation, evaluation), deployment bias (transfer, feedback loop).
- **Bias Audit Methods** : disparate impact test (80% rule, 4/5ths rule), bias audit frameworks (AIF360, Fairlearn, What-If Tool), intersectional bias analysis.
- **Bias in LLMs** : WinoBias, WinoGender, StereoSet, CrowS-Pairs, BBQ (Bias Benchmark for QA), TruthfulQA, BOLD.
- **Bias Mitigation** : pre-processing (reweighing, data augmentation), in-processing (adversarial debiasing, constraint optimization), post-processing (threshold adjustment, calibration).

### Ethical Frameworks
- **Principialisme** : beneficence, non-maleficence, autonomy, justice (Beauchamp & Childress) — adapté à l'IA.
- **Consequentialism vs Deontology vs Virtue Ethics** : utilitarianism (Bentham, Mill), categorical imperative (Kant), virtue ethics (Aristotle, MacIntyre) — appliqué à l'IA.
- **AI Ethics Guidelines Global Inventory (160+)** : OECD AI Principles, EU High-Level Expert Group, UNESCO Recommendation, Beijing AI Principles, Asilomar AI Principles.
- **Value Alignment** : alignment problem (Russell, Norvig, Bostrom), corrigibility, value loading, Coherent Extrapolated Volition (CEV), Inverse Reinforcement Learning for value learning.

---

## 2. Philosophie de l'Esprit et Conscience (Philosophy of Mind & Consciousness)

### Turing Test & Chinese Room
- **Turing Test (1950)** : jeu d'imitation, critique (Searle, Blockhead argument), Total Turing Test, minimal Turing Test.
- **Chinese Room (Searle, 1980)** : syntax vs semantics, système vs agent, replies (Boden, Dennett, Churchland, Block), Strong AI vs Weak AI.
- **Standard AI vs Human-level AI** : symbol grounding problem, intentionality, original vs derived intentionality.

### Global Workspace Theory (GWT)
- **Baars (1988)** : global workspace, competition, conscious access, spotlight metaphor, recursive consciousness.
- **Global Workspace in AI** : GWT-inspired architectures, attention as global workspace, Transformers as global workspace, conscious AI proposals.
- **Critiques** : hard problem of consciousness (Chalmers), explanatory gap (Levine), qualia, what-it-is-like-ness (Nagel).

### Integrated Information Theory (IIT)
- **Tonomi (2004, 2014, 2023)** : phi (Φ), integrated information, cause-effect repertoire, main complex, IIT 3.0/4.0.
- **Computational IIT** : PyPhi, IIT computation, limitations (Φ calculabilité), IIT and AI systems.
- **Critiques** : IIT implique panpsychisme, IIT favorise réseaux small-world, counter-intuitive implications (grid cells high Φ).

### Panpsychism & Phenomenal Consciousness
- **Panpsychism** : consciousness as fundamental (Strawson, Goff, Chalmers), combination problem, constitutive vs emergent panpsychism.
- **Russellian Monism** : intrinsic nature of matter, protophenomenal properties, categorical vs dispositional.
- **AI Consciousness Debate** : can AI be conscious? functionalism vs biological naturalism (Searle), higher-order theories, attention schema theory (Graziano).

---

## 3. Théories de l'Équité (Theories of Justice & Fairness)

### Rawls (Justice as Fairness)
- **Original Position & Veil of Ignorance** : principles of justice (liberty principle, difference principle, fair equality of opportunity).
- **Rawlsian AI** : algorithmic fairness through veil of ignorance, maximin fairness, difference principle in ML.
- **Critiques** : Nozick (libertarian), Sen (capabilities), communitarianism, Rawls-Habermas debate.

### Utilitarianism
- **Classical Utilitarianism** : Bentham, Mill — greatest happiness principle, hedonic calculus, rule vs act utilitarianism.
- **Utilitarianism in AI** : utilité agrégée, social welfare function, sum/avg min/max utilitarianism, risk-neutral AI.
- **Critiques** : rights violations, demandingness, aggregation problem, repugnant conclusion (Parfit).

### Capability Approach (Sen, Nussbaum)
- **Capabilities** : functioning vs capabilities, central human capabilities (Nussbaum), freedom, agency.
- **AI & Capabilities** : capability-based fairness, AI for human development, well-being metrics, doontology.
- **Applications** : AI for the Global South, digital divide, capability-sensitive design.

### Distributive Justice in AI
- **Allocation** : justice in AI resource allocation (credit, healthcare, education), group vs individual fairness.
- **Priority & Equality** : sufficientarianism, prioritarianism, egalitarianism — formalisation mathématique pour l'IA.
- **Equality of Opportunity** : Roemer's equality of opportunity, effort vs circumstances, nivellement.

---

## 4. Responsabilité Morale (Moral Responsibility)

### Moral Agency
- **Machine Ethics** : bottom-up (learning from examples), top-down (explicit rules), hybrid approaches.
- **Requirements for Moral Agency** : intentionality, autonomy, rationality, moral understanding, free will.
- **Levels of Agency** : causal agency, intentional agency, moral agency, full moral agency (Floridi & Sanders).
- **Machine Morality** : Asimov's Laws, extension, W. D. Ross's prima facie duties, moral particularism.

### Accountability Gaps
- **Responsibility Gap** : who is responsible when an autonomous system causes harm? (Matthias, Danaher, de Sio).
- **Accountability** : blameworthiness, backward-looking vs forward-looking, strict vs fault liability.
- **Solutions** : strict liability, enterprise liability, design accountability, algorithmic impact assessment, vicarious liability.

### Responsibility Attribution
- **Legal Frameworks** : product liability (EU Directive 85/374, AI Liability Directive), tort, fault, negligence.
- **AI Act Liability** : classification (unacceptable, high, limited, minimal risk), liability for high-risk AI systems.
- **Legal Personhood** : electronic personhood, legal fictions, corporate personhood analogy, rights/duties debate.

### Tort Liability
- **Negligence** : duty of care, breach, causation, damages — AI as tool vs AI as agent.
- **Strict Liability** : defective products, design defects, manufacturing defects, failure to warn.
- **Vicarious Liability** : employer/principal liability for AI agents, scope of employment, apparent authority.

---

## 5. Philosophie des Sciences Cognitives (Philosophy of Cognitive Science)

### Embodied Cognition & 4E Cognition
- **Embodied** : cognition shaped by body (Varela, Thompson, Rosch, Lakoff, Johnson).
- **Embedded** : cognition situated in environment, ecological psychology (Gibson), affordances.
- **Enacted** : cognition as enaction, sensorimotor coupling, autopoiesis (Maturana, Varela).
- **Extended** : extended mind thesis (Clark, Chalmers), cognitive offloading, active externalism, parity principle.
- **Implications for AI** : embodied AI, robotic cognition, situatedness, world models, sensorimotor contingencies.

### Connectionism vs Symbolism
- **Classical Symbolic AI** : physical symbol system hypothesis (Newell, Simon), symbolic representations, GOFAI.
- **Connectionism** : distributed representations, sub-symbolic, PDP models (Rumelhart, McClelland), backpropagation.
- **Hybrid Systems** : neural-symbolic integration, neuro-symbolic AI, logic tensor networks, differentiable programming.
- **Debate** : systematicity, compositionality, productivity (Fodor, Pylyshyn), connectionist counter-arguments (Smolensky, Chalmers).

### Philosophy of AI & Cognitive Science
- **Marr's Three Levels** : computational, algorithmic, implementational — critique (Churchland, Sejnowski).
- **Predictive Processing** : free energy principle (Friston), predictive coding, active inference, Bayesian brain.
- **Language of Thought Hypothesis (LOTH)** : Fodor — mentalese, compositionality, productivity, systematicity.

---

## 6. Épistémologie de l'IA (Epistemology of AI)

### Knowledge Representation
- **Formal Ontologies** : OWL, RDF, description logics, Cyc, WordNet, upper ontologies (BFO, DOLCE, SUMO).
- **KR & AI** : frames, scripts, semantic networks, conceptual graphs, Bayesian networks.
- **Epistemic Logic** : knowledge, belief, common knowledge, Kripke semantics, dynamic epistemic logic.

### Uncertainty & Bayesian Epistemology
- **Bayesian Epistemology** : degrees of belief, conditionalization, Bayesian updating, probability as logic (Cox, Jaynes).
- **Uncertainty in AI** : aleatoric vs epistemic uncertainty, Bayesian neural networks, MC dropout, ensemble methods.
- **Imprecise Probability** : credal sets, Dempster-Shafer theory, possibility theory, fuzzy logic.

### Machine Discovery
- **Scientific Discovery** : Bacon, AM, Kepler, DENDRAL — AI systems for scientific discovery (Langley, Simon).
- **Automated Reasoning** : inductive logic programming, equation discovery, causal discovery.
- **AI for Science** : deep learning for physics, chemistry, biology, ML for causality, AI-Descartes, AlphaFold, ML for theorem proving.

---

## 7. Governance & AI Safety

### AI Safety
- **Alignment Problem** : outer alignment (reward misspecification), inner alignment (mesa-optimization), goal misgeneralization.
- **Technical Safety** : robust human imitation, adversarial robustness, interpretability (mechanistic, concept-based, feature visualization).
- **Corrigibility** : shut-down problem, off-switch, corrigibility, learning to defer, human oversight.
- **Safety Frameworks** : ARC, MIRI, DeepMind Safety, Anthropic's alignment research, evals, red teaming.

### Régulation
- **EU AI Act** : risk-based approach, prohibited practices (social scoring, real-time biometric), high-risk obligations, transparency, governance, fines.
- **US Executive Orders** : Safe, Secure, and Trustworthy AI (2023), Defense Production Act, NIST AI Risk Management Framework.
- **UNESCO Recommendation** : global ethical framework, 193 member states, values, principles, policy areas.
- **Autres** : China AI regulations, G7 Hiroshima AI Process, OECD AI Principles, Council of Europe Framework Convention.

### Interpretability Requirements
- **Explainable AI (XAI)** : LIME, SHAP, integrated gradients, saliency maps, Grad-CAM, concept bottleneck models.
- **Mechanistic Interpretability** : activation patching, circuit discovery, sparse autoencoders, dictionary learning, SAE (Bricken et al.)
- **Transparency by Design** : GDPR right to explanation, EU AI Act transparency, algorithmic auditing, model cards, datasheets, impact assessments.

---

## Références et Lectures

- **ArXiv** : cs.CY (Computers & Society), cs.AI, cs.HC (Human-Computer Interaction), cs.LG, econ.GN, physics.soc-ph.
- **FAccT (ACM Conference on Fairness, Accountability, and Transparency)** : conférence de référence.
- **AIES (AAAI/ACM Conference on AI, Ethics, and Society)** : éthique et IA.
- **Philosophy of Science / Mind / Ethics** : revues académiques.
- **Journal of Artificial Intelligence Research (JAIR), Minds and Machines, Ethics and Information Technology**.
- **Rapports** : AI Now Institute, Ada Lovelace Institute, Data & Society, Stanford HAI.
- **Ouvrages fondamentaux** : *Superintelligence* (Bostrom), *Weapons of Math Destruction* (O'Neil), *The Alignment Problem* (Christian), *Consciousness Explained* (Dennett), *The Myth of the Machine* (Mumford).
- **AI Ethics Guidelines Global Inventory** : 160+ cadres d'éthique (algorithmwatch.org).