import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

SAMPLE_DIR = Path("sample_media")
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

# 1. Generate sample_screenplay.txt
screenplay_text = """--- PAGE 1 ---
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

(SAMPLE_DIR / "sample_screenplay.txt").write_text(screenplay_text, encoding="utf-8")

# 2. Generate sample_screenplay.pdf
pdf_path = SAMPLE_DIR / "sample_screenplay.pdf"
c = canvas.Canvas(str(pdf_path), pagesize=letter)
c.setFont("Courier", 10)

lines = screenplay_text.split("\n")
y = 750
for line in lines:
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

# 3. Generate sample_set_photo.jpg
img = Image.new("RGB", (1280, 720), color=(26, 32, 44))
draw = ImageDraw.Draw(img)

# Draw simulated film scene elements
# Living room wall
draw.rectangle([50, 50, 1230, 670], fill=(45, 55, 72), outline=(74, 85, 104), width=3)

# Wall art (Modern Copyrighted Painting)
draw.rectangle([100, 100, 450, 400], fill=(221, 107, 32), outline=(255, 255, 255), width=4)
draw.text((120, 150), "[ COPYRIGHTED ARTWORK ]\nModern Abstract Oil Canvas\nArtist: Living Contemporary\n(Requires Artist Release)", fill=(255, 255, 255))

# Desk / Table
draw.rectangle([200, 450, 1100, 650], fill=(29, 36, 48), outline=(90, 105, 125), width=2)

# Branded Prop 1: Apple MacBook
draw.rectangle([300, 420, 550, 540], fill=(160, 174, 192), outline=(255, 255, 255), width=2)
draw.text((320, 460), "[ TRADEMARK_LOGO ]\nApple MacBook Pro\n(Glowing Apple Logo)", fill=(0, 0, 0))

# Branded Prop 2: Starbucks Cup
draw.rectangle([650, 400, 750, 530], fill=(255, 255, 255), outline=(47, 133, 90), width=3)
draw.text((660, 450), "[ LOGO ]\nStarbucks\nSiren Cup", fill=(47, 133, 90))

# Wardrobe item: Nike Hoodie
draw.rectangle([850, 250, 1150, 580], fill=(74, 85, 104), outline=(226, 232, 240), width=2)
draw.text((880, 320), "[ HERO WARDROBE ]\nActor Hoodie\nNIKE 'SWOOSH' Logo\nChest Placement", fill=(255, 255, 255))

# Watermark header
draw.text((50, 20), "CINECLEAR AI - SAMPLE PRODUCTION SET STILL (LEGAL AUDIT TEST)", fill=(160, 174, 192))

img.save(str(SAMPLE_DIR / "sample_set_photo.jpg"), quality=95)
print("Sample media generated successfully!")
