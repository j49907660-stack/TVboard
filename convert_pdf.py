"""Fetch MOC PDF from a private Power Automate endpoint and publish JPG slides."""
import hashlib
import io
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'slides'
ENDPOINT = os.environ.get('MOC_PDF_ENDPOINT', '').strip()
if not ENDPOINT:
    raise SystemExit('Missing GitHub Actions secret MOC_PDF_ENDPOINT')

req = Request(ENDPOINT, data=b'', method='POST', headers={'Accept': 'application/pdf'})
with urlopen(req, timeout=90) as response:
    pdf_data = response.read(60 * 1024 * 1024 + 1)
if len(pdf_data) > 60 * 1024 * 1024:
    raise SystemExit('PDF exceeds 60 MB limit')
if not pdf_data.lstrip().startswith(b'%PDF-'):
    raise SystemExit('Power Automate response is not PDF. Check flow Response body.')

sha = hashlib.sha256(pdf_data).hexdigest()
OUT.mkdir(exist_ok=True)
manifest_file = OUT / 'slides.json'
if manifest_file.exists():
    try:
        old = json.loads(manifest_file.read_text(encoding='utf-8'))
        if old.get('sha256') == sha:
            print('PDF unchanged; keeping existing slides')
            raise SystemExit(0)
    except (ValueError, OSError):
        pass

pdf = fitz.open(stream=pdf_data, filetype='pdf')
if not pdf.page_count:
    raise SystemExit('PDF has no pages')
if pdf.page_count > 250:
    raise SystemExit('Too many pages (limit 250)')

names = []
for idx, page in enumerate(pdf):
    # Fit the longest side to 1920px; JPG is efficient for signage browsers.
    scale = min(2.0, 1920.0 / max(page.rect.width, page.rect.height))
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), colorspace=fitz.csRGB, alpha=False)
    name = 'slide_%03d.jpg' % (idx + 1)
    (OUT / name).write_bytes(pix.tobytes('jpeg', jpg_quality=83))
    names.append(name)

manifest = {'version': sha[:16], 'sha256': sha, 'slides': names}
# Remove obsolete slide images only after all new images are successfully written.
for old in OUT.glob('slide_*.jpg'):
    if old.name not in names:
        old.unlink()
manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Published %d slides, version %s' % (len(names), sha[:16]))
