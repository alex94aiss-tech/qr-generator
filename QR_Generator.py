#!/usr/bin/env python3
"""
QR Code Generator — генерує QR-код з URL, виводить у термінал (ASCII)
і зберігає як PNG файл. Підтримує друк.

Інсталяція:
    pip install qrcode[pil]

Використання:
    python qr_generator.py https://example.com
    python qr_generator.py --url https://example.com --output my_qr.png
    python qr_generator.py --url https://example.com --print
"""

import argparse
import os
import sys
from pathlib import Path

import qrcode


def generate_qr(url: str, output_path: str = None, ascii: bool = True,
                print_: bool = False, error_correction: str = "M",
                box_size: int = 10, border: int = 4) -> str:
    """
    Генерує QR-код для заданого URL.

    Args:
        url: URL для кодування в QR-код.
        output_path: Шлях для збереження PNG (якщо None — автоматичне ім'я).
        ascii: Виводити ASCII-варіант у термінал.
        print_: Надрукувати QR-код (часто використовується для друку на принтерах).
        error_correction: Рівень корекції помилок (L, M, Q, H).
        box_size: Розмір одного "box" у QR-коді.
        border: Розмір кордону.

    Returns:
        Шлях до збереженого PNG файлу.
    """
    # Створюємо QR-код
    qr = qrcode.QRCode(
        version=None,  # автоматично
        error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{error_correction.upper()}"),
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Генеруємо зображення
    img = qr.make_image(fill_color="black", back_color="white")

    # Визначаємо шлях для збереження
    if output_path:
        out_path = Path(output_path)
    else:
        # Автоматичне ім'я файлу з URL
        safe_name = url.replace("https://", "").replace("http://", "").replace("/", "_")[:50]
        out_path = Path(f"qr_{safe_name}.png")

    # Зберігаємо PNG
    img.save(out_path)
    print(f"[✓] QR-код збережено: {out_path.absolute()}")

    # ASCII в терміналі
    if ascii:
        qr.print_ascii(tty=True)

    # Друк (якщо вказано)
    if print_:
        print("[!] Для фізичного друку відкрийте файл PNG у зручному переглядачі і надрукуйте.")

    return str(out_path.absolute())


def main():
    parser = argparse.ArgumentParser(
        description="Генератор QR-кодів з URL. Виводить ASCII у термінал і зберігає PNG.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Приклади:
  %(prog)s https://example.com
  %(prog)s --url https://example.com --output qr.png
  %(prog)s --url https://example.com --no-ascii --print
  %(prog)s --url https://example.com --error-correction H --box-size 15
        """
    )
    parser.add_argument("url", nargs="?", help="URL для QR-коду (або використовуйте --url)")
    parser.add_argument("--url", "-u", help="URL для QR-коду")
    parser.add_argument("--output", "-o", help="Шлях для збереження PNG файлу")
    parser.add_argument("--error-correction", "-e", choices=["L", "M", "Q", "H"],
                        default="M", help="Рівень корекції помилок (L=7% M=15% Q=25% H=30%)")
    parser.add_argument("--box-size", "-b", type=int, default=10,
                        help="Розмір одного боксу QR-коду")
    parser.add_argument("--border", "-r", type=int, default=4,
                        help="Розмір кордону")
    parser.add_argument("--no-ascii", action="store_true",
                        help="Не виводити ASCII в термінал")
    parser.add_argument("--print", "-p", action="store_true",
                        help="Повідомлення про друк")

    args = parser.parse_args()

    # URL — або з аргументу, або з --url, або запитуємо ввід
    url = args.url
    if not url and args.url is None:
        if args.url is None and not args.url and not args.url:
            pass
        print("Введіть URL для генерації QR-коду:")
        url = input("> ").strip()

    if not url:
        print("Помилка: URL не вказано.")
        parser.print_help()
        sys.exit(1)

    # Нормалізуємо URL
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    print(f"\n[→] Генерую QR-код для: {url}\n")

    generate_qr(
        url=url,
        output_path=args.output,
        ascii=not args.no_ascii,
        print_=args.print,
        error_correction=args.error_correction,
        box_size=args.box_size,
        border=args.border,
    )

    print("[✓] Готово!")


if __name__ == "__main__":
    main()
