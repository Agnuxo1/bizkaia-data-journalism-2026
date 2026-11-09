# SPDX-License-Identifier: Apache-2.0
# Research-Project: Hasta el ultimo centimo (Bizkaia minor contracts 2026)
# Research-Author: Francisco Angulo de Lafuente
# Research-ORCID: https://orcid.org/0009-0001-1634-7063
# Research-Date: 2026-11-08
"""Analisis preregistrado (experiments/PREREG.md). Solo produce agregados; no exporta adjudicatarios."""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib_bizkaia import *
import numpy as np

SEED, NB = 20261108, 2000
PRE, POST = range(2014, 2018), range(2019, 2026)
SS = "de servicios|de suministros"


def ultimo_corte(ds):
    """Los ficheros trimestrales son acumulados: se conserva el ultimo corte de cada ejercicio."""
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
    return A, {y: v[0] for y, v in best.items()}


def cargar(ds):
    A, c = ultimo_corte(ds)
    A["imp"] = eur(A["OBLIGACION"])
    assert A["imp"].notna().all()
    A["tipo"] = A["MODELO ADMIN DESCRIPCION"]
    return A, c


def B(x, L):
    a = ((x >= .97 * L) & (x <= L)).sum() / (.03 * L)
    b = ((x >= .85 * L) & (x < .97 * L)).sum() / (.12 * L)
    return float(a / b) if b > 0 else float("nan")


def est(x, L, rng):
    x = np.asarray(x)
    v = [B(rng.choice(x, len(x)), L) for _ in range(NB)] if len(x) else [float("nan")]
    return {"B": round(B(x, L), 2),
            "ic95": [round(float(np.nanpercentile(v, 2.5)), 2), round(float(np.nanpercentile(v, 97.5)), 2)],
            "n_banda": int(((x >= .97 * L) & (x <= L)).sum()),
            "n_ref": int(((x >= .85 * L) & (x < .97 * L)).sum())}


def per(A, r, t):
    return A[A["ej"].isin(r) & A["tipo"].str.contains(t, case=False, na=False)]["imp"].values


def corte(x, L, w):
    return {"debajo": int(((x > L - w) & (x <= L)).sum()), "encima": int(((x > L) & (x <= L + w)).sum())}


rng = np.random.default_rng(SEED)
dfb, cortes = cargar("contratos-menores")
ifas, cortes_i = cargar("contratos-menores-del-ifas")
res = {"cortes_dfb": cortes, "cortes_ifas": cortes_i}


def bloque(A, t):
    return {"POST_18150": est(per(A, POST, t), 18150, rng), "PRE_18150": est(per(A, PRE, t), 18150, rng),
            "PRE_21780": est(per(A, PRE, t), 21780, rng), "POST_21780": est(per(A, POST, t), 21780, rng)}


res["E1_E2_dfb_servicios"] = bloque(dfb, "de servicios")
res["E2b_dfb_suministros"] = bloque(dfb, "de suministros")
res["E3_ifas_servicios"] = bloque(ifas, "de servicios")
res["E3b_ifas_suministros"] = bloque(ifas, "de suministros")
s = per(dfb, POST, "de servicios")
res["E4_placebos_post_servicios"] = {str(L): est(s, L, rng) for L in (16000, 20000, 12100)}
res["E5_obras_dfb"] = {"POST_48400": est(per(dfb, POST, "de obras"), 48400, rng),
                       "PRE_60500": est(per(dfb, PRE, "de obras"), 60500, rng),
                       "PRE_48400": est(per(dfb, PRE, "de obras"), 48400, rng),
                       "POST_60500": est(per(dfb, POST, "de obras"), 60500, rng)}
res["corte_18150_w500"] = {"servicios": corte(s, 18150, 500), "suministros": corte(per(dfb, POST, "de suministros"), 18150, 500)}

A_post = dfb[dfb["ej"].isin(POST)]
ss = A_post[A_post["tipo"].str.contains(SS, case=False, na=False)]
ban = ss[ss["imp"].between(.97 * 18150, 18150)]
res["banda_post"] = {"n": int(len(ban)), "eur": round(float(ban["imp"].sum()), 2),
                     "por_ejercicio": {int(k): int(v) for k, v in ban.groupby("ej")["imp"].size().items()}}
res["exacto"] = {str(v): int((ss["imp"].round(2) == v).sum()) for v in (18150.0, 18149.99, 18000.0, 15000.0, 14999.99)}

sobre = ss[ss["imp"] > 18150]
sob_ob = A_post[A_post["tipo"].str.contains("de obras", case=False, na=False) & (A_post["imp"] > 48400)]
res["sobre_limite_post"] = {"serv_sum_n": int(len(sobre)), "serv_sum_eur": round(float(sobre["imp"].sum()), 2),
                            "serv_sum_max": float(sobre["imp"].max()), "serv_sum_mediana": float(sobre["imp"].median()),
                            "serv_sum_gt_21780": int((sobre["imp"] > 21780).sum()), "obras_n": int(len(sob_ob)),
                            "obras_eur": round(float(sob_ob["imp"].sum()), 2),
                            "por_ejercicio": {int(k): int(v) for k, v in sobre.groupby("ej")["imp"].size().items()}}

