---
name: mobile-forensics
description: Guide complet de forensic mobile — Android (ADB, recovery, root, JTAG) et iOS (iTunes backup, checkm8, libimobiledevice), extraction physique/logique, analyse d'applications, artefacts cloud, et tools Cellebrite/Magnet
tags: [forensics, mobile, android, ios, adb, checkm8, cellebrite, extraction, sqlite]
version: 1.0
---

# Forensic Mobile — Guide Complet

Guide exhaustif d'investigation numérique sur terminaux mobiles Android et iOS : acquisition, analyse, extraction de données, et outils.

---

## 1. Principes Fondamentaux

### Défis Spécifiques du Mobile Forensics

```txt
1. CHIFFREMENT FORT
   Android 10+ : FBE (File-Based Encryption) par défaut
   iOS : HARD (Hardware Assisted Recovery) keys, Secure Enclave
   → Sans code PIN/pattern : aucune extraction possible

2. SÉCURITÉ MATÉRIELLE
   Secure Enclave (iOS) / TEE (Android)
   Effacement après tentatives échouées
   Verified Boot (ne démarre pas si modifié)

3. VOLATILITÉ
   Connexion cellulaire → effacement à distance possible
   Verrouillage automatique
   Écran éteint = données cryptées

4. DIVERSITÉ
   Des centaines de modèles
   Versions OS fragmentées
   Mises à jour irrégulières
```

### Ordre des Actions sur Mobile

```txt
1. ISOLER LE RÉSEAU (Faraday cage / Mode Avion)
   → Empêche l'effacement à distance (Find My iPhone, Android Device Manager)
   → Bloque les mises à jour OTA
   
2. CONTRE LE VERROUILLAGE AUTOMATIQUE
   → Désactiver le verrouillage dans les paramètres (si déverrouillé)
   → Maintenir l'écran allumé

3. CAPTURER L'ÉTAT
   → Photographier l'écran (apps ouvertes, notifications)
   → Noter le niveau de batterie
   → Version OS dans About

4. EXTRACTION PRIORITAIRE
   1. RAM (si root/jailbreak)
   2. Extraction physique (via JTAG/ISP)
   3. Extraction logique (backup)
   4. Cloud extraction (iCloud, Google Drive)
```

---

## 2. Android Forensics

### Acquisition Logique (ADB)

```bash
# Activer ADB (nécessite accès à l'écran déverrouillé)
# Paramètres → Options développeur → Débogage USB

# Vérifier la connexion
adb devices
# Résultat : 12345678        device

# Informations système
adb shell getprop ro.build.version.sdk   # API level
adb shell getprop ro.build.version.release  # Android version
adb shell getprop ro.product.model        # Model
adb shell getprop ro.serialno              # Serial
adb shell getprop | grep -i "build\|product\|serial\|security"

# Extraction ADB Backup (Android 4.0 - 12)
adb backup -apk -shared -all -system -f backup.ab

# Analyser le backup .ab
# En-tête = 24 bytes (version + compression + taille)
dd if=backup.ab bs=1 skip=24 | openssl zlib -d > backup.tar
tar xvf backup.tar
# Contenu : apps/, shared/, data/

# Si chiffré (Android 4.2+ backup password)
# Besoin du mot de passe défini lors du backup
# Tools : Android Backup Extractor, Abe (Android Backup Extractor)
```

### Extraction ADB Approfondie

```bash
# Liste des packages installés
adb shell pm list packages > packages.txt
adb shell pm list packages -3 > user_apps.txt  # Apps tierces seulement

# APK extraction
adb shell pm path com.whatsapp
# Résultat : package:/data/app/com.whatsapp-xxxx/base.apk
adb pull /data/app/com.whatsapp-xxxx/base.apk

# Dump de la base de données (nécessite root)
adb shell
su
cp /data/data/com.whatsapp/databases/msgstore.db /sdcard/
exit
adb pull /sdcard/msgstore.db

# Capture d'écran + écran d'accueil
adb shell screencap -p /sdcard/screen.png
adb pull /sdcard/screen.png

# SMS (Android 10-)
adb shell content query --uri content://sms/inbox > sms.txt
adb shell content query --uri content://sms/sent > sms_sent.txt

# Contacts
adb shell content query --uri content://contacts/phones/ > contacts.txt

# Call log
adb shell content query --uri content://call_log/calls > call_log.txt

# Calendrier
adb shell content query --uri content://calendar/events > calendar.txt
```

