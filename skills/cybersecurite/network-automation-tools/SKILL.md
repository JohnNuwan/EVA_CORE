---
name: network-automation-tools
description: Guide complet de l'automatisation réseau — Ansible, Nornir, Terraform, Netmiko, NAPALM, génération de configuration, tests de réseau, CI/CD, et templates Jinja2.
tags: [ansible, nornir, terraform, netmiko, napalm, jinja2, network-automation, cicd, configuration-management]
---

# Automatisation Réseau — Ansible, Nornir, Terraform

## Présentation

Stack complète d'automatisation pour l'infrastructure réseau : gestion de configuration, déploiement, tests, validation et CI/CD réseau. Couvre les frameworks principaux (Ansible, Nornir, Terraform, Netmiko, NAPALM) avec des exemples multi-constructeurs (Cisco, Juniper, Arista, FRR).

### Stack d'Automatisation

```text
+==========================================+
|   CI/CD Pipeline (GitLab CI, Jenkins)     |
|   → lint → test → deploy → validate       |
+==========================================+
                    |
        +-----------+-----------+
        |                       |
+=======+========+    +=========+========+
| Ansible / AWX  |    | Nornir (Python) |
| Agentless      |    | Multi-threaded  |
| Push-based     |    | Task-based      |
+================+    +=================+
        |                       |
+=======+========+    +=========+========+
| Netmiko        |    | NAPALM          |
| SSH CLI parser |    | API abstraction |
| Multi-vendor   |    | Config replace  |
+================+    +=================+
        |                       |
+=======+========+    +=========+========+
| Terraform      |    | Batfish         |
| Providers      |    | Network intent  |
| Infrastructure |    | Validation      |
| as Code        |    | & tests         |
+================+    +=================+
```

---

## Ansible — Automation Réseau

### Installation et Configuration

```bash
# Installation
pip install ansible ansible-pylibssh

# Exiger Python 3
pip install "ansible-core>=2.15" "ansible>=9.0"

# Collections réseau
ansible-galaxy collection install cisco.ios
ansible-galaxy collection install cisco.nxos
ansible-galaxy collection install junipernetworks.junos
ansible-galaxy collection install arista.eos
ansible-galaxy collection install frr.frr
```

### Inventaire Ansible

```yaml
# inventory/network.yml
all:
  children:
    routers:
      hosts:
        router01:
          ansible_host: 192.168.1.1
          ansible_network_os: cisco.ios.ios
          ansible_user: admin
          ansible_password: "{{ vault_ansible_password }}"
          ansible_connection: ansible.netcommon.network_cli
          ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
        router02:
          ansible_host: 192.168.1.2
          ansible_network_os: junipernetworks.junos.junos
    switches:
      hosts:
        switch01:
          ansible_host: 192.168.2.1
          ansible_network_os: cisco.nxos.nxos
  vars:
    ansible_become: yes
    ansible_become_method: enable
    ansible_become_password: "{{ vault_enable_password }}"
```

### Playbooks Réseau

```yaml
# playbooks/deploy_ospf.yml
---
- name: Déployer OSPF sur les routeurs
  hosts: routers
  gather_facts: false

  tasks:
    - name: Générer la configuration OSPF
      ansible.builtin.template:
        src: ospf.j2
        dest: /tmp/ospf.cfg.j2
      delegate_to: localhost
      run_once: true

    - name: Appliquer OSPF (Cisco IOS)
      cisco.ios.ios_config:
        src: ospf_ios.j2
      when: ansible_network_os == 'cisco.ios.ios'

    - name: Appliquer OSPF (Juniper)
      junipernetworks.junos.junos_config:
        src: ospf_junos.j2
        load: merge
      when: ansible_network_os == 'junipernetworks.junos.junos'

    - name: Vérifier OSPF (Cisco)
      cisco.ios.ios_command:
        commands:
          - show ip ospf neighbor
          - show ip route ospf
      register: ospf_check
      when: ansible_network_os == 'cisco.ios.ios'

    - name: Afficher les voisins OSPF
      ansible.builtin.debug:
        var: ospf_check.stdout_lines

    - name: Valider avec des asserts
      ansible.builtin.assert:
        that:
          - "'FULL' in ospf_check.stdout[0]"
          - "'10.0.0.0/8' in ospf_check.stdout[1]"
        fail_msg: "OSPF mal configuré !"
```

