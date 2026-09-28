#!/usr/bin/env python3
"""
QR Code Generator — генерує QR-код з URL/телефоном/email/Wi-Fi/текстом,
виводить у термінал (ASCII) і зберігає як PNG файл із заголовком. Підтримує друк.
Підтримує конфігураційний файл config.json для типових налаштувань.

Інсталяція:
    pip install qrcode[pil] Pillow

Використання:
    python QR_Generator.py --url https://example.com
    python QR_Generator.py --phone +380****4567 --print --paper-size medium
    python QR_Generator.py --email stasys94@ukr.net --print
    python QR_Generator.py --wifi-ssid STSIS --wifi-pass прихильник --wifi-sec WPA --print
    python QR_Generator.py --text "Привіт, світ!" --print
    python QR_Generator.py --url https://example.com --paper-size 100 --no-caption
    python QR_Generator.py --config my_config.json --type url --print
"""

import argparse
import json
import sys
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont


# ─── Конфігурація розміру паперу ──────────────────────────────────────────
MM_TO_PX = 96.0 / 25.4   # 1 мм ≈ 3.78 пікселів (96 DPI)

PAPER_SIZES = {
    "small":  (80,  50),   # папір 80×80 мм, QR 50×50 мм
    "medium": (100, 70),   # папір 100×100 мм, QR 70×70 мм  ← типово
    "large":  (150, 110),
    "a4":     (210, 160),
}


def mm_to_px(mm: float) -> int:
    return max(1, int(mm * MM_TO_PX))


def get_paper_config(paper_size: str, custom_mm: float = None) -> tuple[int, int]:
    """Повертає (папір_мм, qr_сторона_мм)."""
    if paper_size in PAPER_SIZES:
        return PAPER_SIZES[paper_size]
    if custom_mm is not None:
        qr_side = max(int(custom_mm * 0.7), 20)
        return (int(custom_mm), qr_side)
    return PAPER_SIZES["medium"]


def load_config(config_path: str = None, no_config: bool = False) -> dict:
    """
    Завантажує конфігурацію з config.json.

    Args:
        config_path: шлях до файлу конфігу (якщо None — config.json в поточній папці).
        no_config: якщо True — ігнорувати конфіг і повернути порожній dict.

    Returns:
        dict з налаштуваннями (за замовчуванням порожній, якщо конфіг не знайдено).
    """
    if no_config:
        return {}

    path = config_path or "config.json"
    config_file = Path(path)

    if not config_file.is_file():
        return {}

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except (json.JSONDecodeError, IOError) as e:
        print(f"[WARNING] Помилка завантаження конфігу {path}: {e}")
        return {}


def add_caption_to_image(img: Image.Image, caption: str,
                         font_size: int = 28, padding: int = 16,
                         text_color: str = "black", bg_color: str = "white",
                         align: str = "center") -> Image.Image:
    """Додає текстовий заголовок зверху до QR-коду."""
    img_w, img_h = img.size
    caption_height = font_size + padding
    canvas = Image.new("RGB", (img_w, img_h + caption_height), bg_color)
    draw = ImageDraw.Draw(canvas)

    # Конвертуємо в RGB, якщо потрібно (qrcode дає "1" або "P")
    if img.mode != "RGB":
        img = img.convert("RGB")

    qr_y = caption_height
    canvas.paste(img, (0, qr_y, img_w, qr_y + img_h))

    # Шрифт
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except (IOError, OSError):
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except (IOError, OSError):
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), caption, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    if align == "center":
        text_x = (img_w - text_w) // 2
    elif align == "right":
        text_x = img_w - text_w - padding
    else:
        text_x = padding

    text_y = padding // 2
    draw.text((text_x, text_y), caption, fill=text_color, font=font)
    return canvas


def build_data(qr_type: str, url: str = None, phone: str = None,
               email: str = None, wifi_ssid: str = None, wifi_pass: str = None,
               wifi_sec: str = "WPA", text: str = None) -> str:
    """Будує дані для QR-коду на основі типу."""
    if qr_type == "url":
        if url:
            url = url.strip()
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            return url
        return None

    if qr_type == "tel":
        if phone:
            phone = phone.strip()
            # Додаємо + якщо відсутнє
            if not phone.startswith("+") and not phone.startswith("0+"):
                phone = "+" + phone if phone.startswith("38") else "+" + phone.replace("38", "")
            # Нормалізуємо: +380... замість +38
            if phone.startswith("+38") and len(phone) > 3 and phone[3] != "0":
                phone = "+380" + phone[3:].lstrip("0")
            return "tel:" + phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        return None

    if qr_type == "mailto":
        if email:
            email = email.strip()
            return "mailto:" + email
        return None

    if qr_type == "wifi":
        if wifi_ssid:
            sec = wifi_sec.upper() if wifi_sec else "WPA"
            pw = wifi_pass if wifi_pass else ""
            return f"WIFI:S:{wifi_ssid};T:{sec};P:{pw};;"
        return None

    if qr_type == "text":
        return text if text else None

    # Sumfall — повертаємо raw data
    return url


