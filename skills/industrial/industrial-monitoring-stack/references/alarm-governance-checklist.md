# Checklist de gouvernance des alertes et alarmes

## Avant de créer une alerte
- [ ] Une action claire est attendue.
- [ ] Un destinataire est identifié.
- [ ] Une persistance est définie.
- [ ] Le niveau de sévérité est défini.
- [ ] Le point source est fiable.
- [ ] Le bruit potentiel est évalué.

## Typologie recommandée
- Critique : arrêt, sécurité, perte de production majeure.
- Haute : dérive forte ou défaut bloquant probable.
- Moyenne : dérive à traiter sans urgence immédiate.
- Basse : information de suivi ou pré-alerte.

## Règles d'hygiène
- éviter les seuils sans temporisation ;
- éviter les alertes dupliquées dans plusieurs couches ;
- séparer défaut communication et défaut process ;
- séparer safety, robot, automate, énergie ;
- conserver une trace d'acquittement si l'alerte déclenche une intervention.