### Acquisition Physique (root)

```bash
# Avec root, extraction complète de la partition data
adb root
# ou
adb shell su

# Lister les partitions
adb shell cat /proc/partitions
adb shell ls -la /dev/block/platform/*/by-name/
# boot, recovery, system, data, cache, userdata, etc.

# Dump de la partition userdata
adb shell su -c "dd if=/dev/block/mmcblk0pXX of=/sdcard/userdata.dd bs=4M"
adb pull /sdcard/userdata.dd

# Backup EFS (IMEI, radio)
adb shell su -c "dd if=/dev/block/mmcblk0pXX of=/sdcard/efs.img bs=4M"
adb pull /sdcard/efs.img

# Dump complet du stockage
adb shell su -c "dd if=/dev/block/mmcblk0 of=/sdcard/full_dump.dd bs=4M"
# ATTENTION : selon la capacité du téléphone, peut prendre des heures

# Mémoire RAM (root)
adb shell su -c "cat /proc/kcore" > ram_dump.elf
# ou LiME pour Android (même principe que Linux)
```

### Acquisition via Recovery

```bash
# Custom Recovery (TWRP, CWM)
# Boot en recovery mode (Vol Up + Power)
# Connecter USB, lancer adb

# Dans TWRP :
adb shell
# TWRP monte les partitions en read-write
mount | grep data

# Dump complet (via TWRP)
adb shell dd if=/dev/block/mmcblk0 of=/external_sd/full_dump.dd bs=4M

# Backup TWRP complet
# TWRP → Backup → Select partitions
# Boot, System, Data, Cache, EFS
# Copier le dossier de backup
adb pull /sdcard/TWRP/

# Si bootloader verrouillé → impossible de flasher TWRP
```

### Extraction Via Analyse Physique (ISP/JTAG)

```bash
# JTAG (Joint Test Action Group)
# Méthode matérielle pour lire la mémoire NAND/eMMC
# Contourne le bootloader verrouillé
# Outils : RIFF Box, Medusa, Easy JTAG

# ISP (In-System Programming)
# Brancher des pinces sur les broches eMMC
# Lire la puce directement
# Outils : Z3X, Octoplus, Medusa

# Chip-Off
# Dessouder la puce eMMC/UFS
# Lire avec un lecteur de carte eMMC
# Très risqué (soudure BGA)
# Outils :  Easy JTAG Plus, T13 Tool
```

---

## 3. iOS Forensics

### Extraction Logique (iTunes Backup)

```bash
# iTunes backup (non chiffré)
idevicebackup2 backup /evidence/ios_backup/
# ou via iTunes : Preferences → Devices → Backup

# Backup chiffré (iOS 4+)
# Contient : mot de passe WiFi, Health, Keychain
# Nécessite le mot de passe de backup

# Analyser le backup avec libimobiledevice
brew install libimobiledevice
brew install ideviceinstaller

# Informations du backup
ideviceinfo > device_info.txt
ideviceactivationstate > activation_state.txt

# Structure du backup iOS
/evidence/ios_backup/
├── Manifest.plist        # Info de l'appareil + version iOS
├── Status.plist          # Statut du backup
├── Info.plist            # UUID, IMEI, Serial
└── <hash>/
    ├── 00/
    │   ├── 00f0...
    │   └── ...           # Fichiers par hash du chemin
    └── ...
```

### Décoder le backup iOS

```bash
# Utiliser iBackup Viewer, iExplorer, ou outils CLI

# Avec libimobiledevice + Python
pip install iphone-backup-decrypt

# Déchiffrer un backup (si mot de passe connu)
iphone-backup-decrypt -p "password" -d /evidence/ios_backup /evidence/decrypted/

# Analyser les fichiers
# Base de données SQLite :
# SMS : /root/Library/SMS/sms.db
#    SELECT * FROM message;
#    SELECT * FROM handle;
#    SELECT * FROM attachment;

# Appels : /root/Library/CallHistory/call_history.db
#    SELECT * FROM ZCALLRECORD;

# Contacts : /root/Library/AddressBook/AddressBook.sqlitedb

# Notes : /root/Library/Notes/notes.sqlite

# Calendrier : /root/Library/Calendars/Calendar.sqlitedb

# Safari : /root/Library/Safari/Bookmarks.db
#          /root/Library/Safari/History.db

# Photos : /root/Media/DCIM/... (images + métadonnées)
```