def generate_qr(data: str, qr_type: str = "url", output_path: str = None,
                ascii: bool = True, print_: bool = False,
                error_correction: str = "M", box_size: int = None,
                border: int = 4, paper_size: str = "medium",
                custom_paper_mm: float = None, caption: bool = True,
                caption_text: str = None, font_size: int = 28,
                caption_align: str = "center", caption_color: str = "black") -> str:
    """Генерує QR-код для даних з опціональним caption."""

    if not data:
        print("[ERROR] Дані для QR-коду не вказано.")
        return None

    # ── Розмір ────────────────────────────────────────────────────────────
    paper_mm, qr_side_mm = get_paper_config(paper_size, custom_paper_mm)
    target_px = mm_to_px(qr_side_mm)

    safe_version = 25
    max_boxes = safe_version + border * 2
    box_size = max(2, target_px // max_boxes) if box_size is None else box_size

    # ── QR ────────────────────────────────────────────────────────────────
    ec_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }
    qr = qrcode.QRCode(
        version=None,
        error_correction=ec_map.get(error_correction.upper(), qrcode.constants.ERROR_CORRECT_M),
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # ── Caption ────────────────────────────────────────────────────────────
    if caption:
        display_text = caption_text if caption_text else data
        if len(display_text) > 60:
            display_text = display_text[:57] + "..."
        img = add_caption_to_image(
            img, display_text,
            font_size=font_size, align=caption_align,
            text_color=caption_color,
        )

    # ── Збереження ────────────────────────────────────────────────────────
    if output_path:
        out_path = Path(output_path)
    else:
        safe_name = data.replace("https://", "").replace("http://", "").replace("/", "_").replace("tel:", "").replace("mailto:", "").replace("WIFI:", "")[:50]
        out_path = Path(f"qr_{safe_name}.png")

    img.save(out_path)
    print(f"[✓] QR-код збережено: {out_path.absolute()}")

    # ── ASCII (без caption) ───────────────────────────────────────────────
    if ascii:
        qr_ascii = qrcode.QRCode(
            version=None,
            error_correction=ec_map.get(error_correction.upper(), qrcode.constants.ERROR_CORRECT_M),
            box_size=box_size,
            border=border,
        )
        qr_ascii.add_data(data)
        qr_ascii.make(fit=True)
        qr_ascii.print_ascii()

    # ── Друк ───────────────────────────────────────────────────────────────
    if print_:
        print(f"[!] Папір: {paper_mm}×{paper_mm} мм, QR-квадрат: ≈{qr_side_mm}×{qr_side_mm} мм")
        print(f"[!] Тип QR: {qr_type}")
        print("[!] Для друку відкрийте PNG у переглядачі і надрукуйте на папері "
              f"{paper_mm}×{paper_mm} мм.")

    return str(out_path.absolute())


def main():
    parser = argparse.ArgumentParser(
        description="Генератор QR-кодів: URL, телефон, email, Wi-Fi, текст. "
                    "Виводить ASCII у термінал і зберігає PNG із заголовком. "
                    "Підтримує config.json для типових налаштувань.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Типи QR-кодів:
  --type url      — URL (за замовчуванням)
  --type tel      — Телефон (--phone +380****4567)
  --type mailto   — Email (--email stasys94@ukr.net)
  --type wifi     — Wi-Fi (--wifi-ssid STSIS --wifi-pass пароль)
  --type text     — Вільний текст (--text "Привіт")

Конфігурація:
  --config path   — Використати файл конфігу (замовчування: config.json)
  --no-config     — Ігнорувати конфігураційний файл

Приклади:
  %(prog)s --url https://stasys.com.ua
  %(prog)s --type tel --phone +380****4567 --print
  %(prog)s --type mailto --email stasys94@ukr.net --print
  %(prog)s --type wifi --wifi-ssid STSIS --wifi-pass прихильник --print
  %(prog)s --type text --text "Привіт, світ!" --print
  %(prog)s --url https://example.com --paper-size medium --caption
  %(prog)s --url https://example.com --output qr.png --no-caption
  %(prog)s --config my_config.json --type url --print
  %(prog)s --no-config --type tel --phone +380****4567
        """
    )
    parser.add_argument("--type", "-t", default="url",
                        choices=["url", "tel", "mailto", "wifi", "text"],
                        help="Тип QR-коду: url, tel, mailto, wifi, text (за замовчуванням url)")
    parser.add_argument("--url", "-u", required=False,
                        help="URL для QR-коду (тип url)")
    parser.add_argument("--phone", "-p", required=False,
                        help="Номер телефону (тип tel, наприклад +380****4567)")
    parser.add_argument("--email", "-e", required=False,
                        help="Email (тип mailto, наприклад stasys94@ukr.net)")
    parser.add_argument("--wifi-ssid", required=False,
                        help="SSID Wi-Fi мережі (тип wifi)")
    parser.add_argument("--wifi-pass", required=False,
                        help="Пароль Wi-Fi мережі (тип wifi)")
    parser.add_argument("--wifi-sec", default="WPA", required=False,
                        help="Безпека Wi-Fi: WPA, WEP, nopass (тип wifi, за замовчуванням WPA)")
    parser.add_argument("--text", required=False,
                        help="Вільний текст (тип text)")
    parser.add_argument("--output", "-o", default=None,
                        help="Шлях для збереження PNG файлу")
    parser.add_argument("--error-correction", default=None,
                        choices=["L", "M", "Q", "H"],
                        help="Рівень корекції: L(7pct) M(15pct) Q(25pct) H(30pct)")
    parser.add_argument("--box-size", "-b", type=int, default=None,
                        help="Розмір одного боксу QR-коду (авто, якщо не вказано)")
    parser.add_argument("--border", "-r", type=int, default=None,
                        help="Розмір кордону (кількість модулів)")
    parser.add_argument("--paper-size", default=None,
                        choices=["small", "medium", "large", "a4", "custom"],
                        help="Розмір паперу: small(80mm) medium(100mm) large(150mm) a4(210mm)")
    parser.add_argument("--custom-mm", type=float, default=None,
                        help="Сторона квадратного паперу в мм (для --paper-size custom)")
    parser.add_argument("--no-caption", action="store_true", default=False,
                        help="Не додавати текстовий надпис")
    parser.add_argument("--caption", action="store_true", default=False,
                        help="Додати надпис (за замовчуванням — так, якщо не вказано --no-caption)")
    parser.add_argument("--caption-text", default=None,
                        help="Текст надпису (за замовчуванням — дані)")
    parser.add_argument("--caption-align", default=None,
                        choices=["left", "center", "right"],
                        help="Вирівнювання надпису")
    parser.add_argument("--caption-color", default=None,
                        help="Колір тексту надпису")
    parser.add_argument("--font-size", type=int, default=None,
                        help="Розмір шрифту надпису")
    parser.add_argument("--no-ascii", action="store_true",
                        help="Не виводити ASCII в термінал")
    parser.add_argument("--print", action="store_true",
                        help="Повідомлення для друку")
    parser.add_argument("--config", default=None,
                        help="Шлях до файлу конфігурації (замовчування: config.json)")
    parser.add_argument("--no-config", action="store_true",
                        help="Ігнорувати конфігураційний файл")

    args = parser.parse_args()

    # ── Завантаження конфігу ────────────────────────────────────────────────
    config = load_config(config_path=args.config, no_config=args.no_config)
    default_cfg = config.get("defaults", {})
    types_cfg = config.get("types", {})

    qr_type = args.type
    type_cfg = types_cfg.get(qr_type, {})

    # ── Дані ────────────────────────────────────────────────────────────────
    data = None

    # Функція допомоги: беремо value з args або з конфіга, якщо args is None
    def cfg_or_args(arg_value, config_value):
        """Повертає arg_value якщо він not None, інакше config_value."""
        return arg_value if arg_value is not None else config_value

    if qr_type == "url":
        url = cfg_or_args(args.url, type_cfg.get("url") or default_cfg.get("url"))
        if not url:
            print("Введіть URL для генерації QR-коду:")
            try:
                url = input("> ").strip()
            except EOFError:
                print("Помилка: URL не вказано.")
                parser.print_help()
                sys.exit(1)
        if not url:
            print("Помилка: URL не вказано.")
            parser.print_help()
            sys.exit(1)
        data = build_data("url", url=url)

    elif qr_type == "tel":
        phone = cfg_or_args(args.phone, type_cfg.get("phone"))
        if not phone:
            print("Введіть номер телефону (наприклад +380****4567):")
            try:
                phone = input("> ").strip()
            except EOFError:
                print("Помилка: телефон не вказано.")
                parser.print_help()
                sys.exit(1)
        if not phone:
            print("Помилка: телефон не вказано.")
            parser.print_help()
            sys.exit(1)
        data = build_data("tel", phone=phone)

    elif qr_type == "mailto":
        email = cfg_or_args(args.email, type_cfg.get("email") or default_cfg.get("url"))
        if not email:
            print("Введіть email (наприклад stasys94@ukr.net):")
            try:
                email = input("> ").strip()
            except EOFError:
                print("Помилка: email не вказано.")
                parser.print_help()
                sys.exit(1)
        if not email:
            print("Помилка: email не вказано.")
            parser.print_help()
            sys.exit(1)
        data = build_data("mailto", email=email)

    elif qr_type == "wifi":
        wifi_ssid = cfg_or_args(args.wifi_ssid, type_cfg.get("wifi_ssid"))
        if not wifi_ssid:
            print("Введіть SSID Wi-Fi мережі:")
            try:
                wifi_ssid = input("> ").strip()
            except EOFError:
                print("Помилка: SSID не вказано.")
                parser.print_help()
                sys.exit(1)
        if not wifi_ssid:
            print("Помилка: SSID не вказано.")
            parser.print_help()
            sys.exit(1)
        wifi_pass = cfg_or_args(args.wifi_pass, type_cfg.get("wifi_pass"))
        wifi_sec = cfg_or_args(args.wifi_sec, type_cfg.get("wifi_sec", "WPA")) or "WPA"
        if not wifi_pass:
            print("Введіть пароль Wi-Fi (або залиште порожнім для open):")
            try:
                wifi_pass = input("> ").strip()
            except EOFError:
                wifi_pass = ""
        data = build_data("wifi", wifi_ssid=wifi_ssid, wifi_pass=wifi_pass, wifi_sec=wifi_sec)

    elif qr_type == "text":
        text = cfg_or_args(args.text, type_cfg.get("text"))
        if not text:
            print("Введіть текст для QR-коду:")
            try:
                text = input("> ").strip()
            except EOFError:
                print("Помилка: текст не вказано.")
                parser.print_help()
                sys.exit(1)
        if not text:
            print("Помилка: текст не вказано.")
            parser.print_help()
            sys.exit(1)
        data = build_data("text", text=text)

    # ── Параметри (з конфігу) ────────────────────────────────────────────────
    paper_size = cfg_or_args(args.paper_size, default_cfg.get("paper_size", "medium"))
    custom_mm = args.custom_mm if args.custom_mm is not None else default_cfg.get("paper_mm")
    error_correction = cfg_or_args(args.error_correction, default_cfg.get("error_correction", "M"))
    box_size = args.box_size if args.box_size is not None else default_cfg.get("box_size")
    border = args.border if args.border is not None else default_cfg.get("border", 4)
    font_size = args.font_size if args.font_size is not None else default_cfg.get("font_size", 28)
    caption_align = cfg_or_args(args.caption_align, default_cfg.get("caption_align", "center"))
    caption_color = cfg_or_args(args.caption_color, default_cfg.get("caption_color", "black"))

    # Caption text: спочатку args, потім type-specific, потім defaults
    caption_text = args.caption_text
    if not caption_text:
        caption_text = type_cfg.get("caption") or default_cfg.get("caption")

    # Caption enabled: --no-caption → False, --caption → True, инакше конфіг
    if args.no_caption:
        caption_enabled = False
    elif args.caption:
        caption_enabled = True
    else:
        caption_enabled = default_cfg.get("caption", True)

    # Boolean flags
    ascii_enabled = not args.no_ascii if args.no_ascii else not default_cfg.get("no_ascii", False)
    print_enabled = args.print if args.print else default_cfg.get("print", False)

    # ── Вивід інформації ──────────────────────────────────────────────────────
    paper_mm, _ = get_paper_config(paper_size, custom_mm)
    print(f"\n[→] Генерую QR-код ({qr_type})")
    print(f"    Папір: {paper_mm}×{paper_mm} мм")
    if config:
        print(f"    Конфіг: {args.config or 'config.json'}")

    generate_qr(
        data=data,
        qr_type=qr_type,
        output_path=args.output,
        ascii=ascii_enabled,
        print_=print_enabled,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
        paper_size=paper_size,
        custom_paper_mm=custom_mm,
        caption=caption_enabled,
        caption_text=caption_text,
        font_size=font_size,
        caption_align=caption_align,
        caption_color=caption_color,
    )

    print("[✓] Готово!")


if __name__ == "__main__":
    main()
