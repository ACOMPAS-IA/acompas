"""PDF: capa de texto y rasterizado (ACO-035).

Una página con 100 caracteres o más —valor inicial configurable, ADR-023:51—
se lee sin OCR; por debajo de eso se rasteriza a 300 ppp y se reconoce
(ADR-023:44). El original se trata en memoria y no se guarda.
"""

import pypdfium2 as pdfium

RENDER_DPI = 300


def open_pdf(data: bytes) -> pdfium.PdfDocument:
    """Abre el PDF en memoria. Un PDF cifrado o corrupto lanza `PdfiumError`."""
    return pdfium.PdfDocument(data)


def page_text(page) -> str:
    """Texto de la capa del PDF, sin OCR."""
    return page.get_textpage().get_text_range()


def render_page(page, dpi: int = RENDER_DPI):
    """Rasteriza una página a la resolución indicada y la devuelve como PIL."""
    bitmap = page.render(scale=dpi / 72)
    return bitmap.to_pil()
