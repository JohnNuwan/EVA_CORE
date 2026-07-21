---
name: tls-1-3
description: Guide complet de TLS 1.3 — handshake, 0-RTT, key schedule, cipher suites, PSK, QUIC, résumé de session, implémentations OpenSSL/BoringSSL, et analyse de sécurité.
category: cybersecurite
tags: [tls, tls-1-3, handshake, quic, psk, https, ssl, network, cryptography]
---

# TLS 1.3 — Guide Approfondi

## Sommaire
1. [Architecture et Principes](#architecture-et-principes)
2. [Handshake Complet (1-RTT)](#handshake-complet-1-rtt)
3. [0-RTT — Early Data](#0-rtt-resumption)
4. [Key Schedule Détaillé](#key-schedule-détaillé)
5. [Cipher Suites et AEAD](#cipher-suites-et-aead)
6. [PSK — Pre-Shared Keys](#psk-pre-shared-keys)
7. [QUIC et TLS 1.3](#quic-et-tls-13)
8. [Analyse de Sécurité](#analyse-de-sécurité)
9. [Implémentations](#implémentations)

---

## 1. Architecture et Principes

### 1.1 Différences majeures avec TLS 1.2

| Propriété | TLS 1.2 | TLS 1.3 |
|-----------|---------|---------|
| Handshake | 2 RTT (full) | 1 RTT (full) |
| 0-RTT | ✗ | ✓ (avec risques) |
| Chiffrement du handshake | Non | Oui (dès ServerHello) |
| Modes non-éphemeral (RSA key transport) | ✓ | ✗ (interdit) |
| Cipher suites | ~37 combinaisons | 5 cipher suites |
| Algorithmes négociables | Algorithme + mode + hash | AEAD seul |
| Signature avant le handshake | ✗ | ✓ (certificat chiffré) |
| Renégociation | ✓ | ✗ (supprimée) |
| Compression | ✓ | ✗ (supprimée) |
| DHE/ECDHE | Optionnel | Obligatoire (PFS) |

### 1.2 Diagramme de Séquence (1-RTT)

```
ClientHello (KeyShare)          ──→
    ←── ServerHello (KeyShare) + EncryptedExtensions + Certificate + CertificateVerify + Finished
Client Finished                 ──→
    ←── [Application Data]
Application Data                ───→ (bidirectionnel)
```

---

## 2. Handshake Complet (1-RTT)

### 2.1 ClientHello

Premier message du client, envoyé en clair :

```
struct {
    ProtocolVersion legacy_version = 0x0303;  // TLS 1.2 (compatibilité)
    Random random;                             // 32 octets
    opaque legacy_session_id<0..32>;
    CipherSuite cipher_suites<2..2^16-2>;     // Liste des suites préférées
    opaque legacy_compression_methods<1..2^8-1>;
    Extension extensions<8..2^16-1>;          // Extensions critiques
} ClientHello;
```

**Extensions obligatoires en TLS 1.3 :**

| Extension | Code | Description |
|-----------|------|-------------|
| `supported_versions` | 43 | Annonce la version TLS 1.3 |
| `key_share` | 51 | Partage de clé (X25519, P-256, etc.) |
| `signature_algorithms` | 13 | Algorithmes de signature supportés |
| `supported_groups` | 10 | Courbes supportées |
| `psk_key_exchange_modes` | 45 | Modes PSK |
| `cookie` | 44 | Anti-DoS (réponse serveur) |
| `pre_shared_key` | 41 | Reprise de session |

Exemple de ClientHello décodé (Wireshark/TShark) :
```bash
tshark -r capture.pcap -Y "tls.handshake.type == 1" -V -o tls.keylog_file:keys.log
```

### 2.2 ServerHello

**TLS 1.3 ne peut être détecté qu'après le ServerHello** car le ClientHello annonce `legacy_version = 0x0303` (TLS 1.2) et la version réelle est dans `supported_versions`.

```
struct {
    ProtocolVersion version = 0x0304;  // TLS 1.3
    Random random;                      // 32 octets
    opaque legacy_session_id<0..32>;
    CipherSuite cipher_suite;
    Extension extensions<8..2^16-1>;
} ServerHello;
```

Le ServerHello est suivi de messages **chiffrés** (via la clé de handshake dérivée du partage de clé).

### 2.3 Dérivation de la Clé de Handshake

```python
import hashlib
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand
from cryptography.hazmat.primitives.hmac import HMAC

def derive_early_secret(psk, transcript_hash, hash_func):
    """Dérive le secret initial du handshake TLS 1.3"""
    zeros = b'\x00' * hash_func().digest_size
    
    if psk:
        # PSK-based : utiliser le PSK
        early_secret = hkdf_extract(zeros, psk, hash_func)
    else:
        # Handshake complet : early_secret = HKDF-Extract(0, 0)
        early_secret = hkdf_extract(zeros, zeros, hash_func)
    
    # Dériver le secret pour le handshake
    derived_secret = hkdf_expand_label(
        early_secret, "derived", transcript_hash, hash_func
    )
    
    handshake_secret = hkdf_extract(
        zeros, 
        ecdhe_shared_secret,  # k_partagé de X25519/ECDHE
        hash_func
    )
    
    return handshake_secret

def hkdf_extract(salt, ikm, hash_func):
    """Extraction HKDF pour TLS 1.3"""
    return HMAC(salt, ikm, hash_func).digest()

def hkdf_expand_label(secret, label, context, hash_func, length=None):
    """HKDF-Expand-Label comme défini dans RFC 8446"""
    hlen = hash_func().digest_size
    if length is None:
        length = hlen
    
    hkdf_label = (
        length.to_bytes(2, 'big') +
        len(b"tls13 " + label.encode()).to_bytes(1, 'big') +
        b"tls13 " + label.encode() +
        len(context).to_bytes(1, 'big') +
        context
    )
    
    return HKDFExpand(
        algorithm=hash_func,
        length=length,
        info=hkdf_label,
    ).derive(secret)
```

### 2.4 EncryptedExtensions

Avec la clé de handshake, le serveur envoie :
- `server_name` (SNI — chiffré !)
- `max_fragment_length`
- `supported_versions`
- ALPN
- `key_share` (si pas inclus dans ServerHello)

### 2.5 Certificate et CertificateVerify

Le certificat est envoyé **chiffré** (privacité du certificat) :

```python
def verify_certificate_verify(cert_verify_message, server_public_key, transcript_hash):
    """
    Vérifie CertificateVerify de TLS 1.3.
    Signature sur l'empreinte SHA-256 de la transcription du handshake.
    """
    # 1. Reconstruire le contexte
    context = b' ' * 64 + b"TLS 1.3, server CertificateVerify" + b'\x00'
    context += transcript_hash  # Hash SHA-256 de tout le handshake jusqu'ici
    
    # 2. Vérifier la signature
    sig_scheme = cert_verify_message.signature_scheme  # ex: rsa_pss_rsae_sha256
    signature = cert_verify_message.signature
    
    public_key.verify(
        signature,
        context,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=hashes.SHA256().digest_size
        ),
        hashes.SHA256()
    )
```

### 2.6 Finished

Validation de l'intégrité de tout le handshake :

```python
def compute_finished(key, transcript_hash, hash_func):
    """Calcule le message Finished de TLS 1.3"""
    # verify_data = HMAC(finished_key, transcript_hash)
    finished_key = hkdf_expand_label(
        key, "finished", b'', hash_func
    )
    return HMAC(finished_key, transcript_hash, hash_func).digest()
```

---

## 3. 0-RTT — Early Data

### 3.1 Principe

Permet au client d'envoyer des données dès le premier message (ClientHello), sans attendre le ServerHello.

**Condition** : le client doit avoir une session précédente (PSK).

### 3.2 Flux

```
ClientHello + PSK + early_data + 0-RTT data ──→
    ←── ServerHello + early_data + ...
Plus d'0-RTT data ──→
    ←── Application Data
Application Data ──→
```

### 3.3 Risques et Limitations

**Risques :**
- **Replay attack** : les 0-RTT data peuvent être rejouées
  - Protection : serveur doit implémenter un anti-replay (stockage de tickets)
- **Pas de Forward Secrecy** : les 0-RTT chiffrées avec la clé dérivée du PSK
  - Si le PSK est compromis → toutes les 0-RTT data sont déchiffrables
- **Ambiguïté de l'ordre** : le serveur peut recevoir 0-RTT data avant le Finished

```python
def is_0rtt_safe(psk, ticket_age, server_time):
    """Vérifie si une session PSK est acceptable pour 0-RTT"""
    # Temps trop long → refuser 0-RTT
    if ticket_age > 86400:  # 24h max
        return False
    
    # Pas de PSK → pas de 0-RTT
    if psk is None:
        return False
    
    return True
```

### 3.4 Anti-Replay via Ticket Age

```python
def anti_replay_check(ticket_nonce, ticket_age, server_time, db):
    """Vérifie l'anti-replay pour un ticket 0-RTT"""
    # 1. Vérifier que le ticket n'a pas déjà été utilisé
    ticket_hash = hashlib.sha256(ticket_nonce).digest()
    if db.exists(ticket_hash):
        return False  # Rejeu détecté
    
    # 2. Enregistrer le ticket (expiration dans window_RTT)
    db.store(ticket_hash, expire_in=10)  # 10 secondes
    
    # 3. Vérifier l'âge du ticket
    if ticket_age > max_early_data_size:  # RFC 8446 §8.3
        return False
    
    return True
```

---

## 4. Key Schedule Détaillé

### 4.1 Arbre de Dérivation

```
                           0
                           |
                     HKDF-Extract
                    /            \
               PSK (ou 0)       0
                   |             |
          HKDF-Extract      HKDF-Extract(..., ecdhe)
                   |             |
           Early Secret     Handshake Secret
                   |             |
              [derive]       [derive]
                   |             |
               [0-RTT]    [Handshake]
                   |             |
                   +──────┬──────+
                          |
                    HKDF-Extract
                          |
                   Master Secret
                          |
                    [derive]
                          |
                    Application (traffic)
```

### 4.2 Clés Dérivées

```python
def derive_all_keys(shared_secret, psk, early_data, transcript_hashes, hash_func):
    """Dérive toutes les clés TLS 1.3"""
    zeros = b'\x00' * hash_func().digest_size
    
    # 1. Early Secret (pour 0-RTT)
    early_secret = hkdf_extract(zeros, psk or zeros, hash_func)
    if early_data:
        client_early_traffic_secret = hkdf_expand_label(
            early_secret, "c e traffic", transcript_hashes['hello'], hash_func
        )
        early_exporter_secret = hkdf_expand_label(
            early_secret, "e exp master", transcript_hashes['hello'], hash_func
        )
    
    # 2. Handshake Secret
    derived_early = hkdf_expand_label(early_secret, "derived", b'', hash_func)
    handshake_secret = hkdf_extract(derived_early, shared_secret, hash_func)
    
    client_hs_traffic = hkdf_expand_label(
        handshake_secret, "c hs traffic", transcript_hashes['server_hello'], hash_func
    )
    server_hs_traffic = hkdf_expand_label(
        handshake_secret, "s hs traffic", transcript_hashes['server_hello'], hash_func
    )
    
    # 3. Master Secret
    derived_hs = hkdf_expand_label(handshake_secret, "derived", b'', hash_func)
    master_secret = hkdf_extract(derived_hs, zeros, hash_func)
    
    client_app_traffic = hkdf_expand_label(
        master_secret, "c ap traffic", transcript_hashes['server_finished'], hash_func
    )
    server_app_traffic = hkdf_expand_label(
        master_secret, "s ap traffic", transcript_hashes['server_finished'], hash_func
    )
    
    # 4. Resumption Master Secret
    resumption_master = hkdf_expand_label(
        master_secret, "res master", transcript_hashes['client_finished'], hash_func
    )
    
    return {
        'client_handshake': client_hs_traffic,
        'server_handshake': server_hs_traffic,
        'client_application': client_app_traffic,
        'server_application': server_app_traffic,
        'exporter_master': derived_early if early_data else None,
        'resumption_master': resumption_master,
    }
```

### 4.3 Key Update

TLS 1.3 permet de renouveler les clés de trafic sans handshake :

```python
def key_update(old_traffic_secret, hash_func):
    """Key Update TLS 1.3 — nouveau secret de trafic"""
    new_secret = hkdf_expand_label(
        old_traffic_secret, "traffic upd", b'', hash_func
    )
    return new_secret
```

---

## 5. Cipher Suites et AEAD

### 5.1 Les 5 suites TLS 1.3

| Code | Suite | AEAD | Hash | Sécurité |
|------|-------|------|------|----------|
| 0x1301 | TLS_AES_128_GCM_SHA256 | AES-128-GCM | SHA-256 | 128 bits |
| 0x1302 | TLS_AES_256_GCM_SHA384 | AES-256-GCM | SHA-384 | 256 bits |
| 0x1303 | TLS_CHACHA20_POLY1305_SHA256 | ChaCha20-Poly1305 | SHA-256 | 256 bits |
| 0x1304 | TLS_AES_128_CCM_SHA256 | AES-128-CCM | SHA-256 | 128 bits |
| 0x1305 | TLS_AES_128_CCM_8_SHA256 | AES-128-CCM-8 | SHA-256 | 128 bits (court tag) |

**Recommandation** : ChaCha20-Poly1305 pour les mobiles (pas d'AES-NI), AES-128-GCM sinon.

### 5.2 AEAD Encryption/Decryption

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

def tls13_record_encrypt(plaintext, key, nonce_base, seq_num, content_type):
    """Chiffrement d'un enregistrement TLS 1.3 avec AEAD"""
    # Nonce = nonce_base XOR seq_num (codé sur 12 octets)
    nonce = bytes([nb ^ sn for nb, sn in zip(nonce_base, seq_num.to_bytes(12, 'big'))])
    
    # AAD = seq_num + content_type + version + length
    aad = (
        seq_num.to_bytes(8, 'big') +
        bytes([content_type]) +
        b'\x03\x03' +  # version TLS
        len(plaintext).to_bytes(2, 'big')
    )
    
    cipher = AESGCM(key)
    ciphertext = cipher.encrypt(nonce, plaintext, aad)
    
    return ciphertext  # ciphertext + 16-byte tag
```

### 5.3 Record Layer

```
struct {
    ContentType type;
    ProtocolVersion legacy_record_version = 0x0303;
    uint16 length;
    opaque fragment[TLSPlaintext.length];
} TLSPlaintext;
```

Pour les records chiffrés, le type réel est encapsulé dans le ciphertext (content type 23 = application data, mais le type réel est dérivé de l'inner content type).

---

## 6. PSK — Pre-Shared Keys

### 6.1 Modes PSK

**Outside PSK** : clé partagée hors-bande (pré-configurée).
**Resumption PSK** : dérivé d'une session précédente.

### 6.2 Reprise de Session (Session Ticket)

```
Premier handshake :
Client → Server : ClientHello + key_share
Server → Client : ... + NewSessionTicket (ticket chiffré)

Reprise :
Client → Server : ClientHello + PSK + key_share (optionnel)
Server → Client : ServerHello + ...
```

```python
def create_session_ticket(resumption_master_secret, ticket_nonce, hash_func):
    """Crée un ticket de session TLS 1.3"""
    session_key = hkdf_expand_label(
        resumption_master_secret, "resumption", ticket_nonce, hash_func
    )
    # Le ticket est chiffré avec la clé du serveur, non visible ici
    return session_key
```

### 6.3 Durée de vie des tickets

```python
# RFC 8446 §4.6.1
# max_early_data_size = taille max des 0-RTT data pour ce ticket
# ticket_lifetime = durée de vie en secondes (max 604800 = 7 jours)

ticket = {
    'ticket_lifetime': 86400,       # 24h
    'ticket_age_add': random(),     # Anti-timing
    'ticket_nonce': secrets.token_bytes(16),
    'ticket': encrypted_ticket,     # Chiffré avec la clé serveur
    'max_early_data_size': 16384,   # 16 KB
}
```

---

## 7. QUIC et TLS 1.3

### 7.1 Architecture QUIC

QUIC remplace TCP + TLS 1.3 couche application.

```
HTTP/3
  │
QUIC (UDP)
  ├── Crypto (TLS 1.3 handshake)
  ├── Transport (streams multiplexés, FEC, ACK)
  └── Recovery (loss detection)
  │
UDP
```

### 7.2 Différences avec TLS 1.3 sur TCP

- **Handshake dans les paquets initiaux** : pas de fragmentation TLS séparée
- **Pas de Record Layer** : QUIC gère sa propre protection
- **0-RTT natif** : les 0-RTT data sont des véritables paquets QUIC
- **Connection Migration** : pas de rehandshake si IP change

```python
# QUIC utilise des niveaux de clé différents :
# Initial : dérivé de Destination Connection ID (pas de secret)
# Handshake : clé de handshake (forward secret)
# 1-RTT : clé de trafic (Application)
# 0-RTT : clé early data

def quic_initial_key(conn_id, hash_func):
    """Dérive la clé Initiale de QUIC"""
    salt = b'\x38\x76\x2a\xf8\xef\xcc\x6e\x39\x9f\x5d\x4e\xef\x6b\xf1\xa2\x5d\x4e\xef\x6b\xf1'
    
    initial_secret = hkdf_extract(salt, conn_id, hash_func)
    
    client_initial_key = hkdf_expand_label(
        initial_secret, "quic key", b'', hash_func
    )
    client_initial_iv = hkdf_expand_label(
        initial_secret, "quic iv", b'', hash_func
    )
    
    return client_initial_key, client_initial_iv
```

### 7.3 Comparaison TLS/TCP vs QUIC

| Propriété | TLS 1.3 + TCP | QUIC + TLS 1.3 |
|-----------|--------------|----------------|
| Transport | TCP (ordonné, fiable) | UDP (ordonné par stream) |
| Handshake | 1 RTT (full), 0-RTT (resume) | 0 RTT (souvent) |
| Head-of-line blocking | Oui (TCP) | Non (streams) |
| Migration | Nouveau handshake | Pas de re-handshake |
| Ossification | Record layer modifiable | Protocoles fixes |
| Réseaux | NAT, proxies (bien supporté) | Problèmes de middlebox |

---

## 8. Analyse de Sécurité

### 8.1 Forwards Secrecy (PFS)

TLS 1.3 garantit la **Perfect Forward Secrecy** car RSA key transport est supprimé. Même si la clé privée du serveur est compromise ultérieurement, les sessions passées ne peuvent pas être déchiffrées (sans la clé éphémère).

```
Clé de session = HKDF(ECDHE_SharedSecret, ...)
ECDHE_SharedSecret = a·b·G (éphémère, non stockée après la session)
```

### 8.2 Sécurité Prouvée

TLS 1.3 a une **preuve de sécurité formelle** (Dowling et al., 2015) dans le modèle Multi-Stage Key Exchange :

- **Match security** : chaque session a un identifiant unique
- **Mutual authentication** : client et serveur prouvent leur identité
- **Key indistinguishability** : la clé de session est indistinguable d'une aléatoire

### 8.3 Attaques Connues

| Attaque | Mécanisme | État |
|---------|-----------|------|
| Downgrade to TLS 1.2 | Supprimer `supported_versions` | Contré par "Downgrade Protection" dans ServerHello.random |
| SLOTH (CVE-2015-7575) | Collision MD5 | Pas applicable (pas MD5 dans TLS 1.3) |
| Triple Handshake | Manipulation de session | Contré par le hash de transcription |
| ROBOT (Bleichenbacher) | RSA oracle | Pas applicable (plus de RSA key transport) |
| DROWN | SSLv2 | Désactivé |
| POODLE | CBC padding | Pas applicable (suppression de CBC) |
| CRIME/BREACH | Compression | Pas applicable (suppression de compression) |
| **Replay** | 0-RTT data rejouées | Atténué par anti-replay, pas entièrement éliminé |
| **Traffic Analysis** | Taille des paquets | Inhérent au protocole (pas de solution) |
| **Certificate Inspection** | Metadata SNI | Résolu par ECH (Encrypted Client Hello) |

### 8.4 Encrypted Client Hello (ECH)

Remplace l'extension `server_name` chiffrée. Protège :
- Le nom du site visité
- Les extensions négociées
- La liste des cipher suites

```bash
# Vérifier le support ECH d'un serveur
openssl s_client -connect target.com:443 -ech_status
```

---

## 9. Implémentations

### 9.1 Analyse de connexion (OpenSSL CLI)

```bash
# Connexion basique
openssl s_client -connect google.com:443 -tls1_3

# Afficher les cipher suites supportées
openssl ciphers -s -tls1_3

# Se connecter avec une courbe spécifique
openssl s_client -connect target.com:443 -curves X25519

# Afficher le résumé du handshake
openssl s_client -connect example.com:443 -tlsextdebug -msg

# Forcer TLS 1.3
openssl s_client -connect example.com:443 -tls1_3 -msg

# Export des clés de session pour déchiffrement
SSLKEYLOGFILE=keys.log openssl s_client -connect example.com:443
# → décoder avec Wireshark en chargeant keys.log
```

### 9.2 Déchiffrement avec Wireshark

```bash
# Capturer le trafic
tcpdump -i any -w tls_traffic.pcap port 443

# Déchiffrer avec les clés
tshark -r tls_traffic.pcap -o tls.keylog_file:keys.log -Y "tls"

# Analyser le handshake
tshark -r capture.pcap -Y "tls.handshake.type == 2" -V  # ServerHello
```

### 9.3 Test SSL (testssl.sh)

```bash
git clone https://github.com/drwetter/testssl.sh.git
cd testssl.sh

./testssl.sh --tls13 https://example.com
./testssl.sh -cipher-per-proto https://example.com
./testssl.sh -P https://example.com  # PFS
./testssl.sh -U https://example.com  # Vulnérabilités
```

### 9.4 Programmation

**Python (cryptography)** :
```python
import ssl
import socket

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.minimum_version = ssl.TLSVersion.TLSv1_3
context.load_verify_locations('ca-cert.pem')

with socket.create_connection(('example.com', 443)) as sock:
    with context.wrap_socket(sock, server_hostname='example.com') as tls_sock:
        tls_sock.sendall(b'GET / HTTP/1.1\r\nHost: example.com\r\n\r\n')
        print(tls_sock.version())  # 'TLSv1.3'
```

**Go** :
```go
import "crypto/tls"

conn, _ := tls.Dial("tcp", "example.com:443", &tls.Config{
    MinVersion: tls.VersionTLS13,
})
conn.Write([]byte("GET / HTTP/1.0\r\n\r\n"))
```

**Rust (rustls)** :
```rust
use rustls::ClientConfig;
use std::sync::Arc;

let config = Arc::new(ClientConfig::builder()
    .with_safe_defaults()
    .with_native_roots()
    .with_no_client_auth());
```

### 9.5 Serveur TLS 1.3 avec OpenSSL

```bash
# Génération des clés et certificats
openssl ecparam -genkey -name prime256v1 -out server-key.pem
openssl req -new -key server-key.pem -x509 -days 365 -out server-cert.pem

# Démarrer un serveur TLS 1.3 (OpenSSL 1.1.1+)
openssl s_server -accept 4433 -cert server-cert.pem -key server-key.pem -tls1_3 -www
```

---

## Références

- **RFC 8446 (TLS 1.3)** : https://datatracker.ietf.org/doc/html/rfc8446
- **RFC 9001 (QUIC + TLS 1.3)** : https://datatracker.ietf.org/doc/html/rfc9001
- **TLS 1.3 Handshake Analysis** : https://blog.cloudflare.com/rfc-8446-aka-tls-1-3/
- **Dowling et al. Proof** : https://eprint.iacr.org/2015/914
- **testssl.sh** : https://github.com/drwetter/testssl.sh
- **ECH (Encrypted Client Hello)** : https://datatracker.ietf.org/doc/draft-ietf-tls-esni/
- **Wireshark TLS Decryption** : https://wiki.wireshark.org/TLS
- **QUIC Overview** : https://blog.cloudflare.com/the-quic-handshake-and-early-data/