### Templates Jinja2 Réseau

```jinja
{# templates/ospf_ios.j2 #}
{% for interface, area in ospf_interfaces.items() %}
interface {{ interface }}
 ip ospf {{ ospf_process }} area {{ area }}
 ip ospf network point-to-point
 ip ospf hello-interval {{ ospf_hello | default(10) }}
 ip ospf dead-interval {{ ospf_dead | default(40) }}
{% endfor %}

router ospf {{ ospf_process }}
 router-id {{ router_id }}
{% for network, area in networks.items() %}
 network {{ network }} {{ network | wildcard_netmask }} area {{ area }}
{% endfor %}
{% if stub_areas %}
{% for area in stub_areas %}
 area {{ area }} stub
{% endfor %}
{% endif %}
 passive-interface default
 no passive-interface {{ passive_interfaces | join(', ') }}
```

```yaml
# host_vars/router01.yml
ospf_process: 1
router_id: 10.0.0.1
ospf_interfaces:
  GigabitEthernet0/0: 0
  GigabitEthernet0/1: 1
ospf_hello: 10
ospf_dead: 40
networks:
  "10.0.0.0": 0
  "192.168.1.0": 1
stub_areas: [2]
passive_interfaces:
  - GigabitEthernet0/2
  - GigabitEthernet0/3
```

### Rôles Ansible

```yaml
# roles/bgp/tasks/main.yml
---
- name: Déployer la configuration BGP
  ansible.builtin.template:
    src: bgp.j2
    dest: /tmp/bgp_{{ inventory_hostname }}.cfg
  delegate_to: localhost

- name: Appliquer BGP (multi-vendor)
  ansible.builtin.include_tasks: "{{ ansible_network_os }}.yml"

# roles/bgp/tasks/cisco.ios.ios.yml
- name: Config BGP Cisco IOS
  cisco.ios.ios_config:
    lines: "{{ lookup('template', 'bgp_cisco.j2').split('\n') }}"
    save_when: modified
```

### AWX / Ansible Tower

```bash
# AWX (open source Tower) — Déploiement Docker
git clone https://github.com/ansible/awx.git
cd awx/tools/docker-compose
make docker-compose-build
make docker-compose-db
docker-compose up -d

# Accès : https://localhost:8043
# admin / password
```

---

## Nornir — Automation Python Multi-threadée

### Installation

```bash
pip install nornir nornir-napalm nornir-utils nornir-netmiko nornir-jinja2
```

### Configuration

```yaml
# nornir_config.yaml
---
inventory:
  plugin: SimpleInventory
  options:
    host_file: "inventory/hosts.yaml"
    group_file: "inventory/groups.yaml"
    defaults_file: "inventory/defaults.yaml"

runner:
  plugin: threaded
  options:
    num_workers: 20

logging:
  enabled: true
  level: INFO
```

```yaml
# inventory/hosts.yaml
---
router01:
  hostname: 192.168.1.1
  platform: ios
  username: admin
  password: "{{ vault_password }}"
  data:
    role: core
    bgp_as: 65001

router02:
  hostname: 192.168.1.2
  platform: junos
  username: admin
  password: "{{ vault_password }}"
  data:
    role: edge
    bgp_as: 65002

switch01:
  hostname: 192.168.2.1
  platform: nxos
  username: admin
  password: "{{ vault_password }}"
```

### Scripts Nornir

```python
# scripts/backup_config.py
from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
from nornir_utils.plugins.functions import print_result
from datetime import datetime

def backup_config(task):
    """Sauvegarde la configuration courante"""
    result = task.run(
        task=netmiko_send_command,
        command_string="show running-config",
        use_textfsm=False
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    host = task.host.name
    filename = f"backups/{host}_{timestamp}.cfg"
    with open(filename, "w") as f:
        f.write(result.result)
    return f"Sauvegardé dans {filename}"

def audit_interfaces(task):
    """Audite les interfaces down"""
    result = task.run(
        task=netmiko_send_command,
        command_string="show interfaces status | include disabled|down",
        use_textfsm=True
    )
    return result

nr = InitNornir(config_file="nornir_config.yaml")

# Filtrer et exécuter
core_routers = nr.filter(role="core")
results = core_routers.run(task=backup_config)
print_result(results)
```

