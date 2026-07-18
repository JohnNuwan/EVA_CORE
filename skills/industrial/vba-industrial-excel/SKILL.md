---
name: vba-industrial-excel
description: "Scripter en VBA pour automatiser l'ingénierie sous Excel."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [windows]
metadata:
  tags: [vba, excel, scripting, automation, engineering, import-export, tia-portal, studio-5000, macros]
  related_skills: [industrial-programming-languages, industrial-exchange-formats]
---

# Programmation VBA Excel pour l'Automatisation de l'Ingénierie Industrielle

Cette compétence régit le développement de macros Visual Basic for Applications (VBA) sous Microsoft Excel. Excel sert de pivot d'ingénierie pour générer automatiquement du code automate, structurer des listes d'E/S, formater des alarmes SCADA ou valider des nomenclatures électriques.

---

## 1. Modèle Objet Excel et Optimisation des Performances de Masse

Le scripting d'ingénierie manipule fréquemment des milliers de lignes de variables. Sans optimisation, l'appel répété de cellules via le modèle d'objet d'Excel ralentit dramatiquement l'exécution.

### Règles d'optimisation obligatoires
```vba
Public Sub StartIndustrialProcess()
    ' Desactivation des calculs et de la mise a jour de l'ecran
    Application.ScreenUpdating = False
    Application.DisplayAlerts = False
    Application.Calculation = xlCalculationManual

    On Error GoTo ErrorHandler
    
    ' --- APPEL DE LA LOGIQUE D'INGÉNIERIE ---
    Call GenererTagsPLC
    
CleanExit:
    ' Re-activation imperative des fonctionnalites Excel
    Application.ScreenUpdating = True
    Application.DisplayAlerts = True
    Application.Calculation = xlCalculationAutomatic
    Exit Sub

ErrorHandler:
    MsgBox "Erreur d'execution : " & Err.Description, vbCritical
    Resume CleanExit
End Sub
```

---

## 2. Génération de Fichiers d'Échange Automate (TIA Portal / Studio 5000)

Excel est couramment utilisé pour exporter des tables d'E/S vers des fichiers importables par les logiciels d'automatisation.

### TIA Portal (Génération XML avec MSXML)
Pour générer les structures XML requises par Siemens TIA Portal :
```vba
Public Sub ExportSiemensXml()
    Dim xmlDoc As Object
    Dim root As Object, tagTable As Object, tagsNode As Object, tagNode As Object
    
    Set xmlDoc = CreateObject("MSXML2.DOMDocument.6.0")
    
    ' Definition de la racine
    Set root = xmlDoc.createElement("Document")
    xmlDoc.appendChild root
    
    Set tagTable = xmlDoc.createElement("PlcTagTable")
    tagTable.setAttribute "Name", "Import_Excel_Actemium"
    root.appendChild tagTable
    
    Set tagsNode = xmlDoc.createElement("Tags")
    tagTable.appendChild tagsNode
    
    ' Exemple d'ajout d'une variable lue dans Excel (Ligne 2, Colonnes 1 a 3)
    Set tagNode = xmlDoc.createElement("PlcTag")
    tagNode.setAttribute "Name", Sheet1.Cells(2, 1).Value       ; Symbole
    
    Dim dataTypeNode As Object
    Set dataTypeNode = xmlDoc.createElement("DataType")
    dataTypeNode.Text = Sheet1.Cells(2, 2).Value                ; REAL, BOOL, etc.
    tagNode.appendChild dataTypeNode
    
    Dim addrNode As Object
    Set addrNode = xmlDoc.createElement("LogicalAddress")
    addrNode.Text = Sheet1.Cells(2, 3).Value                   ; %I0.0, %MW10, etc.
    tagNode.appendChild addrNode
    
    tagsNode.appendChild tagNode
    
    ' Sauvegarde sur disque
    xmlDoc.Save "C:\Actemium\Exports\siemens_tags.xml"
End Sub
```

---

## 3. Macro Complète de Nettoyage et Génération CSV pour Rockwell Studio 5000

Cette macro parcourt les lignes d'Excel, nettoie les symboles pour être conformes aux contraintes syntaxiques d'automates, et génère un fichier d'import CSV valide pour Rockwell Automation.

```vba
Public Sub GenererCsvRockwell()
    Dim FilePath As String
    Dim FileNum As Integer
    Dim Row As Long
    Dim Symbole As String
    Dim Adresse As String
    Dim DataType As String
    Dim Description As String
    
    FilePath = "C:\Actemium\Exports\rockwell_tags.csv"
    FileNum = FreeFile
    
    Open FilePath For Output As #FileNum
    
    ' En-tete de format requis par Studio 5000 Import
    Print #FileNum, "0.1"
    Print #FileNum, "TYPE", "SCOPE", "NAME", "DATATYPE", "DESCRIPTION", "SPECIFIER"
    
    Row = 2 ' Demarrage a la ligne 2 (apres les en-tetes Excel)
    
    While Sheet1.Cells(Row, 1).Value <> ""
        Symbole = CleanPlcSymbol(Sheet1.Cells(Row, 1).Value)
        DataType = Sheet1.Cells(Row, 2).Value
        Adresse = Sheet1.Cells(Row, 3).Value
        Description = Sheet1.Cells(Row, 4).Value
        
        ' Ecriture de la ligne CSV formatee (delimiteur virgule)
        Print #FileNum, "TAG", "", Symbole, DataType, """" & Description & """", Adresse
        
        Row = Row + 1
    Wend
    
    Close #FileNum
    MsgBox "Export de " & (Row - 2) & " tags realise avec succes !", vbInformation
End Sub

Private Function CleanPlcSymbol(ByVal inputStr As String) As String
    Dim cleanStr As String
    Dim i As Integer
    Dim c As String
    
    ' Remplacement des caracteres accentues
    inputStr = LCase(inputStr)
    inputStr = Replace(inputStr, "é", "e")
    inputStr = Replace(inputStr, "è", "e")
    inputStr = Replace(inputStr, "à", "a")
    inputStr = Replace(inputStr, "ç", "c")
    
    ' Filtrage des caracteres non conformes
    For i = 1 To Len(inputStr)
        c = Mid(inputStr, i, 1)
        If c Like "[a-z]" Or c Like "[0-9]" Or c = "_" Then
            cleanStr = cleanStr & c
        Else
            cleanStr = cleanStr & "_"
        End If
    Next i
    
    CleanPlcSymbol = UCase(cleanStr)
End Function
```

---

## 4. Outils de Cohérence d'Ingénierie (Contrôles Électriques)

* **Détection des chevauchements de bits (adresses mémoire PLC)** : La macro doit cartographier les adresses physiques saisies (ex: `%MW10` et `%MW11` sont deux entiers de 16 bits distincts, mais `%MD10` qui prend 32 bits chevauche `%MW10` et `%MW11`). L'agent doit implémenter des vérifications d'adresses pour interdire les superpositions mémoires involontaires.
* **Validation du Type/Signal** : Comparer la nature physique de la variable et le type PLC configuré (par exemple : si la description de la variable contient `RESEAU_EAU` et que l'unité est `m3/h`, le type de variable doit être un `REAL` ou `INT` pour représenter la mesure analogique, et non un `BOOL`).
