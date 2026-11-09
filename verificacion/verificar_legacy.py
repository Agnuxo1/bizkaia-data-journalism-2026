# SPDX-License-Identifier: Apache-2.0
"""Capa de verificacion: cada numero del reportaje debe tener una afirmacion que lo recalcule.

Uso: python verificar.py [archivo.md]        verifica el texto
     python verificar.py --ablacion          siembra errores y mide deteccion frente al control
"""
import json, re, sys, pathlib, random

V = pathlib.Path(__file__).parent
R = json.load(open(V / "resultados.json", encoding="utf-8"))
E = json.load(open(V / "exploratorio.json", encoding="utf-8"))
ART = V.parent / "pieza/REPORTAJE.md"


def es(x, d=2):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


s, sm, b = R["E1_E2_dfb_servicios"], R["E2b_dfb_suministros"], R["banda_post"]
ob, pl, ifa = R["E5_obras_dfb"], R["E4_placebos_post_servicios"], R["E3_ifas_servicios"]
serie, rep, rec, conc, obj = R["serie_dfb"], R["E6_repeticion"], R["E6_recurrencia"], R["concentracion_post"], R["objeto_post"]
dic, pmes = E["diciembre"], E["por_mes"]
extras = E["placebos_extra_servicios"]
tot = E["peso_banda"]["eur_total_post"]
n_total = sum(v["n"] for v in serie.values()) + 1676  # 2026 (corte de junio) incluido en las 42.074


def ic(x):
    return es(x["ic95"][0]), es(x["ic95"][1])


