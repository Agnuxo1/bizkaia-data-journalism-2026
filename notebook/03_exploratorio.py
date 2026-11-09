# SPDX-License-Identifier: Apache-2.0
# Research-Project: Hasta el ultimo centimo (Bizkaia minor contracts 2026)
# Research-Author: Francisco Angulo de Lafuente
# Research-ORCID: https://orcid.org/0009-0001-1634-7063
# Research-Date: 2026-11-08
"""Analisis EXPLORATORIO, posterior a ver E1-E7 (no preregistrado). Solo agregados."""
import sys, json, pathlib, runpy
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib_bizkaia import *
import numpy as np

PRE, POST = range(2014, 2018), range(2019, 2026)
SS = "de servicios|de suministros"


def ultimo(ds):
    best = {}
    for x in manifest(ds):
        d = leer(R / f"datos/raw/{ds}/{x['resource_id']}.csv")
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


def Bw(x, L, a=.03, b=.12):
    na = ((x >= (1 - a) * L) & (x <= L)).sum() / (a * L)
    nb = ((x >= (1 - a - b) * L) & (x < (1 - a) * L)).sum() / (b * L)
    return round(float(na / nb), 2) if nb > 0 else None


dfb = ultimo("contratos-menores")
post = dfb[dfb["ej"].isin(POST)]
ss = post[post["tipo"].str.contains(SS, case=False, na=False)]["imp"].values
ser = post[post["tipo"].str.contains("de servicios", case=False, na=False)]["imp"].values
res = {}
res["sensibilidad_B_18150_servicios"] = {f"a={a},b={b}": Bw(ser, 18150, a, b) for a, b in [(.01, .12), (.02, .12), (.03, .12), (.05, .12), (.03, .06), (.03, .2)]}
res["placebos_extra_servicios"] = {str(L): Bw(ser, L) for L in (9000, 11000, 13000, 14000, 17000)}
res["otros_limites_servicios"] = {"15000_exento_iva": Bw(ser, 15000), "16500_iva10": Bw(ser, 16500)}
res["cuantos_15000_exacto_o_justo"] = int(((ser >= 14990) & (ser <= 15000)).sum())

# Por que la razon bajo 18.150 ya era 2,40 antes de la reforma: desglose de la banda previa
pre_s = dfb[dfb["ej"].isin(PRE) & dfb["tipo"].str.contains("de servicios", case=False, na=False)]["imp"].values
b_pre = pre_s[(pre_s >= .97 * 18150) & (pre_s <= 18150)]
res["banda_pre_18150"] = {"n": int(len(b_pre)), "en_18000_exacto": int((np.round(b_pre, 2) == 18000).sum()),
                          "en_17900_18000": int(((b_pre >= 17900) & (b_pre <= 18000)).sum()),
                          "en_18140_18150": int(((b_pre >= 18140) & (b_pre <= 18150)).sum()),
                          "resto": int(len(b_pre) - ((b_pre >= 17900) & (b_pre <= 18000)).sum() - ((b_pre >= 18140) & (b_pre <= 18150)).sum())}

# Fechas con formato mixto: se comprueba cuantas se pueden leer
fv = post.get("FECHA ADJUDICACION")
f = pd.to_datetime(fv, errors="coerce", utc=True, format="mixed", dayfirst=True) if fv is not None else None
v = post[f.notna()].copy()
v["mes"] = f[f.notna()].dt.month
res["fecha_cobertura"] = {"lineas_con_fecha": int(len(v)), "lineas_total": int(len(post)), "por_ejercicio": {int(k): int(n) for k, n in v.groupby("ej").size().items()}}
m = v.groupby("mes")["imp"].agg(["size", "sum"])
res["por_mes"] = {int(k): {"n": int(r["size"]), "eur": round(float(r["sum"]), 2)} for k, r in m.iterrows()}
res["diciembre"] = {"pct_lineas": round(float(m.loc[12, "size"] / m["size"].sum() * 100), 2), "pct_eur": round(float(m.loc[12, "sum"] / m["sum"].sum() * 100), 2), "eur": round(float(m.loc[12, "sum"]), 2), "eur_total": round(float(m["sum"].sum()), 2)}
res["diciembre_por_ej"] = {int(y): round(float(g.loc[g["mes"] == 12, "imp"].sum() / g["imp"].sum() * 100), 2) for y, g in v.groupby("ej")}
banda = v[v["tipo"].str.contains(SS, case=False, na=False) & v["imp"].between(.97 * 18150, 18150)]
res["banda_diciembre_pct"] = round(float((banda["mes"] == 12).mean() * 100), 2)

# Peso de la banda
t = post[post["ej"].isin(POST)]["imp"].sum()
b = post[post["tipo"].str.contains(SS, case=False, na=False) & post["imp"].between(.97 * 18150, 18150)]["imp"].sum()
res["peso_banda"] = {"eur_banda": round(float(b), 2), "eur_total_post": round(float(t), 2), "pct": round(float(b / t * 100), 2), "lineas_total_post": int(len(post))}
res["pct_lineas_bajo_1000_post"] = round(float((post["imp"] < 1000).mean() * 100), 2)
res["eur_medio_anual_banda"] = round(float(b / 7), 2)
(R / "verificacion/exploratorio.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(res, ensure_ascii=False))
