---
name: ansible-automation
description: "Automatisation de configuration avec Ansible — playbooks, rôles, inventaires dynamiques, variables, facts, handlers, vault, AWX/Tower, idempotence"
version: 1.0.0
author: EVA
license: Privée EVA
category: mlops
metadata:
  EVA:
    tags: [ansible, automation, configuration-management, playbooks, rôles, inventaires, vault, awx]
    related_skills: [terraform-iac, kubernetes-avance, docker-avance, prometheus-grafana]
---

# Ansible — Automatisation de Configuration

## Vue d'ensemble

Ansible (Red Hat) est le standard pour l'automatisation de la configuration des serveurs sans agent. Cette compétence couvre l'écriture de playbooks et rôles idempotents, les inventaires dynamiques, Ansible Vault pour les secrets, les handlers, les modules essentiels, l'intégration avec AWX/Tower, et les bonnes pratiques de structure.

## Quand l'utiliser

- Déployer la configuration initiale d'un serveur (cloud-init complément)
- Gérer les utilisateurs, paquets, services sur un parc de machines
- Automatiser des tâches répétitives (mises à jour, backups, audits)
- Déployer des applications avec des rôles réutilisables
- Orchestrer des déploiements multi-couches (load balancer → app → db)

---

## 1. Structure de Projet

```
ansible/
├── inventory/
│   ├── production/
│   │   ├── hosts.yml          # Inventaire statique
│   │   └── group_vars/
│   │       ├── all.yml
│   │       └── webservers.yml
│   └── staging/
│       └── hosts.yml
├── roles/
│   ├── common/
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   ├── handlers/
│   │   │   └── main.yml
│   │   ├── templates/
│   │   │   └── motd.j2
│   │   ├── vars/
│   │   │   └── main.yml
│   │   └── defaults/
│   │       └── main.yml
│   ├── docker/
│   │   └── ... (même structure)
│   └── monitoring/
│       └── ...
├── playbooks/
│   ├── site.yml               # Playbook principal
│   ├── update.yml             # Mise à jour systèmes
│   └── backup.yml             # Sauvegarde
├── ansible.cfg
├── requirements.yml           # Collections & rôles externes
└── vault-password.sh          # Script de déchiffrement vault
```

### ansible.cfg

```ini
[defaults]
inventory = inventory/production/hosts.yml
host_key_checking = False
stdout_callback = yaml
retry_files_enabled = False
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_cache
fact_caching_timeout = 3600
roles_path = roles/
collections_path = collections/

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
```

---

## 2. Inventaires

### Statique YAML

```yaml
# inventory/production/hosts.yml
all:
  children:
    webservers:
      hosts:
        web01:
          ansible_host: 192.168.1.10
          ansible_user: deploy
        web02:
          ansible_host: 192.168.1.11
          ansible_user: deploy
      vars:
        nginx_port: 443
        app_version: "1.2.3"

    databases:
      hosts:
        db01:
          ansible_host: 192.168.1.20
          postgres_version: "16"

    monitoring:
      hosts:
        monitor:
          ansible_host: 192.168.1.30

  vars:
    ansible_python_interpreter: /usr/bin/python3
    timezone: Europe/Paris
    admin_email: admin@eva.local
```

### Dynamique AWS EC2

```yaml
# inventory/aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions:
  - eu-west-3
filters:
  tag:Environment:
    - production
  instance-state-name:
    - running
keyed_groups:
  - key: tags.Role
    prefix: role
  - key: placement.region
    prefix: aws_region
hostnames:
  - network-interface.association.public-dns-name
compose:
  ansible_host: public_ip_address
```

---

## 3. Playbooks

### Site principal

```yaml
# playbooks/site.yml
---
- name: Configuration de base (tous les serveurs)
  hosts: all
  gather_facts: true
  become: true
  roles:
    - role: common
      tags: [common, always]

- name: Déploiement Docker
  hosts: webservers
  become: true
  roles:
    - role: docker
      tags: [docker]
    - role: nginx
      tags: [nginx]
  post_tasks:
    - name: Vérifier que l'application répond
      uri:
        url: "https://{{ ansible_default_ipv4.address }}/health"
        status_code: 200
      tags: [healthcheck]

- name: Configuration base de données
  hosts: databases
  become: true
  roles:
    - role: postgres
      tags: [postgres]
```

### Mise à jour système

```yaml
# playbooks/update.yml
---
- name: Mise à jour et redémarrage
  hosts: all
  become: true
  serial: "20%"  # Rolling update, 20% à la fois

  tasks:
    - name: Mise à jour des paquets (Debian)
      apt:
        update_cache: true
        upgrade: dist
        autoremove: true
      when: ansible_os_family == "Debian"
      register: apt_upgrade

    - name: Redémarrer si kernel mis à jour
      reboot:
        reboot_timeout: 300
        pre_reboot_delay: 30
      when: apt_upgrade.changed and 'linux-image' in apt_upgrade.stdout
```

---

## 4. Rôles

### Role common (base universelle)