CLAIMS = [
    ("lineas_18149_99", "15", R["exacto"]["18149.99"] == 15),
    ("total_lineas", "42.074", n_total == 42074),
    ("serv_debajo", "1.105", R["corte_18150_w500"]["servicios"]["debajo"] == 1105),
    ("serv_encima", "0", R["corte_18150_w500"]["servicios"]["encima"] == 0),
    ("sum_debajo", "101", R["corte_18150_w500"]["suministros"]["debajo"] == 101),
    ("sum_encima", "0", R["corte_18150_w500"]["suministros"]["encima"] == 0),
    ("B_post", es(s["POST_18150"]["B"]), True), ("B_post_ic0", ic(s["POST_18150"])[0], True), ("B_post_ic1", ic(s["POST_18150"])[1], True),
    ("B_12100", es(pl["12100"]["B"]), True), ("B_12100_ic0", ic(pl["12100"])[0], True), ("B_12100_ic1", ic(pl["12100"])[1], True),
    ("placebo_min", es(min(list(extras.values()) + [pl["16000"]["B"]])), True), ("placebo_max", es(max(extras.values())), True),
    ("banda_n", es(b["n"], 0), True), ("banda_meur", es(b["eur"] / 1e6), True), ("banda_anual", es(E["eur_medio_anual_banda"] / 1e6), True),
    ("banda_pct_lineas", es(b["n"] / obj["lineas"] * 100), True), ("banda_pct_eur", es(E["peso_banda"]["pct"]), True),
    ("bajo_1000", es(E["pct_lineas_bajo_1000_post"]), True),
    ("B_pre21780", es(s["PRE_21780"]["B"]), True), ("ic0", ic(s["PRE_21780"])[0], True), ("ic1", ic(s["PRE_21780"])[1], True),
    ("B_pre18150", es(s["PRE_18150"]["B"]), True), ("ic0b", ic(s["PRE_18150"])[0], True), ("ic1b", ic(s["PRE_18150"])[1], True),
    ("post21780_vacio", "ni una sola línea", s["POST_21780"]["n_banda"] == 0 and s["POST_21780"]["n_ref"] == 0),
    ("B_ob_pre60500", es(ob["PRE_60500"]["B"]), True), ("ob0", ic(ob["PRE_60500"])[0], True), ("ob1", ic(ob["PRE_60500"])[1], True),
    ("B_ob_pre48400", es(ob["PRE_48400"]["B"]), True), ("ob2", ic(ob["PRE_48400"])[0], True), ("ob3", ic(ob["PRE_48400"])[1], True),
    ("B_ob_post48400", es(ob["POST_48400"]["B"]), True), ("ob4", ic(ob["POST_48400"])[0], True), ("ob5", ic(ob["POST_48400"])[1], True),
    ("obj_distintos", es(obj["valores_distintos"], 0), True), ("obj_lineas", es(obj["lineas"], 0), True),
    ("obj_top5", es(obj["top5_lineas"] / obj["lineas"] * 100), True), ("obj_top1", es(obj["top1_lineas"], 0), True),
    ("obj_banda_top", es(R["objeto_banda"]["ESTUDIOS Y TRABAJOS TECNICOS"], 0), True),
    ("meur_2025", es(serie["2025"]["eur"] / 1e6), True), ("pct_nm_2025", es(serie["2025"]["eur"] / R["no_menores_obl"]["2025"] * 100), True),
    ("nm_2025", es(R["no_menores_obl"]["2025"] / 1e6), True), ("pct_cap2_2024", es(serie["2024"]["eur"] / R["cap2_obl"]["2024"] * 100), True),
    ("cap2_2024", es(R["cap2_obl"]["2024"] / 1e6), True), ("adjud", es(conc["adjudicatarios"], 0), True), ("top10", es(conc["top10_pct"]), True),
    ("base_90", es(rep["lineas_base"], 0), True), ("rep_lineas", es(rep["lineas_en_pares"], 0), True), ("rep_pares", es(rep["pares_ge2"], 0), True),
    ("rep_meur", es(rep["eur_en_pares"] / 1e6), True), ("rep_max", es(rep["max_lineas_par"], 0), True),
    ("rep_ge4", "Siete", rep["pares_ge4"] == 7), ("rec_total", es(rec["pares_total"], 0), True), ("rec_3", es(rec["pares_3mas_anios"], 0), True),
    ("rec_5", "7", rec["pares_5mas_anios"] == 7),
    ("dic_pct", es(dic["pct_eur"]), True), ("dic_meur", es(dic["eur"] / 1e6), True), ("tot_meur", es(dic["eur_total"] / 1e6), True),
    ("uniforme", es(100 / 12), True), ("dic_lin", es(dic["pct_lineas"]), True),
    ("dic_2019", es(E["diciembre_por_ej"]["2019"]), True), ("dic_2022", es(E["diciembre_por_ej"]["2022"]), True), ("dic_2025", es(E["diciembre_por_ej"]["2025"]), True),
    ("dic_banda", es(E["banda_diciembre_pct"]), True),
    ("B_16000", es(pl["16000"]["B"]), True), ("B_ifas", es(ifa["POST_18150"]["B"]), True), ("ifas0", ic(ifa["POST_18150"])[0], True), ("ifas1", ic(ifa["POST_18150"])[1], True),
    ("ifas_n", es(ifa["POST_18150"]["n_banda"], 0), True),
    ("B_sum_post", es(sm["POST_18150"]["B"]), True), ("sum0", ic(sm["POST_18150"])[0], True), ("sum1", ic(sm["POST_18150"])[1], True),
    ("B_sum_pre", es(sm["PRE_18150"]["B"]), True), ("sum2", ic(sm["PRE_18150"])[0], True), ("sum3", ic(sm["PRE_18150"])[1], True),
    ("pre_n", es(E["banda_pre_18150"]["n"], 0), True), ("pre_179", es(E["banda_pre_18150"]["en_17900_18000"], 0), True),
    ("B_16000_ic0", ic(pl["16000"])[0], True), ("B_16000_ic1", ic(pl["16000"])[1], True),
]
# Cifras externas o definitorias: comprobadas a mano en la fuente citada
EXTERNAS = {"18.149,99", "14.999,99", "21", "15.000", "2019", "2025", "12.100", "10.000", "9.000", "11.000", "13.000", "14.000", "17.000",
            "2014", "18.000", "21.780", "18.150", "2017", "2018", "9", "50.000", "40.000", "60.500", "48.400", "118", "32,09", "268",
            "2024", "2", "95", "14", "17.900", "581", "2.000", "1,5", "0,5", "3", "85", "97", "500", "250", "1", "90", "1.000", "3.000", "2026", "20.000", "16.000", "4", "2022", "0009", "0001", "1634", "7063"}


