# QR Generator

Простий Python-скрипт для генерації QR-кодів з URL. Виводить QR-код у термінал (ASCII) і зберігає як PNG-файл. Підтримує друк.

## Встановлення

### Автоматично (рекомендовано)

#### Windows
Запустіть `install.bat` подвійним кліком або з командного рядка:
```bat
install.bat
```

#### Ubuntu / Linux
Запустіть `install.sh`:
```bash
chmod +x install.sh
./install.sh
```

### Вручну

#### Вимоги
- Python 3.8+
- pip (менеджер пакетів Python)

#### Windows
```bat
python -m pip install "qrcode[pil]"
```

#### Ubuntu / Linux
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
python3 -m pip install --user "qrcode[pil]"
```

> **Примітка:** На Ubuntu може знадобитися `python3-tk` для деяких функцій Pillow:
> ```bash
> sudo apt install python3-tk -y
> ```

## Встановлення з GitHub

### Варіант 1 — однією командою (рекомендовано)
```bash
# Windows
powershell -Command "Invoke-WebRequest -Uri https://raw.githubusercontent.com/alex94aiss-tech/qr-generator/main/install.bat -OutFile install.bat; install.bat"

# Ubuntu / Linux
curl -sL https://raw.githubusercontent.com/alex94aiss-tech/qr-generator/main/install.sh | bash
```

### Варіант 2 — через git (повна версія з документацією)
```bash
git clone https://github.com/alex94aiss-tech/qr-generator.git
cd qr-generator
# Windows:
install.bat
# Ubuntu / Linux:
chmod +x install.sh && ./install.sh
```

### Варіант 3 — через GitHub Gist (тільки скрипт)
```bash
# Завантажити тільки QR_Generator.py з Gist
curl -sL https://gist.githubusercontent.com/alex94aiss-tech/fa1c010144389eba70b38d4bd849e6b3/raw/QR_Generator.py -o QR_Generator.py

# Встановити залежності вручну
pip install "qrcode[pil]"

# Запуск
python QR_Generator.py --url https://stasys.com.ua --print --paper-size medium
```

> Gist містить тільки основний скрипт (`QR_Generator.py`). Встановники `install.bat`/`install.sh`, DEV-нотатки, README і історія — в репозиторії: https://github.com/alex94aiss-tech/qr-generator

## Використання

### Базове

```bash
python QR_Generator.py https://example.com
```

Скрипт запитає URL, якщо його не передати в командному рядку.

### З параметрами

```bash
python QR_Generator.py --url https://example.com --output my_qr.png
```

### Друк (папір 100×100 мм)

```bash
python QR_Generator.py --url https://example.com --print --paper-size medium
```

За замовчуванням `--paper-size medium` дає QR-код ≈70×70 мм на папері 100×100 мм.
З надписом URL зверху (можна змінити через `--caption-text` та `--caption-align`).

### Нові опції (розмір паперу + надпис)

| Опція | Опис | Типово |
|-------|------|--------|
| `--paper-size` | Розмір паперу: **small**(80mm) **medium**(100mm) **large**(150mm) **a4**(210mm) **custom** | medium |
| `--custom-mm` | Сторона квадратного паперу в мм (для custom) | — |
| `--caption` | Додати надпис (за замовчуванням УВІМК) | True |
| `--no-caption` | Без надпису | — |
| `--caption-text` | Текст надпису (за замовчуванням — URL) | URL |
| `--caption-align` | Вирівнювання: **left** / **center** / **right** | center |
| `--caption-color` | Колір тексту | black |
| `--font-size` | Розмір шрифту надпису (пункти) | 28 |

### Повна довідка

```bash
python QR_Generator.py --help
```

## Аргументи

| Аргумент | Опис | Типово |
|----------|------|-------|
| `--url`, `-u` | URL для QR-коду | - |
| `--output`, `-o` | Шлях для PNG | `qr_<safe_name>.png` |
| `--error-correction`, `-e` | Рівень: **L** (7%), **M** (15%), **Q** (25%), **H** (30%) | M |
| `--box-size`, `-b` | Розмір боксу | 10 |
| `--border`, `-r` | Розмір кордону | 4 |
| `--no-ascii` | Не виводити ASCII в термінал | False |
| `--print`, `-p` | Повідомлення для друку | False |

## Приклади

```bash
# Базова генерація
python QR_Generator.py https://stasys.com.ua

# З високим рівнем корекції
python QR_Generator.py --url https://example.com --error-correction H --box-size 15

# Лише PNG, без ASCII
python QR_Generator.py --url https://example.com --no-ascii --output qr.png

# З друком
python QR_Generator.py --url https://example.com --print
```

## Ви출력

Скрипт:
1. Генерує PNG-файл з QR-кодом
2. Виводить ASCII-представлення в терміналі
3. Якщо вказано `--print` — повідомляє про можливість друку

## Ліцензія

MIT

---

## GitHub Gist (швидкий доступ до скрипта)

Якщо потрібно швидко викачати тільки `QR_Generator.py` без всього репозиторію:

🔗 https://gist.github.com/alex94aiss-tech/fa1c010144389eba70b38d4bd849e6b3

Там же знаходиться оновлений скрипт — достатньо перейти за посиланням і натиснути **Raw** (або **Download**).

> Повна версія з встановниками, документацією і DEV-нотатками — в репозиторії: https://github.com/alex94aiss-tech/qr-generator
