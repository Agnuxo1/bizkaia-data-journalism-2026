# SPDX-License-Identifier: Apache-2.0
# Research-Project: Hasta el ultimo centimo (Bizkaia minor contracts 2026)
# Research-Author: Francisco Angulo de Lafuente
# Research-ORCID: https://orcid.org/0009-0001-1634-7063
# Research-Date: 2026-11-08
"""Figuras del reportaje. Solo agregados; marca de autoria visible."""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib_bizkaia import *
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker

ACC, BASE, INK, MUTED, GRID = "#B4432B", "#7B8794", "#1F2933", "#616E7C", "#E4E7EB"
FIRMA = "Francisco Angulo de Lafuente · ORCID 0009-0001-1634-7063 · Datos: Open Data Bizkaia"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": .8, "axes.axisbelow": True})
OUT = R / "pieza/figuras"
PRE, POST = range(2014, 2018), range(2019, 2026)


def ultimo():
    best = {}
    for x in manifest("contratos-menores"):
        d = leer(R / f"datos/raw/contratos-menores/{x['resource_id']}.csv")
        d = d.loc[:, ~d.columns.str.startswith("Unnamed")]
        d.columns = [c.split("/")[-1].strip() for c in d.columns]
        y, m = int(d["EJERCICIO"].iloc[0]), int(d["MES HASTA"].iloc[0])
        if y not in best or m > best[y][0]:
            best[y] = (m, d)
    A = pd.concat([v[1] for v in best.values()], ignore_index=True)
    A["ej"] = A["EJERCICIO"].astype(int)
    A["imp"] = eur(A["OBLIGACION"])
    A["tipo"] = A["MODELO ADMIN DESCRIPCION"]
    return A


def firma(fig):
    fig.text(.995, .006, FIRMA, ha="right", va="bottom", fontsize=7.5, color=MUTED)


def eje_eur(ax):
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", ".") + " €"))


A = ultimo()
ser = A[A["tipo"].str.contains("de servicios", case=False, na=False)]
post, pre = ser[ser["ej"].isin(POST)]["imp"].values, ser[ser["ej"].isin(PRE)]["imp"].values

# Figura 1: la pared
fig, ax = plt.subplots(figsize=(9.2, 4.6), dpi=170)
e = np.arange(8000, 22001, 250)
h, _ = np.histogram(post, bins=e)
c = [ACC if (l >= 17500 and l < 18150) else BASE for l in e[:-1]]
ax.bar(e[:-1], h, width=210, align="edge", color=c)
ax.axvline(18150, color=INK, lw=1.2)
ax.annotate("Límite legal con IVA: 18.150 €\n0 líneas por encima", xy=(18150, h.max() * .86), xytext=(18650, h.max() * .86), fontsize=10.5, color=INK, va="center", arrowprops=dict(arrowstyle="-", color=INK, lw=.8))
ax.annotate("12.100 € = 10.000 € + IVA\n(número redondo)", xy=(12150, h[(12000 - 8000) // 250]), xytext=(9000, h.max() * .55), fontsize=10, color=MUTED, arrowprops=dict(arrowstyle="-", color=MUTED, lw=.7))
ax.set_ylabel("Líneas contables por tramo de 250 €")
ax.set_xlabel("Importe de la obligación reconocida, IVA incluido")
eje_eur(ax)
ax.set_title("Contratos menores de servicios de la Diputación, 2019-2025", loc="left", color=INK, fontsize=13, fontweight="bold")
fig.tight_layout(rect=(0, .03, 1, 1)); firma(fig); fig.savefig(OUT / "fig1_pared.png"); plt.close(fig)

# Figura 2: experimento natural (pequenos multiplos con escala propia por densidad)
fig, axs = plt.subplots(2, 1, figsize=(9.2, 5.6), dpi=170, sharex=True)
e = np.arange(12000, 24001, 250)
for ax, x, lab, L in ((axs[0], pre, "2014-2017 · límite 21.780 €", 21780), (axs[1], post, "2019-2025 · límite 18.150 €", 18150)):
    h, _ = np.histogram(x, bins=e)
    ax.bar(e[:-1], h / len(x[x >= 3000]) * 100, width=210, align="edge", color=[ACC if (L - 650 <= l < L) else BASE for l in e[:-1]])
    ax.axvline(L, color=INK, lw=1.2)
    ax.set_title(lab, loc="left", color=INK, fontsize=11.5, fontweight="bold")
    ax.set_ylabel("% de líneas ≥ 3.000 €")
eje_eur(axs[1])
axs[1].set_xlabel("Importe, IVA incluido")
fig.tight_layout(rect=(0, .03, 1, 1)); firma(fig); fig.savefig(OUT / "fig2_experimento.png"); plt.close(fig)

# Figura 3: lineas en banda por ejercicio
r = json.load(open(R / "verificacion/resultados.json", encoding="utf-8"))["B_por_ejercicio"]
ys = sorted(int(k) for k in r)
fig, ax = plt.subplots(figsize=(9.2, 4), dpi=170)
ax.plot(ys, [r[str(y)]["n_21780"] for y in ys], color=BASE, lw=2, marker="o", ms=7, mec="white")
ax.plot(ys, [r[str(y)]["n_18150"] for y in ys], color=ACC, lw=2, marker="o", ms=7, mec="white")
ax.axvline(2018.19, color=INK, lw=1, ls=(0, (3, 3)))
ax.text(2018.27, 214, "Marzo de 2018: entra en vigor\nla nueva ley", fontsize=10, color=INK, va="top")
ax.text(2025.1, r["2025"]["n_18150"], "Justo bajo\n18.150 €", fontsize=10, color=INK, va="center")
ax.text(2014.0, r["2014"]["n_21780"] + 34, "Justo bajo 21.780 €", fontsize=10, color=INK)
ax.set_xlim(2013.7, 2026.1); ax.set_ylim(0, 225)
ax.set_xticks(ys)
ax.set_ylabel("Líneas en el 3 % bajo cada cifra")
ax.set_title("Las líneas pegadas al límite cambian de cifra al cambiar la ley", loc="left", color=INK, fontsize=13, fontweight="bold")
fig.tight_layout(rect=(0, .03, 1, 1)); firma(fig); fig.savefig(OUT / "fig3_serie.png"); plt.close(fig)

# Figura 4: gasto por mes
ex = json.load(open(R / "verificacion/exploratorio.json", encoding="utf-8"))["por_mes"]
ms = list(range(1, 13)); v = [ex[str(m)]["eur"] / 1e6 for m in ms]
fig, ax = plt.subplots(figsize=(9.2, 3.8), dpi=170)
ax.bar(ms, v, width=.72, color=[ACC if m == 12 else BASE for m in ms])
ax.set_xticks(ms); ax.set_xticklabels("ene feb mar abr may jun jul ago sep oct nov dic".split())
ax.grid(axis="x", visible=False)
ax.set_ylabel("Millones de euros")
ax.set_title("Gasto en contratos menores por mes de adjudicación, 2019-2025 acumulado", loc="left", color=INK, fontsize=13, fontweight="bold")
fig.tight_layout(rect=(0, .03, 1, 1)); firma(fig); fig.savefig(OUT / "fig4_diciembre.png"); plt.close(fig)
print("ok")