def numeros(t):
    t = re.sub(r"\]\([^)]*\)", "]", t)
    t = re.sub(r"!\[[^\]]*\]", "", t)
    return re.findall(r"(?<![\w.,])\d{1,3}(?:\.\d{3})+(?:,\d+)?|(?<![\w.,])\d+(?:,\d+)?", t)


def verificar(texto):
    fallos, conocidos = [], set(EXTERNAS)
    for cid, lit, ok in CLAIMS:
        conocidos.add(lit)
        if not ok:
            fallos.append(f"CALCULO {cid}: {lit}")
        elif lit not in texto:
            fallos.append(f"AUSENTE {cid}: {lit}")
    for n in numeros(texto):
        if n not in conocidos:
            fallos.append(f"SIN_FUENTE {n}")
    return fallos


def control_ingenuo(texto):
    """Control: un numero vale si aparece en cualquier parte de los JSON de resultados o entre las cifras externas."""
    bolsa = json.dumps([R, E], ensure_ascii=False)
    res = []
    for n in numeros(texto):
        if n in EXTERNAS:
            continue
        crudo = n.replace(".", "").replace(",", ".")
        if crudo not in bolsa and crudo.rstrip("0").rstrip(".") not in bolsa:
            res.append(n)
    return res


def ablacion(semillas=(1, 2, 3), k=20):
    base = ART.read_text(encoding="utf-8")
    cuerpo = [m for m in re.finditer(r"(?<![\w.,/-])\d{1,3}(?:\.\d{3})*,\d{2}(?![\d])", base)]
    out = []
    for sd in semillas:
        rng = random.Random(sd)
        elegidos = rng.sample(cuerpo, min(k, len(cuerpo)))
        t = base
        n_ok_v, n_ok_c, n_tot = 0, 0, 0
        for m in sorted(elegidos, key=lambda x: -x.start()):
            orig = m.group(0)
            ds = [i for i, c in enumerate(orig) if c.isdigit()]
            i = rng.choice(ds[-3:])
            nuevo = orig[:i] + str((int(orig[i]) + rng.randint(1, 8)) % 10) + orig[i + 1:]
            un = t[:m.start()] + nuevo + t[m.end():]
            n_tot += 1
            n_ok_v += verificar(un) != verificar(base)
            n_ok_c += control_ingenuo(un) != control_ingenuo(base)
            t = t
        # Errores de otro tipo: intercambiar dos cifras validas de sitio
        n_sw_v, n_sw_c = 0, 0
        for _ in range(k):
            a, c = rng.sample(cuerpo, 2)
            if a.group(0) == c.group(0):
                continue
            x, y = sorted((a, c), key=lambda m: m.start())
            un = base[:x.start()] + y.group(0) + base[x.end():y.start()] + x.group(0) + base[y.end():]
            n_sw_v += verificar(un) != verificar(base)
            n_sw_c += sorted(control_ingenuo(un)) != sorted(control_ingenuo(base))
        out.append({"semilla": sd, "errores": n_tot, "detectados_verificador": n_ok_v, "detectados_control": n_ok_c,
                    "intercambios": k, "intercambios_verificador": n_sw_v, "intercambios_control": n_sw_c})
    return out


if __name__ == "__main__":
    if "--ablacion" in sys.argv:
        r = ablacion()
        (V / "ablacion.json").write_text(json.dumps(r, indent=1), encoding="utf-8")
        print(json.dumps(r))
        sys.exit(0)
    f = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ART
    fs = verificar(f.read_text(encoding="utf-8"))
    (V / "informe_verificacion.txt").write_text(f"Afirmaciones: {len(CLAIMS)}\nFallos: {len(fs)}\n" + "\n".join(fs), encoding="utf-8")
    print(len(CLAIMS), "afirmaciones;", len(fs), "fallos")
    print("\n".join(fs[:40]))
    sys.exit(1 if fs else 0)