### Extraction Physique (checkm8)

```bash
# checkm8 — BootROM exploit (iPhone 4S à iPhone X)
# Exploit matériel non patchable (ROM)
# Donne accès au filesystem même sans code PIN
# Outils : ipwndfu, checkra1n, palera1n

# 1. Mettre l'iPhone en DFU mode
# iPhone 7+ : Volume Down + Power (10s) → Volume Down (5s)
# iPhone 6s- : Home + Power (10s) → Home (5s)

# 2. Lancer checkra1n
sudo checkra1n -c  # CLI mode

# 3. Une fois jailbreaké, extraire
# Via SSH ramdisk :
ssh root@localhost -p 2222

# Extraire les fichiers
tar czf /tmp/data.tar.gz /private/var/
scp -P 2222 root@localhost:/tmp/data.tar.gz .

# Ou dump complet de la partition
dd if=/dev/disk0s1 of=/tmp/disk.dd bs=4M
scp -P 2222 root@localhost:/tmp/disk.dd .

# Ramdisk forensique (SSH ramdisk)
# Créer un ramdisk personnalisé avec SSH activé
# Booter via checkm8 → ramdisk → extraction
```

### Acquisition iOS via libimobiledevice

```bash
# Installation
sudo apt install libimobiledevice-utils usbmuxd

# Liste des appareils
idevice_id -l
# Résultat : 00008020-XXXXXXXXXXXXXX

# Informations
ideviceinfo -s  # Simple, sans pairing
ideviceinfo      # Complet, nécessite pairing

# Capture d'écran
idevicescreenshot

# Logs système
idevicesyslog > syslog.txt

# Journal diagnostic
idevicediagnostics diagnostics

# Backup
idevicebackup2 backup --full /evidence/ios_backup/

# Restaurer (attention : écrase)
# idevicebackup2 restore /evidence/ios_backup/

# Installer une app (IPA)
ideviceinstaller -i app.ipa

# Lister les apps
ideviceinstaller -l
```

---

## 4. Analyse d'Applications

### WhatsApp

```bash
# Android — Base de données
adb shell su -c "cp /data/data/com.whatsapp/databases/msgstore.db /sdcard/"
adb shell su -c "cp /data/data/com.whatsapp/databases/wa.db /sdcard/"  # Contacts
adb pull /sdcard/msgstore.db
adb pull /sdcard/wa.db

# Analyse SQLite msgstore.db
sqlite3 msgstore.db "
.headers on
.mode column

-- Messages textes
SELECT chat_view.subject AS group_name,
       message.timestamp,
       message.from_me,
       message.text_data,
       message.media_url
FROM message
LEFT JOIN chat_view ON message.chat_row_id = chat_view._id
ORDER BY message.timestamp DESC;

-- Contacts
SELECT jid, wa_name, display_name
FROM wa_contacts;

-- Pièces jointes
SELECT file_path, mime_type, file_size
FROM message_media;
"

# iOS — Backup
# Dans le backup iTunes, extraire :
# /AppDomainGroup-group.net.whatsapp/ChatStorage.sqlite
sqlite3 ChatStorage.sqlite "
SELECT ZWACHATSESSION.ZCONTACTNAME,
       ZWAMESSAGE.ZMESSAGEDATE,
       ZWAMESSAGE.ZTEXT
FROM ZWAMESSAGE
LEFT JOIN ZWACHATSESSION ON ZWAMESSAGE.ZSESSION = ZWACHATSESSION.Z_PK
ORDER BY ZWAMESSAGE.ZMESSAGEDATE DESC;
"
```

### Telegram

