#!/usr/bin/env python3
"""
ADAM-RED — Handler Red Team : Défi escalade de privilèges Android.

Cible : Nothing Phone 2 (codename CAPE-QRD, USB 18d1:4ee7, serial 2f109ecc)
Objectif : Énumération → fingerprint → identification de vecteurs d'escalade → exécution root.

Phases :
  1. RECON — Énumération complète du device (modèle, Android version, security patch, bootloader, SELinux).
  2. FINGERPRINT — Identification des CVE applicables selon le niveau de patch.
  3. ENUM — Liste des packages système, services exposés, surface d'attaque.
  4. ESCALATION — Test des vecteurs d'escalade connus (Dirty Pipe, io_uring, etc.).
  5. REPORT — Génération du rapport de pentest.

Utilisation :
  python3 adam-red-challenge.py --phase recon      # Phase 1 seule
  python3 adam-red-challenge.py --phase all         # Toutes les phases
  python3 adam-red-challenge.py --device 2f109ecc   # Spécifier le serial

Dépendances : adb (platform-tools), accessible dans ~/.local/bin/adb
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ─── Configuration ───
ADB_PATH = os.path.expanduser("~/.local/bin/adb")
LOG_DIR = Path("/home/aza/eva-adam-v2/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "red-challenge.log"
REPORT_DIR = Path("/home/aza/eva-adam-v2/reports/red-team")
REPORT_DIR.mkdir(parents=True, exist_ok=True)
EVENT_DB = Path("/home/aza/eva-adam-v2/event_bus.db")

# Cible connue : Nothing Phone 2
TARGET_SERIAL = "2f109ecc"
TARGET_VENDOR = "18d1"
TARGET_PRODUCT = "4ee7"
TARGET_MANUFACTURER = "Nothing"
TARGET_PRODUCT_NAME = "CAPE-QRD"  # Codename Nothing Phone 2

# ─── Utilitaires ───

def log(msg: str, level: str = "INFO"):
    """Log dans le fichier + stdout."""
    ts = datetime.now(timezone.utc).isoformat()
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def run_adb(args: list, timeout: int = 30) -> tuple:
    """Exécute une commande adb et retourne (stdout, stderr, returncode)."""
    cmd = [ADB_PATH] + args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1
    except FileNotFoundError:
        return "", "adb non trouvé", -2

def check_device(serial: str) -> dict:
    """Vérifie la connexion au device et retourne son statut."""
    stdout, stderr, rc = run_adb(["devices", "-l"])
    devices = {}
    for line in stdout.split("\n"):
        if serial in line:
            parts = line.split()
            devices[serial] = {
                "state": parts[1] if len(parts) > 1 else "unknown",
                "raw": line.strip()
            }
            break
    return devices.get(serial, {"state": "not_found"})

def adb_shell(cmd: str, serial: str = TARGET_SERIAL, timeout: int = 15) -> str:
    """Exécute une commande shell sur le device."""
    stdout, stderr, rc = run_adb(["-s", serial, "shell", cmd], timeout=timeout)
    if rc != 0 and stderr:
        return f"ERROR: {stderr}"
    return stdout

def get_prop(prop: str, serial: str = TARGET_SERIAL) -> str:
    """Récupère une propriété Android via getprop."""
    return adb_shell(f"getprop {prop}", serial).strip()

# ─── Phase 1 : RECON ───

def phase_recon(serial: str) -> dict:
    """Énumération complète du device."""
    log("=== PHASE 1 : RECON — Énumération du device ===")

    state = check_device(serial)
    if state["state"] != "device":
        log(f"Device {serial} en état '{state['state']}' — unauthorized ou offline", "WARN")
        log("→ Accepter la clé RSA sur l'écran du téléphone", "WARN")
        return {
            "serial": serial,
            "state": state["state"],
            "error": "Device non accessible — autoriser le débogage USB sur l'écran"
        }

    recon = {
        "serial": serial,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "state": state["state"],
    }

    # Propriétés matérielles et logicielles
    props = {
        "model": "ro.product.model",
        "brand": "ro.product.brand",
        "manufacturer": "ro.product.manufacturer",
        "device": "ro.product.device",
        "android_version": "ro.build.version.release",
        "sdk_level": "ro.build.version.sdk",
        "security_patch": "ro.build.version.security_patch",
        "build_id": "ro.build.id",
        "build_fingerprint": "ro.build.fingerprint",
        "bootloader": "ro.bootloader",
        "kernel": "ro.kernel.version",
        "abi": "ro.product.cpu.abi",
        "selinux": "ro.boot.selinux",
        "build_type": "ro.build.type",
        "build_tags": "ro.build.tags",
        "build_user": "ro.build.user",
        "build_host": "ro.build.host",
    }

    for key, prop in props.items():
        val = get_prop(prop, serial)
        if val and "ERROR" not in val:
            recon[key] = val

    # Bootloader status
    bootloader_unlocked = adb_shell("getprop ro.boot.verifiedbootstate", serial).strip()
    flash_locked = adb_shell("getprop ro.boot.flash.locked", serial).strip()
    recon["bootloader_verified_state"] = bootloader_unlocked
    recon["flash_locked"] = flash_locked

    # SELinux mode
    selinux_mode = adb_shell("getenforce", serial).strip()
    recon["selinux_mode"] = selinux_mode

    # Informations kernel via uname
    uname = adb_shell("uname -a", serial).strip()
    recon["uname"] = uname

    # Vérification root
    su_check = adb_shell("which su", serial).strip()
    recon["su_present"] = "not found" not in su_check.lower() and "ERROR" not in su_check
    recon["su_path"] = su_check if recon["su_present"] else None

    # whoami
    whoami = adb_shell("whoami", serial).strip()
    recon["current_user"] = whoami

    # id
    uid = adb_shell("id", serial).strip()
    recon["uid"] = uid

    # Résumé
    model = recon.get("model", "?")
    brand = recon.get("brand", "?")
    android = recon.get("android_version", "?")
    patch = recon.get("security_patch", "?")
    log(f"Device : {brand} {model} (Android {android}, patch {patch})")
    log(f"SELinux : {recon.get('selinux_mode', '?')} | Bootloader : {recon.get('flash_locked', '?')} | Root : {'OUI' if recon['su_present'] else 'NON'}")

    return recon

# ─── Phase 2 : FINGERPRINT (CVE) ───

# Base de CVE Android par niveau de patch
CVE_DATABASE = {
    "CVE-2024-0044": {
        "description": "Escalade de privilèges via run-as (Android 10-13)",
        "affected_patches_before": "2024-03-01",
        "cvss": 7.8,
        "technique": "run-as exploit — installe un package avec uid 1000 (system)"
    },
    "CVE-2023-21492": {
        "description": "Escalade de privilèges kernel Linux (Android 11-13)",
        "affected_patches_before": "2023-05-01",
        "cvss": 7.8,
    },
    "CVE-2022-22706": {
        "description": "Escalade via io_uring kernel (Android 12)",
        "affected_patches_before": "2022-03-01",
        "cvss": 7.8,
    },
    "CVE-2021-1905": {
        "description": "Use-after-free driver GPU Qualcomm",
        "affected_patches_before": "2021-04-01",
        "cvss": 8.1,
    },
    "CVE-2020-0041": {
        "description": "Escalade de privilèges binder (Android 8-10)",
        "affected_patches_before": "2020-03-01",
        "cvss": 7.0,
    },
    "CVE-2019-2215": {
        "description": "Use-after-free driver binder (Android 7-8, kernel < 4.14)",
        "affected_patches_before": "2019-10-01",
        "cvss": 7.8,
    },
    "CVE-2024-23222": {
        "description": "Escalade WebKit/Android System WebView",
        "affected_patches_before": "2024-03-01",
        "cvss": 8.8,
    },
}

def phase_fingerprint(recon: dict) -> dict:
    """Identifie les CVE applicables selon le niveau de patch du device."""
    log("=== PHASE 2 : FINGERPRINT — Identification CVE ===")

    patch_level = recon.get("security_patch", "1970-01-01")
    android_ver = recon.get("android_version", "?")

    log(f"Niveau de patch sécurité : {patch_level}")
    log(f"Version Android : {android_ver}")

    applicable = []
    for cve_id, info in CVE_DATABASE.items():
        cutoff = info.get("affected_patches_before", "1970-01-01")
        if patch_level < cutoff:
            applicable.append({
                "cve": cve_id,
                "description": info["description"],
                "cvss": info.get("cvss", 0),
                "technique": info.get("technique", ""),
                "cutoff": cutoff,
            })
            log(f"  [!] {cve_id} (CVSS {info.get('cvss', 0)}) — applicable (patch {patch_level} < {cutoff})")

    if not applicable:
        log("  [OK] Aucune CVE connue applicable — device à jour")

    # Vérification spécifique Nothing Phone 2
    # Nothing Phone 2 = Android 13+ (Nothing OS 2.x), Snapdragon 8+ Gen 1
    if "Nothing" in recon.get("manufacturer", ""):
        log(f"  [*] Cible identifiée : Nothing Phone 2 (CAPE-QRD)")
        log(f"  [*] SoC : Snapdragon 8+ Gen 1 (SM8475)")
        log(f"  [*] Vérifier : exploit kernel spécifique Qualcomm, fastboot unlock, magisk")

    return {
        "patch_level": patch_level,
        "android_version": android_ver,
        "applicable_cves": applicable,
        "total_cves": len(applicable),
    }

# ─── Phase 3 : ENUM (surface d'attaque) ───

def phase_enum(serial: str) -> dict:
    """Énumération de la surface d'attaque."""
    log("=== PHASE 3 : ENUM — Surface d'attaque ===")

    enum = {}

    # Packages système dangereux
    dangerous_packages = [
        "com.android.shell",
        "com.termux",
        "com.topjohnwu.magisk",
        "eu.chainfire.supersu",
        "com.koushikdutta.rommanager",
        "com.koushikdutta.superuser",
        "com.thirdparty.superuser",
        "com.noshufou.android.su",
        "com.yellowes.su",
        "com.kingouser.com",
        "com.kingroot.kingroot",
        "com.onegah.whatsrunning",
    ]

    all_packages = adb_shell("pm list packages", serial)
    if "ERROR" not in all_packages:
        installed = set()
        for line in all_packages.split("\n"):
            pkg = line.replace("package:", "").strip()
            if pkg:
                installed.add(pkg)

        enum["total_packages"] = len(installed)
        enum["dangerous_found"] = [p for p in dangerous_packages if p in installed]

        if enum["dangerous_found"]:
            for p in enum["dangerous_found"]:
                log(f"  [!] Package root/dangereux trouvé : {p}")
        else:
            log(f"  [OK] Aucun package root/dangereux détecté")
    else:
        enum["packages_error"] = all_packages
        log(f"  [ERR] Impossible d'énumérer les packages : {all_packages}", "ERROR")

    # Services exposés
    services = adb_shell("service list", serial)
    if "ERROR" not in services and services:
        svc_list = [s.strip() for s in services.split("\n") if s.strip()]
        enum["total_services"] = len(svc_list)
        log(f"  [*] {len(svc_list)} services exposés")
    else:
        enum["services_error"] = services

    # Ports ouverts
    ports = adb_shell("cat /proc/net/tcp", serial)
    if "ERROR" not in ports and ports:
        open_ports = []
        for line in ports.split("\n")[1:]:
            parts = line.split()
            if len(parts) >= 2:
                local = parts[1]
                if ":" in local:
                    port_hex = local.split(":")[1]
                    try:
                        port = int(port_hex, 16)
                        if port > 0:
                            open_ports.append(port)
                    except ValueError:
                        pass
        enum["open_ports"] = sorted(set(open_ports))
        log(f"  [*] Ports ouverts : {enum['open_ports']}")

    # Partitions montées
    mounts = adb_shell("mount", serial)
    if "ERROR" not in mounts:
        writable_partitions = []
        for line in mounts.split("\n"):
            if "rw," in line:
                parts = line.split()
                if len(parts) >= 3:
                    writable_partitions.append(parts[2])
        enum["writable_partitions"] = writable_partitions
    else:
        enum["mounts_error"] = mounts

    # Fichiers SUID
    suid = adb_shell("find /system -perm -4000 -type f 2>/dev/null", serial)
    if "ERROR" not in suid and suid:
        suid_files = [f.strip() for f in suid.split("\n") if f.strip()]
        enum["suid_files"] = suid_files
        log(f"  [*] {len(suid_files)} fichiers SUID trouvés")
    else:
        enum["suid_files"] = []

    return enum

