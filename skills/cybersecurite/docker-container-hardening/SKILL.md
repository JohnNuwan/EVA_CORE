---
name: docker-container-hardening
description: Guide complet de sécurisation Docker et containers — rootless, image scanning, seccomp, AppArmor, read-only rootfs, resource limits, non-root user, et audit de sécurité.
domain: [cybersecurite, devops]
tags: [docker, container, securite, hardening, rootless, apparmor, seccomp]
priority: haute
---

# 🐳 Docker & Container Hardening

Guide de sécurisation des containers Docker pour environnements de production.  
Couvre : configuration du daemon, profils de sécurité, rootless, builds sécurisés, et auditing.

---

## 1. Configuration du Daemon Docker

### 1.1 Fichier `/etc/docker/daemon.json`

```json
{
  "icc": false,
  "live-restore": true,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "userland-proxy": false,
  "iptables": true,
  "userns-remap": "default",
  "no-new-privileges": true,
  "seccomp-profile": "/etc/docker/seccomp-default.json",
  "disable-legacy-registry": true,
  "allow-nondistributable-artifacts": []
}
```

**Explications :**
- `icc: false` — désactive la communication inter-conteneurs
- `userns-remap: "default"` — mappe root container → utilisateur non-privilégié
- `no-new-privileges: true` — empêche les escalades via suid
- `seccomp-profile` — restreint les appels système autorisés
- `userland-proxy: false` — réduit la surface d'attaque réseau

### 1.2 Vérification

```bash
docker info --format '{{.SecurityOptions}}'
# Doit contenir : name=seccomp,profile=default, name=no-new-privileges
```

---

## 2. Exécution Rootless

### 2.1 Installation Rootless

```bash
# Installer le daemon rootless
dockerd-rootless-setuptool.sh install

# Variables d'environnement
export DOCKER_HOST=unix:///run/user/$UID/docker.sock
export PATH=/usr/bin:$PATH

# Activer le service au démarrage
systemctl --user enable docker
systemctl --user start docker
```

### 2.2 Vérification

```bash
docker info | grep -i rootless
# Doit afficher : rootless
```

---

## 3. Sécurité par Container

### 3.1 Docker Compose Sécurisé

```yaml
services:
  app:
    image: mon-app:latest
    restart: unless-stopped
    
    # Restreindre les bindings réseau
    ports:
      - "127.0.0.1:8000:8000"    # ← 127.0.0.1 PAS 0.0.0.0
    
    # Dropper les capacités
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE        # Seulement ce qui est nécessaire
    
    # Sécurité renforcée
    security_opt:
      - no-new-privileges:true
      - seccomp=default
    
    # AppArmor
    security_opt:
      - apparmor:docker-default
    
    # Read-only rootfs
    read_only: true
    tmpfs:
      - /tmp
      - /var/run
    
    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    
    # Non-root user
    user: "1000:1000"
    
    # Pas de privilèges
    privileged: false
    
    # Volumes limités
    volumes:
      - type: bind
        source: ./data
        target: /data
        read_only: true
```

### 3.2 Check-list de Sécurité par Container

| Option | Valeur | Risque si absent |
|--------|--------|------------------|
| `user:` | 1000:1000 | Exécution en root |
| `cap_drop: ALL` | — | Capacités root inutiles |
| `read_only: true` | — | Écriture dans rootfs |
| `privileged: false` | — | Accès complet au host |
| `security_opt: no-new-privileges` | — | Escalade via suid |
| `ports: 127.0.0.1:` | — | Exposition réseau |
| `restart: unless-stopped` | — | Pas de restart policy |

---

## 4. Image Scanning

### 4.1 Trivy (Recommandé)

```bash
# Installation
apt install trivy
# ou
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh

# Scan d'image
trivy image mon-image:latest

# Scan dans CI/CD avec sortie JSON
trivy image --format json --output trivy-report.json mon-image:latest

# Scan avec seuils
trivy image --severity CRITICAL,HIGH --exit-code 1 mon-image:latest
```

### 4.2 Docker Scout

```bash
# Activer Docker Scout
docker scout quickview mon-image:latest

# Analyse détaillée
docker scout recommendations mon-image:latest

# Comparer avec une autre image
docker scout compare mon-image:latest --to alpine:latest
```

### 4.3 Grype

```bash
# Installation
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# Scan
grype mon-image:latest
```

---

## 5. AppArmor pour Containers

### 5.1 Profil par défaut

```bash
# Voir le profil par défaut Docker
cat /etc/apparmor.d/docker

# Vérifier que Docker utilise AppArmor
docker run --rm alpine cat /proc/1/attr/current
# Doit retourner : docker-default (enforce)
```

### 5.2 Profil personnalisé