### Nornir + NAPALM pour Configuration

```python
# scripts/deploy_config.py
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_configure
from nornir_utils.plugins.functions import print_result

def deploy_config(task):
    # Générer la config
    config = task.render(template="bgp_template.j2")
    # Appliquer via NAPALM (merge/replace)
    result = task.run(
        task=napalm_configure,
        configuration=config,
        replace=False,  # True pour remplacer toute la config
    )
    # Valider la configuration
    diff = task.run(
        task=napalm_configure,
        configuration=config,
        dry_run=True,
    )
    return result

nr = InitNornir(config_file="nornir_config.yaml")
results = nr.run(task=deploy_config)
print_result(results)
```

---

## Terraform — Infrastructure as Code Réseau

### Provider Cisco Catalyst Center / Meraki

```hcl
# main.tf
terraform {
  required_providers {
    meraki = {
      source = "cisco-open/meraki"
      version = "~> 2.0"
    }
    dnacenter = {
      source = "cisco-en-programmability/dnacenter"
      version = "~> 1.0"
    }
  }
}

provider "meraki" {
  api_key = var.meraki_api_key
}

provider "dnacenter" {
  base_url = var.dna_center_url
  username = var.dna_username
  password = var.dna_password
}

# Meraki — Gestion de réseaux
resource "meraki_network" "corp" {
  name          = "Réseau Corporate"
  organization_id = var.org_id
  product_types = ["switch", "wireless", "appliance"]
  timezone      = "Europe/Paris"
  tags          = ["production", "corporate"]
}

resource "meraki_network_vlan" "vlan_100" {
  network_id = meraki_network.corp.id
  id         = "100"
  name       = "INTRANET"
  subnet     = "10.0.100.0/24"
  appliance_ip = "10.0.100.1"
}

# Cisco Catalyst Center — Profil de switch
resource "dnacenter_site" "datacenter" {
  site {
    area {
      name = "Paris"
    }
    building {
      name   = "DC1"
      address = "123 Rue Tech"
    }
    floor {
      name       = "Floor1"
      height     = 10.0
      length     = 50.0
      width      = 40.0
    }
  }
}
```

### Terraform + NAPALM (via external provider)

```hcl
# Gestion de configuration via SSH
resource "external" "configure_router" {
  program = ["python3", "${path.module}/scripts/apply_napalm.py"]

  query = {
    hostname = "192.168.1.1"
    platform = "ios"
    username = "admin"
    config_file = "${path.module}/configs/router01.cfg"
  }
}
```

---

## Netmiko — Multi-Vendor SSH

```python
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetmikoTimeoutException, NetmikoAuthenticationException

devices = [
    {
        'device_type': 'cisco_ios',
        'host': '192.168.1.1',
        'username': 'admin',
        'password': 'secret',
        'port': 22,
        'secret': 'enable_secret',
        'session_log': 'logs/device.log',
    },
    {
        'device_type': 'juniper_junos',
        'host': '192.168.1.2',
        'username': 'admin',
        'password': 'secret',
    },
]

for device in devices:
    try:
        conn = ConnectHandler(**device)
        conn.enable()  # Mode privilégié
        output = conn.send_command('show running-config')
        version = conn.send_command('show version', use_textfsm=True)
        conn.send_config_set([
            'interface GigabitEthernet0/0',
            'description Uplink-Spine',
            'ip ospf cost 10',
            'no shutdown',
        ])
        conn.save_config()
        conn.disconnect()
    except NetmikoTimeoutException:
        print(f"Timeout: {device['host']}")
    except NetmikoAuthenticationException:
        print(f"Auth fail: {device['host']}")
```

---

## NAPALM — Network Abstraction Layer

