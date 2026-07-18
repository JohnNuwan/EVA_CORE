#!/bin/bash
# install_mt5.sh — Installation complète MT5 sous Wine
# Usage: sudo bash install_mt5.sh

set -e

echo "=== Installation Wine ==="
dpkg --add-architecture i386
apt update
apt install -y wine64 wine32:i386 winetricks xvfb

echo "=== Création préfixe Wine ==="
export WINEPREFIX=/home/$SUDO_USER/.wine_mt5
mkdir -p "$WINEPREFIX"
chown -R $SUDO_USER:$SUDO_USER "$WINEPREFIX"

echo "=== Téléchargement MT5 ==="
sudo -u $SUDO_USER mkdir -p /home/$SUDO_USER/mt5_setup
cd /home/$SUDO_USER/mt5_setup

if [ ! -f mt5setup.exe ]; then
    sudo -u $SUDO_USER wget -q "https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe"
fi

echo "=== Installation MT5 ==="
sudo -u $SUDO_USER WINEPREFIX="$WINEPREFIX" xvfb-run -a wine mt5setup.exe /auto || true

echo "=== Vérification ==="
MT5_PATH=$(sudo -u $SUDO_USER find "$WINEPREFIX" -name "terminal64.exe" 2>/dev/null | head -1)
if [ -n "$MT5_PATH" ]; then
    echo "✅ MT5 installé: $MT5_PATH"
else
    echo "❌ MT5 non trouvé"
    exit 1
fi

echo "=== Installation Python Windows ==="
sudo -u $SUDO_USER wget -q "https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe" -O python-installer.exe
sudo -u $SUDO_USER WINEPREFIX="$WINEPREFIX" xvfb-run -a wine python-installer.exe /quiet InstallAllUsers=0 PrependPath=1 || true

sleep 10

WIN_PYTHON="$WINEPREFIX/drive_c/users/$SUDO_USER/AppData/Local/Programs/Python/Python312/python.exe"
if [ -f "$WIN_PYTHON" ]; then
    echo "=== Installation packages Python ==="
    sudo -u $SUDO_USER WINEPREFIX="$WINEPREFIX" xvfb-run -a wine "$WIN_PYTHON" -m pip install MetaTrader5 pandas pyarrow "numpy<2.0"
    echo "✅ Python Windows installé"
else
    echo "⚠️ Python Windows non trouvé, installez manuellement"
fi

echo ""
echo "=== Installation terminée ==="
echo "Pour lancer MT5:"
echo "  WINEPREFIX=~/.wine_mt5 xvfb-run -a wine '$MT5_PATH'"
