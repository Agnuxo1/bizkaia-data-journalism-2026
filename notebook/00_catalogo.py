# SPDX-License-Identifier: Apache-2.0
# Research-Project: Hasta el ultimo centimo (Bizkaia minor contracts 2026)
# Research-Author: Francisco Angulo de Lafuente
# Research-ORCID: https://orcid.org/0009-0001-1634-7063
# Research-Date: 2026-11-08
"""Descarga el catalogo CKAN completo de Open Data Bizkaia con la API documentada."""
import json, urllib.request, pathlib, datetime as dt
B = "https://www.opendatabizkaia.eus/es/api/3/action/"
OUT = pathlib.Path(__file__).resolve().parents[1] / "datos" / "catalogo.json"
items, start, total = [], 0, None
while total is None or start < total:
    r = json.load(urllib.request.urlopen(f"{B}package_search?rows=500&start={start}", timeout=180))
    assert r["success"]
    total = r["result"]["count"]
    page = r["result"]["results"]
    assert page
    items += page
    start += len(page)
assert len({p["id"] for p in items}) == total, (len(items), total)
OUT.write_text(json.dumps({"descargado_utc": dt.datetime.now(dt.UTC).isoformat(), "count": total, "results": items}, ensure_ascii=False), encoding="utf-8")
print(total, len(items))
