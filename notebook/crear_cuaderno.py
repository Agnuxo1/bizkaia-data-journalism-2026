# SPDX-License-Identifier: Apache-2.0
"""Genera y ejecuta notebook/analisis.ipynb: reproduce catalogo, descarga opcional, analisis, figuras y verificacion."""
import pathlib, nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor

N = pathlib.Path(__file__).parent
nb = nbf.v4.new_notebook()
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells = [
    md("# Hasta el último céntimo — análisis reproducible\n\nFrancisco Angulo de Lafuente · ORCID 0009-0001-1634-7063\n\nCuaderno del reportaje sobre contratos menores de la Diputación Foral de Bizkaia. Preregistro en `experiments/PREREG.md`.\n\n**Para partir de cero**, ejecuta `python notebook/00_catalogo.py` y `python notebook/01_descarga.py contratos-menores contratos-menores-del-ifas contratos-no-menores contratos-no-menores-del-ifas liquidacion-del-presupuesto plan-anual-de-contratacion-pac`. Los CSV contienen nombres de adjudicatarios y por eso no se redistribuyen; este cuaderno los lee de `datos/raw/`. Los resultados solo guardan agregados."),
    code("import json, subprocess, sys, pathlib\nraiz = pathlib.Path.cwd().parent\ndef correr(s):\n    r = subprocess.run([sys.executable, str(raiz/s)], capture_output=True, text=True, cwd=raiz)\n    print(r.stdout[-300:]); assert r.returncode == 0, r.stderr[-1500:]\ncorrer('notebook/02_analisis.py')\ncorrer('notebook/03_exploratorio.py')\ncorrer('notebook/04_figuras.py')\ncorrer('auditoria/audit_robustness.py')"),
    md("## Resultados preregistrados"),
    code("R = json.load(open(raiz/'verificacion/resultados.json', encoding='utf-8'))\nE = json.load(open(raiz/'verificacion/exploratorio.json', encoding='utf-8'))\nfor k in ('E1_E2_dfb_servicios','E2b_dfb_suministros','E3_ifas_servicios','E4_placebos_post_servicios','E5_obras_dfb','corte_18150_w500','banda_post','E6_repeticion','E6_recurrencia'):\n    print(k, json.dumps(R[k], ensure_ascii=False))"),
    md("## Criterios numéricos originales: alcance observacional"),
    code("s = R['E1_E2_dfb_servicios']\nassert s['POST_18150']['ic95'][0] > 2  # E1\nassert s['POST_18150']['ic95'][0] > s['PRE_18150']['ic95'][1]  # Descriptive criterion; not a causal test\nassert s['POST_21780']['n_banda'] == 0 and s['PRE_21780']['n_banda'] > 0  # Descriptive criterion; not a causal test\nassert R['corte_18150_w500']['servicios']['encima'] == 0\nprint('aserciones correctas')"),
    md("## Exploratorio (posterior al preregistro)"),
    code("print(json.dumps({k: E[k] for k in ('sensibilidad_B_18150_servicios','placebos_extra_servicios','diciembre','diciembre_por_ej','peso_banda')}, ensure_ascii=False, indent=1))"),
    md("## Verificación de cifras del reportaje"),
    code("r = subprocess.run([sys.executable, str(raiz/'verificacion/verificar_revisado.py')], capture_output=True, text=True, cwd=raiz)\nprint(r.stdout); assert r.returncode == 0\nprint(json.load(open(raiz/'verificacion/ablacion.json')))"),
]
ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
ep.preprocess(nb, {"metadata": {"path": str(N)}})
nbf.write(nb, N / "analisis.ipynb")
print("cuaderno ejecutado")
