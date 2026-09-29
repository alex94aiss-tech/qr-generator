# QR Generator

Генератор QR-кодів: URL, телефон, email, Wi-Fi, текст. Виводить ASCII у термінал і зберігає PNG із заголовком. Підтримує друк.

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

### Встановлення з GitHub

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

## Конфігурація (config.json)

Скрипт підтримує конфігураційний файл `config.json` для типових налаштувань (за замовчуванням — для СТАСИС).

### За замовчуванням (config.json)
- **URL:** https://stasys.com.ua
- **Caption:** "СТАСИС — ПрАТ Стабільні системи"
- **Папір:** 100×100 мм (medium)
- **Телефон:** +380****3815
- **Email:** stasys94@ukr.net
- **Wi-Fi:** STSIS (WPA, пароль порожній)

### Використання конфігу
```bash
# Використати config.json (за замовчуванням, якщо файл існує)
python QR_Generator.py --type url --print

# Вказати інший файл конфігу
python QR_Generator.py --config my_config.json --type tel --print

# Ігнорувати конфіг і використовувати тільки аргументи
python QR_Generator.py --no-config --type tel --phone +380****1234
```

### Перекриття конфігу аргументами
Будь-який аргумент командного рядка перекриває відповідне поле в config.json:
```bash
# Конфіг каже URL: https://stasys.com.ua, але ми перезаписуємо
python QR_Generator.py --url https://example.com --type url --print
```

## Оновлення скрипта

Скрипт підтримує самооновлення з GitHub Gist:

```bash
# Оновлення з підтвердженням
python QR_Generator.py --update

# Оновлення без запиту (з розширенням резервної копії .py.bak)
python QR_Generator.py --update-force
```

### Структура config.json
```json
{
  "defaults": {
    "url": "https://stasys.com.ua",
    "caption": "СТАСИС — ПрАТ Стабільні системи",
    "paper_size": "medium",
    "paper_mm": 100,
    "error_correction": "M",
    "border": 4,
    "font_size": 28,
    "caption_align": "center",
    "caption_color": "black"
  },
  "types": {
    "url": { "caption": "...", "url": "..." },
    "tel": { "caption": "...", "phone": "+380..." },
    "mailto": { "caption": "...", "email": "..." },
    "wifi": { "caption": "...", "wifi_ssid": "...", "wifi_pass": "...", "wifi_sec": "WPA" },
    "text": { "caption": "...", "text": "..." }
  }
}
```

## Типи QR-кодів

Скрипт підтримує 5 типів QR-кодів:

| Тип | Опції | Приклад |
|-----|-------|---------|
| **url** (замовчування) | `--url` | `python QR_Generator.py --url https://stasys.com.ua` |
| **tel** | `--phone` | `python QR_Generator.py --type tel --phone +380671234567` |
| **mailto** | `--email` | `python QR_Generator.py --type mailto --email stasys94@ukr.net` |
| **wifi** | `--wifi-ssid`, `--wifi-pass`, `--wifi-sec` | `python QR_Generator.py --type wifi --wifi-ssid STSIS --wifi-pass пароль` |
| **text** | `--text` | `python QR_Generator.py --type text --text "Привіт, світ!"` |

## Використання

### URL (за замовчуванням)
```bash
python QR_Generator.py https://example.com
```
Скрипт запитає URL, якщо його не передати в командному рядку.

### З параметрами
```bash
python QR_Generator.py --url https://example.com --output my_qr.png
```

### Телефон
```bash
python QR_Generator.py --type tel --phone +380671234567 --print
```

### Email
```bash
python QR_Generator.py --type mailto --email stasys94@ukr.net --print
```

### Wi-Fi
```bash
python QR_Generator.py --type wifi --wifi-ssid STSIS --wifi-pass прихильник [--wifi-sec WPA] --print
```
Підтримує WPA (замовчування), WEP, nopass (відкрита мережа).

### Текст
```bash
python QR_Generator.py --type text --text "Привіт, світ!" --print
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
| `--caption-text` | Текст надпису (за замовчуванням — дані) | дані |
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
| `--type`, `-t` | Тип QR: **url**, **tel**, **mailto**, **wifi**, **text** | url |
| `--url`, `-u` | URL (для типу url) | - |
| `--phone` | Номер телефону (для типу tel, наприклад +380671234567) | - |
| `--email` | Email (для типу mailto) | - |
| `--wifi-ssid` | SSID Wi-Fi мережі (для типу wifi) | - |
| `--wifi-pass` | Пароль Wi-Fi мережі (для типу wifi) | - |
| `--wifi-sec` | Безпека Wi-Fi: **WPA**, **WEP**, **nopass** | WPA |
| `--text` | Вільний текст (для типу text) | - |
| `--output`, `-o` | Шлях для PNG | `qr_<safe_name>.png` |
| `--error-correction`, `-e` | Рівень: **L** (7%), **M** (15%), **Q** (25%), **H** (30%) | M |
| `--box-size`, `-b` | Розмір боксу | 10 |
| `--border`, `-r` | Розмір кордону | 4 |
| `--no-ascii` | Не виводити ASCII в термінал | False |
|| `--print`, `-p` | Повідомлення для друку | False |
|| `--batch` | Файл з URL-ами (по одному в рядку) для масової генерації | - |
|| `--output-dir` | Папка для збереження QR-кодів | поточна |
|| `--name-as-filename` | Використовувати назву з файлу як ім'я файлу PNG | False |
|| `--config` | Шлях до config.json | config.json |
|| `--no-config` | Ігнорувати config.json | False |
|| `--update` | Оновити скрипт з GitHub Gist (з підтвердженням) | - |
|| `--update-force` | Оновити скрипт з GitHub Gist без запиту | - |

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

# Телефон
python QR_Generator.py --type tel --phone +380671234567 --print

# Email
python QR_Generator.py --type mailto --email stasys94@ukr.net --print

# Wi-Fi
python QR_Generator.py --type wifi --wifi-ssid STSIS --wifi-pass прихильник --print

# Текст
python QR_Generator.py --type text --text "Привіт, світ!" --print

# Ручний текст надпису
python QR_Generator.py --url https://stasys.com.ua --caption-text "СТАСИС — стабільні системи" --output stasys_qr.png

# Оновлення скрипта з Gist
python QR_Generator.py --update
```

## Вивід
Скрипт:
1. Генерує PNG-файл з QR-кодом (включно з надписом зверху)
2. Виводить ASCII-представлення в терміналі
3. Якщо вказано `--print` — повідомляє розмір паперу і QR-коду для друку

## Джерела
- **Репозиторій:** https://github.com/alex94aiss-tech/qr-generator
- **Gist (тільки скрипт):** https://gist.github.com/alex94aiss-tech/fa1c010144389eba70b38d4bd849e6b3

## Ліцензія
MIT
