---
name: incident-response-dfir
description: Guide complet de réponse aux incidents et forensic numérique (DFIR) — playbooks, acquisition, analyse mémoire, chaîne de custody, et remédiation.
domain: [cybersecurite, securite, operations]
tags: [incident-response, dfir, forensic, memory-forensic, playbook, ir]
priority: haute
---

# 🚨 Incident Response & Digital Forensics (DFIR)

Guide de réponse aux incidents et analyse forensique pour environnements Linux.  
Couvre : playbooks IR, acquisition mémoire/disque, analyse de logs, chaîne de custody, et remédiation.

---

## 1. Pyramide de Réponse aux Incidents

```
                   ╱╲
                  ╱  ╲
                 ╱    ╲
                ╱  IR  ╲
               ╱────────╲
              ╱  Analyse  ╲
             ╱──────────── ╲
            ╱  Containment  ╲
           ╱──────────────── ╲
          ╱  Eradication      ╲
         ╱──────────────────── ╲
        ╱   Recovery            ╲
       ╱──────────────────────── ╲
      ╱     Lessons Learned       ╲
     ╱──────────────────────────── ╲
```

---

## 2. Playbooks IR

### 2.1 Playbook Générique (NIST SP 800-61)

| Phase | Action | Outils | Durée |
|-------|--------|--------|-------|
| 1. Preparation | Hardening, logs, backups | Osquery, auditd, rsync | Continu |
| 2. Detection | Alerte, triage | Wazuh, Prometheus | T+0 |
| 3. Triage | Classification, priorité | CVSS scoring | T+15min |
| 4. Containment | Isolation réseau | iptables, Docker stop | T+30min |
| 5. Analysis | Acquisition mémoire | LiME, volatility | T+1h |
| 6. Eradication | Nettoyage, patch | Ansible, yum/apt | T+2h |
| 7. Recovery | Restauration | rsync, duplicity | T+4h |
| 8. Lessons Learned | Rapport, amélioration | — | T+1sem |

### 2.2 Playbook Brute-Force SSH

```bash
# 1. DETECTION — Voir les tentatives échouées
sudo journalctl -u sshd --since "1 hour ago" | grep "Failed password"

# 2. CONTAINMENT — Bloquer l'IP attaquante
sudo iptables -A INPUT -s <IP_ATTAQUANT> -j DROP

# 3. ANALYSE — Sauvegarder les logs d'auth
sudo cp /var/log/auth.log /forensics/auth-$(date +%Y%m%d-%H%M).log

# 4. ÉRADICATION — Vérifier les comptes compromis
sudo lastlog | grep -v "Never logged in"
sudo lastb | head -20

# 5. REMÉDIATION — Durcir SSH
sudo sed -i 's/^#MaxAuthTries.*/MaxAuthTries 3/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

### 2.3 Playbook Container Compromis

```bash
# 1. DÉTECTION
docker logs <container> --tail 100 --since 10m

# 2. CONTAINMENT — Arrêter et isoler
docker stop <container>
docker network disconnect <network> <container>
iptables -A INPUT -p tcp --dport <PORT> -j DROP

# 3. ACQUISITION — Sauvegarder l'image
docker commit <container> compromised/container:$(date +%s)
docker save compromised/container:latest -o /forensics/container.tar

# 4. ANALYSE — Inspecter les couches
docker history --no-trunc <container>
docker inspect <container> > /forensics/container-inspect.json

# 5. ÉRADICATION — Supprimer le container
docker rm -f <container>
```

---

## 3. Acquisition Forensique

### 3.1 Acquisition Mémoire (RAM)

```bash
# AVANT DE TOUTE CHOSE — capturer la RAM
# La mémoire vitale doit être la première acquisition

# Option 1 : LiME (Linux Memory Extractor)
wget https://github.com/504ensicsLabs/LiME/archive/refs/tags/v1.9.1.tar.gz
tar xzf v1.9.1.tar.gz && cd LiME-1.9.1/src
make
sudo insmod lime-*.ko "path=/forensics/ram-$(hostname)-$(date +%Y%m%d-%H%M).lime format=lime"
# Ou format=raw pour Volatility 3

# Option 2 : AVML (Microsoft)
wget https://github.com/microsoft/avml/releases/latest/download/avml
chmod +x avml
sudo ./avml /forensics/ram-$(hostname).core

# Option 3 : fmem (kernel module)
git clone https://github.com/NateBrune/fmem.git
cd fmem && make
sudo ./run.sh /forensics/ram.raw

