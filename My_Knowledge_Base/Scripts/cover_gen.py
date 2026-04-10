"""
Cover generator for VAI weekly digest.
Requires: pip install Pillow

Date logic: start = today - 6 days, end = today
"""

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import os, random, glob

# --- Paths (relative to this script's location) ---
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR    = os.path.join(SCRIPTS_DIR, "..", "Cover_Elements")
OUTPUT_PATH = "/tmp/cover.png"

BG_DIR       = os.path.join(BASE_DIR, "backgrounds")
LINES_PATH   = os.path.join(BASE_DIR, "lines.png")
NOVOSTI_PATH = os.path.join(BASE_DIR, "novosti_nedeli.png")
VAI_PATH     = os.path.join(BASE_DIR, "vai.png")
FONT_PATH    = os.path.join(BASE_DIR, "swissck.ttf")

# --- Date config ---
DATE_FONT_SIZE = 42
DATE_Y_RATIO   = 0.34
DATE_COLOR     = "#FFFFFF"


def get_week_dates():
    """today-6 days → today"""
    today = datetime.today()
    start = today - timedelta(days=6)
    return start.strftime("%d.%m.%y"), today.strftime("%d.%m.%y")


def generate_cover(date_start=None, date_end=None):
    if not date_start or not date_end:
        date_start, date_end = get_week_dates()

    date_text = f"{date_start}-{date_end}"
    print(f"Generating cover for: {date_text}")

    backgrounds = glob.glob(os.path.join(BG_DIR, "*.png"))
    bg_path = random.choice(backgrounds)
    print(f"Background: {os.path.basename(bg_path)}")

    base = Image.open(bg_path).convert("RGBA")
    width, height = base.size

    base.paste(Image.open(LINES_PATH).convert("RGBA"),   (0, 0), Image.open(LINES_PATH).convert("RGBA"))
    base.paste(Image.open(NOVOSTI_PATH).convert("RGBA"), (0, 0), Image.open(NOVOSTI_PATH).convert("RGBA"))
    base.paste(Image.open(VAI_PATH).convert("RGBA"),     (0, 0), Image.open(VAI_PATH).convert("RGBA"))

    font = ImageFont.truetype(FONT_PATH, size=DATE_FONT_SIZE)
    draw = ImageDraw.Draw(base)
    bbox = draw.textbbox((0, 0), date_text, font=font)
    x = (width - (bbox[2] - bbox[0])) // 2
    y = int(height * DATE_Y_RATIO) - (bbox[3] - bbox[1]) // 2
    draw.text((x, y), date_text, fill=DATE_COLOR, font=font)

    base.convert("RGB").save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    generate_cover()
