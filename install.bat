@echo off
:: QR Generator - Installer for Windows
:: Installs dependencies and sets up environment

chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

echo.
echo ==================================================
echo  QR Generator - Installer (Windows)
echo ==================================================
echo.

:: Switch to installer directory
cd /d "%~dp0"

:: 1. Check Python
echo [1/4] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install from https://python.org
    echo.
    pause
    exit /b 1
)
echo [OK] Python found

:: 2. Install dependencies
echo.
echo [2/4] Installing dependencies (qrcode + Pillow)...
echo.

python -m pip install --quiet --upgrade pip
python -m pip install --quiet "qrcode[pil]"

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    echo.
    pause
    exit /b 1
)
echo [OK] Dependencies installed

:: 3. Test installation
echo.
echo [3/4] Testing installation...
echo.

python -c "import qrcode; from PIL import Image; print('[OK] Libraries work')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Failed to import libraries.
    echo.
    pause
    exit /b 1
)

:: 4. Done
echo.
echo [4/4] Done!
echo.

echo.
echo ==================================================
echo  Installation complete!
echo ==================================================
echo.
echo Run:
echo   python QR_Generator.py --url https://stasys.com.ua --print
echo.
echo Or create a desktop shortcut for convenience.
echo.
pause