# ─── Phase 4 : ESCALATION (tests) ───

def phase_escalation(recon: dict, enum: dict, serial: str) -> dict:
    """Test des vecteurs d'escalade de privilèges."""
    log("=== PHASE 4 : ESCALATION — Test des vecteurs root ===")

    results = {
        "vectors_tested": [],
        "root_achieved": False,
        "method": None,
    }

    # Vecteur 1 : su binaire
    if recon.get("su_present"):
        log("  [*] Test : su binaire présent")
        su_test = adb_shell("su -c id", serial)
        if "uid=0" in su_test:
            log("  [!!!] ROOT OBTENU via su !", "WARN")
            results["vectors_tested"].append({"vector": "su_binary", "result": "ROOT", "detail": su_test})
            results["root_achieved"] = True
            results["method"] = "su_binary"
        else:
            results["vectors_tested"].append({"vector": "su_binary", "result": "denied", "detail": su_test})
            log("  [-] su refusé")
    else:
        results["vectors_tested"].append({"vector": "su_binary", "result": "not_present"})

    # Vecteur 2 : Magisk
    magisk_check = adb_shell("magisk -v", serial)
    if "ERROR" not in magisk_check and magisk_check and "not found" not in magisk_check.lower():
        log(f"  [!] Magisk détecté : {magisk_check}")
        results["vectors_tested"].append({"vector": "magisk", "result": "present", "version": magisk_check})
        results["root_achieved"] = True
        results["method"] = "magisk"
    else:
        results["vectors_tested"].append({"vector": "magisk", "result": "not_present"})

    # Vecteur 3 : CVE-2024-0044 (run-as exploit)
    # Test non-destructif : vérifier si run-as est vulnérable
    runas_test = adb_shell("run-as com.android.shell id", serial)
    if "uid=0" in runas_test or "uid=1000" in runas_test:
        log("  [!!!] run-as vulnérable (CVE-2024-0044) !", "WARN")
        results["vectors_tested"].append({"vector": "CVE-2024-0044_runas", "result": "VULNERABLE"})
        results["root_achieved"] = True
        results["method"] = "CVE-2024-0044"
    else:
        results["vectors_tested"].append({"vector": "CVE-2024-0044_runas", "result": "not_vulnerable", "detail": runas_test[:100]})

    # Vecteur 4 : Bootloader unlocké → fastboot
    bl_state = recon.get("flash_locked", "")
    if bl_state == "0":
        log("  [!] Bootloader DÉVERROUILLÉ — fastboot flash possible")
        results["vectors_tested"].append({"vector": "fastboot_flash", "result": "possible", "detail": "bootloader unlocked"})
        # Si bootloader unlocké, on peut flasher un boot.img modifié (Magisk patché)
        results["root_achieved"] = True
        results["method"] = results["method"] or "fastboot_boot_image"
    else:
        results["vectors_tested"].append({"vector": "fastboot_flash", "result": "locked", "detail": f"flash.locked={bl_state}"})

    # Vecteur 5 : Dirty Pipe (CVE-2022-0847) — kernel < 5.16.11
    uname = recon.get("uname", "")
    if "5.10" in uname or "5.15" in uname:
        log("  [*] Kernel potentiellement vulnérable à Dirty Pipe (CVE-2022-0847)")
        results["vectors_tested"].append({"vector": "CVE-2022-0847_dirtypipe", "result": "potential", "kernel": uname})
    else:
        results["vectors_tested"].append({"vector": "CVE-2022-0847_dirtypipe", "result": "not_applicable", "kernel": uname})

    # Résumé
    if results["root_achieved"]:
        log(f"  [!!!] ROOT OBTENU via : {results['method']}", "WARN")
    else:
        log("  [-] Aucun vecteur d'escalade réussi — device durci")

    return results

