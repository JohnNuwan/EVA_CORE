---
name: terraform-iac
description: "Infrastructure as Code avec Terraform — modules réutilisables, gestion d'état, providers (AWS, GCP, Azure, Proxmox), workspaces, remote state, best practices"
version: 1.0.0
author: EVA
license: Privée EVA
category: mlops
metadata:
  EVA:
    tags: [terraform, iac, infrastructure, hcl, modules, state, providers, cloud, provionnement]
    related_skills: [ansible-automation, kubernetes-avance, ci-cd-pipelines, prometheus-grafana]
---

# Terraform — Infrastructure as Code

## Vue d'ensemble

Terraform (HashiCorp) est le standard pour provisionner l'infrastructure de manière déclarative. Cette compétence couvre l'écriture de configuration HCL, la gestion des modules, les backends d'état distants, les workspaces, les providers cloud et Proxmox, les bonnes pratiques de sécurité et l'intégration CI/CD.

## Quand l'utiliser

- Provisionner des ressources cloud (VM, VPC, RDS, S3, Kubernetes)
- Gérer un parc d'infrastructure avec Git comme source de vérité
- Créer des modules réutilisables pour standardiser les déploiements
- Orchestrer des ressources hétérogènes (multi-cloud, on-prem)
- Auditer et documenter l'infrastructure existante

---

## 1. Structure de Projet

```
infrastructure/
├── environments/
│   ├── dev/
│   │   └── main.tf
│   ├── staging/
│   │   └── main.tf
│   └── prod/
│       ├── main.tf
│       └── backend.tf
├── modules/
│   ├── compute/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── database/
│       ├── main.tf
│       └── variables.tf
├── providers.tf
├── versions.tf
└── remote-state/
    ├── dev.tfbackend
    └── prod.tfbackend
```

### Fichier racine

```hcl
# versions.tf
terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# providers.tf
provider "aws" {
  region = local.region
  default_tags {
    tags = {
      Environment = terraform.workspace
      ManagedBy   = "terraform"
      Project     = "eva"
    }
  }
}

locals {
  region = var.region
  name   = "eva-${terraform.workspace}"
}
```

---

## 2. Remote State (S3 + DynamoDB)

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "eva-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "eu-west-3"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

```bash
# Initialisation avec backend distant
terraform init -backend-config=remote-state/prod.tfbackend

# Migration du state local vers distant
terraform init -migrate-state
```

### DynamoDB pour le locking

```hcl
resource "aws_dynamodb_table" "terraform_lock" {
  name         = "terraform-state-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
```

---

## 3. Modules Réutilisables

### Module Compute (VM / Instance EC2)

```hcl
# modules/compute/variables.tf
variable "name" {
  description = "Nom de l'instance"
  type        = string
}

variable "instance_type" {
  description = "Type d'instance"
  type        = string
  default     = "t3.medium"
}

variable "subnet_id" {
  description = "ID du sous-réseau"
  type        = string
}

variable "user_data" {
  description = "Script de démarrage (cloud-init)"
  type        = string
  default     = null
}

# modules/compute/main.tf
resource "aws_instance" "this" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [aws_security_group.this.id]
  user_data              = var.user_data

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
    encrypted   = true
  }

  metadata_options {
    http_tokens                 = "required"    # IMDSv2 obligatoire
    http_put_response_hop_limit = 1
  }

  tags = {
    Name = var.name
  }
}

# modules/compute/outputs.tf
output "instance_id" {
  value = aws_instance.this.id
}

output "private_ip" {
  value = aws_instance.this.private_ip
}

output "public_ip" {
  value = aws_instance.this.public_ip
}
```

### Utilisation

```hcl
module "web_server" {
  source = "../../modules/compute"

  name          = "web-${local.name}"
  instance_type = var.env == "prod" ? "t3.large" : "t3.medium"
  subnet_id     = module.vpc.public_subnets[0]
  user_data     = templatefile("${path.module}/cloud-init.yml", {
    role = "web"
  })
}
```

---

## 4. Workspaces & Comportements Multi-Environnements

```bash
# Créer et basculer
terraform workspace new staging
terraform workspace select prod
terraform workspace list

# Dans le code
locals {
  env = terraform.workspace
}

resource "aws_instance" "main" {
  instance_type = local.env == "prod" ? "t3.xlarge" : "t3.medium"
  count         = local.env == "prod" ? 3 : 1
}
```

---

## 5. Provider Proxmox (on-prem The Hive)

