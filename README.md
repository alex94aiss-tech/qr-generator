# QR Generator

Простий Python-скрипт для генерації QR-кодів з URL. Виводить QR-код у термінал (ASCII) і зберігає як PNG-файл. Підтримує друк.

## Встановлення

```bash
pip install qrcode[pil]
```

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

### Друк

```bash
python QR_Generator.py --url https://example.com --print
```

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
