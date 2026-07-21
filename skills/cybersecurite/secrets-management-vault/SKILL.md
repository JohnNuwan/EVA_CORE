---
name: secrets-management-vault
description: Guide complet de gestion des secrets — HashiCorp Vault, SOPS, Git-crypt, Bitwarden CLI, et bonnes pratiques pour éviter les fuites de credentials.
domain: [cybersecurite, devops, securite]
tags: [secrets, vault, sops, git-crypt, passwords, credentials, hsm]
priority: haute
---

# 🔑 Gestion des Secrets — Vault, SOPS, Git-crypt

Guide de gestion sécurisée des secrets (API keys, tokens, mots de passe, certificats) pour environnements de production.  
Couvre : HashiCorp Vault, SOPS, Git-crypt, Bitwarden CLI, et hardening du stockage.

---

## 1. Principes Fondamentaux

### 1.1 Règles d'Or

1. **Jamais de secrets dans le code** — ni en dur, ni dans des fichiers non chiffrés
2. **Jamais de secrets dans .env committé** — template .env.example uniquement
3. **Rotation régulière** — tous les 90 jours maximum
4. **Moindre privilège** — chaque service a accès uniquement aux secrets dont il a besoin
5. **Audit** — chaque accès à un secret est journalisé

### 1.2 Matrice des Solutions

| Solution | Usage | Stockage | Rotation | Audit | Prix |
|----------|-------|----------|----------|-------|------|
| **HashiCorp Vault** | Centralisé, dynamique, cloud | Backend HA | Automatique | ✅ Complet | Gratuit (OSS) |
| **SOPS** | Secrets dans Git chiffrés | Git + KMS | Manuelle | ❌ | Gratuit |
| **Git-crypt** | Tout fichier dans Git | Git + GPG | Manuelle | ❌ | Gratuit |
| **Bitwarden CLI** | Organisation personnelle | Cloud/self-host | Manuelle | ✅ | Gratuit |
| **1Password CLI** | Team/entreprise | Cloud | Automatique | ✅ | Payant |
| **Kubernetes Secrets** | K8s natif | etcd | Manuelle | ⚠️ | Inclus |

---

## 2. HashiCorp Vault

### 2.1 Installation

```bash
# Installation locale
wget https://releases.hashicorp.com/vault/1.18.0/vault_1.18.0_linux_amd64.zip
unzip vault_1.18.0_linux_amd64.zip
sudo mv vault /usr/local/bin/
vault -autocomplete-install

# Vérification
vault --version
```

### 2.2 Démarrage en Dev (test uniquement)

```bash
# NE JAMAIS utiliser en production
vault server -dev -dev-root-token-id=root
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'
```

### 2.3 Configuration Production (HA + TLS)

```hcl
# /etc/vault/config.hcl
ui = true
api_addr = "https://127.0.0.1:8200"
cluster_addr = "https://127.0.0.1:8201"

storage "raft" {
  path = "/opt/vault/data"
  node_id = "node1"
}

listener "tcp" {
  address       = "127.0.0.1:8200"
  tls_disable   = false
  tls_cert_file = "/etc/vault/tls/cert.pem"
  tls_key_file  = "/etc/vault/tls/key.pem"
}

seal "awskms" {
  region     = "eu-west-1"
  kms_key_id = "alias/vault-unseal"
}

telemetry {
  prometheus_retention_time = "30s"
  disable_hostname = true
}
```

### 2.4 Commandes Essentielles

```bash
# Définir l'adresse et le token
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='hvs.xxxx'

# Écrire un secret
vault kv put secret/api/production \
  API_KEY="sk-xxxxx" \
  API_SECRET="secret-xxxxx" \
  DB_PASSWORD="p@ssw0rd!"

# Lire un secret
vault kv get secret/api/production

# Lire un champ spécifique
vault kv get -field=API_KEY secret/api/production

# Lister les secrets
vault kv list secret/api/

# Supprimer un secret
vault kv delete secret/api/production

# Versioning (KV v2 uniquement)
vault kv get -version=2 secret/api/production
vault kv rollback secret/api/production 1
```

### 2.5 Politiques d'Accès (ACL)

