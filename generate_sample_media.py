from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

SAMPLE_DIR = Path("sample_media")

SCREENPLAY_TEXT = """--- PAGE 1 ---
SCENE 1: INT. PENTHOUSE OFFICE - NIGHT

MARK (30s), wearing an athletic black hoodie with a visible NIKE 'SWOOSH' on the chest, sits at a glass desk.
On the table is an open APPLE MACBOOK PRO glowing in the dim light and a half-empty STARBUCKS SIREN coffee cup.

MARK
(dialing his iPhone)
The deal closes tonight. No loose ends.

He scribbles a contact number on a hotel notepad: (212) 555-8392.

--- PAGE 2 ---
SCENE 2: INT. ART GALLERY - DAY

ELENA (40s) stands before a massive, newly painted contemporary abstract mural titled "NEON CHAOS 2024" by local street artist KAIRO.

ELENA
We don't have the artist's release yet. If this ends up in the final cut, legal will have our heads.

MARK
Nobody notices the background.

ELENA
E&O insurance won't clear the trailer.

--- PAGE 3 ---
SCENE 3: EXT. PARIS HIGHWAY - NIGHT

Mark speeds down the boulevard. Through the rear windshield, the EIFFEL TOWER ILLUMINATED NIGHT LIGHTING beams brightly across the skyline.

RADIO DJ (V.O.)
And now, classic rock for your midnight drive...

TRACK: "Immigrant Song" by Led Zeppelin begins blasting through the car speakers.

FADE OUT.
"""


def _write_screenplay_pdf(pdf_path: Path, screenplay_text: str) -> None:
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.setFont("Courier", 10)
    y = 750
    for line in screenplay_text.split("\n"):
        if line.startswith("--- PAGE"):
            if y < 700:
                c.showPage()
                c.setFont("Courier", 10)
                y = 750
            c.drawString(50, y, line)
            y -= 20
        else:
            c.drawString(50, y, line)
            y -= 14
            if y < 50:
                c.showPage()
                c.setFont("Courier", 10)
                y = 750
    c.save()


def _write_sample_set_photo(jpg_path: Path) -> None:
    img = Image.new("RGB", (1280, 720), color=(26, 32, 44))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 1230, 670], fill=(45, 55, 72), outline=(74, 85, 104), width=3)
    draw.rectangle([100, 100, 450, 400], fill=(221, 107, 32), outline=(255, 255, 255), width=4)
    draw.text((120, 150), "[ COPYRIGHTED ARTWORK ]\nModern Abstract Oil Canvas\nArtist: Living Contemporary\n(Requires Artist Release)", fill=(255, 255, 255))
    draw.rectangle([200, 450, 1100, 650], fill=(29, 36, 48), outline=(90, 105, 125), width=2)
    draw.rectangle([300, 420, 550, 540], fill=(160, 174, 192), outline=(255, 255, 255), width=2)
    draw.text((320, 460), "[ TRADEMARK_LOGO ]\nApple MacBook Pro\n(Glowing Apple Logo)", fill=(0, 0, 0))
    draw.rectangle([650, 400, 750, 530], fill=(255, 255, 255), outline=(47, 133, 90), width=3)
    draw.text((660, 450), "[ LOGO ]\nStarbucks\nSiren Cup", fill=(47, 133, 90))
    draw.rectangle([850, 250, 1150, 580], fill=(74, 85, 104), outline=(226, 232, 240), width=2)
    draw.text((880, 320), "[ HERO WARDROBE ]\nActor Hoodie\nNIKE 'SWOOSH' Logo\nChest Placement", fill=(255, 255, 255))
    draw.text((50, 20), "CINECLEAR AI - SAMPLE PRODUCTION SET STILL (LEGAL AUDIT TEST)", fill=(160, 174, 192))
    img.save(str(jpg_path), quality=95)


def ensure_sample_media(sample_dir: Optional[Path] = None, force: bool = False) -> Path:
    """Creates bundled Hollywood sample assets if they are missing (e.g. PDFs gitignored)."""
    target = Path(sample_dir) if sample_dir is not None else SAMPLE_DIR
    target.mkdir(parents=True, exist_ok=True)

    txt_path = target / "sample_screenplay.txt"
    pdf_path = target / "sample_screenplay.pdf"
    jpg_path = target / "sample_set_photo.jpg"

    if force or not txt_path.exists():
        txt_path.write_text(SCREENPLAY_TEXT, encoding="utf-8")
    if force or not pdf_path.exists():
        _write_screenplay_pdf(pdf_path, SCREENPLAY_TEXT)
    if force or not jpg_path.exists():
        _write_sample_set_photo(jpg_path)
    return target


if __name__ == "__main__":
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    ensure_sample_media(SAMPLE_DIR, force=True)
    print("Sample media generated successfully!")
