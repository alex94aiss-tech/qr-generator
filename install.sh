#!/bin/bash
# QR Generator — Installer for Linux/Ubuntu

set -e

echo ""
echo "═══════════════════════════════════════════════"
echo " QR Generator — Installer (Linux/Ubuntu)"
echo "═══════════════════════════════════════════════"
echo ""

# Переход в каталог установки
cd "$(dirname "$0")"

# 1. Проверка Python
echo "[1/4] Проверка Python..."
if ! command -v python3 &>/dev/null; then
    echo "✘ Python3 не найден. Установите: sudo apt install python3"
    exit 1
fi
echo "✔ Python3 найден: $(python3 --version)"

# 2. Установка зависимостей
echo ""
echo "[2/4] Установка зависимостей (qrcode + Pillow)..."
echo ""

# Установка pip если нужен
python3 -m pip install --quiet --upgrade pip 2>/dev/null || true

# Установка qrcode[pil]
python3 -m pip install --quiet "qrcode[pil]"

echo "✔ Зависимости установлены"

# 3. Проверка работоспособности
echo ""
echo "[3/4] Проверка работоспособности..."
echo ""

python3 -c "import qrcode; from PIL import Image; print('✔ Библиотеки работают')" 2>/dev/null

# 4. Настройка
echo ""
echo "[4/4] Готово!"
echo ""

echo ""
echo "═══════════════════════════════════════════════"
echo " Установка завершена!"
echo "═══════════════════════════════════════════════"
echo ""
echo "Запуск:"
echo "  python3 QR_Generator.py --url https://stasys.com.ua --print"
echo ""
echo "Или добавьте в PATH для запуска из любой директории:"
echo "  sudo cp QR_Generator.py /usr/local/bin/qr-gen"
echo "  sudo chmod +x /usr/local/bin/qr-gen"
echo ""