```bash
# Android
adb shell su -c "cp -r /data/data/org.telegram.messenger /sdcard/telegram_data/"
adb pull /sdcard/telegram_data/

# Fichier important : cache4.db (cache SQLite)
# cache4.db contient les messages en cache
sqlite3 cache4.db "
SELECT DISTINCT uid, date, message
FROM messages
ORDER BY date DESC;
"

# iOS — Telegram dans backup
# AppDomainGroup-group.ph.telegra.Telegraph/
# Chiffré E2E pour les messages secrets (indéchiffrable sans les clés)
# Messages non-secrets : SQLite dans le sandbox

# Fichier : telegram-data/Documents/telegram-data/
# Les messages sont dans messages.sqlite (chiffré !)
```

### Signal

```bash
# Android — Chiffrement E2E fort
# Base de données : signal.db (chiffrée avec SQLCipher)
# Nécessite la clé (dans SharedPreferences)

# /data/data/org.thoughtcrime.securesms/databases/
adb shell su -c "cp /data/data/org.thoughtcrime.securesms/databases/signal.db /sdcard/"
adb shell su -c "cp /data/data/org.thoughtcrime.securesms/shared_prefs/org.thoughtcrime.securesms_preferences.xml /sdcard/"

# Extraction de la clé
grep "passphrase" org.thoughtcrime.securesms_preferences.xml

# Déchiffrement
sqlcipher signal.db
sqlite> PRAGMA key='passphrase_here';
sqlite> PRAGMA cipher_use_hmac=OFF;
sqlite> .tables

# iOS — Chiffrement complet, pas d'accès sans clé
```

### Navigateurs Mobiles

```bash
# Chrome Android
adb shell su -c "cp /data/data/com.android.chrome/app_chrome/Default/History /sdcard/"
adb pull /sdcard/History

sqlite3 History "
SELECT url, title, visit_count,
       datetime(last_visit_time / 1000000 + 11644473600, 'unixepoch') as visit_time
FROM urls ORDER BY last_visit_time DESC;
"

# Safari iOS
# Dans backup :
# /root/Library/Safari/History.db
# /root/Library/Safari/Bookmarks.db (plist format)
sqlite3 History.db "
SELECT url, visit_time
FROM history_visits
JOIN history_items ON history_visits.history_item = history_items.id
ORDER BY visit_time DESC;
"
```

---

## 5. Artefacts Cloud et Comptes

### iCloud Extraction

```bash
# iCloud backup (légal)
# Nécessite Apple ID + mot de passe + 2FA
# OU : Elcomsoft Phone Breaker (brute-force iCloud)

# Via iCloud.com :
# Paramètres → iCloud → Gérer le stockage → sauvegardes

# Via Elcomsoft Cloud Explorer :
# 1. Connecter l'Apple ID
# 2. Télécharger les photos, contacts, calendrier
# 3. Télécharger le backup iCloud complet

# Via Python :
# icloudpd — iCloud Photos downloader
pip install icloudpd
icloudpd --download --directory /evidence/icloud/ --username suspect@email.com
```

### Google Account (Android)

```bash
# Sans accès au téléphone, extraction Google Takeout :
# https://takeout.google.com/
# Données exportables :
# - Chrome (historique, bookmarks)
# - Contacts
# - Drive
# - Gmail
# - Photos
# - YouTube
# - Maps (Localisation !)
# - Fit (santé)
# - Locations historiques

# Avec accès au téléphone :
# backup des comptes Google
adb shell su -c "cp /data/system/accounts.db /sdcard/"
adb pull /sdcard/accounts.db
sqlite3 accounts.db ".tables"

# Google Play Services location history
# /data/data/com.google.android.gms/databases/
adb shell su -c "cp /data/data/com.google.android.gms/databases/* /sdcard/gms_backup/"
adb pull /sdcard/gms_backup/
```

---

## 6. Outils Mobile Forensics

### Commercial

```bash
# Cellebrite UFED / Premium
# - Le standard de l'industrie
# - Extraction physique, logique, cloud
# - Supporte 30,000+ devices
# - Extraction avancée (Android + iOS)
# - Analyse dans Cellebrite Physical Analyzer
# - Coût : ~$10,000-50,000/an

# Magnet AXIOM
# - Analyse mobile + cloud + disque
# - Extraction avec Magnet ACQUIRE
# - Analyse des artefacts dans AXIOM
# - Rapports judiciaires
# - Coût : ~$5,000-15,000

# Elcomsoft Phone Breaker
# - Extraction iCloud, iOS backup
# - Brute-force passwords
# - Cloud extraction
# - Coût : ~$1,000

# Oxygen Forensic Detective
# - Extraction logique/physique
# - Analyse cloud
# - Rapports
# - Coût : ~$3,000-10,000
```

