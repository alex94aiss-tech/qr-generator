#!/usr/bin/env python3

"""
QR Code Generator - generates QR codes of various types (URL, phone, email, Wi-Fi, text),
outputs ASCII to terminal and saves PNG with caption. Supports print.

Installation:
    pip install qrcode[pil]

Usage:
    python QR_Generator.py https://example.com
    python QR_Generator.py --url https://example.com --output my_qr.png
    python QR_Generator.py --url https://example.com --print --caption
    python QR_Generator.py --url https://example.com --paper-size 100 --no-caption
    python QR_Generator.py --type tel --phone +380671234567 --print
    python QR_Generator.py --type mailto --email stasys94@ukr.net --print
    python QR_Generator.py --type wifi --wifi-ssid STSIS --wifi-pass password --print
    python QR_Generator.py --type text --text "Hello, world!" --print
"""

import argparse

import json
import os
import re
import sys
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont


# -- Paper size config -------------------------------------------------

MM_TO_PX = 96.0 / 25.4   # 1 mm ~ 3.78 pixels (96 DPI)

PAPER_SIZES = {
    "small":  (80,  50),   # paper 80x80 mm, QR 50x50 mm
    "medium": (100, 70),   # paper 100x100 mm, QR 70x70 mm  <-- default
    "large":  (150, 110),
    "a4":     (210, 160),
}


def mm_to_px(mm: float) -> int:
    return max(1, int(mm * MM_TO_PX))


def get_paper_config(paper_size: str, custom_mm: float = None) -> tuple[int, int]:
    """Returns (paper_mm, qr_side_mm)."""
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
    """Adds text caption above QR code."""
    img_w, img_h = img.size
    caption_height = font_size + padding
    canvas = Image.new("RGB", (img_w, img_h + caption_height), bg_color)
    draw = ImageDraw.Draw(canvas)

    if img.mode != "RGB":
        img = img.convert("RGB")

    qr_y = caption_height
    canvas.paste(img, (0, qr_y, img_w, qr_y + img_h))

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


def load_config(config_path: str = "config.json") -> dict:
    """Loads config.json."""
    path = Path(config_path)
    if not path.is_file():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def build_qr_data(args: argparse.Namespace, config: dict) -> tuple[str, str]:
    """
    Builds QR data based on type and args.
    Returns (qr_data, caption_text).
    CLI args take priority over config.json.
    """
    cfg_defaults = config.get("defaults", {})
    cfg_types = config.get("types", {})

    qr_type = args.type or "url"

    if qr_type == "url":
        url = args.url
        if not url:
            url = cfg_defaults.get("url") or cfg_types.get("url", {}).get("url")
        if not url:
            return "", "URL not specified"
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        caption = args.caption_text or cfg_defaults.get("caption") or cfg_types.get("url", {}).get("caption") or url
        return url, caption

    if qr_type == "tel":
        phone = args.phone
        if not phone:
            phone = cfg_defaults.get("phone") or cfg_types.get("tel", {}).get("phone")
        if not phone:
            return "", "Phone not specified (use --phone)"
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10:
            return "", f"Invalid phone: {phone}"
        qr_data = "tel:" + phone
        caption = args.caption_text or cfg_defaults.get("caption") or cfg_types.get("tel", {}).get("caption") or "Phone: " + phone
        return qr_data, caption

    if qr_type == "mailto":
        email = args.email
        if not email:
            email = cfg_defaults.get("email") or cfg_types.get("mailto", {}).get("email")
        if not email:
            return "", "Email not specified (use --email)"
        if "@" not in email:
            return "", f"Invalid email: {email}"
        qr_data = "mailto:" + email
        caption = args.caption_text or cfg_defaults.get("caption") or cfg_types.get("mailto", {}).get("caption") or "Email: " + email
        return qr_data, caption

    if qr_type == "wifi":
        ssid = args.wifi_ssid
        if not ssid:
            ssid = cfg_defaults.get("wifi_ssid") or cfg_types.get("wifi", {}).get("wifi_ssid")
        if not ssid:
            return "", "Wi-Fi SSID not specified (use --wifi-ssid)"
        wpass = args.wifi_pass or cfg_defaults.get("wifi_pass") or cfg_types.get("wifi", {}).get("wifi_pass") or ""
        wsec = args.wifi_sec or cfg_defaults.get("wifi_sec") or cfg_types.get("wifi", {}).get("wifi_sec") or "WPA"
        wsec = wsec.upper()
        if wsec not in ("WPA", "WEP", "NOPASS"):
            wsec = "WPA"
        if wsec == "NOPASS":
            qr_data = "WIFI:S:" + ssid + ";T:nopass;;"
        else:
            qr_data = "WIFI:S:" + ssid + ";T:" + wsec + ";P:" + wpass + ";;"
        caption = args.caption_text or cfg_defaults.get("caption") or cfg_types.get("wifi", {}).get("caption") or "Wi-Fi: " + ssid
        return qr_data, caption

    if qr_type == "text":
        text = args.text
        if not text:
            text = cfg_types.get("text", {}).get("text", "")
        if not text:
            return "", "Text not specified (use --text)"
        qr_data = text
        caption = args.caption_text or cfg_defaults.get("caption") or cfg_types.get("text", {}).get("caption") or text[:50]
        return qr_data, caption

    return "", "Unknown QR type: " + qr_type


