---
name: pki-x509
description: Guide complet de l'Infrastructure à Clé Publique (PKI) — X.509, Autorités de Certification, OCSP, CRL, Certificate Transparency, ACME, mTLS, Web PKI, et déploiement.
category: cybersecurite
tags: [pki, x509, ca, certificate, ocsp, crl, certificate-transparency, acme, mtls, cryptography]
---

# PKI (Public Key Infrastructure) — Guide Approfondi

## Sommaire
1. [Concepts Fondamentaux](#concepts-fondamentaux)
2. [Structure des Certificats X.509](#structure-des-certificats-x509)
3. [Hiérarchie des CA](#hiérarchie-des-ca)
4. [Validation de Chaîne de Certificats](#validation-de-chaîne-de-certificats)
5. [OCSP et CRL](#ocsp-et-crl)
6. [Certificate Transparency (CT)](#certificate-transparency-ct)
7. [ACME — Let's Encrypt](#acme-lets-encrypt)
8. [mTLS et Certificats Clients](#mtls-et-certificats-clients)
9. [Web PKI](#web-pki)
10. [Déploiement et Gestion](#déploiement-et-gestion)

---

## 1. Concepts Fondamentaux

### 1.1 Qu'est-ce qu'une PKI ?

**PKI** (Public Key Infrastructure) : ensemble de politiques, procédures, et technologies pour créer, gérer, distribuer, et révoquer des certificats numériques.

**Trust Model** : hiérarchie de confiance enracinée dans des **Root CA** (Autorités de Certification Racines) dont les clés sont protégées hors-ligne.

### 1.2 Composants d'une PKI

| Composant | Rôle |
|-----------|------|
| **Root CA** | Émet les certificats des CA intermédiaires. Clé stockée hors-ligne. |
| **Intermediate CA** | Émet les certificats finaux (leaf). Rotation régulière possible. |
| **End-Entity (Leaf)** | Certificat utilisateur/final (serveur, client, signature de code). |
| **CRL Issuer** | Publie les listes de révocation. |
| **OCSP Responder** | Répond aux requêtes de statut en temps réel. |
| **RA (Registration Authority)** | Vérifie l'identité du demandeur. |
| **HSM (Hardware Security Module)** | Protège physiquement les clés privées. |

---

## 2. Structure des Certificats X.509

### 2.1 Format ASN.1 (Abstract Syntax Notation One)

Un certificat X.509 v3 (RFC 5280) :

```asn1
Certificate ::= SEQUENCE {
    tbsCertificate       TBSCertificate,
    signatureAlgorithm   AlgorithmIdentifier,
    signatureValue       BIT STRING
}

TBSCertificate ::= SEQUENCE {
    version         [0]  EXPLICIT INTEGER DEFAULT v1,
    serialNumber         INTEGER,
    signature            AlgorithmIdentifier,
    issuer               Name,
    validity             Validity,
    subject              Name,
    subjectPublicKeyInfo SubjectPublicKeyInfo,
    issuerUniqueID  [1]  IMPLICIT BIT STRING OPTIONAL,
    subjectUniqueID [2]  IMPLICIT BIT STRING OPTIONAL,
    extensions      [3]  EXPLICIT Extensions OPTIONAL
}
```

### 2.2 Décodage d'un certificat

```bash
# Afficher TOUS les champs
openssl x509 -in cert.pem -text -noout

# Format court
openssl x509 -in cert.pem -subject -issuer -dates -noout

# Afficher les extensions
openssl x509 -in cert.pem -ext basicConstraints,keyUsage,extendedKeyUsage -noout

# Afficher l'empreinte
openssl x509 -in cert.pem -fingerprint -sha256 -noout

# Afficher la clé publique
openssl x509 -in cert.pem -pubkey -noout

# Afficher en format DER
openssl x509 -in cert.pem -inform PEM -outform DER -out cert.der
```

### 2.3 Champs Critiques

**Serial Number** : identifiant unique (max 20 octets). Doit être imprévisible.

**Validity** :
```bash
openssl x509 -in cert.pem -noout -dates
# notBefore=Apr  1 00:00:00 2024 GMT
# notAfter=Apr  1 00:00:00 2025 GMT
```

**Subject** : Distinguished Name (DN)
```
CN = example.com
O = Example Corp
OU = IT
L = Paris
ST = Île-de-France
C = FR
```

### 2.4 Extensions X.509 v3

| Extension | OID | Critique | Description |
|-----------|-----|----------|-------------|
| Basic Constraints | 2.5.29.19 | ✓ | CA:TRUE/FALSE, pathLenConstraint |
| Key Usage | 2.5.29.15 | ✓ | digitalSignature, keyEncipherment, keyCertSign, cRLSign |
| Extended Key Usage | 2.5.29.37 | ✗ | serverAuth, clientAuth, codeSigning, emailProtection |
| Subject Alternative Name | 2.5.29.17 | ✗ | DNS, IP, email, URI |
| Authority Key Identifier | 2.5.29.35 | ✗ | Hash de la clé publique de l'émetteur |
| Subject Key Identifier | 2.5.29.14 | ✗ | Hash de la clé publique du sujet |
| CRL Distribution Points | 2.5.29.31 | ✗ | URLs des CRL |
| Authority Information Access | 2.5.29.32 | ✗ | OCSP Responder, CA Issuers |
| Certificate Policies | 2.5.29.32 | ✗ | OID des politiques de certification |
| Name Constraints | 2.5.29.30 | ✓ | Limite les noms de domaine autorisés |
| Policy Constraints | 2.5.29.36 | ✗ | Contraintes de politiques |
| Inhibit anyPolicy | 2.5.29.54 | ✓ | Bloque la propagation de anyPolicy |
| Subject Information Access | 2.5.29.33 | ✗ | Signed Object Timestamp |

**Exemple de création de certificat avec extensions :**

```bash
# Fichier de configuration OpenSSL
cat > cert_config.cnf << 'EOF'
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_ext
prompt = no

[req_distinguished_name]
C = FR
ST = Paris
L = Paris
O = Example Corp
CN = server.example.com

[v3_ext]
basicConstraints = critical, CA:FALSE
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = server.example.com
DNS.2 = *.example.com
EOF

openssl req -new -x509 -days 365 \
  -config cert_config.cnf \
  -key server.key -out server.crt
```

### 2.5 Certificate Revocation Lists (CRL)

```asn1
CertificateList ::= SEQUENCE {
    tbsCertList          TBSCertList,
    signatureAlgorithm   AlgorithmIdentifier,
    signatureValue       BIT STRING
}

TBSCertList ::= SEQUENCE {
    version                 INTEGER OPTIONAL,
    signature               AlgorithmIdentifier,
    issuer                  Name,
    thisUpdate              Time,
    nextUpdate              Time,
    revokedCertificates     SEQUENCE OF SEQUENCE {
        userCertificate         INTEGER,  -- serial number
        revocationDate          Time,
        crlEntryExtensions      Extensions OPTIONAL
    } OPTIONAL,
    extensions              [0] EXPLICIT Extensions OPTIONAL
}
```

**Analyse :**
```bash
# Télécharger et afficher une CRL
wget -q -O - http://crl.example.com/ca.crl | openssl crl -inform DER -text -noout

# Vérifier le statut d'un certificat par rapport à une CRL
openssl verify -crl_check -CRLfile ca.crl -CAfile ca.crt cert.pem
```

---

## 3. Hiérarchie des CA

### 3.1 Architecture typique

```
┌─────────────────────┐
│     Root CA         │  ← Offline, HSM, 10-20 ans de validité
│   (self-signed)     │
└──────────┬──────────┘
           │
┌──────────┴──────────┐
│  Intermediate CA 1  │  ← Online, rotation tous les 3-5 ans
└──────────┬──────────┘
           │
┌──────────┴──────────┐
│  Intermediate CA 2  │  ← Délégation par région/usage
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │  Leaf Certs  │  ← 90 jours (Let's Encrypt) à 2 ans
    └─────────────┘
```

### 3.2 Création d'une PKI complète

```bash
#!/bin/bash
# ===== Root CA =====
# Générer la clé Root (hors-ligne, HSM)
openssl genrsa -aes256 -out root-ca.key 4096

# Créer le certificat Root (self-signed, 10 ans)
openssl req -x509 -new -key root-ca.key -sha256 -days 3650 \
  -out root-ca.crt \
  -subj "/C=FR/O=My Root CA/CN=My Root CA"

# ===== Intermediate CA =====
# Générer la clé intermediate
openssl genrsa -out intermediate-ca.key 4096

# CSR
openssl req -new -key intermediate-ca.key -sha256 \
  -out intermediate-ca.csr \
  -subj "/C=FR/O=My Intermediate CA/CN=My Intermediate CA"

# Signer par la Root
openssl x509 -req -in intermediate-ca.csr -CA root-ca.crt -CAkey root-ca.key \
  -CAcreateserial -out intermediate-ca.crt -days 1825 -sha256 \
  -extfile <(echo "basicConstraints=critical,CA:TRUE,pathlen:0
keyUsage=critical,keyCertSign,cRLSign
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always,issuer:always")

# ===== Server Certificate =====
# CSR
openssl req -new -newkey rsa:2048 -nodes -keyout server.key \
  -out server.csr \
  -subj "/C=FR/O=Example/CN=server.example.com"

# Signer par l'Intermediate
openssl x509 -req -in server.csr -CA intermediate-ca.crt -CAkey intermediate-ca.key \
  -CAcreateserial -out server.crt -days 365 -sha256 \
  -extfile <(echo "basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:server.example.com,DNS:*.example.com")

# ===== Chaîne =====
cat server.crt intermediate-ca.crt root-ca.crt > fullchain.pem
```

### 3.3 Cross-Signing

Permet à un certificat d'être valide sous plusieurs racines :

```bash
# Cross-sign un certificat par une autre CA
openssl x509 -req -in cert.csr -CA other-root.crt -CAkey other-root.key \
  -CAcreateserial -out cross-signed.crt -days 365
```

---

## 4. Validation de Chaîne de Certificats

### 4.1 Algorithme de validation

```python
def validate_cert_chain(cert, trusted_roots, intermediates,
                        time=None, crl_set=None, ocsp_responders=None):
    """
    Valide une chaîne de certificats selon RFC 5280.
    Retourne (valid, error_chain).
    """
    if time is None:
        time = datetime.utcnow()
    
    # Construire la chaîne
    chain = [cert]
    current = cert
    
    while not is_trust_anchor(current, trusted_roots):
        issuer = find_issuer(current, intermediates + trusted_roots)
        if issuer is None:
            return False, "Cannot find issuer"
        chain.append(issuer)
        current = issuer
    
    # Valider chaque certificat
    for i, c in enumerate(chain):
        # 1. Période de validité
        if not (c.not_before <= time <= c.not_after):
            return False, f"Cert {i} expired"
        
        # 2. Signature
        if not verify_signature(c, chain[i+1] if i+1 < len(chain) else c):
            return False, f"Cert {i} invalid signature"
        
        # 3. Basic Constraints
        if i < len(chain) - 1:  # Tous sauf leaf
            if not c.is_ca:
                return False, f"Cert {i} not marked as CA"
            if c.path_len is not None and c.path_len < (len(chain) - i - 2):
                return False, f"Cert {i} path length exceeded"
        
        # 4. Name Constraints (si présent)
        # 5. Key Usage
        # 6. Extended Key Usage (pour le leaf)
        
        # 7. Révocation
        if not check_revocation(c, crl_set, ocsp_responders):
            return False, f"Cert {i} revoked"
    
    return True, "Valid"
```

### 4.2 Vérification pratique

```bash
# Vérification basique
openssl verify -CAfile root-ca.crt -untrusted intermediate-ca.crt server.crt

# Vérification avec CRL
openssl verify -crl_check -CAfile root-ca.crt -CRLfile ca.crl server.crt

# Vérification complète
openssl verify -CAfile root-ca.crt -untrusted intermediate-ca.crt \
  -policy_check -x509_strict -show_chain server.crt

# Afficher la chaîne
openssl s_client -connect example.com:443 -showcerts
```

---

## 5. OCSP et CRL

### 5.1 OCSP (Online Certificate Status Protocol)

RFC 6960. Requête/réponse sur le statut d'un certificat :

```bash
# Trouver l'URL OCSP depuis le certificat
openssl x509 -in cert.pem -noout -ocsp_uri

# Requête OCSP (via OpenSSL)
openssl ocsp -issuer ca.pem -cert cert.pem -url http://ocsp.example.com -text

# Avec nonce (anti-replay)
openssl ocsp -issuer ca.pem -cert cert.pem -url http://ocsp.example.com -nonce

# Vérifier la réponse OCSP
openssl ocsp -issuer ca.pem -cert cert.pem \
  -url http://ocsp.example.com \
  -CAfile root-ca.crt \
  -verify_other intermediate-ca.crt \
  -VAfile ocsp-responder.crt
```

### 5.2 OCSP Stapling

Le serveur inclut une réponse OCSP signée dans le handshake TLS, évitant au client de contacter l'OCSP responder :

```bash
# NGINX : OCSP stapling
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/ssl/certs/chain.pem;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# Vérification
openssl s_client -connect example.com:443 -status
# OCSP Response Status: successful
```

### 5.3 CRL (Certificate Revocation List)

Raison de révocation (CRLReason) :
- **unspecified** (0)
- **keyCompromise** (1) — clé privée compromise
- **cACompromise** (2) — CA compromise
- **affiliationChanged** (3) — changement d'emploi
- **superseded** (4) — nouveau certificat émis
- **cessationOfOperation** (5) — plus nécessaire
- **certificateHold** (6) — suspension temporaire
- **removeFromCRL** (8) — pour les delta CRL

```bash
# Générer une CRL
openssl ca -gencrl -out ca.crl -config openssl.cnf

# Révoguer un certificat
openssl ca -revoke cert.pem -reason keyCompromise -config openssl.cnf

# Régénérer la CRL après révocation
openssl ca -gencrl -out ca.crl -config openssl.cnf
```

---

## 6. Certificate Transparency (CT)

### 6.1 Principe

RFC 6962. Tous les certificats émis par une CA publique doivent être enregistrés dans des logs publics (tamper-evident, append-only).

**Merkle Tree** : chaque certificat est une feuille d'un arbre de Merkle, dont la racine est publiée périodiquement.

### 6.2 Composants CT

- **Log** : serveur append-only qui accepte et enregistre les certificats
- **Monitor** : observe les logs et alerte sur les certificats suspects
- **Auditor** : vérifie la consistance des logs
- **SCT (Signed Certificate Timestamp)** : preuve qu'un certificat a été soumis à un log

### 6.3 Types de SCT

```bash
# 1. X.509 v3 extension (embedded SCT) : le CA inclut le SCT dans le certificat
openssl x509 -in cert.pem -text -noout | grep -A2 "Signed Certificate Timestamp"

# 2. TLS extension (OCSP stapling) : le serveur envoie les SCTs pendant le handshake
openssl s_client -connect example.com:443 -status | grep -A5 "signed_certificate_timestamp"

# 3. TLS extension séparée : le serveur envoie les SCTs dans une extension TLS
openssl s_client -connect example.com:443 -tlsextdebug | grep -A5 "signed_certificate_timestamp"
```

### 6.4 Vérification CT

```bash
# Avec un outil CT
pip install certifi ctools

# Vérifier qu'un certificat a des SCTs valides
python -c "
from ct.cert_analysis import check_certificate
from cryptography import x509

with open('cert.pem', 'rb') as f:
    cert = x509.load_pem_x509_certificate(f.read())

# Vérifier les SCTs
scts = cert.extensions.get_extension_for_oid(
    x509.oid.ExtensionOID.PRECERTIFICATE_SIGNED_CERTIFICATE_TIMESTAMPS
)
print(f'SCTs: {len(scts.value)}')
"
```

---

## 7. ACME — Let's Encrypt

### 7.1 Protocole ACME (RFC 8555)

Automatic Certificate Management Environment — permet l'automatisation complète de l'émission et du renouvellement de certificats.

### 7.2 Défis (Challenges)

**HTTP-01** : prouver le contrôle d'un domaine :
```bash
# Le serveur doit répondre sur http://domain/.well-known/acme-challenge/<token>
# avec une valeur spécifique que le CA vérifie

# Certbot
certbot certonly --standalone -d example.com -d www.example.com
```

**DNS-01** : prouver le contrôle du DNS :
```bash
# Créer un enregistrement TXT _acme-challenge.example.com
certbot certonly --manual --preferred-challenges dns -d example.com

# Avec API DNS (Cloudflare, OVH, Gandi)
certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.cloudflare/credentials.ini \
  -d example.com
```

**TLS-ALPN-01** : vérification via le port 443 (pas de port 80) — utilisé par les reverse proxies :
```bash
certbot certonly --standalone --preferred-challenges tls-alpn-01 -d example.com
```

### 7.3 Workflow ACME

```python
import requests
import hashlib
import base64
import json
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def acme_register(account_key, directory_url="https://acme-v02.api.letsencrypt.org/directory"):
    """Enregistrement ACME basique"""
    # 1. Obtenir le directory
    dir = requests.get(directory_url).json()
    
    # 2. Créer un compte
    # ... (JWS signing, etc.)
    return kid, account

def acme_issue_certificate(domain, account_key, contact_email):
    """Émet un certificat via ACME"""
    # 1. Enregistrer le compte
    # 2. Créer un ordre
    # 3. Relever le défi (HTTP-01)
    # 4. Finaliser
    # 5. Télécharger le certificat
    pass
```

### 7.4 Renouvellement automatique

```bash
# Certbot
certbot renew --quiet --deploy-hook "systemctl reload nginx"

# acme.sh (bash)
acme.sh --issue -d example.com --dns dns_cf
acme.sh --renew -d example.com --force

# Lego (Go)
lego --domains example.com --email admin@example.com --http renew

# Préparer la vérification
certbot renew --dry-run
```

---

## 8. mTLS et Certificats Clients

### 8.1 Mutual TLS

Le client présente aussi un certificat, authentifié par le serveur.

```nginx
# NGINX
ssl_client_certificate /etc/ssl/certs/client-ca.crt;
ssl_verify_client on;
ssl_verify_depth 2;

# Transmettre l'information au backend
proxy_set_header X-Client-Cert $ssl_client_escaped_cert;
proxy_set_header X-Client-DN $ssl_client_s_dn;
proxy_set_header X-Client-Verify $ssl_client_verify;
```

### 8.2 Génération de certificats clients

```bash
# 1. CA pour les clients
openssl genrsa -out client-ca.key 4096
openssl req -x509 -new -key client-ca.key -days 3650 -out client-ca.crt \
  -subj "/C=FR/O=Client CA/CN=Client CA"

# 2. Certificat client
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr \
  -subj "/C=FR/O=Example/CN=client1.example.com"
openssl x509 -req -in client.csr -CA client-ca.crt -CAkey client-ca.key \
  -CAcreateserial -out client.crt -days 365 \
  -extfile <(echo "extendedKeyUsage=clientAuth")

# 3. Package PKCS#12 (pour navigateurs)
openssl pkcs12 -export -in client.crt -inkey client.key \
  -out client.p12 -passout pass:password
```

### 8.3 Vérification

```bash
# Vérifier que le serveur demande un certificat client
openssl s_client -connect example.com:443 -verify_return_error \
  -cert client.crt -key client.key

# Vérifier la chaîne client
openssl verify -CAfile client-ca.crt client.crt
```

---

## 9. Web PKI

### 9.1 Trust Stores

Chaque OS/browser maintient sa liste de CA racines :

```bash
# Debian/Ubuntu
ls /usr/share/ca-certificates/mozilla/
update-ca-certificates  # Mise à jour
cat /etc/ssl/certs/ca-certificates.crt  # Bundle complet

# Red Hat
ls /etc/pki/tls/certs/
update-ca-trust extract

# macOS
security find-certificate -a -p /Library/Keychains/System.keychain

# Firefox (indépendant)
ls ~/.mozilla/firefox/*.default/cert9.db
```

### 9.2 Mozilla CA Program

Les CA racines sont incluses dans les navigateurs après audit :
- **WebTrust** : audit annuel des pratiques de la CA
- **Baseline Requirements** (CA/Browser Forum) : règles minimales d'émission

### 9.3 Durée de vie des certificats

| Période | Durée max | Raison |
|---------|-----------|--------|
| Pré-2018 | 5 ans | — |
| Mars 2018 | 825 jours | Apple réduction |
| Sept 2020 | 398 jours | CA/Browser Forum |
| 2024+ | 90 jours (proposé) | Apple/Google |

---

## 10. Déploiement et Gestion

### 10.1 HSM (Hardware Security Module)

```bash
# Utiliser un HSM PKCS#11 avec OpenSSL
openssl engine -t pkcs11
openssl pkeyutl -sign -engine pkcs11 -keyform engine \
  -inkey "pkcs11:token=MyToken;object=mykey" \
  -in message.txt -out signature.bin
```

### 10.2 Rotation des clés

```bash
# Rotation d'une CA intermédiaire
# 1. Créer la nouvelle clé intermédiaire
openssl genrsa -out new-intermediate.key 4096

# 2. Nouveau CSR
openssl req -new -key new-intermediate.key -out new-intermediate.csr \
  -subj "/C=FR/O=Intermediate CA/CN=Intermediate CA 2024"

# 3. Cross-signer par l'ancienne CA intermédiaire
openssl x509 -req -in new-intermediate.csr \
  -CA old-intermediate.crt -CAkey old-intermediate.key \
  -CAcreateserial -out new-cross.crt -days 365

# 4. Signer par la Root CA
openssl x509 -req -in new-intermediate.csr \
  -CA root-ca.crt -CAkey root-ca.key \
  -CAcreateserial -out new-intermediate.crt -days 1825
```

### 10.3 Monitoring

```bash
#!/bin/bash
# Vérification auto des certificats

for domain in example.com; do
    expiry=$(openssl s_client -connect "$domain:443" -servername "$domain" \
        </dev/null 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
    expiry_epoch=$(date -d "$expiry" +%s)
    now_epoch=$(date +%s)
    days_left=$(( (expiry_epoch - now_epoch) / 86400 ))
    
    if [ $days_left -lt 30 ]; then
        echo "ALERT: $domain expires in $days_left days"
    fi
done
```

### 10.4 OuvrirSSL pour la gestion de CA

```bash
# Créer la structure de la CA
mkdir -p ca/{certs,crl,newcerts,private,csr}
chmod 700 ca/private
touch ca/index.txt
echo 1000 > ca/serial

# Configuration CA
cat > ca/openssl.cnf << 'EOF'
[ ca ]
default_ca = CA_default

[ CA_default ]
database = index.txt
serial = serial
new_certs_dir = newcerts
certificate = ca.crt
private_key = private/ca.key
default_md = sha256
default_days = 365
policy = policy_match
x509_extensions = v3_intermediate

[ policy_match ]
countryName = match
stateOrProvinceName = supplied
organizationName = match
organizationalUnitName = optional
commonName = supplied
EOF
```

---

## Références

- **RFC 5280 (X.509 PKIX)** : https://datatracker.ietf.org/doc/html/rfc5280
- **RFC 6960 (OCSP)** : https://datatracker.ietf.org/doc/html/rfc6960
- **RFC 6962 (Certificate Transparency)** : https://datatracker.ietf.org/doc/html/rfc6962
- **RFC 8555 (ACME)** : https://datatracker.ietf.org/doc/html/rfc8555
- **CA/Browser Forum Baseline Requirements** : https://cabforum.org/baseline-requirements-documents/
- **Let's Encrypt** : https://letsencrypt.org
- **Mozilla CA Program** : https://wiki.mozilla.org/CA
- **Certbot** : https://certbot.eff.org
- **acme.sh** : https://github.com/acmesh-official/acme.sh
- **OpenSSL PKI Tutorial** : https://pki-tutorial.readthedocs.io