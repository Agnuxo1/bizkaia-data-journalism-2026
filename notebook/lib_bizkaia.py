# SPDX-License-Identifier: Apache-2.0
# Research-Project: Hasta el ultimo centimo (Bizkaia minor contracts 2026)
# Research-Author: Francisco Angulo de Lafuente
# Research-ORCID: https://orcid.org/0009-0001-1634-7063
# Research-Date: 2026-11-08
"""Lectura robusta de los CSV de Open Data Bizkaia."""
import pandas as pd, pathlib, json
R = pathlib.Path(__file__).resolve().parents[1]
def leer(f):
    for e in ("utf-8-sig", "cp1252"):
        try:
            return pd.read_csv(f, sep=";", encoding=e, dtype=str, on_bad_lines="error")
        except UnicodeDecodeError:
            continue
    raise ValueError(f)
def manifest(ds=None):
    m = [json.loads(l) for l in open(R/"datos/manifest.jsonl", encoding="utf-8")]
    return [x for x in m if ds is None or x["dataset"] == ds]
def eur(s):
    return pd.to_numeric(s.astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False), errors="coerce")
