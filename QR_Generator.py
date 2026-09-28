#!/usr/bin/env python3

"""

QR Code Generator — генерує QR-код з URL, виводить у термінал (ASCII)

і зберігає як PNG файл із заголовком. Підтримує друк.



Інсталяція:

    pip install qrcode[pil] Pillow



Використання:

    python QR_Generator.py https://example.com

    python QR_Generator.py --url https://example.com --output my_qr.png

    python QR_Generator.py --url https://example.com --print --caption

    python QR_Generator.py --url https://example.com --paper-size 100 --no-caption

"""



import argparse

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





def generate_qr(url: str, output_path: str = None, ascii: bool = True,

                print_: bool = False, error_correction: str = "M",

                box_size: int = None, border: int = 4,

                paper_size: str = "medium", custom_paper_mm: float = None,

                caption: bool = True, caption_text: str = None,

                font_size: int = 28, caption_align: str = "center",

                caption_color: str = "black") -> str:

    """Генерує QR-код для URL з опціональним caption."""



    # ── Розмір ────────────────────────────────────────────────────────────

    paper_mm, qr_side_mm = get_paper_config(paper_size, custom_paper_mm)

    target_px = mm_to_px(qr_side_mm)



    # box_size обчислюється так, щоб QR-код (з border) помістився в qr_side_mm

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

    qr.add_data(url)

    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")



    # ── Caption ────────────────────────────────────────────────────────────

    if caption:

        display_text = caption_text if caption_text else url

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

        safe_name = url.replace("https://", "").replace("http://", "").replace("/", "_")[:50]

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

        qr_ascii.add_data(url)

        qr_ascii.make(fit=True)

        qr_ascii.print_ascii()



    # ── Друк ───────────────────────────────────────────────────────────────

    if print_:

        print(f"[!] Папір: {paper_mm}×{paper_mm} мм, QR-квадрат: ≈{qr_side_mm}×{qr_side_mm} мм")

        print("[!] Для друку відкрийте PNG у переглядачі і надрукуйте на папері "

              f"{paper_mm}×{paper_mm} мм.")



    return str(out_path.absolute())





def main():

    parser = argparse.ArgumentParser(

        description="Генератор QR-кодів з URL. Виводить ASCII у термінал і зберігає PNG із заголовком.",

        formatter_class=argparse.RawDescriptionHelpFormatter,

        epilog="""

Приклади:

  %(prog)s --url https://stasys.com.ua

  %(prog)s --url https://example.com --paper-size medium --caption

  %(prog)s --url https://example.com --output qr.png --no-caption

  %(prog)s --url https://example.com --paper-size custom --custom-mm 100 --print

  %(prog)s --url https://example.com --error-correction H --box-size 15

        """

    )

    parser.add_argument("--url", "-u", required=False,

                        help="URL для QR-коду")

    parser.add_argument("--output", "-o", default=None,

                        help="Шлях для збереження PNG файлу")

    parser.add_argument("--error-correction", "-e",

                        choices=["L", "M", "Q", "H"], default="M",

                        help="Рівень корекції: L(7pct) M(15pct) Q(25pct) H(30pct)")

    parser.add_argument("--box-size", "-b", type=int, default=None,

                        help="Розмір одного боксу QR-коду (авто, якщо не вказано)")

    parser.add_argument("--border", "-r", type=int, default=4,

                        help="Розмір кордону (кількість модулів)")

    parser.add_argument("--paper-size", default="medium",

                        choices=["small", "medium", "large", "a4", "custom"],

                        help="Розмір паперу: small(80mm) medium(100mm) large(150mm) a4(210mm)")

    parser.add_argument("--custom-mm", type=float, default=None,

                        help="Сторона квадратного паперу в мм (для --paper-size custom)")

    parser.add_argument("--no-caption", action="store_true", default=False,

                        help="Не додавати текстовий надпис")

    parser.add_argument("--caption", action="store_true", default=True,

                        help="Додати надпис (за замовчуванням)")

    parser.add_argument("--caption-text", default=None,

                        help="Текст надпису (за замовчуванням — URL)")

    parser.add_argument("--caption-align", default="center",

                        choices=["left", "center", "right"],

                        help="Вирівнювання надпису")

    parser.add_argument("--caption-color", default="black",

                        help="Колір тексту надпису")

    parser.add_argument("--font-size", type=int, default=28,

                        help="Розмір шрифту надпису")

    parser.add_argument("--no-ascii", action="store_true",

                        help="Не виводити ASCII в термінал")

    parser.add_argument("--print", "-p", action="store_true",

                        help="Повідомлення для друку")



    args = parser.parse_args()



    # ── URL ────────────────────────────────────────────────────────────────

    url = args.url

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



    url = url.strip()

    if not url.startswith(("http://", "https://")):

        url = "https://" + url



    paper_mm, _ = get_paper_config(args.paper_size, args.custom_mm)

    print(f"\n[→] Генерую QR-код для: {url}")

    print(f"    Папір: {paper_mm}×{paper_mm} мм")



    generate_qr(

        url=url,

        output_path=args.output,

        ascii=not args.no_ascii,

        print_=args.print,

        error_correction=args.error_correction,

        box_size=args.box_size,

        border=args.border,

        paper_size=args.paper_size,

        custom_paper_mm=args.custom_mm,

        caption=not args.no_caption,

        caption_text=args.caption_text,

        font_size=args.font_size,

        caption_align=args.caption_align,

        caption_color=args.caption_color,

    )



    print("[✓] Готово!")





if __name__ == "__main__":

    main()

