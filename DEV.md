# DEV · Внутрішня документація QR Generator

> Для розробника. Як зрозуміти проект, якщо треба щось змінити/додати.

---

## 1. Структура проекту

```
qr-generator/
├── QR_Generator.py     # Головний скрипт (CLI)
├── README.md           # Користувацька документація (публічна)
├── LICENSE             # MIT
├── DEV.md              # Цей файл — внутрішня документація
├── install.bat         # Встановник для Windows (подвійний клік або cmd)
├── install.sh          # Встановник для Linux/Ubuntu (bash)
└── .git/               # Git-репозиторій
```

---

## 2. Залежності

| Пакет | Призначення | Встановлення |
|-------|-------------|--------------|
| `qrcode` | Генерація QR-кодів | `pip install qrcode[pil]` |
| `Pillow` (PIL) | Робота з PNG-зображеннями + drawing тексту | автоматично з `qrcode[pil]` |

**Дві версії Python:**
- Системний `python` (3.14.7, шлях: `C:\Users\Admin\AppData\Local\hermes\tools\python-3.14.7+…\python.exe`) — **основний**, треба встановлювати пакети сюди.
- venv Hermes (`C:\Users\Admin\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`) — **резервний**, qrcode встановлена тільки тут.

> ⚠️ Якщо `import qrcode` не працює — встанови в системний Python: `python -m pip install qrcode[pil]`.

---

## 3. Архітектура скрипта

```
main()
  ├─ argparse — парсинг CLI-аргументів (--url, --paper-size, --caption, ...)
  ├─ input() — запит URL вручну, якщо не вказано в аргументах
  └─ generate_qr()
       ├─ Визначення розміру паперу (get_paper_config)
       ├─ Обчислення box_size: mm_to_px(qr_side_mm) // (safe_version + border*2)
       ├─ Створення QRCode (версія auto, рівень корекції, box_size, border)
       ├─ Додавання даних (URL)
       ├─ make_image(fill_color="black", back_color="white") → "1" (1-bit)
       ├─ Конвертація в RGB: img.convert("RGB")
       ├─ add_caption_to_image()  ← текст URL зверху
       │     ├─ Canvas RGB (ширина img.w, висота img.h + caption_height)
       │     ├─ Paste QR-коду вниз
       │     ├─ Truetype шрифт (arial → DejaVu → default)
       │     └─ draw.text() — текст
       ├─ save(path) — PNG
       └─ print_ascii() — ASCII в термінал (окремий QR без caption)
```

**Рівні паперу (PAPER_SIZES):**
| Ключ | Папір (мм) | QR-сторона (мм) |
|------|------------|------------------|
| small | 80×80 | 50 |
| medium | 100×100 | 70 | ← типово |
| large | 150×150 | 110 |
| a4 | 210×210 | 160 |

Мінімальний QR-код — 20×20 мм (безпека пристрою).

---

## 4. CLI-інтерфейс

| Флаг | Тип | Типово | Опис |
|------|-----|--------|------|
| `--url`, `-u` | str | (ввід) | URL для QR-коду |
| `--output`, `-o` | str | `qr_<safe>.png` | Шлях до PNG |
| `--error-correction`, `-e` | L/M/Q/H | M | Рівень корекції |
| `--box-size`, `-b` | int | None (авто) | Розмір боксу |
| `--border`, `-r` | int | 4 | Кордон (модулі) |
| `--paper-size` | small/medium/large/a4/custom | **medium** | Розмір паперу |
| `--custom-mm` | float | None | Сторона паперу в мм (custom) |
| `--no-caption` | flag | False | Виключити надпис |
| `--caption` | flag | True | Додати надпис (за замовчуванням) |
| `--caption-text` | str | URL | Текст надпису |
| `--caption-align` | left/center/right | center | Вирівнювання |
| `--caption-color` | str | black | Колір тексту |
| `--font-size` | int | 28 | Розмір шрифту надпису |
| `--no-ascii` | flag | False | Виключити ASCII |
| `--print`, `-p` | flag | False | Повідомлення для друку |

