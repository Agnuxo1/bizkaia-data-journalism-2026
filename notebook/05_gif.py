# SPDX-License-Identifier: Apache-2.0
# Research-Project: Hasta el ultimo centimo (Bizkaia minor contracts 2026)
# Research-Author: Francisco Angulo de Lafuente
# Research-ORCID: https://orcid.org/0009-0001-1634-7063
# Research-Date: 2026-11-08
"""GIF cientifico para el README: el histograma anual de servicios y suministros, con datos reales."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib_bizkaia import *
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
import io

best = {}
for x in manifest("contratos-menores"):
    d = leer(R / f"datos/raw/contratos-menores/{x['resource_id']}.csv")
    d = d.loc[:, ~d.columns.str.startswith("Unnamed")]
    d.columns = [c.split("/")[-1].strip() for c in d.columns]
    y, m = int(d["EJERCICIO"].iloc[0]), int(d["MES HASTA"].iloc[0])
    if y not in best or m > best[y][0]:
        best[y] = (m, d)
frames = []
e = np.arange(12000, 24001, 500)
for y in range(2014, 2026):
    d = best[y][1]
    x = eur(d[d["MODELO ADMIN DESCRIPCION"].str.contains("de servicios|de suministros", case=False, na=False)]["OBLIGACION"]).values
    L = 21780 if y < 2018 else 18150
    fig, ax = plt.subplots(figsize=(7.6, 3.6), dpi=100)
    h, _ = np.histogram(x, bins=e)
    ax.bar(e[:-1], h, width=430, align="edge", color=["#B4432B" if L - 500 <= l < L else "#7B8794" for l in e[:-1]])
    ax.axvline(L, color="#1F2933", lw=1.3)
    ax.set_ylim(0, 260); ax.set_xlim(12000, 24000)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(f"{y}: legal ceiling {L:,} EUR incl. VAT" + (" (2018: law changed in March)" if y == 2018 else ""), loc="left", fontsize=12, fontweight="bold", color="#1F2933")
    ax.set_xlabel("Minor-contract line amount (EUR, VAT incl.)"); ax.set_ylabel("Lines per 500 EUR")
    fig.text(.995, .01, "Francisco Angulo de Lafuente · ORCID 0009-0001-1634-7063 · Open Data Bizkaia", ha="right", fontsize=6.5, color="#616E7C")
    fig.tight_layout(rect=(0, .03, 1, 1))
    b = io.BytesIO(); fig.savefig(b, format="png"); plt.close(fig); b.seek(0)
    frames.append(Image.open(b).convert("P", palette=Image.ADAPTIVE))
out = R / "pieza/figuras/histograma_anual.gif"
frames[0].save(out, save_all=True, append_images=frames[1:], duration=900, loop=0, optimize=True)
print(out.stat().st_size)