# Hash d'intégrité
sha256sum /forensics/ram-*.lime > /forensics/hashes.txt
```

### 3.2 Acquisition Disque

```bash
# Image disque complète (dd)
# ⚠️ Écrire sur un disque externe, PAS sur le disque source
sudo dd if=/dev/sda of=/forensics/disk-image.dd bs=4M conv=noerror,sync status=progress

# Image compressée (dcfldd/dcfldd)
sudo dcfldd if=/dev/sda of=/forensics/disk-image.dd hash=sha256 hashlog=/forensics/hash.log

# Image logique (seulement les fichiers pertinents)
sudo rsync -avz --delete --one-file-system / /forensics/rootfs/

# Acquisition des logs système
sudo tar czf /forensics/system-logs-$(date +%Y%m%d).tar.gz \
  /var/log/ \
  /var/lib/docker/containers/ \
  /etc/ \
  /var/spool/cron/
```

### 3.3 Collecte Ciblée (Live Response Script)

```bash
#!/bin/bash
# live_response.sh — Collecte forensique rapide
# Exécuter sur la machine compromise

OUTDIR="/forensics/live-$(hostname)-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUTDIR"

echo "=== PROCESSUS ===" > "$OUTDIR/processes.txt"
ps auxf >> "$OUTDIR/processes.txt"
ps aux --forest >> "$OUTDIR/processes.txt"

echo "=== CONNEXIONS RÉSEAU ===" > "$OUTDIR/network.txt"
ss -tunap >> "$OUTDIR/network.txt"
ss -tlnp >> "$OUTDIR/listen.txt"
netstat -rn >> "$OUTDIR/routes.txt"

echo "=== DOCKER ===" > "$OUTDIR/docker.txt"
docker ps -a >> "$OUTDIR/docker.txt"
docker images >> "$OUTDIR/docker-images.txt"
docker network ls >> "$OUTDIR/docker-network.txt"

echo "=== CRON ===" > "$OUTDIR/cron.txt"
crontab -l >> "$OUTDIR/cron.txt"
ls -la /etc/cron* >> "$OUTDIR/cron-files.txt"

echo "=== UTILISATEURS ===" > "$OUTDIR/users.txt"
cat /etc/passwd >> "$OUTDIR/users.txt"
cat /etc/shadow >> "$OUTDIR/shadow.txt"
last -F 100 >> "$OUTDIR/lastlog.txt"
w >> "$OUTDIR/who.txt"

echo "=== FICHIERS SUSPECTS (setuid) ===" > "$OUTDIR/setuid.txt"
find / -perm -4000 -type f 2>/dev/null >> "$OUTDIR/setuid.txt"

echo "=== MODULES KERNEL ===" > "$OUTDIR/kernel-modules.txt"
lsmod >> "$OUTDIR/kernel-modules.txt"
cat /proc/modules >> "$OUTDIR/kernel-modules.txt"

echo "=== HISTORIQUE BASH ===" > "$OUTDIR/bash-history.txt"
cat ~/.bash_history >> "$OUTDIR/bash-history.txt"
cat ~/.bashrc >> "$OUTDIR/bashrc.txt"