---

## 5. Можливі напрями розширення

### 5.1 Види QR-кодів більше ніж URL
Наразі скрипт очікує URL і нормалізує його до `https://...`. Можна розширити:
- Підтримка телефонів: `tel:+380...`
- Підтримка тексту: `--type text`
- Підтримка відбитків електронної пошти: `mailto:`
- Wi-Fi QR: `WIFI:S:SSID;T:WPA;P:password;;`

### 5.2 Формати виводу
- SVG (краща якість для друку)
- EPS
- Інтерактивне SVG з URL-результатом

### 5.3 Інтеграції
- Генерація кількох QR одночасно (із файлу/CSV)
- Вбудована генерація для внутрішніх посилань СТАСИС
- Відправка на друк через системний принтер (Windows: `win32print`)

### 5.4 GUI
- Tkinter / Qt — графічний інтерфейс для не-технічних користувачів

---

## 6. Процес оновлення

```bash
# 1. Змінити код
# 2. Тестувати локально
python QR_Generator.py --url https://example.com --output test.png --no-ascii

# 3. Commit + push на GitHub
git add QR_Generator.py
git commit -m "Опис змін"
git push origin main
```

**Тестові URL для перевірки:**
- `https://stasys.com.ua`
- `https://example.com`
- `https://github.com/alex94aiss-tech/qr-generator`

**Тестові сценарії:**
```bash
# Типовий (100мм + caption)
python QR_Generator.py --url https://stasys.com.ua --output test.png --paper-size medium --print --caption

# Без надпису
python QR_Generator.py --url https://example.com --output qr_no_caption.png --no-caption

# Кастомний розмір
python QR_Generator.py --url https://example.com --paper-size custom --custom-mm 120 --print

# Ручний текст надпису
python QR_Generator.py --url https://stasys.com.ua --caption-text "СТАСИС — стабільні системи" --output stasys_qr.png
```

---

## 7. Примітки по Windows

- **CRLF**: Git може конвертувати LF→CRLF. Не критично для Python.
- **Папка скрипта**: `C:\Users\Admin\qr-generator\` (або будь-де, де `python QR_Generator.py`).
- **Шлях до системного Python**: `C:\Users\Admin\AppData\Local\hermes\tools\python-3.14.7+202****0901-win32-x64\python.exe`
- **Шрифти для caption**: спочатку намагається `arial.ttf`, потім `DejaVuSans.ttf`, потім дефолтний. Windows: arial зазвичай є.
- **Друк PNG**: через стандартний переглядач зображень → Print. Скрипт лише повідомляє розмір паперу флагом `--print`.
- **install.bat**: запускається подвійним кліком або з cmd. Вимагає Python в PATH. Використовує UTF-8 (chcp 65001).

---

## 8. GitHub-репозиторій

- **URL**: https://github.com/alex94aiss-tech/qr-generator
- **Власник**: alex94aiss-tech
- **Віджет**: gh auth status → логін `alex94aiss-tech`, токен у keyring, scope: `repo`, `admin:org`, `gist`, `workflow` тощо.
- **Бранча**: `main`

## 9. GitHub Gist (швидкий доступ до скрипта)

- **URL**: https://gist.github.com/alex94aiss-tech/fa1c010144389eba70b38d4bd849e6b3
- **Що в Gist**: тільки `QR_Generator.py` — основний скрипт
- **Зручно**: швидко забрати оновлений скрипт без клонування всього репо
- **Не зручно**: нема install.bat/install.sh, DEV.md, README — все тільки в репо

> Гist і репо існують одночасно. Gist — для швидкого доступу до скрипта, репо — для повної документації, встановників і історії розробки.

---

*Останнє оновлення цього файлу: 2026-09-28*
