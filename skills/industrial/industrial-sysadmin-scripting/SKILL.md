---
name: industrial-sysadmin-scripting
description: "Scripter en Bash et PowerShell pour l'administration OT."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [windows, linux]
metadata:
  tags: [bash, powershell, sysadmin, backup, ot, cybersecurity, network, monitoring, docker]
  related_skills: [sql-for-industrial-systems, ot-it-integration-languages]
---

# Scripting Shell (PowerShell & Bash) pour l'Administration et la Maintenance OT

Cette compétence encadre l'écriture de scripts d'administration système (PowerShell sous Windows, Bash sous Linux) dédiés à la maintenance des serveurs industriels, à la sauvegarde automatique de projets d'automates, à la surveillance des ressources matérielles et à la sécurité réseau des ateliers.

---

## 1. PowerShell Professionnel sous Windows Server

Les serveurs industriels exécutent des environnements de virtualisation (Hyper-V) ou des serveurs d'acquisition. Le script ci-dessous supervise l'exécution du service de serveurs OPC UA, gère les credentials et consigne les anomalies dans le journal d'événements Windows (Event Log).

```powershell
# Script de monitoring de service industriel avec journalisation Event Log
$ServiceName = "Kepware.KEPServerEX.V6"
$EventLogSource = "EVAOT"
$EventLogName = "Application"

# Enregistrement de la source d'evenements si absente (requis execution Admin)
if (-not [System.Diagnostics.EventLog]::SourceExists($EventLogSource)) {
    New-EventLog -Source $EventLogSource -LogName $EventLogName
}

$Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue

if ($null -eq $Service) {
    Write-EventLog -LogName $EventLogName -Source $EventLogSource -EventId 1001 -EntryType Error `
        -Message "Le service de communication Kepware ($ServiceName) est introuvable sur le serveur !"
    exit 1
}

if ($Service.Status -ne 'Running') {
    Write-EventLog -LogName $EventLogName -Source $EventLogSource -EventId 1002 -EntryType Warning `
        -Message "Le service $ServiceName est arrete (Statut actuel: $($Service.Status)). Tentative de redemarrage automatique..."
    
    Start-Service -Name $ServiceName
    Start-Sleep -Seconds 15
    
    $Service.Refresh()
    if ($Service.Status -eq 'Running') {
        Write-EventLog -LogName $EventLogName -Source $EventLogSource -EventId 1003 -EntryType Information `
            -Message "Le service $ServiceName a ete redemarre avec succes par le script EVA."
    } else {
        Write-EventLog -LogName $EventLogName -Source $EventLogSource -EventId 1004 -EntryType Error `
            -Message "Echec critique de redemarrage du service $ServiceName !"
    }
}
```

---

## 2. Bash de Production pour Passerelles IoT Edge Linux

Les passerelles industrielles miniatures (ex: Advantech sous Debian) exigent une écriture robuste (gestion des erreurs, traçabilité par syslog).

### Script d'export et archivage automatique
Ce script réalise une copie de sauvegarde d'une configuration automate, génère un condensé SHA-256 pour garantir l'intégrité, et la transfère sur un serveur d'archivage OT sécurisé.

```bash
#!/bin/bash
set -euo pipefail # Arrêt immédiat sur erreur, variables non déclarées ou échec de pipe

# Configuration
BACKUP_SOURCE="/opt/EVA/gateway/configs"
BACKUP_DEST_DIR="/tmp/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ARCHIVE_NAME="config_backup_${TIMESTAMP}.tar.gz"
DEST_SERVER="192.168.1.50"
DEST_USER="ot_archiver"
SSH_KEY="/home/ot_admin/.ssh/id_ed25519"

mkdir -p "$BACKUP_DEST_DIR"

# 1. Creation de l'archive tar.gz
tar -czf "${BACKUP_DEST_DIR}/${ARCHIVE_NAME}" -C "$BACKUP_SOURCE" .

# 2. Generation de la signature SHA-256 d'integrite
sha256sum "${BACKUP_DEST_DIR}/${ARCHIVE_NAME}" > "${BACKUP_DEST_DIR}/${ARCHIVE_NAME}.sha256"

# 3. Transfert securise via SFTP (sans mot de passe - utilise la cle SSH)
sftp -i "$SSH_KEY" -b - "${DEST_USER}@${DEST_SERVER}" <<EOF
put ${BACKUP_DEST_DIR}/${ARCHIVE_NAME} /backups/
put ${BACKUP_DEST_DIR}/${ARCHIVE_NAME}.sha256 /backups/
quit
EOF

# 4. Nettoyage local
rm -f "${BACKUP_DEST_DIR}/${ARCHIVE_NAME}" "${BACKUP_DEST_DIR}/${ARCHIVE_NAME}.sha256"

logger -t EVAOT "[INFO] Archive de sauvegarde ${ARCHIVE_NAME} transmise avec succes."
```

---

## 3. Déploiement Industriel Edge (Docker Compose de Production)

Pour déployer la stack de collecte d'atelier (Telegraf / InfluxDB / Grafana), le fichier de configuration Docker Compose doit intégrer des règles de limitation de ressources strictes pour ne jamais surcharger la passerelle et bloquer d'autres services locaux.

```yaml
version: '3.8'

services:
  telegraf:
    image: telegraf:1.28-alpine
    container_name: EVA-telegraf-collector
    restart: unless-stopped
    read_only: true
    # Restriction stricte de consommation CPU et memoire
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 128M
        reservations:
          memory: 64M
    # Montage de dossiers temporaires en RAM pour eviter l'usure de carte SD
    tmpfs:
      - /tmp
      - /run
    volumes:
      - ./telegraf.conf:/etc/telegraf/telegraf.conf:ro
    environment:
      - OPC_UA_SERVER_URL=opc.tcp://192.168.1.100:4840
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  influxdb:
    image: influxdb:2.7-alpine
    container_name: EVA-influxdb-telemetry
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
    volumes:
      - influxdb-data:/var/lib/influxdb2
    ports:
      - "8086:8086"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  influxdb-data:
    driver: local
```

---

## 4. Durcissement Réseau (Hardening) de la Passerelle

* **Isolement des interfaces** : Bloquez tout routage entre l'interface réseau connectée au réseau usine automate (ex. `eth1`) et l'interface connectée au réseau entreprise IT (ex. `eth0`) pour éviter les intrusions directes.
* **Fermeture des ports non requis** : N'ouvrez aucun port d'écoute autre que les ports de collecte et d'administration de la passerelle. Désactivez les protocoles non sécurisés de base (Telnet, FTP, HTTP non sécurisé).