```
# /etc/apparmor.d/containers/mon-app
#include <tunables/global>

profile mon-app flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  #include <abstractions/lxc/container-base>
  
  # Réseau
  network tcp,
  network udp,
  network inet stream,
  
  # Lecture fichiers
  /etc/ssl/** r,
  /usr/lib/** rm,
  
  # Écriture limitée
  /data/** rwk,
  
  # Interdire
  deny /proc/sys/kernel/** w,
  deny /sys/devices/system/cpu/** w,
}
```

**Charger le profil :**
```bash
apparmor_parser -r /etc/apparmor.d/containers/mon-app
docker run --security-opt apparmor=mon-app mon-image
```

---

## 6. Seccomp

### 6.1 Vérifier les appels système bloqués

```bash
# Lister les appels système autorisés par défaut
docker run --rm alpine sh -c 'cat /proc/self/status | grep Seccomp'
# 2 = filtré

# Voir le profil par défaut
docker info --format '{{json .SecurityOptions}}' | jq
```

### 6.2 Profil personnalisé

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": ["accept4", "bind", "connect", "listen", "read", "write", "openat", "close", "mmap", "munmap", "brk", "futex", "nanosleep", "clock_gettime", "getpid", "exit", "exit_group"],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

**Utilisation :**
```bash
docker run --security-opt seccomp=custom-profile.json mon-image
```

---

## 7. Audit Docker

### 7.1 Docker Bench Security

```bash
# Audit complet CIS Benchmark
git clone https://github.com/docker/docker-bench-security.git
cd docker-bench-security
sudo sh docker-bench-security.sh

# Score formaté
sudo sh docker-bench-security.sh | grep -E '\[WARN\]|\[PASS\]'
```

### 7.2 Lynis Audit

```bash
# Audit système complet + Docker
git clone https://github.com/CISOfy/lynis
cd lynis
./lynis audit system

# Rapport
cat /var/log/lynis-report.dat
```

### 7.3 Audit Manuel

```bash
# Vérifier les containers privilegiés
docker ps --quiet | xargs docker inspect --format '{{.Name}} {{.HostConfig.Privileged}}'

# Vérifier les containers avec cap_sys_admin
docker ps --quiet | xargs docker inspect --format '{{.Name}} {{range $cap := .HostConfig.CapAdd}}{{$cap}} {{end}}'

# Vérifier les montages de volumes sensibles
docker ps --quiet | xargs docker inspect --format '{{.Name}} {{range $m := .Mounts}}{{$m.Source}} {{end}}'

# Vérifier les containers en root
docker ps --quiet | xargs docker inspect --format '{{.Name}} {{.Config.User}}'
```

---

## 8. Docker Socket Protection

> **⚠️ ATTENTION :** `/var/run/docker.sock` est un accès root complet.

### 8.1 Audit des accès

```bash
# Voir qui peut accéder au socket
getent group docker
ls -la /var/run/docker.sock

# Surveiller les accès avec auditd
sudo auditctl -w /var/run/docker.sock -p rwa -k docker-sock-access

# Voir les logs
sudo ausearch -k docker-sock-access
```

### 8.2 Proxy de socket sécurisé

```bash
# Utiliser docker-socket-proxy pour exposer seulement certaines API
docker run -d \
  --name docker-socket-proxy \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e CONTAINERS=1 \
  -e POST=0 \
  -p 127.0.0.1:2375:2375 \
  tecnativa/docker-socket-proxy
```

---

## 9. Images de Base Recommandées

| Image | Taille | Usage | Sécurité |
|-------|--------|-------|----------|
| `alpine:3.20` | ~7 MB | Apps Go/Python/Rust | ✅ Minimal |
| `debian:stable-slim` | ~80 MB | Apps complexes | ✅ Support long |
| `gcr.io/distroless/base-nonroot` | ~20 MB | Apps statiques | ✅ Rootless par défaut |
| `chainguard/python:latest` | ~50 MB | Python | ✅ CVE 0 |
| `scratch` | 0 B | Binaires statiques | ✅ Minimal absolu |

---

## 10. CI/CD Pipeline Check

```yaml
# .github/workflows/docker-security.yml
name: Docker Security Audit
on: [push]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build
        run: docker build -t app .
      
      - name: Trivy Scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'app'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
      
      - name: Docker Bench
        run: |
          git clone https://github.com/docker/docker-bench-security.git
          cd docker-bench-security
          sudo sh docker-bench-security.sh > bench-report.txt
      
      - name: Check non-root user
        run: |
          if docker run --rm app whoami | grep -q root; then
            echo "❌ Container runs as root!"
            exit 1
          fi
```

---

## Pitfalls

- **Ne JAMAIS** exposer `/var/run/docker.sock` dans un container — équivalent root
- **Ne JAMAIS** utiliser `network_mode: host` sauf nécessité absolue
- **Ne JAMAIS** utiliser `privileged: true`
- **Toujours** spécifier un utilisateur non-root
- **Toujours** utiliser `127.0.0.1:` binding pour les ports internes
- Ne pas oublier de restreindre aussi les ports dans `docker-compose.yml` **et** dans la commande `docker run`