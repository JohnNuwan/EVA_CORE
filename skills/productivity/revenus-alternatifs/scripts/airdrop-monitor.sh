#!/bin/bash
# Airdrop Monitor E.V.A — script watchdog pour cron (no_agent=True)
# Silencieux si rien de nouveau, alerte si nouveaux protocoles détectés
# À placer dans ~/.hermes/scripts/

cd /home/aza/revenus-alternatifs/airdrop || exit 1

OUTPUT=$(uv run --with requests,web3 python3 airdrop_bot.py --check 2>&1)

if echo "$OUTPUT" | grep -q "NOUVEAUX PROTOCOLES"; then
    echo "=== Airdrop Monitor E.V.A ==="
    echo "$OUTPUT"
fi
# Si aucun nouveau protocole : sortie silencieuse (exit 0)