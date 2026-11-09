"""Écrans MK2 : image Pillow 1 bit → rapports HID.

Format (cabl, `GDisplayMaschineMK2` et `MaschineMK2::sendFrame`) : 256 × 64,
un octet = 8 pixels horizontaux, bit de poids fort à gauche, 32 octets par
ligne, 2048 octets par écran. Envoi en 8 tranches de 8 lignes, chacune
précédée de l'en-tête `E0|écran, 0, 0, y, 0, 0x20, 0, 0x08, 0`.
"""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

WIDTH = 256
HEIGHT = 64
ROW_BYTES = WIDTH // 8
FRAME_BYTES = ROW_BYTES * HEIGHT
CHUNK_ROWS = 8
N_DISPLAYS = 2


class DisplayError(Exception):
    """Image ou index d'écran invalide."""


def new_image() -> Image.Image:
    return Image.new("1", (WIDTH, HEIGHT), 0)


def image_to_frame(image: Image.Image) -> bytes:
    """Pixels allumés = bits à 1 ; le mode « 1 » de Pillow a déjà ce tassement."""
    if image.size != (WIDTH, HEIGHT):
        raise DisplayError(f"image {image.size}, attendu {(WIDTH, HEIGHT)}")
    return image.convert("1").tobytes()


def frame_reports(display: int, frame: bytes) -> list[bytes]:
    if not 0 <= display < N_DISPLAYS:
        raise DisplayError(f"écran {display} inexistant")
    if len(frame) != FRAME_BYTES:
        raise DisplayError(f"trame de {len(frame)} octets, attendu {FRAME_BYTES}")
    chunk = ROW_BYTES * CHUNK_ROWS
    return [
        bytes([0xE0 | display, 0, 0, y, 0, ROW_BYTES, 0, CHUNK_ROWS, 0])
        + frame[y * ROW_BYTES : y * ROW_BYTES + chunk]
        for y in range(0, HEIGHT, CHUNK_ROWS)
    ]


def mire(display: int) -> Image.Image:
    """Mire : cadre, coins, damier, bandes de largeur 1-2-4-8 px, texte."""
    img = new_image()
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=1)
    for x, y in ((2, 2), (WIDTH - 6, 2), (2, HEIGHT - 6), (WIDTH - 6, HEIGHT - 6)):
        d.rectangle((x, y, x + 3, y + 3), fill=1)
    for y in range(8, 32):
        for x in range(8, 40):
            if (x + y) % 2 == 0:
                img.putpixel((x, y), 1)
    x = 48
    for w in (1, 2, 4, 8):
        for _ in range(3):
            d.rectangle((x, 8, x + w - 1, 31), fill=1)
            x += 2 * w
        x += 6
    font = ImageFont.load_default()
    d.text((8, 38), f"mk-brain  ecran {display}  {WIDTH}x{HEIGHT}", font=font, fill=1)
    d.text((8, 50), "<- gauche" if display == 0 else "droite ->", font=font, fill=1)
    return img


TEXT_SIZE = 13  # police vectorielle intégrée à Pillow (Aileron), présente aussi sur le Pi
TEXT_LINES = 5  # 64 / 5 = 12,8 px par ligne
TEXT_TOP = -3  # 3 px vides en tête de police : descendantes de la 5e ligne entières


def text_image(lines: list[str], bold: frozenset[int] = frozenset()) -> Image.Image:
    """Les 5 dernières lignes ; `bold` = index (dans `lines`) des libellés graissés d'1 px.

    Police vectorielle maigre en 13 : la police bitmap se lisait mal (6 pris pour 8).
    """
    img = new_image()
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=TEXT_SIZE)
    first = max(0, len(lines) - TEXT_LINES)
    for i, line in enumerate(lines[first:]):
        y = TEXT_TOP + round(HEIGHT * i / TEXT_LINES)
        for dx in (0, 1) if first + i in bold else (0,):
            d.text((2 + dx, y), line, font=font, fill=1)
    return img


def big_text_image(text: str, size: int = 44) -> Image.Image:
    """Texte en très gros, centré (division du note repeat, compte à rebours)."""
    img = new_image()
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=size)
    left, top, right, bottom = d.textbbox((0, 0), text, font=font)
    x = (WIDTH - (right - left)) // 2 - left
    y = (HEIGHT - (bottom - top)) // 2 - top
    d.text((x, y), text, font=font, fill=1)
    return img
