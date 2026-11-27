"""Genera los nueve renders sintéticos de la calibración (ACO-035).

Tres documentos de ACO-051 por tres formas de entrega: PDF escaneado a
300 ppp, foto en JPG y PDF con capa de texto (ADR-023:25). Los seis primeros
pasan por OCR; los tres últimos son el control del extractor.

Uso:

    python -m tests.anonymization.renders.generate --font /ruta/DejaVuSans.ttf

El comando reescribe los nueve ficheros y, si se pide, el README con sus
hashes. No se ejecuta durante los tests: los renders se commitean para que la
medición sea reproducible sin fuente ni `reportlab` en la imagen.
"""

import argparse
import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

DOCUMENTS = (
    "informe_patologia_01",
    "analitica_01",
    "carta_oncologia_01",
)

RENDERS_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = RENDERS_DIR.parents[1] / "synthetic_data" / "documents"

# A4 a 300 ppp: el rasterizado que pide ADR-023:44.
DPI = 300
PAGE_WIDTH = 2480
PAGE_HEIGHT = 3508

FONT_SIZE = 46  # ≈ 11 pt a 300 ppp: el cuerpo de un informe real
LINE_HEIGHT = 62
MARGIN = 180

# La foto tiene que caber entera en una sola imagen: un JPG no tiene páginas.
# Se compone con cuerpo menor que el escaneo y el generador comprueba que los
# tres documentos de ACO-051 caben en una página.
PHOTO_FONT_SIZE = 20
PHOTO_LINE_HEIGHT = 30


def read_document(name: str) -> str:
    """Texto del documento sintético de ACO-051."""
    return (DOCUMENTS_DIR / f"{name}.txt").read_text(encoding="utf-8")


def wrap(text: str, font, width: int) -> list[str]:
    """Reparte el texto en líneas que caben en `width` píxeles."""
    lines: list[str] = []
    for paragraph in text.split("\n"):
        current = ""
        for word in paragraph.split():
            candidate = f"{current} {word}".strip()
            if font.getlength(candidate) <= width:
                current = candidate
                continue
            if current:
                lines.append(current)
            current = word
        lines.append(current)
    return lines


def render_pages(text: str, font, line_height: int = LINE_HEIGHT) -> list[Image.Image]:
    """Rasteriza el texto en páginas A4 a 300 ppp."""
    lines = wrap(text, font, PAGE_WIDTH - 2 * MARGIN)
    per_page = (PAGE_HEIGHT - 2 * MARGIN) // line_height

    pages: list[Image.Image] = []
    for start in range(0, len(lines), per_page):
        image = Image.new("L", (PAGE_WIDTH, PAGE_HEIGHT), color=255)
        draw = ImageDraw.Draw(image)
        for offset, line in enumerate(lines[start : start + per_page]):
            draw.text(
                (MARGIN, MARGIN + offset * line_height),
                line,
                fill=0,
                font=font,
            )
        pages.append(image)
    return pages


def write_scanned_pdf(pages: list[Image.Image], target: Path) -> None:
    """PDF sin capa de texto: cada página es la imagen, como un escaneo."""
    first, *rest = pages
    first.save(target, "PDF", resolution=DPI, save_all=True, append_images=rest)


def write_photo(pages: list[Image.Image], target: Path) -> None:
    """Foto de la primera página en JPG.

    El JPG no tiene páginas, así que quien lo escribe ya se ha asegurado de que
    el documento cabe entero en una.
    """
    pages[0].convert("RGB").save(target, "JPEG", quality=90)


def write_text_layer_pdf(text: str, target: Path) -> None:
    """PDF con el texto en su capa, para el control del extractor."""
    document = canvas.Canvas(str(target), pagesize=A4)
    width, height = A4
    leading = 14

    document.setFont("Helvetica", 10)
    y = height - 60
    for line in wrap_text(text, 10, width - 120):
        if y < 60:
            document.showPage()
            document.setFont("Helvetica", 10)
            y = height - 60
        document.drawString(60, y, line)
        y -= leading
    document.showPage()
    document.save()


def wrap_text(text: str, size: int, width: float) -> list[str]:
    """Reparte el texto en líneas de ancho `width` puntos."""
    from reportlab.pdfbase.pdfmetrics import stringWidth

    lines: list[str] = []
    for paragraph in text.split("\n"):
        current = ""
        for word in paragraph.split():
            candidate = f"{current} {word}".strip()
            if stringWidth(candidate, "Helvetica", size) <= width:
                current = candidate
                continue
            if current:
                lines.append(current)
            current = word
        lines.append(current)
    return lines


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--font",
        default="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        help="TTF con la que se dibujan los renders de imagen",
    )
    parser.add_argument(
        "--readme",
        action="store_true",
        help="reescribe README.md con los hashes generados",
    )
    args = parser.parse_args()

    font = ImageFont.truetype(args.font, FONT_SIZE)
    photo_font = ImageFont.truetype(args.font, PHOTO_FONT_SIZE)

    targets: list[Path] = []
    for name in DOCUMENTS:
        text = read_document(name)
        pages = render_pages(text, font)
        photo_pages = render_pages(text, photo_font, PHOTO_LINE_HEIGHT)
        if len(photo_pages) != 1:
            raise SystemExit(
                f"{name}: la foto ocupa {len(photo_pages)} páginas; un JPG solo "
                "puede tener una"
            )

        scanned = RENDERS_DIR / f"{name}_escaneo.pdf"
        photo = RENDERS_DIR / f"{name}_foto.jpg"
        layer = RENDERS_DIR / f"{name}_capa.pdf"

        write_scanned_pdf(pages, scanned)
        write_photo(photo_pages, photo)
        write_text_layer_pdf(text, layer)
        targets.extend([scanned, photo, layer])

    for path in targets:
        print(f"{sha256(path)}  {path.name}")

    if args.readme:
        write_readme(targets, args.font)


def write_readme(targets: list[Path], font_path: str) -> None:
    """README con composición, procedencia y hashes."""
    import reportlab

    try:
        import pytesseract

        tesseract = pytesseract.get_tesseract_version()
    except Exception:  # pragma: no cover - depende de la máquina
        tesseract = "no disponible"

    lines = [
        "# Renders de calibración (ACO-035)",
        "",
        "Documentos sintéticos de ACO-051 en las tres formas de entrega de",
        "ADR-023:25. Los `_escaneo.pdf` y `_foto.jpg` pasan por OCR; los",
        "`_capa.pdf` son el control del extractor y no deben tocar Tesseract.",
        "",
        "| Dato | Valor |",
        "| --- | --- |",
        f"| Fuente | `{Path(font_path).name}` |",
        f"| reportlab | {reportlab.Version} |",
        "| Resolución | %d ppp (%d×%d px) |" % (DPI, PAGE_WIDTH, PAGE_HEIGHT),
        "",
        f"Versión calibrada: tesseract {tesseract}.",
        "Si la CI instala otra, avisa y la tabla se rehace (ADR-023:30).",
        "",
        "Los escaneos son PDF de una o dos páginas. Las fotos son un único JPG",
        "con el documento entero, en cuerpo menor para que quepa en una página.",
        "",
        "Se regeneran con:",
        "",
        "```",
        "cd backend",
        "python -m tests.anonymization.renders.generate --readme",
        "```",
        "",
        "## Hashes",
        "",
        "| Fichero | SHA-256 |",
        "| --- | --- |",
    ]
    for path in targets:
        lines.append(f"| `{path.name}` | `{sha256(path)}` |")
    lines.append("")
    (RENDERS_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