```hcl
# /etc/vault/policies/api-service.hcl
path "secret/data/api/*" {
  capabilities = ["read", "list"]
}

path "secret/data/api/production" {
  capabilities = ["read"]
}

path "secret/metadata/api/*" {
  capabilities = ["list"]
}

path "sys/lease" {
  capabilities = ["read"]
}
```

Application :
```bash
vault policy write api-service /etc/vault/policies/api-service.hcl
```

### 2.6 Intégration avec Applications

**Python :**
```python
import hvac
import os

client = hvac.Client(
    url=os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200"),
    token=os.environ.get("VAULT_TOKEN")
)

# Lire un secret
secret = client.secrets.kv.v2.read_secret_version(
    path="api/production",
    mount_point="secret"
)
api_key = secret["data"]["data"]["API_KEY"]
```

**Docker :**
```bash
# Utiliser envconsul pour injecter les secrets
docker run -e VAULT_TOKEN=$VAULT_TOKEN \
  -e VAULT_ADDR=$VAULT_ADDR \
  hashicorp/envconsul \
  -secret="secret/api/production" \
  ./start-app.sh
```

---

## 3. SOPS (Secrets OPerationS)

### 3.1 Installation

```bash
# Installer SOPS
wget https://github.com/getsops/sops/releases/download/v3.9.3/sops-v3.9.3.linux.amd64
sudo mv sops-v3.9.3.linux.amd64 /usr/local/bin/sops
chmod +x /usr/local/bin/sops
```

### 3.2 Configuration

```yaml
# .sops.yaml
creation_rules:
  - path_regex: secrets/.*\.yaml$
    encrypted_regex: '^(api_key|password|token|secret|key)$'
    age: age1xxxxx...
  
  - path_regex: secrets/.*\.env$
    age: age1xxxxx...
```

### 3.3 Chiffrement/Déchiffrement

```bash
# Chiffrer un fichier (crée fichier.chiffré)
sops --encrypt secrets/prod.yaml > secrets/prod.enc.yaml

# Déchiffrer
sops --decrypt secrets/prod.enc.yaml

# Éditer directement (déchiffre, édite, rechiffre)
sops secrets/prod.enc.yaml

# Chiffrer avec une clé AGE
sops --encrypt --age age1xxxxx... secrets/prod.yaml > secrets/prod.enc.yaml

# Intégration Git — git diff déchiffré
sops diff main HEAD
```

### 3.4 Intégration CI/CD

```yaml
# .github/workflows/deploy.yml
jobs:
  deploy:
    steps:
      - uses: actions/checkout@v4
      
      - name: Déchiffrer les secrets
        run: |
          sops --decrypt secrets/prod.enc.yaml > secrets/prod.yaml
      
      - name: Docker build avec secrets
        run: |
          docker build --secret id=aws,src=secrets/prod.yaml -t app .
```

---

## 4. Git-crypt

### 4.1 Installation

```bash
# Installation
sudo apt install git-crypt

# OU
brew install git-crypt
```

### 4.2 Configuration

```bash
# Initialiser dans un dépôt
cd mon-projet
git-crypt init

# Ajouter les collaborateurs
git-crypt add-gpg-user <GPG_KEY_ID>

# Configurer les fichiers à chiffrer
cat > .gitattributes << 'EOF'
*.env filter=git-crypt diff=git-crypt
secrets/** filter=git-crypt diff=git-crypt
*.key filter=git-crypt diff=git-crypt
EOF

git add .gitattributes
git commit -m "Ajout du chiffrement git-crypt"
```

### 4.3 Usage

```bash
# Vérifier le statut
git-crypt status

# Déverrouiller le dépôt
git-crypt unlock

# Vérrouiller
git-crypt lock

# Exporter la clé pour CI/CD
git-crypt export-key /tmp/git-crypt-key
```

---

## 5. Détection de Fuites

### 5.1 GitLeaks (Scan automatisé)

```bash
# Installation
brew install gitleaks
# OU
wget https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks-linux-amd64
sudo mv gitleaks-linux-amd64 /usr/local/bin/gitleaks

# Scan d'un dépôt
gitleaks detect --source /chemin/vers/repo -v

# Scan du dernier commit
gitleaks detect --source . --log-opts="HEAD~1..HEAD"

# Scan avec un seuil
gitleaks detect --source . --verbose --exit-code 1

# Générer un rapport JSON
gitleaks detect --source . -f json -r gitleaks-report.json
```