```hcl
# providers.tf (ajout)
provider "proxmox" {
  pm_api_url      = "https://192.168.1.5:8006/api2/json"
  pm_user         = var.pve_user
  pm_password     = var.pve_password
  pm_tls_insecure = true
}

# modules/compute-proxmox/main.tf
resource "proxmox_vm_qemu" "vm" {
  name        = var.name
  target_node = "pve"
  clone       = "ubuntu-24.04-template"
  full_clone  = true
  os_type     = "cloud-init"

  cores   = var.cores
  sockets = 1
  memory  = var.memory

  disk {
    type    = "scsi"
    storage = "local-zfs"
    size    = "${var.disk_size}G"
  }

  network {
    model  = "virtio"
    bridge = "vmbr0"
  }

  cicustom  = "user=local:snippets/${var.name}-ci.yaml"
  ipconfig0 = "ip=${var.ip}/24,gw=192.168.1.1"
}
```

---

## 6. Intégration CI/CD

```yaml
# .github/workflows/terraform.yml
name: Terraform

on:
  pull_request:
    paths:
      - 'infrastructure/**'
  push:
    branches: [main]
    paths:
      - 'infrastructure/**'

env:
  TF_VERSION: "1.9"
  AWS_REGION: "eu-west-3"

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Format check
        run: terraform fmt -check -recursive
        working-directory: infrastructure/environments/${{ vars.TF_WORKSPACE }}

      - name: Init
        run: terraform init
        working-directory: infrastructure/environments/${{ vars.TF_WORKSPACE }}

      - name: Validate
        run: terraform validate
        working-directory: infrastructure/environments/${{ vars.TF_WORKSPACE }}

      - name: Plan
        id: plan
        run: terraform plan -no-color -out=tfplan
        working-directory: infrastructure/environments/${{ vars.TF_WORKSPACE }}

      - uses: actions/github-script@v7
        if: github.event_name == 'pull_request'
        with:
          script: |
            const fs = require('fs');
            const output = fs.readFileSync('infrastructure/environments/${{ vars.TF_WORKSPACE }}/plan.txt', 'utf8');
            github.rest.issues.createComment({
              ...context.repo,
              issue_number: context.issue.number,
              body: `## Plan Terraform\n\`\`\`diff\n${output}\n\`\`\``
            });

  apply:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    needs: plan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}
      - run: terraform init && terraform apply -auto-approve
        working-directory: infrastructure/environments/prod
```

---

## 7. Sécurité & Bonnes Pratiques

```bash
# Vérifications
terraform plan -out=tfplan                      # Toujours planifier avant d'appliquer
terraform show tfplan                           # Lire le plan détaillé
checkov -d .                                    # Analyse de sécurité des templates
tflint --recursive                              # Linter HCL
terrascan scan -t aws                           # Scan de conformité
```

### Fichier .tflint.hcl

```hcl
config {
  format = "compact"
}

plugin "aws" {
  enabled = true
  version = "0.34"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

rule "terraform_required_providers" {
  enabled = true
}

rule "terraform_required_version" {
  enabled = true
}
```

---

## 8. Pièges Courants

1. **State partagé non verrouillé :** Terraform peut corrompre le state si deux applis concurrents. Toujours DynamoDB locking.
2. **Variables sensibles en clair :** `terraform.tfvars` contient parfois des mots de passe. Utiliser `sensitive = true` + un vault (AWS Secrets Manager, SOPS).
3. **Count vs for_each :** `count` crée des index fragiles. `for_each` avec une clé stable (nom, ID) est préféré.
4. **Destruction involontaire :** `terraform apply` peut détruire une ressource si son nom change. Utiliser `prevent_destroy = true` sur les ressources critiques.
5. **Drift non détecté :** Terraform ne détecte pas les modifications faites à la main. Utiliser `terraform plan` en cron job ou Drift Detection (Terraform Cloud).

---

## 9. Checklist Production

- [ ] Remote state avec locking (S3+DynamoDB, Terraform Cloud, GCS)
- [ ] `terraform fmt -check -recursive` dans le CI
- [ ] `prevent_destroy = true` sur les ressources critiques (DB, buckets)
- [ ] Variables sensibles marquées `sensitive = true`
- [ ] Modules versionnés avec `source = "git::https://...?ref=v1.2"`
- [ ] Plan commenté sur chaque PR avant merge
- [ ] Workspaces ou dossiers séparés par environnement
- [ ] Checkov / Terrascan dans le pipeline CI
- [ ] Pas de credentials en dur dans le code