---
name: autolisp-cad-automation
description: "Développer en AutoLISP pour automatiser AutoCAD et la CAO."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [windows]
metadata:
  tags: [autolisp, lisp, autocad, cad, electrical-drawings, dxf, dcl]
  related_skills: [industrial-programming-languages, industrial-exchange-formats]
---

# Programmation AutoLISP pour la CAO Électrique et l'Automatisation AutoCAD

Cette compétence encadre l'écriture de scripts et de programmes en AutoLISP destinés à piloter AutoCAD (ou GstarCAD/BricsCAD) afin d'automatiser le dessin de schémas électriques industriels, l'extraction de nomenclatures de composants et le traitement par lots de plans d'armoires.

---

## 1. Fondements de Syntaxe AutoLISP et Listes DXF

AutoLISP s'appuie sur le paradigme LISP. Tout code ou donnée est représenté sous forme de liste parenthésée (S-expression). Les entités de dessin AutoCAD sont stockées et manipulées sous forme de listes de paires pointées DXF.

### Syntaxe de base
* **Définition de fonction/commande** : `defun` définit une fonction. Le préfixe `c:` rend la fonction appelable directement depuis la ligne de commande AutoCAD comme une commande native.
  ```lisp
  (defun c:HelloActemium ()
    (alert "Logiciel d'automatisation de BE Actemium actif.")
    (princ)
  )
  ```
* **Variables et calculs** : L'affectation s'effectue via `setq`.
  ```lisp
  (setq distance 150.0)
  (setq point_depart (list 0.0 0.0 0.0))
  ```

---

## 2. Sélection d'Objets et Modification d'Entités DXF

### Sélection par Filtres (`ssget`)
Permet de cibler précisément des objets de dessin (par exemple, uniquement les blocs nommés "SYM_DISJONCTEUR" sur le calque "E_PUISSANCE").
```lisp
(setq selection 
  (ssget "X" 
    '(
      (0 . "INSERT")                   ; Entite de type Bloc
      (2 . "SYM_DISJONCTEUR")          ; Nom du bloc CAO
      (8 . "E_PUISSANCE")              ; Calque specifique
    )
  )
)
```

### Lecture et Modification (`entget` / `entmod` / `entupd`)
Chaque entité de dessin possède un nom unique (`Entity Name`). La fonction `entget` extrait sa liste DXF. Pour la modifier, on reconstruit la paire pointée et on applique `entmod`.
```lisp
(setq nom_entite (car (entsel "\nSelectionnez le repere de fil: ")))
(setq donnees_dxf (entget nom_entite))

; Le code DXF 1 represente la valeur textuelle d'une entite texte
; Remplacement de la valeur actuelle par "W01" (repere de fil)
(setq ancienne_paire (assoc 1 donnees_dxf))
(setq nouvelle_paire (cons 1 "W01"))
(setq donnees_dxf (subst nouvelle_paire ancienne_paire donnees_dxf))

; Application de la modification dans la base de donnees de dessin
(entmod donnees_dxf)
(entupd nom_entite) ; Rafraîchissement graphique de l'entite
```

---

## 3. Exemple de Script Complet (Repérage automatique de Borniers)

Ce programme AutoLISP recherche tous les blocs d'attributs de bornes électriques et y injecte le préfixe d'origine ou d'armoire configuré.

```lisp
(defun c:RenommerBornes ( / ss i ent dxf nom_bornier nouvelle_valeur assoc_dxf)
  (princ "\n--- Lancement de la macro de reperage de bornes ---")
  
  ; Capture de toutes les bornes (blocs contenant "BORNE_REP")
  (setq ss (ssget "X" '((0 . "INSERT") (2 . "*BORNE_REP*"))))
  
  (if ss
    (progn
      (setq i 0)
      (while (< i (sslength ss))
        (setq ent (ssname ss i))
        ; Parcourir les attributs du bloc pour trouver le repere
        (setq sub_ent (entnext ent))
        (setq continuer T)
        (while (and sub_ent continuer)
          (setq dxf (entget sub_ent))
          (if (= (cdr (assoc 0 dxf)) "ATTRIB")
            (progn
              ; Si le tag de l'attribut est "BORNE_ID"
              (if (= (cdr (assoc 2 dxf)) "BORNE_ID")
                (progn
                  (setq valeur_actuelle (cdr (assoc 1 dxf)))
                  ; Ajouter le prefixe d'armoire "-X1:"
                  (setq nouvelle_valeur (strcat "-X1:" valeur_actuelle))
                  (setq assoc_dxf (assoc 1 dxf))
                  (setq dxf (subst (cons 1 nouvelle_valeur) assoc_dxf dxf))
                  (entmod dxf)
                  (entupd sub_ent)
                )
              )
              (setq sub_ent (entnext sub_ent))
            )
            (setq continuer nil) ; Fin des attributs du bloc
          )
        )
        (setq i (1+ i))
      )
      (princ (strcat "\nTraite : " (itoa i) " bornes avec succes."))
    )
    (princ "\nAucun bloc de borne trouve dans ce plan.")
  )
  (princ)
)
```

---

## 4. Interfaces Graphiques Associées avec DCL (Dialog Control Language)

Pour permettre au dessinateur-projeteur du bureau d'études de configurer les variables, AutoLISP s'interface avec des fichiers `.dcl` de définition de boîtes de dialogue.

```text
// Fichier config_bornes.dcl
config_bornes : dialog {
  label = "Configuration Reperage Actemium";
  : edit_box {
    label = "Prefixe Armoire :";
    key = "eb_prefix";
    edit_width = 15;
  }
  ok_cancel;
}
```

Chargement et appel en AutoLISP :
```lisp
(setq dcl_id (load_dialog "config_bornes.dcl"))
(if (new_dialog "config_bornes" dcl_id)
  (progn
    (set_tile "eb_prefix" "-X1") ; Valeur par defaut
    (action_tile "accept" "(setq prefixe (get_tile \"eb_prefix\")) (done_dialog 1)")
    (action_tile "cancel" "(done_dialog 0)")
    (setq resultat (start_dialog))
    (unload_dialog dcl_id)
  )
)
```
