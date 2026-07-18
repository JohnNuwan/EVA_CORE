---
name: cloud-devops-sre
description: "Compétence niveau expert en cloud computing, DevOps et SRE assistés par IA. Couvre AWS, Azure, GCP, Kubernetes, Docker, Terraform, CI/CD, observability, monitoring, incident response, chaos engineering, SLO/SLI/SLA, error budget, capacity planning, FinOps, cloud security, service mesh, Istio, et GitOps."
keywords: [cloud, AWS, Azure, GCP, Kubernetes, DevOps, SRE, Terraform, CI/CD, observability, monitoring]
categories: [cs.DC, cs.NI, cs.SE, cs.CR, cs.AI, cs.LG]
---

# Compétence Cloud, DevOps et SRE

## Présentation

Cette compétence couvre l'ensemble des disciplines du cloud computing, DevOps et Site Reliability Engineering, des providers cloud à l'observabilité en passant par la conteneurisation, l'IaC et les pratiques SRE.

---

## Cloud Providers

- **AWS (200+ services)** : EC2, Lambda (serverless), S3 (stockage), RDS/DynamoDB (bases de données)
- **AWS Infra** : ECS/EKS (conteneurs), VPC (réseau), IAM (sécurité), CloudFront (CDN)
- **AWS Services** : Route53 (DNS), API Gateway, SQS/SNS (messaging), Kinesis (streaming)
- **AWS Advanced** : Step Functions (orchestration), Bedrock (IA générative), SageMaker (ML)
- **Azure** : Azure VM, Functions, Blob Storage, AKS, CosmosDB, Azure DevOps, Active Directory
- **GCP** : Compute Engine, Cloud Functions, Cloud Storage, GKE, BigQuery, Cloud Run
- **Comparaisons Cloud** : Services équivalents entre AWS/Azure/GCP

## Containers et Orchestration

- **Docker** : Image building, multi-stage builds, distroless images, Dockerfile optimization
- **Kubernetes Architecture** : Pods, deployments, services, ingress, configmap, secrets
- **K8s Security** : RBAC, network policies, Pod Security Standards
- **K8s Autoscaling** : HPA (Horizontal Pod Autoscaler), VPA (Vertical), KEDA
- **K8s Operations** : PDB (Pod Disruption Budgets), storage (CSI), CRDs, operators
- **Helm / Kustomize** : Gestionnaire de packages Kubernetes, overlay configurations
- **K3s / MicroK8s** : Kubernetes légers pour edge et dev
- **Managed K8s** : EKS (AWS), AKS (Azure), GKE (GCP), OpenShift (Red Hat)

## Infrastructure as Code (IaC)

- **Terraform** : Providers, modules, state management, remote backend, HCL, workspaces
- **Pulumi** : IaC avec langages de programmation (Python, TypeScript, Go)
- **CloudFormation / CDK** : AWS IaC natif et Cloud Development Kit
- **Ansible** : Automation de configuration et déploiement
- **Packer** : Création d'images machine identiques
- **Vagrant** : Environnements de développement reproductibles
- **Crossplane** : Control plane multi-cloud Kubernetes natif
- **Terragrunt** : Wrapper Terraform pour DRY configurations

## CI/CD

- **GitHub Actions** : CI/CD workflows, matrix builds, reusable workflows
- **GitLab CI** : Pipelines, runners, auto DevOps
- **Jenkins** : Pipelines déclaratives, shared libraries
- **ArgoCD / Flux (GitOps)** : GitOps pour Kubernetes
- **Tekton** : CI/CD Kubernetes natif
- **Spinnaker / Harness** : Plateformes de delivery avancées
- **Feature Flags (LaunchDarkly)** : Flags de fonctionnalités
- **Deployment Strategies** : Canary, blue/green, rolling, progressive delivery

## Observabilité et Monitoring

- **Prometheus** : Metrics collection, PromQL, exporters, service discovery
- **Grafana** : Dashboards, alerting, Loki (logs), Tempo (traces), Mimir (metrics scalable)
- **Datadog / NewRelic** : Plateformes d'observabilité SaaS
- **OpenTelemetry** : Standard pour traces, metrics, logs (collector, exporters)
- **Structured Logging** : JSON logging, log levels, log aggregation
- **Distributed Tracing** : Trace context propagation, spans, root cause
- **RED / USE Metrics** : Rate/Errors/Duration (services), Utilization/Saturation/Errors (resources)
- **Alerting** : Alertmanager, receivers, routing, escalation, silencing
- **Incident Management** : PagerDuty, Opsgenie, incident.io

## SRE et Fiabilité

- **SLO / SLI / SLA** : Service Level Objectives, Indicators, Agreements
- **Error Budget** : Budget d'erreur (disponibilité - SLO)
- **Burn Rate** : Taux de consommation du budget d'erreur
- **Multi-Window Multi-Burn-Rate** : Alerting basé sur plusieurs fenêtres de burn rate
- **Toil Automation** : Automatisation du travail manuel (toil)
- **Capacity Planning** : Planification de capacité (modélisation, scaling)
- **Load Testing (k6)** : Tests de charge modernes (k6, Locust, Gatling)
- **Chaos Engineering** : Chaos Mesh, Litmus, Gremlin
- **Resilience Testing** : Fault injection, chaos experiments
- **Postmortem / Incident Command** : Blameless postmortem, incident command system
- **AIOps / Anomaly Detection** : Détection d'anomalies par IA, ML pour ops