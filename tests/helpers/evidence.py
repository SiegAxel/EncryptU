import os
import time
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageGrab


def _ensure_dir(out_dir: str) -> Path:
    p = Path(out_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p


def text_to_image(text: str, out_dir: str = 'reports/evidence', filename: str | None = None) -> str:
    """Render a long text into a PNG image and return the path.

    Useful to attach API JSON/text responses as evidence in reports.
    """
    out = _ensure_dir(out_dir)
    if filename is None:
        filename = f'response_{int(time.time() * 1000)}.png'
    path = out / filename

    # Basic layout settings
    font = ImageFont.load_default()
    max_width = 1000
    margin = 10
    
    # Get line height using getbbox (modern Pillow) or fallback to estimate
    try:
        bbox = font.getbbox('A')
        line_height = bbox[3] - bbox[1] + 2
    except (AttributeError, TypeError):
        line_height = 20  # Fallback estimate

    wrapped = []
    for paragraph in text.splitlines() or ['']:
        wrapped.extend(textwrap.wrap(paragraph, width=100) or [''])

    img_height = margin * 2 + line_height * max(1, len(wrapped))
    img = Image.new('RGB', (max_width, int(img_height)), color='white')
    draw = ImageDraw.Draw(img)

    y = margin
    for line in wrapped:
        draw.text((margin, y), line, fill='black', font=font)
        y += line_height

    img.save(path)
    return str(path)


def take_screenshot(out_dir: str = 'reports/evidence', filename: str | None = None) -> str:
    """Take a screenshot of the primary display (Windows-friendly) and return the path.

    Tries `ImageGrab.grab()` (Pillow) which works on Windows.
    """
    out = _ensure_dir(out_dir)
    if filename is None:
        filename = f'screenshot_{int(time.time() * 1000)}.png'
    path = out / filename

    try:
        img = ImageGrab.grab()
        img.save(path)
        return str(path)
    except Exception:
        # As fallback create a tiny image with an error message
        img = Image.new('RGB', (600, 30), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((5, 5), 'Could not take screenshot on this environment', fill='red')
        img.save(path)
        return str(path)
