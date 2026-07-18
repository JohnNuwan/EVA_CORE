---
name: email-automation
description: "Automatiser l'envoi, la réception, le filtrage et l'analyse d'emails avec Python. Gestion des pièces jointes, templates HTML, protocoles SMTP/IMAP et OAuth2."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags:
      - email
      - smtp
      - imap
      - email-automation
      - python
      - mail
      - attachments
      - templates
      - oauth2
      - mime
      - notification
      - reporting
    related_skills:
      - himalaya
      - os-linux-admin
      - industrial-diagnostic
      - cron
---

# Automatisation et Traitement d'Emails avec Python

## Vue d'ensemble

L'automatisation des flux d'emails est un pilier de l'informatique d'entreprise, particulièrement dans les environnements industriels où les rapports de production, les alertes de pannes et les notifications doivent être distribués de manière fiable. Cette compétence guide la conception et le déploiement de scripts Python robustes pour :

- **L'envoi d'emails** : Notifications HTML formatées avec pièces jointes via SMTP (STARTTLS/SSL).
- **La réception et le filtrage** : Interrogation de boîtes aux lettres via IMAP avec extraction de pièces jointes et classification automatique.
- **L'authentification** : Support des méthodes modernes (OAuth 2.0 pour Microsoft 365 / Google Workspace) et gestion sécurisée des credentials.
- **L'intégration** : Pipeline complet de l'email vers le système d'information (base de données, API REST, stockage fichier).

### Architecture typique d'automatisation email

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Expéditeur     │     │   Traitement     │     │   Destinataire   │
│                  │     │                  │     │                  │
│  ┌────────────┐  │     │  ┌────────────┐  │     │  ┌────────────┐  │
│  │ Template   │  │     │  │ Parser MIME│  │     │  │  SMTP      │  │
│  │ HTML +     │──┼────▶│  │ + Filtre   │──┼────▶│  │ (STARTTLS) │  │
│  │ Pièce jointe│  │     │  │ IMAP       │  │     │  └────────────┘  │
│  └────────────┘  │     │  └────────────┘  │     └──────────────────┘
│                  │     │         │         │
│  ┌────────────┐  │     │  ┌────────────┐  │
│  │ SMTP       │  │     │  │ Base de    │  │
│  │ Client     │  │     │  │ données /  │  │
│  └────────────┘  │     │  │ Fichiers   │  │
└──────────────────┘     │  └────────────┘  │
                         └──────────────────┘
```

## Quand l'utiliser

### À utiliser lorsque l'utilisateur demande de :

- Envoyer des rapports automatiques de production par email (corps HTML + pièce jointe CSV/PDF).
- Surveiller une boîte mail pour extraire des fichiers joints (CSV, Excel, PDF) et les intégrer dans un système d'information.
- Envoyer des alertes critiques lors de pannes machine (SMTP avec timeouts et retries).
- Configurer les paramètres SMTP/IMAP sécurisés (SSL/TLS, OAuth 2.0).
- Automatiser l'envoi de bulletins périodiques avec templates HTML responsives.
- Mettre en place une chaîne de traitement : réception → classification → routage vers API/dossier.

### Ne pas utiliser pour :

- La configuration de serveurs de messagerie (Postfix, Exchange, Dovecot) — administration système uniquement.
- L'administration système pure de clients mail en ligne de commande (comme Himalaya, bien que ce dernier puisse être complémentaire).
- L'envoi massif (marketing, newsletters) — utiliser une plateforme dédiée (SendGrid, Mailchimp, AWS SES).
- Le chiffrement de bout en bout (PGP/GPG) — bibliothèques spécialisées requises.

---

## 1. Sécurisation des Identifiants

### 1.1 Variables d'environnement (.env)

Les identifiants SMTP/IMAP ne doivent jamais être codés en dur. Utiliser un fichier `.env` :

```bash
# .env (NE PAS COMMITTER)
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USER=automation@actemium.com
SMTP_PASS=xxxxxxxxxxxxxxxxxxxx
IMAP_SERVER=outlook.office365.com
IMAP_USER=automation@actemium.com
IMAP_PASS=xxxxxxxxxxxxxxxxxxxx
```

### 1.2 Coffre-fort de mots de passe (Windows Credential Manager)

```powershell
# Stockage dans Windows Credential Manager
Add-Type -AssemblyName System.Web
$cred = New-Object System.Management.Automation.PSCredential("automation@actemium.com", (ConvertTo-SecureString "MonMotDePasse" -AsPlainText -Force))
$cred | Export-Clixml -Path "$env:USERPROFILE\email_credentials.xml"
```

```python
# Lecture depuis le coffre Windows
import json, os

