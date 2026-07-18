---
name: opc-ua-scanner
description: "Explorer un serveur OPC UA et valider les tags EPH/EM."
version: 1.2.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [industrial, opc-ua, opcua, scanner, tags, automation, security-policies, unified-architecture]
    related_skills: [plc-connectivity, industrial-audit]
---

# Exploration Dynamique OPC UA (opc-ua-scanner)

## Vue d'ensemble

Le protocole **OPC UA (Open Platform Communications Unified Architecture)** est la norme industrielle de référence pour l'échange de données indépendant des constructeurs. Il structure ses informations sous forme d'un graphe d'objets, de variables et de méthodes appelé **Espace d'Adressage**.

Cette compétence fournit à l'agent EVA les connaissances et outils nécessaires pour :
1. Se connecter à un serveur OPC UA de manière sécurisée (chiffrement et authentification).
2. Explorer récursivement (Browsing) l'espace d'adressage de manière performante.
3. Lire, écrire ou s'abonner (Subscription) aux variables de données (Tags) d'équipements (EM) et de phases (EPH).
4. Appeler des méthodes d'automatisation exposées sur le serveur.
5. Générer et gérer les certificats de sécurité clients requis.

Le script d'assistance associé à cette compétence est disponible sous [opc_ua_scanner.py](scripts/opc_ua_scanner.py).

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Se connecter à un automate (PLC), un serveur de communication (Kepware, CODESYS, UaGateway) ou un SCADA exposant un serveur OPC UA.
- Parcourir l'arborescence des tags pour auditer leur structure ou valider la conformité par rapport à un standard.
- Lire ou écrire en direct des valeurs de procédé (consignes, mesures).
- S'abonner aux événements d'un capteur pour un suivi asynchrone performant.
- Diagnostiquer des rejets de certificats SSL ou des erreurs de politique de sécurité.

---

## 1. Structure de l'Espace d'Adressage OPC UA

Chaque information de l'espace d'adressage est matérialisée par un **Nœud (Node)**. Un nœud possède plusieurs attributs :

- **NodeID :** L'identifiant unique du nœud. Il contient un index d'espace de nom (`ns`) et un identifiant qui peut être numérique (`i`), textuel/chaîne (`s`), un GUID (`g`) ou opaque/binaire (`b`).
  - *Exemple :* `ns=2;s=Line1.Boiler.Temperature` (Espace de nom 2, identifiant string).
- **NodeClass :** La classe du nœud, qui définit sa fonction :
  - `Object` : Conteneur logique ou physique (ex: Vanne, Ligne).
  - `Variable` : Tag contenant une valeur typée (BOOL, REAL, INT...) ainsi que son état de qualité (StatusCode) et son horodatage (SourceTimestamp).
  - `Method` : Fonction exécutable à distance sur l'automate.
- **BrowseName & DisplayName :** Le nom symbolique interne du nœud et son libellé lisible (DisplayName peut être traduit).

---

## 2. Recette Python `asyncua` : Client Sécurisé, Abonnement et Méthode

Voici un script Python de production basé sur la bibliothèque `asyncua` illustrant l'authentification sécurisée, la génération de certificat client, la lecture asynchrone par abonnement et l'appel de méthode.

### Génération de Certificat Client via `cryptography`
Pour les politiques de sécurité (ex: `Basic256Sha256`), le client doit présenter son certificat X.509 (.der) et sa clé privée (.pem).

```python
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_self_signed_cert(cert_path="client_cert.der", key_path="client_key.pem"):
    """Génère un certificat auto-signé X.509 requis pour la connexion sécurisée OPC UA."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"EVA_OPCUA_Client"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"EVA"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([x509.UniformResourceIdentifier(u"urn:EVA:client")]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Sauvegarde de la clé privée PEM
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
        
    # Sauvegarde du certificat DER
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.DER))
        
    print(f"Certificat et clé générés : {cert_path}, {key_path}")
```

### Script Client OPC UA Complet :

