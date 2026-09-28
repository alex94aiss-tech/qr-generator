# DEV · Внутрішня документація QR Generator

> Для розробника. Як зрозуміти проект, якщо треба щось змінити/додати.

---

## 1. Структура проекту

```
qr-generator/
├── QR_Generator.py     # Головний скрипт (CLI)
├── README.md           # Користувацька документація (публічна)
├── LICENSE             # MIT
└── .git/               # Git-репозиторій
```

---

## 2. Залежності

| Пакет | Призначення | Встановлення |
|-------|-------------|--------------|
| `qrcode` | Генерація QR-кодів | `pip install qrcode[pil]` |
| `Pillow` (PIL) | Робота з PNG-зображеннями (посилається qrcode) | автоматично з `qrcode[pil]` |

**Дві версії Python:**
- Системний `python` (3.14.7, шлях: `C:\Users\Admin\AppData\Local\hermes\tools\python-3.14.7+…\python.exe`) — **основний**, треба встановлювати пакети сюди.
- venv Hermes (`C:\Users\Admin\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`) — **резервний**, qrcode встановлена тільки тут.

> ⚠️ Якщо `import qrcode` не працює — встанови в системний Python: `python -m pip install qrcode[pil]`.

---

## 3. Архітектура скрипта

```
main()
  ├─ argparse — парсинг CLI-аргументів (--url, --output, --error-correction, ...)
  ├─ input() — запит URL вручну, якщо не вказано в аргументах
  └─ generate_qr()
       ├─ Створення QRCode (версія auto, рівень корекції, box_size, border)
       ├─ Додавання даних (URL)
       ├─ make_image(fill_color="black", back_color="white")
       ├─ save(path) — PNG
       └─ print_ascii(tty=True) — ASCII в термінал
```

**Ключові параметри QRCode:**
- `version=None` — автоматичний вибір розміру (1-40)
- `error_correction` — `ERROR_CORRECT_L` (7%), `M` (15%, типово), `Q` (25%), `H` (30%)
- `box_size` — розмір одного модуля (пікселі)
- `border` — кордон (кількість модулів)

---

## 4. CLI-інтерфейс

| Флаг | Тип | Типово | Опис |
|------|-----|--------|------|
| `--url`, `-u` | str | (ввід) | URL для QR-коду |
| `--output`, `-o` | str | `qr_<safe>.png` | Шлях до PNG |
| `--error-correction`, `-e` | L/M/Q/H | M | Рівень корекції |
| `--box-size`, `-b` | int | 10 | Розмір боксу |
| `--border`, `-r` | int | 4 | Кордон |
| `--no-ascii` | flag | False | Виключити ASCII |
| `--print`, `-p` | flag | False | Повідомлення про друк |

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

---

## 7. Примітки по Windows

- **CRLF**: Git може конвертувати LF→CRLF. Не критично для Python.
- **Папка скрипта**: `C:\Users\Admin\qr-generator\` (або будь-де, де `python QR_Generator.py`).
- **Шлях до системного Python**: `C:\Users\Admin\AppData\Local\hermes\tools\python-3.14.7+202****0901-win32-x64\python.exe`
- **Друк PNG**: через стандартний переглядач зображень → Print. Скрипт лише повідомляє про це флагом `--print`.

---

## 8. GitHub-репозиторій

- **URL**: https://github.com/alex94aiss-tech/qr-generator
- **Власник**: alex94aiss-tech
- **Віджет**: gh auth status → логін `alex94aiss-tech`, токен у keyring, scope: `repo`, `admin:org`, `gist`, `workflow` тощо.
- **Бранча**: `main`

---

*Останнє оновлення цього файлу: 2026-09-28*
