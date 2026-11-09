# Registro de experimentos — bizkaia-datos

| id | fecha | hipotesis | config | metrica | decision |
|----|-------|-----------|--------|---------|----------|
| V000 | 2026-10-30 | La convocatoria 2026 existe, sigue abierta y Fran es elegible | lectura de la ficha oficial del tramite 3104 con el navegador integrado (la SPA no renderiza por WebFetch) | n/a | CONFIRMADA: abierta hasta 20/11/2026 13:00 Madrid; Fran elegible como persona fisica individual; sin requisito de residencia, perfil periodistico ni euskera |
| V001 | 2026-10-30 | Open Data Bizkaia expone API CKAN estandar (/api/3/action/package_list) | curl a opendatabizkaia.eus y opendata.bizkaia.eus | HTTP 404 en ambos | RECHAZADA: no es CKAN. Usar el catalogo web y la pagina oficial "API de Datos" (https://www.opendatabizkaia.eus/es/info/api-de-datos) con descarga directa por dataset |

Sin experimentos de computo en esta fase: JEV decidio (trabajar_ahora = 0,24)
no desarrollar el proyecto en esta ventana. Ver CHECKPOINT.md.

| V002 | 2026-11-08 | Corrige V001: el portal SI es CKAN, bajo /es/api/3/action/ | ejemplo Python de la pagina API de Datos | HTTP 200, 1348 registros | CONFIRMADA; V001 probo la ruta sin /es/ |
| E1-E7 | 2026-11-08 | Ver PREREG.md | notebook/02_analisis.py, semilla 20261108 | resultados.json | E1, E2, E5 confirmadas; E3 no concluyente; E4 parcial; E6-E7 descriptivas |
| X1 | 2026-11-08 | Exploratorio | notebook/03_exploratorio.py | exploratorio.json | Placebos 0,82-0,95; diciembre 30,86 %; banda previa 54/100 junto a 18.000 |
| A1 | 2026-11-08 | Verificador frente a control | verificacion/verificar.py --ablacion, semillas 1-3 | ablacion.json | Alteraciones 60/60 frente a 50/60; intercambios 0/60 en ambos |

Descartados: SPEIS (trabajo premiado en 2025 sobre el mismo dataset), residuos y Bizkaibus (menos tension informativa). JEV: a_contratos, confianza 0,97, provenance=jev.

| R1 |2026-11-09|Auditoría exploratoria de dependencia/influencia tras los resultados originales|41hashes y42074líneas; bootstrap4281proveedores,10000réplicas,semilla20261109|Bpost8,09403;ICproveedor[7,09380;9,25801];diferenciaPRE/POST[4,42945;7,01773];leaveproveedor[8,00723;8,21284],leaveaño[7,64133;8,44346]|Reproducido; recuentos descriptivos, sin causalidad. E2 no satisface el contraste de intervalos cuandoBposterior21780es0/0. Originales conservados; corrección explícita del estado previo«confirmada».|
| R2 |2026-11-09|Asociar siete cifras revisadas con su magnitud|Siete intercambios dirigidos de dos cifras válidas, preservando presencia global|7/7detectados por vínculo de frase;0/7porliteralesglobales|Pruebas de regresión acotadas; no comparación general de detectores.91controles numéricos y7vínculos pasan.|
| R3 |2026-11-09|Reproducción portable y revisión de PDFs|Cuaderno aislado completo,5celdascódigo; revisión EGM concontextolimpio|Sin errores en celdas; agregados y4figuras idénticos; auditoría proveedorexacta; PDF7+5p conautor/ORCID|HallazgoIVAcorregido: elfiltro porimporte noexcluyeexentos. BasesdefinitivasBOBI865recuperadas. Materiales revisados; firma/solicitud/justificante pendientes.|
