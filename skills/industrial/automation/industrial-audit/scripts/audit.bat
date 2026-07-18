@echo off
set ROOT_DIR=%~dp0..\..\..\..\..\
cd /d "%ROOT_DIR%"

color 0A
echo ========================================================
echo       LANCEMENT DE L'AUDIT INDUSTRIEL EPH
echo ========================================================

:: Creation du timestamp une seule fois au debut (Format: YYYY-MM-DD_HH)
for /f "usebackq tokens=*" %%I in (`powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd_HH'"`) do set TIMESTAMP=%%I
set OUTPUT_PATH=output\audit\%TIMESTAMP%\audit_report.md

echo.
echo Activation de l'environnement virtuel...
if exist .\.venv\Scripts\activate.bat (
    call .\.venv\Scripts\activate.bat
) else (
    call .\venv\Scripts\activate.bat
)

:loop
echo Execution du script Python (Dossier : %TIMESTAMP%)...
python skills\industrial\automation\industrial-audit\scripts\audit_pdf.py --time-limit 240 --output "%OUTPUT_PATH%" %*

if errorlevel 100 if not errorlevel 101 (
    echo.
    echo ========================================================
    echo   Temps limite atteint. Sauvegarde automatique reussie.
    echo   Pause de 5 secondes avant reprise - dossier %TIMESTAMP%...
    echo ========================================================
    ping 127.0.0.1 -n 6 >nul
    goto loop
)

echo.
echo ========================================================
echo L'audit est termine. La fenetre va se fermer automatiquement.
ping 127.0.0.1 -n 10 >nul