base = ss[(ss["imp"] >= .9 * 18150) & (ss["imp"] <= 18150)]
g = base.groupby(["PERSONA ADJUDICATARIA", "OBJETO_CAS", "ej"])["imp"].agg(["size", "sum"])
r = g[g["size"] >= 2]
res["E6_repeticion"] = {"lineas_base": int(len(base)), "eur_base": round(float(base["imp"].sum()), 2), "pares_ge2": int(len(r)),
                        "lineas_en_pares": int(r["size"].sum()), "eur_en_pares": round(float(r["sum"].sum()), 2),
                        "pares_ge4": int((r["size"] >= 4).sum()), "max_lineas_par": int(r["size"].max())}
g2 = base.groupby(["PERSONA ADJUDICATARIA", "OBJETO_CAS"])["ej"].nunique()
res["E6_recurrencia"] = {"pares_3mas_anios": int((g2 >= 3).sum()), "pares_5mas_anios": int((g2 >= 5).sum()), "pares_total": int(len(g2))}
ad = A_post.groupby("PERSONA ADJUDICATARIA")["imp"].sum().sort_values(ascending=False)
res["concentracion_post"] = {"adjudicatarios": int(len(ad)), "top10_pct": round(float(ad.head(10).sum() / ad.sum() * 100), 2),
                             "top1pct_pct": round(float(ad.head(max(1, int(len(ad) * .01))).sum() / ad.sum() * 100), 2)}

ob = A_post["OBJETO_CAS"].value_counts()
res["objeto_post"] = {"valores_distintos": int(len(ob)), "lineas": int(len(A_post)), "top1": str(ob.index[0]), "top1_lineas": int(ob.iloc[0]),
                      "top5_lineas": int(ob.head(5).sum()), "top": {str(k): int(v) for k, v in ob.head(6).items()}}
res["objeto_banda"] = {str(k): int(v) for k, v in ban["OBJETO_CAS"].value_counts().head(6).items()}

ser = dfb[dfb["ej"].isin(range(2014, 2026))].groupby("ej")["imp"].agg(["size", "sum", "median"])
res["serie_dfb"] = {int(k): {"n": int(v["size"]), "eur": round(float(v["sum"]), 2), "mediana": round(float(v["median"]), 2)} for k, v in ser.iterrows()}
res["serie_ifas"] = {int(k): {"n": int(v["size"]), "eur": round(float(v["sum"]), 2)}
                     for k, v in ifas[ifas["ej"].isin(range(2014, 2026))].groupby("ej")["imp"].agg(["size", "sum"]).iterrows()}
bs = {}
for y in range(2014, 2026):
    x = dfb[(dfb["ej"] == y) & dfb["tipo"].str.contains(SS, case=False, na=False)]["imp"].values
    bs[y] = {"B18150": round(B(x, 18150), 2), "B21780": round(B(x, 21780), 2),
             "n_18150": int(((x >= .97 * 18150) & (x <= 18150)).sum()), "n_21780": int(((x >= .97 * 21780) & (x <= 21780)).sum())}
res["B_por_ejercicio"] = bs

if "FECHA ADJUDICACION" in dfb:
    f = pd.to_datetime(dfb["FECHA ADJUDICACION"], errors="coerce", utc=True)
    v = dfb[f.notna() & dfb["ej"].isin(POST)].copy()
    v["mes_adj"] = f[f.notna()].dt.month
    res["mes_adjudicacion"] = {"n": int(len(v)), "ejercicios": sorted(int(i) for i in v["ej"].unique()),
                               "por_mes": {int(k): int(n) for k, n in v["mes_adj"].value_counts().sort_index().items()},
                               "eur_por_mes": {int(k): round(float(n), 2) for k, n in v.groupby("mes_adj")["imp"].sum().items()}}

nm, _ = ultimo_corte("contratos-no-menores")
nm["obl"] = eur(nm["OBLIGACION"])
res["no_menores_obl"] = {int(k): round(float(v), 2) for k, v in nm[nm["ej"].isin(range(2014, 2026))].groupby("ej")["obl"].sum().items()}

gast = []
for x in manifest("liquidacion-del-presupuesto"):
    d = leer(R / f"datos/raw/liquidacion-del-presupuesto/{x['resource_id']}.csv")
    d.columns = [c.split("/")[-1].strip() for c in d.columns]
    if any(c.upper().startswith("OBLIGACI") for c in d.columns):
        gast.append(d)
g0 = pd.concat(gast, ignore_index=True).drop_duplicates()
ocol = [c for c in g0.columns if c.upper().startswith("OBLIGACI")][0]
g0["ej"] = g0["EJERCICIO"].astype(int)
g0["cap"] = g0["CAPITULO"].astype(str).str.replace('="', "", regex=False).str.replace('"', "", regex=False).str.strip()
g0["o"] = eur(g0[ocol])
res["liquidacion_columnas"] = list(g0.columns)
res["liquidacion_col_usada"] = ocol
res["cap2_obl"] = {int(k): round(float(v), 2) for k, v in g0[g0["cap"] == "2"].groupby("ej")["o"].sum().items()}
res["total_obl"] = {int(k): round(float(v), 2) for k, v in g0.groupby("ej")["o"].sum().items()}
res["liq_filas_por_ej"] = {int(k): int(v) for k, v in g0.groupby("ej").size().items()}

(R / "verificacion/resultados.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
print("ok")