```python
import napalm

# Connexion multi-vendor
driver = napalm.get_network_driver('ios')
device = driver(
    hostname='192.168.1.1',
    username='admin',
    password='secret',
    optional_args={'secret': 'enable_secret'}
)

device.open()

# Méthodes NAPALM unifiées
facts = device.get_facts()
interfaces = device.get_interfaces()
ip_addrs = device.get_interfaces_ip()
config = device.get_config(retrieve='running')
bgp_neighbors = device.get_bgp_neighbors()
arp_table = device.get_arp_table()
mac_table = device.get_mac_address_table()
ntp_stats = device.get_ntp_peers()
lldp_neighbors = device.get_lldp_neighbors()

# Diff et commit
device.load_merge_candidate(config='interface Gi0/1\n description Uplink')
diff = device.compare_config()
if diff:
    print(diff)
    device.commit_config()
device.close()
```

---

## CI/CD pour le Réseau (GitLab CI)

```yaml
# .gitlab-ci.yml
stages:
  - lint
  - validate
  - test
  - deploy
  - verify

variables:
  ANSIBLE_FORCE_COLOR: "true"
  ANSIBLE_HOST_KEY_CHECKING: "false"

# Lint des playbooks Ansible
ansible-lint:
  stage: lint
  script:
    - ansible-lint playbooks/*.yml
  only:
    - merge_requests

# Validation syntaxique Jinja2
jinja2-validate:
  stage: validate
  script:
    - pip install j2lint
    - j2lint templates/*.j2
  only:
    - merge_requests

# Test dans un lab virtuel
network-test:
  stage: test
  script:
    - ansible-playbook -i inventory/test.yml playbooks/deploy_ospf.yml --check
  only:
    - main

# Déploiement avec approbation manuelle
deploy-prod:
  stage: deploy
  script:
    - ansible-playbook -i inventory/prod.yml playbooks/deploy_ospf.yml
  environment:
    name: production
  when: manual
  allow_failure: false
  only:
    - tags

# Validation post-déploiement
post-deploy-verify:
  stage: verify
  script:
    - ansible-playbook -i inventory/prod.yml playbooks/verify_ospf.yml
  only:
    - tags
```

---

## Batfish — Validation de Configuration

```python
# Validation de configuration réseau
from pybatfish.client.session import Session

bf = Session(host='localhost', port=9999)
bf.set_network('corp')

# Upload configs
with open('configs/router01.cfg') as f:
    bf.upload_snapshot(
        snapshot='router01',
        config_text=f.read(),
        device_type='cisco_ios'
    )

# Vérifier les politiques
bf.q.nodeProperties().answer().frame()
bf.q.ospfSessionStatus().answer().frame()
bf.q.bgpSessionStatus().answer().frame()

# Vérifier les ACLs
bf.q.filterReachable(
    filter="acl_name",
    src="10.0.0.1",
    dst="10.0.1.1",
).answer().frame()

# Détection de redondance
bf.q.denyOverlap().answer().frame()
```

---

## Pièges et Bonnes Pratiques

- **Idempotence** : Toujours tester avec `--check` (Ansible) ou `dry_run=True` (Nornir)
- **Vault** : Ne jamais stocker les mots de passe en clair — utiliser ansible-vault ou HashiCorp Vault
- **Gestion des erreurs** : Toujours capturer les timeouts SSH et les échecs d'authentification
- **Rollback** : Avoir un playbook de rollback prêt avant chaque déploiement
- **Inventory dynamique** : Utiliser des inventaires dynamiques (Cisco DNA, NSO, AWX) pour les grands parcs
- **Parallelisme** : Ansible forks=20, Nornir num_workers=20 — ne pas saturer le CPU du contrôleur
- **Validation** : Toujours valider avec Batfish avant de déployer en production

## Ressources

- Ansible Network : https://docs.ansible.com/ansible/latest/network/
- Nornir : https://nornir.readthedocs.io/
- NAPALM : https://napalm.readthedocs.io/
- Netmiko : https://ktbyers.github.io/netmiko/
- Batfish : https://batfish.org/
- Terraform Network Providers : https://registry.terraform.io/namespaces/cisco-open