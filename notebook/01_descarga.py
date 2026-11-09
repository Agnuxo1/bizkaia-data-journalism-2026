# SPDX-License-Identifier: Apache-2.0
# Research-Project: Hasta el ultimo centimo (Bizkaia minor contracts 2026)
# Research-Author: Francisco Angulo de Lafuente
# Research-ORCID: https://orcid.org/0009-0001-1634-7063
# Research-Date: 2026-11-08
"""Descarga los CSV originales de los datasets indicados, con hash y registro."""
import json, urllib.request, pathlib, hashlib, sys, time, datetime as dt, re
R = pathlib.Path(__file__).resolve().parents[1]
cat = {p["name"]: p for p in json.load(open(R/"datos/catalogo.json", encoding="utf-8"))["results"]}
manifest_path = R/"datos/manifest.jsonl"
done = {json.loads(l)["resource_id"] for l in manifest_path.open(encoding="utf-8")} if manifest_path.exists() else set()
for name in sys.argv[1:]:
    p = cat[name]
    d = R/"datos/raw"/name; d.mkdir(parents=True, exist_ok=True)
    for r in p["resources"]:
        if "CSV" not in (r.get("format") or "").upper() or r["id"] in done: continue
        fn = d/(r["id"]+".csv")
        try:
            b = urllib.request.urlopen(r["url"], timeout=120).read()
        except Exception as e:
            print("ERR", name, r["url"], e); continue
        fn.write_bytes(b)
        nm = r.get("name"); nm = nm.get("es") if isinstance(nm, dict) else nm
        with manifest_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"dataset": name, "resource_id": r["id"], "resource_name": nm, "url": r["url"], "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(), "descargado_utc": dt.datetime.now(dt.UTC).isoformat()}, ensure_ascii=False)+"\n")
        time.sleep(0.3)
    print(name, "ok", flush=True)