# Hachage
sha256sum "$OUTDIR"/* > "$OUTDIR/hashes.txt"

# Empaqueter
tar czf "$OUTDIR.tar.gz" "$OUTDIR"
```

---

## 4. Analyse Mémoire avec Volatility 3

```bash
# Installation
pip install volatility3

# Lister les profils
volatility3 -f ram.lime windows.info

# Pour Linux, détecter automatiquement
volatility3 -f ram.lime linux.banner

# Analyser les processus
volatility3 -f ram.lime linux.pslist
volatility3 -f ram.lime linux.psaux
volatility3 -f ram.lime linux.pstree

# Connexions réseau
volatility3 -f ram.lime linux.netstat
volatility3 -f ram.lime linux.arp

# Modules kernel chargés
volatility3 -f ram.lime linux.lsmod

# Sysfs / Procfs
volatility3 -f ram.lime linux.proc.Malfind
volatility3 -f ram.lime linux.check_afinfo

# Caches bash
volatility3 -f ram.lime linux.bash

# Dump d'un processus
volatility3 -f ram.lime linux.proc.Dump --pid <PID> --dump
```

---

## 5. Analyse de Logs

### 5.1 Logs Système Linux

```bash
# Authentification
sudo journalctl -u sshd --no-pager | grep -E "Failed|Accepted|Invalid user"
sudo ausearch -m LOGIN --start today

# Sudo
sudo journalctl -u sudo --no-pager

# Kernel
sudo dmesg --level=err,warn | tail -100

# AppArmor
sudo journalctl -u apparmor --no-pager | grep DENIED

# Docker
docker logs <container> --since 24h
```

### 5.2 Recherche d'IOCs

```bash
# Reverse shell patterns
sudo grep -r "bash -i" /var/log/ 2>/dev/null
sudo grep -r "/dev/tcp/" /var/log/ 2>/dev/null
sudo grep -r "exec 5<>/dev/tcp" /var/log/ 2>/dev/null

# Crypto miners
sudo grep -r "stratum" /var/log/ 2>/dev/null
sudo grep -r "xmr" /var/log/ 2>/dev/null
sudo grep -r "mine" /var/log/syslog 2>/dev/null

# Outils d'énumération
sudo grep -r "nmap\|masscan\|nikto\|sqlmap" ~/.bash_history 2>/dev/null
```

---

## 6. Chaîne de Custody

### 6.1 Documentation des Preuves

```bash
# Calculer les hashes de toutes les preuves
find /forensics/ -type f -exec sha256sum {} \; > /forensics/chain-of-custody.txt

# Signer avec GPG
gpg --detach-sign --armor /forensics/chain-of-custody.txt

# Horodatage
echo "Acquisition: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> /forensics/chain-of-custody.txt
echo "Acquisiteur: $(whoami)@$(hostname)" >> /forensics/chain-of-custody.txt
echo "Méthode: dd / LiME / AVML" >> /forensics/chain-of-custody.txt
```

### 6.2 Template de Rapport

```
═══ RAPPORT D'INCIDENT ═══

ID: IR-2026-XXXXX
Date: YYYY-MM-DD HH:MM UTC
Détecté par: [Wazuh / Prometheus / Manuelle]
Sévérité: [CRITICAL / HIGH / MEDIUM / LOW]

═══ CHRONOLOGIE ═══
T+0:00  — Détection initiale
T+0:15  — Triage terminé, containment initié
T+0:30  — Acquisition mémoire effectuée
T+1:00  — Analyse en cours
T+2:00  — Root cause identifiée
T+3:00  — Éradication
T+4:00  — Rétablissement

═══ INDICATEURS DE COMPROMISSION (IOC) ═══
- IP: 10.0.0.X (source de l'attaque)
- Hash: sha256:... (fichier malveillant)
- Domaine: evil.com (C2)
- PID: 12345 (processus malveillant)

═══ ACTIONS ═══
1. Blocage IP dans iptables
2. Suppression du fichier /tmp/evil
3. Changement de toutes les clés SSH
4. ...

═══ LEÇONS APPRISES ═══
- Amélioration : ajouter fail2ban
- Amélioration : audit des permissions
```

---

## 7. Remédiation Automatisée

### 7.1 Post-Incident Hardening

```bash
# 1. Changer tous les mots de passe
for user in $(cat /etc/passwd | grep /home | cut -d: -f1); do
    passwd $user
done

# 2. Regénérer les clés SSH
sudo rm -f /etc/ssh/ssh_host_*
sudo dpkg-reconfigure openssh-server

# 3. Audit des crontabs
for user in $(cut -f1 -d: /etc/passwd); do
    crontab -u $user -l 2>/dev/null | grep .
done

# 4. Audit des services
sudo systemctl list-units --type=service --state=running

# 5. Audit des ports
ss -tlnp
```

---

## 8. Outils DFIR Essentiels

| Outil | Usage | Installation |
|-------|-------|--------------|
| **LiME** | Acquisition mémoire | Compilation kernel module |
| **AVML** | Acquisition mémoire | Binaire statique |
| **Volatility 3** | Analyse mémoire | `pip install volatility3` |
| **Autopsy** | Analyse disque | `apt install autopsy` |
| **Sleuth Kit** | Analyse filesystem | `apt install sleuthkit` |
| **Zeek** | NSM réseau | `apt install zeek` |
| **Wazuh** | SIEM + EDR | Docker Compose |
| **Osquery** | Endpoint visibility | `apt install osquery` |
| **TheHive** | Case management | Docker Compose |
| **Rekall** | Memory forensics | `pip install rekall` |

---

## Pitfalls

- **Toujours** capturer la RAM en premier — les données volatiles sont perdues au redémarrage
- **Ne JAMAIS** éteindre la machine compromise avant d'avoir capturé la mémoire
- **Ne JAMAIS** écrire les preuves sur le disque source — utiliser un disque externe
- **Toujours** documenter la chaîne de custody avec des hashes
- **Toujours** préserver les métadonnées (timestamps, permissions)
- Ne pas faire confiance aux binaires du système compromis — utiliser des binaires statiques
- Vérifier que les outils d'acquisition ne modifient pas la mémoire/le disque