def load_credentials(profile: str = "default") -> dict:
    """Charge les credentials depuis Windows Credential Manager."""
    if os.name == "nt":
        import subprocess
        cmd = f'cmdkey /list | findstr "{profile}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        # ... parsing du résultat
    else:
        # Fallback vers .env
        from dotenv import load_dotenv
        load_dotenv()
        return {
            "smtp_user": os.environ["SMTP_USER"],
            "smtp_pass": os.environ["SMTP_PASS"],
        }
```

### 1.3 Authentification OAuth 2.0 (Microsoft 365 / Google)

```python
from O365 import Account

def get_oauth_client():
    """Initialise un client OAuth 2.0 pour Microsoft 365."""
    credentials = (os.environ["OAUTH_CLIENT_ID"], os.environ["OAUTH_CLIENT_SECRET"])
    account = Account(credentials, tenant_id=os.environ["OAUTH_TENANT_ID"])
    if not account.is_authenticated:
        account.authenticate(scopes=["Mail.Send", "Mail.Read", "Mail.ReadWrite"])
    return account
```

---

## 2. Envoi d'Emails (SMTP)

### 2.1 Envoi basique avec STARTTLS et pièce jointe

```python
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate, formataddr

def send_email(
    subject: str,
    html_body: str,
    to_email: str | list[str],
    cc_email: str | list[str] = None,
    file_path: str = None,
    priority: str = "normal",
) -> bool:
    """Envoie un email HTML sécurisé avec pièce jointe optionnelle.

    Args:
        subject: Objet de l'email.
        html_body: Corps HTML de l'email.
        to_email: Destinataire(s) principal(aux).
        cc_email: Destinataire(s) en copie.
        file_path: Chemin optionnel vers une pièce jointe.
        priority: Priorité ('high', 'normal', 'low').

    Returns:
        bool: True si l'envoi a réussi.

    Raises:
        smtplib.SMTPException: En cas d'échec de connexion ou d'envoi.
    """
    creds = load_credentials()

    # Construction du message multipart
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr(("Automation Actemium", creds["smtp_user"]))
    msg["To"] = ", ".join(to_email if isinstance(to_email, list) else [to_email])
    msg["Date"] = formatdate(localtime=True)

    if cc_email:
        msg["Cc"] = ", ".join(cc_email if isinstance(cc_email, list) else [cc_email])

    # Priorité
    if priority == "high":
        msg["X-Priority"] = "1"
        msg["Importance"] = "High"
    elif priority == "low":
        msg["X-Priority"] = "5"
        msg["Importance"] = "Low"

    # Corps HTML
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # Pièce jointe
    if file_path and os.path.exists(file_path):
        filename = os.path.basename(file_path)
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename=\"{filename}\"")
            msg.attach(part)

    # Envoi avec STARTTLS et timeout
    recipients = [to_email] if isinstance(to_email, str) else to_email
    if cc_email:
        recipients += [cc_email] if isinstance(cc_email, str) else cc_email

    with smtplib.SMTP(creds["smtp_server"], int(creds.get("smtp_port", 587)), timeout=15) as server:
        server.starttls()
        server.login(creds["smtp_user"], creds["smtp_pass"])
        server.sendmail(creds["smtp_user"], recipients, msg.as_string())

    return True