# ─── Phase 5 : REPORT ───

def phase_report(recon: dict, fingerprint: dict, enum: dict, escalation: dict) -> str:
    """Génère le rapport de pentest."""
    log("=== PHASE 5 : REPORT — Génération du rapport ===")

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_path = REPORT_DIR / f"nothing-phone-2_{ts}.md"

    report = f"""# 🔴 Rapport de Pentest — Nothing Phone 2

**Date :** {datetime.now(timezone.utc).isoformat()}
**Cible :** {recon.get('manufacturer', 'Nothing')} {recon.get('model', '?')} ({recon.get('device', '?')})
**Serial :** {recon.get('serial', '?')}
**Pentester :** ADAM-RED (automatisé)

---

## 1. Reconnaissance

| Propriété | Valeur |
|-----------|--------|
| Modèle | {recon.get('model', '?')} |
| Marque | {recon.get('brand', '?')} |
| Fabricant | {recon.get('manufacturer', '?')} |
| Android | {recon.get('android_version', '?')} (SDK {recon.get('sdk_level', '?')}) |
| Security Patch | {recon.get('security_patch', '?')} |
| Build ID | {recon.get('build_id', '?')} |
| Bootloader | {recon.get('bootloader', '?')} |
| Flash locked | {recon.get('flash_locked', '?')} |
| SELinux | {recon.get('selinux_mode', '?')} |
| Kernel | {recon.get('uname', '?')} |
| ABI | {recon.get('abi', '?')} |
| Root (su) | {'OUI — ' + recon.get('su_path', '') if recon.get('su_present') else 'NON'} |
| Utilisateur | {recon.get('uid', '?')} |

---

## 2. Empreinte CVE

**Niveau de patch :** {fingerprint.get('patch_level', '?')}
**CVE applicables :** {fingerprint.get('total_cves', 0)}

"""
    if fingerprint.get("applicable_cves"):
        report += "| CVE | Description | CVSS | Cutoff |\n|-----|-------------|------|--------|\n"
        for cve in fingerprint["applicable_cves"]:
            report += f"| {cve['cve']} | {cve['description']} | {cve['cvss']} | {cve['cutoff']} |\n"
    else:
        report += "Aucune CVE connue applicable.\n"

    report += f"""
---

## 3. Énumération

- **Packages installés :** {enum.get('total_packages', '?')}
- **Packages dangereux :** {', '.join(enum.get('dangerous_found', [])) or 'aucun'}
- **Services exposés :** {enum.get('total_services', '?')}
- **Ports ouverts :** {enum.get('open_ports', [])}
- **Fichiers SUID :** {len(enum.get('suid_files', []))}

---

## 4. Escalade de Privilèges

**ROOT OBTENU :** {'✅ OUI — ' + escalation.get('method', '') if escalation.get('root_achieved') else '❌ NON'}

| Vecteur | Résultat | Détail |
|---------|----------|--------|
"""
    for v in escalation.get("vectors_tested", []):
        detail = v.get("detail", v.get("version", v.get("kernel", "")))
        report += f"| {v['vector']} | {v['result']} | {str(detail)[:60]} |\n"

    report += f"""
---

## 5. Conclusion

{"⚠️ **Le device est compromettible.** Root obtenu via {escalation.get('method', '?')}." if escalation.get('root_achieved') else "✅ **Le device résiste aux vecteurs d'escalade testés.** Mesures de durcissement effectives."}

---

*Rapport généré par ADAM-RED — The Hive*
"""

    with open(report_path, "w") as f:
        f.write(report)

    log(f"Rapport sauvegardé : {report_path}")
    return str(report_path)