### Open Source / Gratuit

```bash
# ADB (Android Debug Bridge)
# - Inclus dans Android SDK Platform Tools
# - Extraction logique
# - Backup Android
# - GRATUIT

# libimobiledevice
# - Extraction iOS (Linux)
# - Backup, syslog, screenshot
# - GRATUIT

# checkra1n
# - Jailbreak iOS (checkm8 exploit)
# - iPhone 5S à X
# - Nécessite Linux/Mac
# - GRATUIT

# Santoku Linux
# - Distribution Linux forensique mobile
# - Outils pré-installés
# - GRATUIT

# AFLogical (via adb)
# - Extraction logique automatisée
# - SMS, contacts, call logs
# - GRATUIT
```

---

## 7. Analyse de Localisation

### Google Timeline

```bash
# Google Location History
# Via Google Takeout
# Fichier : Location History.json ou Records.json

# Analyse Python
python3 << 'EOF'
import json

with open('Location History.json') as f:
    data = json.load(f)

for loc in data['locations'][:10]:  # 10 premières entrées
    ts = loc['timestampMs']
    lat = loc['latitudeE7'] / 1e7
    lon = loc['longitudeE7'] / 1e7
    acc = loc.get('accuracy', 'N/A')
    print(f"{ts}: {lat},{lon} (accuracy: {acc}m)")
EOF
```

### Exif Photos

```bash
# Extraire les coordonnées GPS des photos
find /evidence/DCIM/ -name "*.jpg" -exec exiftool -gps* {} \;

# Exporter vers KML pour Google Earth
exiftool -p gpx.fmt -gps* /evidence/DCIM/ > trace.gpx
# Convertir GPX en KML
gpsbabel -i gpx -f trace.gpx -o kml -F locations.kml
```

---

## 8. Extraction et Analyse d'Appels / Messages

### SMS/MMS Android

```bash
# mmssms.db — Base des SMS/MMS
adb shell su -c "cp /data/data/com.android.providers.telephony/databases/mmssms.db /sdcard/"
adb pull /sdcard/mmssms.db

# Analyse
sqlite3 mmssms.db "
SELECT address, date/1000 as timestamp, body
FROM sms
WHERE type=1  -- inbox
ORDER BY date DESC
LIMIT 50;
"
```

### Call Logs Android

```bash
# contacts2.db — Appels et contacts
adb shell su -c "cp /data/data/com.android.providers.contacts/databases/contacts2.db /sdcard/"
adb pull /sdcard/contacts2.db

# Analyse des appels
sqlite3 contacts2.db "
SELECT number, duration,
       datetime(date/1000, 'unixepoch', 'localtime') as call_time,
       CASE type
           WHEN 1 THEN 'INCOMING'
           WHEN 2 THEN 'OUTGOING'
           WHEN 3 THEN 'MISSED'
       END as call_type
FROM calls
ORDER BY date DESC
LIMIT 100;
"
```

---

## 9. Script d'Acquisition Automatisé Android