```

### 2.2 Template HTML responsive

```python
def build_production_report_html(machine: str, metrics: dict) -> str:
    """Génère un rapport de production au format HTML responsive."""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0;
         background-color: #f4f4f4; }}
  .container {{ max-width: 600px; margin: 20px auto; background: white;
               border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
  .header {{ background: #005F99; color: white; padding: 20px; }}
  .header h1 {{ margin: 0; font-size: 20px; }}
  .content {{ padding: 20px; }}
  .metric {{ display: flex; justify-content: space-between; padding: 10px 0;
             border-bottom: 1px solid #eee; }}
  .metric:last-child {{ border-bottom: none; }}
  .metric-label {{ color: #666; font-weight: 500; }}
  .metric-value {{ font-weight: 600; }}
  .alert {{ background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px;
            padding: 12px; margin: 10px 0; }}
  .footer {{ background: #f8f9fa; padding: 15px 20px; font-size: 12px; color: #888; }}
  @media (max-width: 600px) {{ .container {{ margin: 10px; }} }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📊 Rapport de Production - {machine}</h1>
    <p style="margin:5px 0 0;opacity:0.8;">{__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
  </div>
  <div class="content">
    <h2>Indicateurs</h2>
    {"".join(
        f'<div class="metric"><span class="metric-label">{k}</span>'
        f'<span class="metric-value">{v}</span></div>'
        for k, v in metrics.items()
    )}
    {"<div class='alert'>⚠️ Seuil d'alerte dépassé sur un ou plusieurs indicateurs.</div>"
     if any(v < 0 for v in metrics.values()) else ""}
  </div>
  <div class="footer">
    Rapport généré automatiquement par Helios Agent - Actemium
  </div>
</div>
</body>
</html>"""
```

### 2.3 Envoi avec OAuth 2.0

```python
def send_with_oauth(subject: str, html_body: str, to_email: str):
    """Envoie un email via Microsoft Graph API (OAuth 2.0)."""
    import requests

    access_token = get_oauth_token()  # Récupération du token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    email_data = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html_body},
            "toRecipients": [{"emailAddress": {"address": to_email}}],
        }
    }

    response = requests.post(
        "https://graph.microsoft.com/v1.0/me/sendMail",
        headers=headers,
        json=email_data,
        timeout=15,
    )
    response.raise_for_status()
```

---

## 3. Réception et Filtrage (IMAP)

### 3.1 Lecture et extraction des pièces jointes

```python
import imaplib
import email
import os
from email.header import decode_header

def fetch_and_save_attachments(
    imap_server: str,
    imap_user: str,
    imap_pass: str,
    search_criteria: str = '(UNSEEN SUBJECT "Rapport Production")',
    download_dir: str = "downloads",
    mark_seen: bool = True,
) -> list[dict]:
    """Récupère les emails non lus, extrait les pièces jointes et les sauvegarde.

    Args:
        imap_server: Serveur IMAP.
        imap_user: Utilisateur IMAP.
        imap_pass: Mot de passe IMAP.
        search_criteria: Critères de recherche IMAP.
        download_dir: Dossier de destination des pièces jointes.
        mark_seen: Marquer les emails comme lus après traitement.

    Returns:
        list[dict]: Liste des pièces jointes extraites avec métadonnées.
    """
    os.makedirs(download_dir, exist_ok=True)
    attachments = []

    # Connexion IMAP avec SSL
    mail = imaplib.IMAP4_SSL(imap_server, timeout=15)
    mail.login(imap_user, imap_pass)
    mail.select("inbox")

    status, messages = mail.search(None, search_criteria)
    if status != "OK":
        mail.logout()
        return attachments

    for num in messages[0].split():
        status, data = mail.fetch(num, "(RFC822)")
        if status != "OK":
            continue

        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Décodage propre du sujet
        subject_parts = decode_header(msg["Subject"] or "Sans objet")
        subject = "".join(
            part.decode(charset or "utf-8") if isinstance(part, bytes) else part
            for part, charset in subject_parts
        )

        # Décodage de l'expéditeur
        from_parts = decode_header(msg["From"] or "Inconnu")
        sender = "".join(
            part.decode(charset or "utf-8") if isinstance(part, bytes) else part
            for part, charset in from_parts
        )

        print(f"📧 Traitement : {subject} de {sender}")

        # Parcours des parties MIME
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") is None:
                continue

            filename = part.get_filename()
            if not filename:
                continue

            # Nettoyage du nom de fichier (sécurité)
            filename = os.path.basename(filename)
            filepath = os.path.join(download_dir, filename)

            # Éviter l'écrasement
            counter = 1
            while os.path.exists(filepath):
                name, ext = os.path.splitext(filename)
                filepath = os.path.join(download_dir, f"{name}_{counter}{ext}")
                counter += 1

            with open(filepath, "wb") as f:
                f.write(part.get_payload(decode=True))

            size_kb = os.path.getsize(filepath) / 1024
            attachments.append({
                "filename": filename,
                "path": filepath,
                "size_kb": round(size_kb, 1),
                "subject": subject,
                "sender": sender,
            })
            print(f"  ✅ Sauvegardé : {filename} ({size_kb:.1f} KB)")

        # Marquage comme lu
        if mark_seen:
            mail.store(num, "+FLAGS", "\\Seen")

    mail.close()
    mail.logout()
    return attachments
```

### 3.2 Classification et routage automatique

```python
def classify_and_route(attachments: list[dict]) -> None:
    """Classe les pièces jointes par type et les route vers les dossiers appropriés."""
    for att in attachments:
        ext = os.path.splitext(att["filename"])[1].lower()

        if ext == ".csv":
            target = "data/csv_reports/"
        elif ext == ".xlsx":
            target = "data/excel_reports/"
        elif ext == ".pdf":
            target = "data/pdf_reports/"
        else:
            target = "data/other/"

        os.makedirs(target, exist_ok=True)
        dest = os.path.join(target, att["filename"])
        shutil.move(att["path"], dest)
        att["routed_to"] = dest
        print(f"  📁 Routé vers : {dest}")
```

---

## 4. Gestion des Erreurs et Résilience

### 4.1 Mécanisme de réessai

```python
import time
from functools import wraps

def retry_on_failure(max_retries: int = 3, backoff: int = 5):
    """Décorateur pour réessayer une fonction d'envoi email en cas d'échec."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (smtplib.SMTPException, ConnectionError, TimeoutError) as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        wait = backoff * (2 ** attempt)  # Exponential backoff
                        print(f"⚠️ Échec (tentative {attempt+1}/{max_retries}). "
                              f"Nouvel essai dans {wait}s...")
                        time.sleep(wait)
            raise last_error
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, backoff=10)
def send_critical_alert(subject: str, body: str, to: str):
    """Envoie une alerte critique avec réessai automatique."""
    return send_email(subject=subject, html_body=body,
                      to_email=to, priority="high")
```

### 4.2 Validation des pièces jointes (sécurité)

```python
import magic

def validate_attachment(filepath: str) -> bool:
    """Valide qu'une pièce jointe est bien du type attendu (prévention d'extension spoofing)."""
    allowed_types = {
        ".csv": ["text/csv", "text/plain", "application/csv"],
        ".pdf": ["application/pdf"],
        ".xlsx": [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ],
        ".zip": ["application/zip", "application/x-zip-compressed"],
    }

    ext = os.path.splitext(filepath)[1].lower()
    if ext not in allowed_types:
        return False

    mime_type = magic.from_file(filepath, mime=True)
    return mime_type in allowed_types[ext]
```

---

## 5. Intégration Continue (Pipeline)

### 5.1 Script de polling IMAP avec cron

```python
# poll_inbox.py — À exécuter toutes les 15 minutes via cron
def main():
    """Pipeline complet : réception → extraction → routage → notification."""
    print("🔍 Vérification des nouveaux emails...")
    attachments = fetch_and_save_attachments(
        imap_server=os.environ["IMAP_SERVER"],
        imap_user=os.environ["IMAP_USER"],
        imap_pass=os.environ["IMAP_PASS"],
        search_criteria='(UNSEEN SUBJECT "Rapport Production")',
    )

    if not attachments:
        print("📭 Aucun nouvel email.")
        return

    classify_and_route(attachments)

    # Notification de synthèse
    summary = f"{len(attachments)} fichier(s) traité(s)"
    send_email(
        subject=f"✅ Rapport de traitement email — {__import__('datetime').datetime.now():%d/%m/%Y}",
        html_body=f"<p>{summary}</p><ul>"
                   + "".join(f"<li>{a['filename']} → {a['routed_to']}</li>"
                            for a in attachments)
                   + "</ul>",
        to_email=os.environ["NOTIFICATION_EMAIL"],
    )
    print(f"✅ {summary}")

if __name__ == "__main__":
    main()
```

### 5.2 Intégration avec une API REST

```python
def process_to_api(attachments: list[dict], api_url: str, api_key: str):
    """Envoie les pièces jointes extraites vers une API REST."""
    for att in attachments:
        with open(att["path"], "rb") as f:
            files = {"file": (att["filename"], f, "application/octet-stream")}
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.post(api_url, files=files, headers=headers, timeout=30)

        if response.status_code == 200:
            print(f"  ✅ Envoyé vers API : {att['filename']}")
        else:
            print(f"  ❌ Erreur API ({response.status_code}) : {att['filename']}")
```

---

## Pièges Courants (Common Pitfalls)

1. **Identifiants codés en dur** :
   - *Erreur* : Écrire l'utilisateur et le mot de passe SMTP/IMAP directement dans le script Python.
   - *Correction* : Toujours charger les credentials depuis des variables d'environnement (`os.environ.get()`), un coffre-fort, ou OAuth 2.0.

2. **Absence de timeout sur les connexions** :
   - *Erreur* : Ne pas spécifier de timeout. Si le serveur de mail ne répond pas, le script bloque indéfiniment.
   - *Correction* : Toujours spécifier `timeout=15` (ou valeur adaptée) dans `smtplib.SMTP()` et `imaplib.IMAP4_SSL()`.

3. **Traitement inefficace des encodages de sujets** :
   - *Erreur* : Extraire `msg['Subject']` directement sans décoder. Les accents apparaissent sous forme encodée (`=?UTF-8?B?...==?`).
   - *Correction* : Utiliser `email.header.decode_header()` pour décoder proprement le sujet et l'expéditeur.

4. **Pièces jointes sans Content-Disposition** :
   - *Erreur* : Certains clients mail n'ajoutent pas `Content-Disposition: attachment`, ce qui fait que `part.get_filename()` retourne `None`.
   - *Correction* : Vérifier aussi `part.get_param('name', header='Content-Type')` et `part.get_content_type()`.

5. **Traversée de chemin (path traversal)** :
   - *Erreur* : Utiliser directement `os.path.join(download_dir, filename)` sans validation, ce qui permet à un attaquant d'écrire en dehors du dossier cible.
   - *Correction* : Utiliser `os.path.basename(filename)` pour supprimer tout chemin relatif, et valider le type MIME.

6. **Non-respect des limites de débit (rate limiting)** :
   - *Erreur* : Envoyer des centaines d'emails en rafale, ce qui déclenche le blocage temporaire du compte.
   - *Correction* : Implémenter un délai (`time.sleep(1)` ou plus) entre les envois, et respecter les limites du fournisseur (Exchange : 30 msg/min, Gmail : 2000 msg/jour).

7. **Absence de gestion des emails sans contenu texte** :
   - *Erreur* : Un email peut être multipart avec une partie HTML mais pas de partie text. La recherche de partie text échoue.
   - *Correction* : Utiliser `email.message.get_content().get_content_subtype()` avec fallback sur HTML.

---

## Liste de vérification (Checklist)

- [ ] Les identifiants de messagerie sont récupérés de manière sécurisée (variables d'environnement, coffre-fort, OAuth).
- [ ] Un timeout explicite est défini pour toutes les connexions réseau SMTP/IMAP (minimum 15 secondes).
- [ ] Le chiffrement TLS (STARTTLS ou SSL) est configuré et validé lors de la connexion.
- [ ] Les sujets et expéditeurs sont décodés via `email.header.decode_header()`.
- [ ] Les noms de fichiers des pièces jointes sont nettoyés (`os.path.basename()`) pour éviter les traversées de chemin.
- [ ] Les types MIME des pièces jointes sont validés avant écriture sur disque.
- [ ] Un mécanisme de réessai avec backoff exponentiel est implémenté pour les envois critiques.
- [ ] Les emails lus sont correctement marqués comme traités (`\Seen`) ou déplacés (`\Deleted`) pour éviter la double lecture.
- [ ] Les limites de débit (rate limiting) du fournisseur sont respectées (délai entre les envois).
- [ ] Les logs incluent l'horodatage, le statut de chaque opération et les erreurs éventuelles.
- [ ] Un mode dégradé (fallback) est prévu en cas d'indisponibilité du serveur SMTP/IMAP (file d'attente locale, notification alternative).