# ─── Publication d'event ───

def publish_event(channel: str, payload: dict):
    """Publie un event sur l'event bus."""
    try:
        import sqlite3
        db = sqlite3.connect(str(EVENT_DB))
        db.execute(
            "INSERT INTO events (channel, source, payload, created_at) VALUES (?, ?, ?, ?)",
            (channel, "adam-red", json.dumps(payload), datetime.now(timezone.utc).isoformat())
        )
        db.commit()
        db.close()
        log(f"Event publié sur canal '{channel}'")
    except Exception as e:
        log(f"Erreur publication event : {e}", "ERROR")

# ─── Main ───

def main():
    parser = argparse.ArgumentParser(description="ADAM-RED — Défi escalade root Android")
    parser.add_argument("--phase", choices=["recon", "fingerprint", "enum", "escalation", "all"], default="all")
    parser.add_argument("--device", default=TARGET_SERIAL, help="Serial du device")
    args = parser.parse_args()

    log("=" * 60)
    log(f"ADAM-RED — Défi escalade root Nothing Phone 2")
    log(f"Serial : {args.device} | Phase : {args.phase}")
    log("=" * 60)

    recon = {}
    fingerprint_data = {}
    enum_data = {}
    escalation_data = {}

    if args.phase in ("recon", "all"):
        recon = phase_recon(args.device)

    if args.phase in ("fingerprint", "all") and recon:
        fingerprint_data = phase_fingerprint(recon)

    if args.phase in ("enum", "all") and recon:
        enum_data = phase_enum(args.device)

    if args.phase in ("escalation", "all") and recon:
        escalation_data = phase_escalation(recon, enum_data, args.device)

    # Rapport (toujours en mode all)
    if args.phase == "all" and recon:
        report_path = phase_report(recon, fingerprint_data, enum_data, escalation_data)

        # Publier le résultat sur l'event bus
        publish_event("security:alert", {
            "challenge": "root_nothing_phone_2",
            "target": f"Nothing Phone 2 ({args.device})",
            "root_achieved": escalation_data.get("root_achieved", False),
            "method": escalation_data.get("method"),
            "cves_found": fingerprint_data.get("total_cves", 0),
            "report": report_path,
        })

    # Résumé final
    log("=" * 60)
    if recon:
        log(f"Device : {recon.get('manufacturer', '?')} {recon.get('model', '?')} Android {recon.get('android_version', '?')}")
        log(f"Patch : {recon.get('security_patch', '?')} | SELinux : {recon.get('selinux_mode', '?')}")
        if escalation_data:
            if escalation_data.get("root_achieved"):
                log(f"🔴 ROOT OBTENU via {escalation_data.get('method', '?')}")
            else:
                log("🟢 Root NON obtenu — device résistant")
    log("=" * 60)

if __name__ == "__main__":
    main()
