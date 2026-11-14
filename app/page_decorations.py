"""Page overlays and visual cropping; neither operation securely redacts content."""

from io import BytesIO
import math

from pypdf import PdfReader
from reportlab.pdfgen.canvas import Canvas

from app.pdf_engine import MergeError


def decorate(writer, operation, indices, options):
    text = options.get('text', '')
    if operation == 'watermark' and (not text.strip() or len(text) > 120 or not text.isascii() or any(ord(c) < 32 for c in text)):
        raise MergeError('Watermarks need 1–120 printable ASCII characters in this version.')
    try:
        margin = float(options.get('margin', '24'))
        if not math.isfinite(margin) or not 0 <= margin <= 500:
            raise ValueError
    except ValueError as exc:
        raise MergeError('Margin must be between 0 and 500 PDF points.') from exc
    for index in indices:
        page = writer.pages[index]
        if operation == 'crop':
            left, bottom, right, top = map(float, page.cropbox)
            if not all(math.isfinite(v) for v in (left, bottom, right, top)) or margin * 2 >= min(right - left, top - bottom):
                raise MergeError('Crop margin would remove the entire visible page.')
            page.cropbox.lower_left = (left + margin, bottom + margin)
            page.cropbox.upper_right = (right - margin, top - margin)
            continue
        # Normalize visual rotation before positioning overlays.
        page.transfer_rotation_to_content()
        width, height = float(page.cropbox.width), float(page.cropbox.height)
        if not all(math.isfinite(v) and 50 <= v <= 14400 for v in (width, height)):
            raise MergeError('Page dimensions are unsupported for text overlays.')
        output = BytesIO()
        canvas = Canvas(output, pagesize=(width, height))
        if operation == 'page-numbers':
            canvas.setFont('Helvetica', 10)
            canvas.drawCentredString(width / 2, 18, f'{index + 1} / {len(writer.pages)}')
        else:
            canvas.saveState()
            canvas.setFillAlpha(0.22)
            canvas.setFillColorRGB(0.3, 0.3, 0.3)
            canvas.setFont('Helvetica', min(36, width / max(len(text), 1)))
            canvas.translate(width / 2, height / 2)
            canvas.rotate(35)
            canvas.drawCentredString(0, 0, text)
            canvas.restoreState()
        canvas.save()
        overlay = PdfReader(BytesIO(output.getvalue())).pages[0]
        # Position inside the visible crop box, including chained crop operations.
        from pypdf import Transformation
        page.merge_transformed_page(overlay, Transformation().translate(float(page.cropbox.left), float(page.cropbox.bottom)))
