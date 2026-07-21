#!/usr/bin/env python3
"""Script utilitaire pour OverTheWire Bandit — connexion rapide à n'importe quel niveau."""
import subprocess, sys, os

HOST = "bandit.labs.overthewire.org"
PORT = 2220

PASSWORDS = {
    0: "bandit0",
    1: "6y2kwnwK6grgvwvpvLaa2T1cpFEKOhNR",
    2: "PK8fYLZg2hnHSz83plBL1iEPKdD3QToB",
    3: "7ZZ2LFrykP2zEyvBl4m3clcL7tGYJPME",
    4: "xzTXq1rDJQVVAzdv5cHq1TQytTWufAMq",
    5: "6C7h9GD8M6ai5nr7wo1RonrzFjj9yIrG",
    6: "pXa26xhMWaC2SvDotA4r9EgZkulOeSBW",
    7: "Bmnnvf82KzQlfxgAI2d1zYbr1u9pr3E3",
    8: "VR1ljMayciFxbnUokuQmJFw6QC9VKtub",
    9: "EjmOSvuAu7sGAHqHVcBDPirRe9T03kxl",
    10: "B0s2khmbT9u0geKuOoVGW3JZKhndE3BG",
    11: "pYfOY6HwUsDj5rL9UvyhU7MCmv8vN5Ro",
    12: "GROozWPO8QyN0mGrjUkID0WCYkZiQxrN",
    13: "qQYQiHOBPR8zR61qxYqX45quvihF2uzk",
    14: "aaWecNkG4FhxJQxz07uiwzVP6bJiYS65",
    15: "pbLYuZtTg4MgaqfJx8jbA9gKKGqM68A7",
    16: "kS0Hf0u5HiXFwKMKFqXvPdOTNGGa0X8V",
    17: "pWXMAZoxGC8JmDMfmT5MGEsobMM3vnj2",
    18: "OQxXZjELndr90zuhOTDYBEomI0SZITXI",
    19: "KpsOfPkcP7i1FlIExk2QEjyt6dw8dxZI",
    20: "4pIjcunZ0fK2vmp3IwfG8Vf7VhxD6pOA",
    21: "bW9kBv5WC3P4yoDyf12LSdGuNz5ka6hY",
    22: "RYVux2rHEm9tiXHmLFzuR7Vhx6AZQMEz",
}

def run(level, cmd=""):
    pw = PASSWORDS.get(level)
    if not pw:
        print(f"Mot de passe pour niveau {level} inconnu")
        sys.exit(1)
    
    ssh_cmd = [
        "sshpass", "-p", pw,
        "ssh", "-o", "StrictHostKeyChecking=no",
        f"bandit{level}@{HOST}", "-p", str(PORT)
    ]
    
    if cmd:
        ssh_cmd.append(cmd)
    
    r = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
    # Filter out the banner
    lines = r.stdout.split('\n')
    content = '\n'.join(line for line in lines if line and 'bandit' not in line.lower() and 'overthewire' not in line.lower() and 'backend' not in line.lower() and 'This is an' not in line.lower() and 'More information' not in line.lower() and '####' not in line.lower() and '|' not in line.lower())
    # Just return the last meaningful lines
    meaningful = [l for l in lines if l.strip() and not l.startswith('_') and 'bandit' not in l.lower()[:20] and 'overthewire' not in l.lower() and 'backend' not in l.lower()]
    print('\n'.join(meaningful[-10:]) if meaningful else r.stdout)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: bandit.py <level> [command]")
        sys.exit(1)
    level = int(sys.argv[1])
    cmd = sys.argv[2] if len(sys.argv) > 2 else ""
    run(level, cmd)