### 5.2 TruffleHog

```bash
# Installation
pip install trufflehog

# Scan d'un dépôt
trufflehog git https://github.com/user/repo.git

# Scan d'un répertoire local
trufflehog filesystem /chemin/vers/repo

# Scan avec sortie JSON
trufflehog git https://github.com/user/repo.git --json
```

### 5.3 Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
    
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: detect-private-key
      - id: check-added-large-files
```

---

## 6. Bitwarden CLI

```bash
# Installation
sudo snap install bw
# OU
wget https://github.com/bitwarden/clients/releases/latest/download/bw-linux-2024.xx.zip
unzip bw-linux-*.zip -d /opt/bitwarden

# Login
bw login
export BW_SESSION=$(bw unlock --raw)

# Lister les items
bw list items

# Chercher un secret
bw get item "API Production"

# Récupérer un mot de passe
bw get password "API Production"

# Exporter
bw export --format json --output /tmp/vault-export.json
```

---

## 7. Hardening du Stockage

### 7.1 Permissions

```bash
# .env — 600 (lecture seule par le propriétaire)
chmod 600 /home/aza/.hermes/.env

# Dossier secrets — 700
chmod 700 /home/aza/secrets/

# Clés SSH — 600
chmod 600 ~/.ssh/id_*

# Fichiers de configuration avec secrets — 640
chmod 640 /etc/vault/config.hcl
```

### 7.2 Audit des Accès

```bash
# Vérifier qui a accès aux fichiers sensibles
find /home/aza -name ".env" -o -name "*.key" -o -name "*secret*" 2>/dev/null | \
  while read f; do
    echo "=== $f ==="
    ls -la "$f"
    echo "Processus utilisant ce fichier:"
    lsof "$f" 2>/dev/null
  done

# Vérifier les secrets dans les logs
grep -r "API_KEY\|SECRET\|PASSWORD\|TOKEN" /home/aza/.hermes/logs/*.log 2>/dev/null
```

### 7.3 Rotation Automatique

```bash
#!/bin/bash
# rotate-secrets.sh — Rotation automatique des secrets
# Exécution : cron mensuel

DATE=$(date +%Y%m%d)
VAULT_ADDR="http://127.0.0.1:8200"

# 1. Générer un nouveau secret
NEW_SECRET=$(openssl rand -base64 32)

# 2. Écrire dans Vault
vault kv put secret/api/production \
  API_KEY=$(openssl rand -hex 16) \
  API_SECRET=$NEW_SECRET

# 3. Notifier les services
curl -X POST http://localhost:8080/reload-secrets

# 4. Journaliser
echo "[$DATE] Rotation des secrets API effectuée" >> /var/log/secret-rotation.log
```

---

## 8. Checklist de Sécurité

- [ ] Aucun secret en clair dans Git (passé et présent)
- [ ] .env dans .gitignore
- [ ] .env.example fourni (valeurs vides)
- [ ] Vault ou SOPS opérationnel
- [ ] Rotation des secrets automatisée
- [ ] Audit des accès aux secrets
- [ ] Permissions 600 sur les fichiers de secrets
- [ ] Pre-commit hook GitLeaks activé
- [ ] Logs d'application ne contiennent pas de secrets
- [ ] Variables d'environnement dans les Dockerfiles — non, utiliser --secret ou Vault
- [ ] Chiffrement au repos pour les secrets stockés
- [ ] MFA sur les accès administrateurs Vault

---

## Pitfalls

- **NE JAMAIS** committer `.env` ou `.env.local` — même une fois
- **NE JAMAIS** logger les secrets dans des fichiers de log
- **NE JAMAIS** exposer l'API Vault sur `0.0.0.0` — toujours `127.0.0.1`
- **NE JAMAIS** utiliser `vault server -dev` en production
- **NE JAMAIS** stocker les clés de déchiffrement SOPS dans le même dépôt
- **Toujours** faire tourner les secrets régulièrement (90 jours max)
- Vault ne fait pas de magie — si un attaquant a accès au serveur, il peut aussi accéder à Vault
- Ne pas oublier de sauvegarder les clés de déchiffrement (unseal keys) hors ligne