```yaml
# roles/common/tasks/main.yml
---
- name: Configurer le fuseau horaire
  timezone:
    name: "{{ timezone }}"

- name: Créer l'utilisateur admin
  user:
    name: "{{ admin_user }}"
    groups: sudo
    shell: /bin/bash
    create_home: true
    ssh_key_file: .ssh/authorized_keys

- name: Déployer clé SSH autorisée
  authorized_key:
    user: "{{ admin_user }}"
    key: "{{ lookup('file', 'files/{{ admin_user }}.pub') }}"

- name: Configurer le pare-feu (UFW)
  ufw:
    rule: "{{ item.rule }}"
    port: "{{ item.port | default(omit) }}"
    proto: "{{ item.proto | default('tcp') }}"
  loop:
    - { rule: 'allow', port: '22' }
    - { rule: 'allow', port: '80' }
    - { rule: 'allow', port: '443' }
  when: configure_firewall | default(false)

- name: Configurer fail2ban
  template:
    src: jail.local.j2
    dest: /etc/fail2ban/jail.local
  notify: restart fail2ban

# handlers
---
# roles/common/handlers/main.yml
- name: restart fail2ban
  systemd:
    name: fail2ban
    state: restarted
    daemon_reload: true
```

### Role Docker

```yaml
# roles/docker/tasks/main.yml
---
- name: Installer les dépendances Docker
  apt:
    name:
      - ca-certificates
      - curl
      - gnupg
    state: present

- name: Ajouter le dépôt Docker officiel
  apt_repository:
    repo: "deb [arch={{ 'arm64' if ansible_architecture == 'aarch64' else 'amd64' }}] https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable"
    state: present

- name: Installer Docker
  apt:
    name:
      - docker-ce
      - docker-ce-cli
      - containerd.io
      - docker-compose-plugin
    state: present

- name: Démarrer et activer Docker
  systemd:
    name: docker
    enabled: true
    state: started

- name: Ajouter l'utilisateur au groupe docker
  user:
    name: "{{ admin_user }}"
    groups: docker
    append: true

- name: Installer docker-compose
  get_url:
    url: "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-{{ ansible_architecture }}"
    dest: /usr/local/bin/docker-compose
    mode: '0755'
```

---

## 5. Ansible Vault (Secrets)

```bash
# Créer un fichier chiffré
ansible-vault create secrets.yml

# Éditer
ansible-vault edit secrets.yml

# Voir le contenu déchiffré
ansible-vault view secrets.yml

# Chiffrer un fichier existant
ansible-vault encrypt group_vars/production/vault.yml

# Exécuter un playbook avec vault
ansible-playbook playbooks/site.yml --ask-vault-pass

# Avec script de déchiffrement (CI)
ansible-playbook playbooks/site.yml --vault-password-file vault-password.sh
```

### Fichier vault structuré

```yaml
# group_vars/production/vault.yml
vault_db_password: "s3cur3P@ssw0rd!"
vault_api_key: "sk-proj-xxx"
vault_ssl_private_key: |
  -----BEGIN PRIVATE KEY-----
  ...
  -----END PRIVATE KEY-----
```

---

## 6. Modules Essentiels

| Module | Usage | Exemple |
|--------|-------|---------|
| `copy` | Copier fichiers locaux | `copy: src=nginx.conf dest=/etc/nginx/` |
| `template` | Templates Jinja2 | `template: src=app.env.j2 dest=/opt/app/.env` |
| `command` / `shell` | Commandes arbitraires | `shell: df -h \| grep /dev/sda1` |
| `systemd` | Gestion services | `systemd: name=nginx state=restarted daemon_reload=yes` |
| `uri` | Requêtes HTTP | `uri: url=http://localhost:8080/health return_content=yes` |
| `docker_container` | Gestion conteneurs | `docker_container: name=nginx image=nginx:alpine ports=80:80` |
| `community.docker.docker_compose_v2` | Docker Compose | `docker_compose_v2: project_src=/opt/app` |
| `iptables` / `ufw` | Firewall | `ufw: rule=allow port=443 proto=tcp` |

---

## 7. Pièges Courants

1. **Pas d'idempotence :** Utiliser `shell:` au lieu de modules spécialisés. `command`/`shell` ne sont pas idempotents — préférer `copy`, `template`, `apt`, `systemd`.
2. **Facts désactivés :** `gathering: explicit` empêche l'accès à `ansible_os_family`, `ansible_default_ipv4`, etc. Garder `smart` ou `implicit`.
3. **Tags manquants :** Sans tags, `ansible-playbook --tags docker` ne fonctionne pas. Tagger chaque rôle et tâche.
4. **Handlers oubliés :** Un handler ne s'exécute qu'à la fin du playbook, pas immédiatement. Ne pas compter dessus pour des actions séquentielles.
5. **Vault en clair dans le repo :** Commiter un fichier vault non chiffré expose les secrets. Toujours `ansible-vault encrypt` avant commit.
6. **Serial ignoré :** `serial: 1` pour les déploiements zéro-downtime. Sans ça, Ansible peut redémarrer 100 serveurs simultanément.

---

## 8. Checklist Production

- [ ] Structure de rôles complète (tasks, handlers, defaults, vars, templates)
- [ ] `ansible-lint` passe sur tous les playbooks
- [ ] Idempotence vérifiée : exécuter deux fois de suite sans changements
- [ ] Tags sur chaque rôle pour exécution sélective
- [ ] Vault utilisé pour tous les secrets (jamais en clair)
- [ ] Fichier `.ansible-lint` configuré avec les règles du projet
- [ ] `serial` paramétré pour les déploiements rolling
- [ ] Tests avec `--check --diff` avant chaque `ansible-playbook`
- [ ] Inventaire dynamique pour les environnements cloud
- [ ] Handler `restart service` uniquement quand la config change vraiment