def generate_qr(url: str, output_path: str = None, ascii: bool = True,
                print_: bool = False, error_correction: str = "M",
                box_size: int = None, border: int = 4,
                paper_size: str = "medium", custom_paper_mm: float = None,
                caption: bool = True, caption_text: str = None,
                font_size: int = 28, caption_align: str = "center",
                caption_color: str = "black") -> str:
    """Generates QR code for URL with optional caption."""
    paper_mm, qr_side_mm = get_paper_config(paper_size, custom_paper_mm)
    target_px = mm_to_px(qr_side_mm)

    safe_version = 25
    max_boxes = safe_version + border * 2
    box_size = max(2, target_px // max_boxes) if box_size is None else box_size

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

    if caption:
        display_text = caption_text if caption_text else url
        if len(display_text) > 60:
            display_text = display_text[:57] + "..."
        img = add_caption_to_image(
            img, display_text,
            font_size=font_size, align=caption_align,
            text_color=caption_color,
        )

    if output_path:
        out_path = Path(output_path)
    else:
        safe_name = url.replace("https://", "").replace("http://", "").replace("/", "_")[:50]
        out_path = Path("qr_" + safe_name + ".png")

    img.save(out_path)
    print("[OK] QR code saved: " + str(out_path.absolute()))

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

    if print_:
        print("[!] Paper: " + str(paper_mm) + "x" + str(paper_mm) + " mm, QR square: ~" + str(qr_side_mm) + "x" + str(qr_side_mm) + " mm")
        print("[!] To print: open PNG in viewer and print on " + str(paper_mm) + "x" + str(paper_mm) + " mm paper.")

    return str(out_path.absolute())


def batch_generate(input_file: str, output_dir: str = ".",
                   name_as_filename: bool = False,
                   error_correction: str = "M", box_size: int = None,
                   border: int = 4, paper_size: str = "medium",
                   custom_mm: float = None,
                   caption: bool = True, no_caption: bool = False,
                   caption_text: str = None, font_size: int = 28,
                   caption_align: str = "center", caption_color: str = "black") -> list:
    """Generates QR codes for each line in a file."""
    results = []

    with open(input_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    for i, line in enumerate(lines):
        safe_name = re.sub(r'[^\w\-]', '_', line[:40]) or ("qr_" + str(i))
        out_path = Path(output_dir) / (safe_name + ".png")

        print("[" + str(i+1) + "/" + str(len(lines)) + "] Generating: " + line[:60] + "...")

        generate_qr(line, str(out_path),
                    error_correction=error_correction, box_size=box_size,
                    border=border, paper_size=paper_size, custom_mm=custom_mm,
                    caption=caption, no_caption=no_caption,
                    caption_text=caption_text, font_size=font_size,
                    caption_align=caption_align, caption_color=caption_color,
                    no_ascii=True)

        results.append(str(out_path))

    return results


GIST_RAW_URL = "https://gist.githubusercontent.com/alex94aiss-tech/fa1c010144389eba70b38d4bd849e6b3/raw/QR_Generator.py"


def update_from_gist(force: bool = False) -> bool:
    """
    Updates current script from GitHub Gist.
    If force=False, prompts before replacing.
    Returns True on success.
    """
    import urllib.request

    print("[>] Updating from GitHub Gist: " + GIST_RAW_URL)

    try:
        with urllib.request.urlopen(GIST_RAW_URL, timeout=30) as resp:
            new_content = resp.read().decode("utf-8")
    except Exception as e:
        print("[X] Download error: " + str(e))
        return False

    current_path = Path(__file__).resolve()
    current_content = current_path.read_text(encoding="utf-8")

    if new_content == current_content and not force:
        print("[OK] Script is already up-to-date (nothing changed)")
        return True

    if not force:
        print("[!] Current script differs from Gist version.")
        try:
            answer = input("Replace current script with updated? (y/N): ").strip().lower()
        except EOFError:
            print("[X] Cancelled (EOF)")
            return False
        if answer not in ("y", "yes"):
            print("[X] Cancelled")
            return False

    backup_path = current_path.with_suffix(".py.bak")
    backup_path.write_text(current_content, encoding="utf-8")
    print("[OK] Backup saved: " + str(backup_path))

    current_path.write_text(new_content, encoding="utf-8")
    print("[OK] Script updated: " + str(current_path))
    print("[OK] Run the script again to verify.")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="QR code generator: URL, phone, email, Wi-Fi, text. "
                    "Outputs ASCII to terminal and saves PNG with caption. Supports print.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url https://stasys.com.ua
  %(prog)s --url https://example.com --paper-size medium --caption
  %(prog)s --url https://example.com --output qr.png --no-caption
  %(prog)s --url https://example.com --paper-size custom --custom-mm 100 --print
  %(prog)s --url https://example.com --error-correction H --box-size 15
  %(prog)s --type tel --phone +380671234567 --print
  %(prog)s --type mailto --email stasys94@ukr.net --print
  %(prog)s --type wifi --wifi-ssid STSIS --wifi-pass password --print
  %(prog)s --type text --text "Hello, world!" --print
  %(prog)s --config my_config.json --type url --print
  %(prog)s --update
        """
    )

    parser.add_argument("--type", "-t",
                        choices=["url", "tel", "mailto", "wifi", "text"],
                        default="url",
                        help="QR type: url, tel, mailto, wifi, text (default: url)")

    parser.add_argument("--url", "-u", default=None,
                        help="URL for QR code (type: url)")
    parser.add_argument("--phone", default=None,
                        help="Phone number (type: tel, e.g. +380671234567)")
    parser.add_argument("--email", default=None,
                        help="Email (type: mailto, e.g. stasys94@ukr.net)")
    parser.add_argument("--wifi-ssid", default=None,
                        help="Wi-Fi SSID (type: wifi)")
    parser.add_argument("--wifi-pass", default=None,
                        help="Wi-Fi password (type: wifi)")
    parser.add_argument("--wifi-sec", default=None,
                        choices=["WPA", "WEP", "nopass"],
                        help="Wi-Fi security: WPA, WEP, nopass (type: wifi, default: WPA)")
    parser.add_argument("--text", default=None,
                        help="Free text (type: text)")

    parser.add_argument("--config", default=None,
                        help="Path to config.json (default: config.json in current folder)")
    parser.add_argument("--no-config", action="store_true", default=False,
                        help="Ignore config.json, use only CLI args")

    parser.add_argument("--output", "-o", default=None,
                        help="Path to save PNG file")
    parser.add_argument("--error-correction", "-e",
                        choices=["L", "M", "Q", "H"], default="M",
                        help="Error correction: L(7pct) M(15pct) Q(25pct) H(30pct)")
    parser.add_argument("--box-size", "-b", type=int, default=None,
                        help="QR box size (auto if not set)")
    parser.add_argument("--border", "-r", type=int, default=4,
                        help="Border size (modules)")
    parser.add_argument("--paper-size", default="medium",
                        choices=["small", "medium", "large", "a4", "custom"],
                        help="Paper size: small(80mm) medium(100mm) large(150mm) a4(210mm)")
    parser.add_argument("--custom-mm", type=float, default=None,
                        help="Square paper side in mm (for --paper-size custom)")
    parser.add_argument("--no-caption", action="store_true", default=False,
                        help="No text caption")
    parser.add_argument("--caption", action="store_true", default=True,
                        help="Add caption (default)")
    parser.add_argument("--caption-text", default=None,
                        help="Caption text (default: data)")
    parser.add_argument("--caption-align", default="center",
                        choices=["left", "center", "right"],
                        help="Caption alignment")
    parser.add_argument("--caption-color", default="black",
                        help="Caption text color")
    parser.add_argument("--font-size", type=int, default=28,
                        help="Caption font size")
    parser.add_argument("--no-ascii", action="store_true",
                        help="No ASCII output to terminal")
    parser.add_argument("--print", "-p", action="store_true",
                        help="Print info message")

    parser.add_argument("--batch", default=None,
                        help="File with URLs (one per line) for batch generation")
    parser.add_argument("--output-dir", default=None,
                        help="Folder to save QR codes (default: current)")
    parser.add_argument("--name-as-filename", action="store_true", default=False,
                        help="Use name from file as PNG filename")

    parser.add_argument("--update", action="store_true",
                        help="Update script from GitHub Gist (prompts)")
    parser.add_argument("--update-force", action="store_true",
                        help="Update script from GitHub Gist without prompt (backups)")

    args = parser.parse_args()

    if args.update or args.update_force:
        success = update_from_gist(force=args.update_force)
        sys.exit(0 if success else 1)

    config = {}
    if not args.no_config:
        config_path = args.config or "config.json"
        config = load_config(config_path)
        if config:
            print("[>] Loaded config from: " + config_path)

    if args.batch:
        if not os.path.exists(args.batch):
            print("Error: file " + args.batch + " not found.")
            sys.exit(1)
        output_dir = args.output_dir or "."
        os.makedirs(output_dir, exist_ok=True)
        results = batch_generate(args.batch, output_dir, args.name_as_filename,
                                 args.error_correction, args.box_size, args.border,
                                 args.paper_size, args.custom_mm,
                                 args.caption, args.no_caption, args.caption_text,
                                 args.font_size, args.caption_align, args.caption_color)
        print("\n[OK] Generated " + str(len(results)) + " QR codes in " + output_dir + "/")
        for r in results:
            print("  - " + r)
        sys.exit(0)

    qr_data, caption_text = build_qr_data(args, config)

    if not qr_data:
        print("Error: " + caption_text)
        parser.print_help()
        sys.exit(1)

    output_path = args.output

    paper_mm, _ = get_paper_config(args.paper_size, args.custom_mm)
    print("\n[>] Generating QR code (" + args.type + "): " + qr_data[:60] + "...")
    print("    Paper: " + str(paper_mm) + "x" + str(paper_mm) + " mm")

    generate_qr(
        url=qr_data,
        output_path=output_path,
        ascii=not args.no_ascii,
        print_=args.print,
        error_correction=args.error_correction,
        box_size=args.box_size,
        border=args.border,
        paper_size=args.paper_size,
        custom_paper_mm=args.custom_mm,
        caption=not args.no_caption,
        caption_text=caption_text,
        font_size=args.font_size,
        caption_align=args.caption_align,
        caption_color=args.caption_color,
    )

    print("[OK] Done!")


if __name__ == "__main__":
    main()