```bash
#!/bin/bash
# android_acquire.sh — Extraction forensique Android complète

DEVICE_ID=$(adb devices | grep -v "List" | head -1 | awk '{print $1}')
OUTDIR="/evidence/android_${DEVICE_ID}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTDIR"

echo "=== ANDROID FORENSICS ACQUISITION ==="
echo "Device: $DEVICE_ID"
echo "Output: $OUTDIR"

# 1. Device info
echo "[1] Device info..."
adb shell getprop > "$OUTDIR/properties.txt"
adb shell cat /proc/version > "$OUTDIR/kernel_version.txt"

# 2. Applications
echo "[2] Package listing..."
adb shell pm list packages -3 -f > "$OUTDIR/user_packages.txt"
adb shell pm list permissions -g > "$OUTDIR/permissions.txt"

# 3. SMS/Call logs (si accessible)
echo "[3] Communications..."
adb shell content query --uri content://sms/inbox > "$OUTDIR/sms_inbox.txt" 2>/dev/null
adb shell content query --uri content://sms/sent > "$OUTDIR/sms_sent.txt" 2>/dev/null
adb shell content query --uri content://call_log/calls > "$OUTDIR/call_log.txt" 2>/dev/null

# 4. Contacts
echo "[4] Contacts..."
adb shell content query --uri content://contacts/phones > "$OUTDIR/contacts.txt" 2>/dev/null

# 5. Screenshots
echo "[5] Screenshots..."
adb shell screencap -p /sdcard/screen_$(date +%s).png
adb pull /sdcard/screen_*.png "$OUTDIR/screenshots/"

# 6. SD Card content
echo "[6] SD card listing..."
adb shell find /sdcard/ -type f -ls > "$OUTDIR/sdcard_files.txt" 2>/dev/null

# 7. WiFi
echo "[7] WiFi config..."
adb shell cat /data/misc/wifi/wpa_supplicant.conf > "$OUTDIR/wifi.conf" 2>/dev/null

# 8. Full backup
echo "[8] ADB backup..."
adb backup -apk -shared -all -system -f "$OUTDIR/full_backup.ab" 2>/dev/null

# 9. Hash
echo "[9] Generating hashes..."
sha256sum "$OUTDIR"/*.ab "$OUTDIR"/*.txt > "$OUTDIR/hashes.txt"

echo ""
echo "=== DONE ==="
echo "Files saved to: $OUTDIR"
```

---

## 10. Analyse d'Images WhatsApp / Téléchargements

```bash
# WhatsApp images
# Android : /sdcard/WhatsApp/Media/WhatsApp Images/
# iOS : /AppDomainGroup-group.net.whatsapp/ChatStorage/Media/

# Récupérer toutes les images WhatsApp
find /evidence/ -path "*WhatsApp*Media*" -name "*.jpg" -exec cp {} /evidence/images/ \;

# Exif (metadata + GPS si présent)
exiftool -a -gps* /evidence/images/ > image_metadata.txt

# Hash SHA256 pour chaîne de custody
for img in /evidence/images/*.jpg; do
    sha256sum "$img" >> /evidence/images_sha256.txt
done
```

---

## 11. Dépannage

```txt
PROBLÈME : "adb: error: device unauthorized"
SOLUTION : Déverrouiller l'écran et accepter la demande ADB

PROBLÈME : iOS "This device is passcode locked"
SOLUTION : 
   - checkm8 (iPhone 4S-X) si le bootloader le permet
   - Sinon, extraction iCloud uniquement

PROBLÈME : Base de données chiffrée (Signal, WhatsApp crypted)
SOLUTION : 
   - WhatsApp : Fichiers crypt.db4 (Android) → version antérieure
   - Signal : SQLCipher → clé dans SharedPreferences
   - iOS : impossible sans clé utilisateur

PROBLÈME : Téléphone verrouillé après trop d'essais
SOLUTION :
   - Android : connexion au Google account pour déverrouiller
   - iOS : iTunes backup si backups automatiques activés
   - Sinon : effacement → plus rien à extraire
```

---

## 12. Chaîne de Custody Mobile

```txt
ÉLÉMENTS À DOCUMENTER :
- Modèle exact, IMEI, MEID, Serial
- Version OS + build number
- État de l'écran (verrouillé/déverrouillé)
- État du bootloader (verrouillé/déverrouillé)
- Code PIN/motif (si connu)
- Comptes iCloud/Google associés
- Niveau batterie
- Opérateur téléphonique
- IMSI (SIM card)

PRÉCAUTIONS :
- NE PAS éteindre (perte RAM + verrouillage)
- NE PAS tenter de déverrouiller sans méthode éprouvée
- Utiliser une cage de Faraday (Faraday bag)
- Documenter chaque extraction
- Conserver l'original sous scellé
```

---

## 13. Ressources

- **Cellebrite** : https://www.cellebrite.com/
- **Magnet Forensics** : https://www.magnetforensics.com/
- **libimobiledevice** : https://libimobiledevice.org/
- **checkra1n** : https://checkra.in/
- **AFLogical** : https://github.com/nowsecure/af logical
- **Elcomsoft** : https://www.elcomsoft.com/
- **Santoku Linux** : https://santoku-linux.com/
- **Google Takeout** : https://takeout.google.com/
- **iCloudPD** : https://github.com/icloudpd/icloudpd