```python
import asyncio
from asyncua import Client, ua

# Définition du gestionnaire d'événements pour l'abonnement (Subscription)
class SubscriptionHandler:
    def datachange_notification(self, node, val, data):
        """Déclenché de manière asynchrone lors du changement de valeur d'un tag abonnés."""
        print(f"[Abonnement] Valeur modifiée sur le nœud {node} : {val}")

async def main():
    server_url = "opc.tcp://192.168.1.100:4840"
    
    # 1. Configuration du client
    client = Client(url=server_url)
    
    # Configurer l'authentification (si nécessaire)
    client.set_user("operateur_EVA")
    client.set_password("SecuredPassword99!")
    
    # Configurer la sécurité cryptographique
    # En production, charger le certificat client généré
    try:
        await client.set_security(
            policy=ua.SecurityPolicyType.Basic256Sha256,
            certificate_ids="client_cert.der",
            private_key_ids="client_key.pem",
            server_certificate_ids=None # Téléchargé automatiquement lors de la négociation
        )
    except FileNotFoundError:
        print("Certificats de sécurité absents. Connexion sans chiffrement (None)...")
        # Pas d'appel set_security pour utiliser None/None

    try:
        # 2. Établissement de la session
        await client.connect()
        print("Connecté au serveur OPC UA.")
        
        # 3. Lecture asynchrone directe d'une variable
        temp_node_id = "ns=2;s=Line1.Boiler.Temperature"
        temp_node = client.get_node(temp_node_id)
        val = await temp_node.read_value()
        print(f"Valeur actuelle de la température : {val} °C")
        
        # 4. Abonnement asynchrone (Subscription)
        handler = SubscriptionHandler()
        sub = await client.create_subscription(500, handler)  # 500 ms d'intervalle d'échantillonnage
        await sub.subscribe_data_change(temp_node)
        print(f"Abonnement actif sur {temp_node_id} (attente de changements...)")
        
        # 5. Appel d'une méthode OPC UA sur l'automate (ex: reset défaut machine)
        object_parent = client.get_node("ns=2;s=Line1.Boiler")
        method_to_call = client.get_node("ns=2;s=Line1.Boiler.ResetFault")
        
        # Appel avec les arguments requis (ex: ID opérateur)
        result = await object_parent.call_method(method_to_call, ua.Variant(42, ua.VariantType.Int32))
        print(f"Résultat de l'appel de méthode : {result}")
        
        # Attendre pour voir les notifications d'abonnement
        await asyncio.sleep(5)
        
        # Nettoyage
        await sub.unsubscribe_all()
        
    except Exception as e:
        print(f"Erreur de communication : {e}")
    finally:
        await client.disconnect()
        print("Déconnecté du serveur.")

if __name__ == "__main__":
    # Activer la boucle d'événements
    asyncio.run(main())
```

---

## Pièges Courants (Common Pitfalls)

1. **Parcours récursif sans limite depuis la racine (CPU Lockup) :**
   * *Erreur :* Lancer un browse récursif complet depuis le nœud racine `ns=0;i=84` (RootNode) sur un automate de production. Cela peut surcharger la mémoire du serveur OPC UA de l'automate et provoquer son arrêt ou une perte de communication avec la supervision.
   * *Correction :* Toujours démarrer le parcours depuis le nœud `Objects` (`ns=0;i=85`) ou un sous-dossier spécifique de l'application (`ns=2;s=Application`), et brider strictement la profondeur maximale (`depth <= 3`).

2. **Rejet du Certificat Client (Rejected Certificates) :**
   * *Erreur :* Le client ne parvient pas à se connecter avec la politique de sécurité configurée, l'automate renvoyant une erreur d'accès refusé ou de certificat non valide.
   * *Correction :* Sur l'automate ou le serveur de communication (ex: Kepware), il faut ouvrir le magasin de certificats et déplacer manuellement le certificat du client EVA depuis le dossier "Rejected" vers le dossier "Trusted". S'assurer également que l'horloge système du PC client est synchronisée avec l'automate (décalage horaire max souvent fixé à 10 minutes).

3. **Multiplication excessive des abonnements :**
   * *Erreur :* Créer un abonnement séparé (Subscription) pour chacune des 5000 variables d'une ligne de production. Cela génère des milliers de requêtes de surveillance internes et ralentit l'automate.
   * *Correction :* Regrouper les variables dans un nombre restreint de Subscriptions (ex: une seule pour toutes les variables d'une même machine avec un groupe de notifications).

---

## Liste de vérification (Checklist)

- [ ] La description frontmatter YAML fait moins de 60 caractères et se termine par un point.
- [ ] Le port TCP `4840` (ou port spécifique du serveur) est ouvert dans la configuration réseau.
- [ ] La profondeur de parcours récursif est limitée par un paramètre de garde (`depth` <= 3) pour ne pas saturer l'automate.
- [ ] Les NodeIDs complets (`ns=...;...`) sont collectés pour les accès directs en lecture/écriture à la place des noms textuels instables.
- [ ] Les certificats de sécurité du client sont générés au format DER (certificat) et PEM (clé privée) avec des URI d'application valides.
- [ ] Le certificat du client EVA a été explicitement déplacé dans les certificats de confiance (Trusted) du serveur cible.
- [ ] Les variables fréquemment actualisées font l'objet d'abonnements (Subscriptions) collectifs plutôt que de lectures périodiques répétées.

