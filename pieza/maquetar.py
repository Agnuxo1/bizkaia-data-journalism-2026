# SPDX-License-Identifier: Apache-2.0
"""Convierte REPORTAJE.md e INFORME_TECNICO.md en PDF (pandoc + Edge sin cabeceras). Marca visible de autoria."""
import pathlib, subprocess, sys, re

P = pathlib.Path(__file__).parent
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CSS = """
@page { size: A4; margin: 22mm 21mm 20mm 21mm; }
:root { color-scheme: light; }
body { font-family: Georgia, 'Times New Roman', serif; color: #1F2933; font-size: 11.2pt; line-height: 1.55; background: #fff; }
h1 { font-family: 'Segoe UI', Arial, sans-serif; font-size: 34pt; line-height: 1.08; margin: 0 0 8pt; letter-spacing: -.5pt; }
h2 { font-family: 'Segoe UI', Arial, sans-serif; font-size: 15pt; line-height: 1.25; margin: 20pt 0 6pt; break-after: avoid; }
h1 + h2 { font-weight: 400; font-size: 15.5pt; color: #3E4C59; margin-top: 0; }
p { margin: 0 0 9pt; orphans: 3; widows: 3; }
a { color: #8A3220; text-decoration: none; border-bottom: .4pt solid #C98E7F; }
img { width: 100%; display: block; margin: 8pt 0 2pt; }
figure { margin: 0; break-inside: avoid; } figcaption { display: none; }
.figure-caption-group { break-inside: avoid; page-break-inside: avoid; }
tr { break-inside: avoid; }
th:first-child, td:first-child { min-width: 22pt; overflow-wrap: normal; }
ul { break-inside: avoid; }
em { color: #52606D; }
table { border-collapse: collapse; width: 100%; font-family: 'Segoe UI', Arial, sans-serif; font-size: 8.8pt; margin: 8pt 0 12pt; }
th, td { border-bottom: .5pt solid #CBD2D9; padding: 4pt 5pt; text-align: left; vertical-align: top; overflow-wrap: anywhere; }
th { color: #52606D; font-weight: 600; }
hr { border: 0; border-top: .6pt solid #CBD2D9; margin: 16pt 0; }
code { font-family: Consolas, monospace; font-size: 9pt; }
"""


def sellar(pdf):
    """Pie visible con autoria y pagina en cada hoja."""
    import io
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    r = PdfReader(str(pdf)); w = PdfWriter(); n = len(r.pages)
    for i, pg in enumerate(r.pages, 1):
        W, H = float(pg.mediabox.width), float(pg.mediabox.height)
        b = io.BytesIO(); c = canvas.Canvas(b, pagesize=(W, H)); c.setFont("Helvetica", 7.5); c.setFillColorRGB(.48, .53, .58)
        c.drawRightString(W - 59, 26, f"Francisco Angulo de Lafuente - ORCID 0009-0001-1634-7063 - {i}/{n}"); c.save(); b.seek(0)
        pg.merge_page(PdfReader(b).pages[0]); w.add_page(pg)
    w.add_metadata({"/Author": "Francisco Angulo de Lafuente", "/Title": pdf.stem})
    with open(pdf, "wb") as f:
        w.write(f)


for nombre, titulo in (("REPORTAJE", "Hasta el último céntimo"), ("INFORME_TECNICO", "Informe técnico")):
    html = P / f"{nombre}.html"
    (P / "_estilo.css").write_text(CSS, encoding="utf-8")
    subprocess.run(["pandoc", str(P / f"{nombre}.md"), "-f", "gfm", "-t", "html5", "-s", "--metadata", f"title={titulo}", "-V", "title=", "--css", "_estilo.css",
                    "-V", "lang=es", "-o", str(html)], check=True, cwd=P)
    t = html.read_text(encoding="utf-8")
    t = t.replace('<header id="title-block-header">', '<header id="title-block-header" style="display:none">')
    t = re.sub(r'(<p><img\b[^>]*>\s*</p>)(\s*<p><em>Figura\s+\d+\..*?</em></p>)',
               r'<div class="figure-caption-group">\1\2</div>', t, flags=re.S)
    html.write_text(t, encoding="utf-8")
    pdf = P / f"{nombre}.pdf"
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", f"--user-data-dir=D:/PROJECTS/.cognition/bizkaia-rescue-20261109/tmp/edge", html.as_uri()], check=True, timeout=120)
    sellar(pdf)
    print(nombre, pdf.stat().st_size)
