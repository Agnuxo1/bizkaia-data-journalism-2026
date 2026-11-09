# Informe técnico — «Hasta el último céntimo»

Reto del periodismo de datos de la Diputación Foral de Bizkaia 2026 · Categoría c) Investigación periodística basada en datos

Autor: Francisco Angulo de Lafuente · ORCID 0009-0001-1634-7063

## 1. Conjuntos de datos de Open Data Bizkaia utilizados

Todos descargados el 8 de noviembre de 2026 con la API documentada por el portal (`/es/api/3/action/`). `datos/manifest.jsonl` conserva la URL, el tamaño y el SHA-256 de cada fichero.

| Dataset | URL | Uso | Ficheros |
|---|---|---|---|
| Contratos menores | https://www.opendatabizkaia.eus/es/catalogo/contratos-menores | Análisis principal, 2014-2026 | 41 |
| Contratos menores del IFAS | https://www.opendatabizkaia.eus/es/catalogo/contratos-menores-del-ifas | Réplica en otra entidad | 42 |
| Contratos no menores | https://www.opendatabizkaia.eus/es/catalogo/contratos-no-menores | Escala del fenómeno | 43 |
| Contratos no menores del IFAS | https://www.opendatabizkaia.eus/es/catalogo/contratos-no-menores-del-ifas | Descargado; no usado en el texto | 42 |
| Liquidación del presupuesto | https://www.opendatabizkaia.eus/es/catalogo/liquidacion-del-presupuesto | Capítulo 2 de gastos | 19 |
| Plan anual de contratación | https://www.opendatabizkaia.eus/es/catalogo/plan-anual-de-contratacion-pac | Descargado; no usado en el texto | 8 |

## 2. Otras fuentes consultadas

| Fuente | Identificador o URL | Uso |
|---|---|---|
| Ley 9/2017 de Contratos del Sector Público, art. 118, art. 101 y D. F. 16.ª | BOE-A-2017-12902 | Límites vigentes, IVA excluido del valor estimado, entrada en vigor |
| Real Decreto Legislativo 3/2011 (TRLCSP), art. 138.3 | BOE-A-2011-17887 | Límites anteriores |
| Autoridad Vasca de la Competencia, Decálogo de buenas prácticas en contratos menores por las entidades locales (LEA/AVC n.º 581-PROM-2022) | https://www.cnmc.es/sites/default/files/editor_contenidos/Promocion/Municipios%20y%20competencia/202211_MyC_DECÁLOGO%20CONTRATACIÓN%20MENOR.pdf | Marco de fraccionamiento, recurrencia y planificación |
| OIReScon, Informe Anual de Supervisión 2025, módulo 10 | https://www.hacienda.gob.es/rsc/oirescon/informe-anual-supervision-2025/ias2025-modulo10.pdf | Contexto de control interno |
| Palguta y Pertold (2017), *American Economic Journal: Economic Policy* 9(2), 293-315 | doi:10.1257/pol.20150511 | Antecedente académico |

## 3. Proceso de trabajo

1. **Selección del tema.** Se revisaron los 1.348 registros del catálogo y se compararon cuatro ángulos. Se descartaron bomberos (ya premiado en 2025 en visualización), residuos y Bizkaibus (menos tensión informativa).
2. **Preregistro.** `experiments/PREREG.md` fija métrica, periodos, placebos y criterios antes de la confirmación. Antes solo se vio un histograma exploratorio, y así se declara en el documento.
3. **Limpieza.** Los ficheros trimestrales son acumulativos, de modo que se usa el último corte de cada ejercicio. Los campos de importe se convierten del formato español.
4. **Análisis.** Razón B(L): densidad de líneas en [0,97L, L] dividida por la densidad en [0,85L, 0,97L). Intervalos bootstrap percentil del 95 % con 2.000 réplicas y semilla 20261108.
5. **Cruces.** Contratos menores frente a no menores y capítulo 2 de la liquidación. Réplica en IFAS.
6. **Verificación.** `verificacion/verificar.py` comprueba las 81 afirmaciones numéricas contra los resultados recalculados y marca cualquier número del texto sin fuente.

Herramientas: Python 3.13, pandas, NumPy, Matplotlib. Sin datos personales en la pieza: los adjudicatarios solo se tratan en agregado.

## 4. Resultados del preregistro

| Id | Hipótesis | Resultado | Decisión |
|---|---|---|---|
| E1 | B(18.150) servicios 2019-2025 > 2 | 8,09 (7,31–8,97, remuestreo por línea) | Criterio numérico original superado; evidencia observacional |
| E2 | B(18.150) sube y B(21.780) baja tras la reforma | 2,40→8,09; banda y referencia de 21.780 vacías después | Patrón descriptivo compatible. B posterior en 21.780 es indefinida (0/0); no permite el contraste de intervalos preregistrado |
| E3 | E2 en IFAS | Efecto actual 6,22 (3,45–12,00); antes de 2018 solo 2 líneas en la banda de 21.780 | No concluyente |
| E4 | Placebos en [0,5; 1,5] | 16.000: 0,63 (0,48–0,79); 20.000: no válido; 12.100: 2,09 (1,70–2,55) | Parcial |
| E5 | Obras: el salto sigue al límite | 48.400: 2,00→7,66; 60.500 antes: 9,52 | Patrón descriptivo, muestra menor y misma reforma que servicios/suministros |
| E6 | Repetición cerca del límite | 103 pares, 236 líneas, 4,20 M€ | Indicio, no prueba |
| E7 | Escala | 3,41 % de los no menores en 2025 | Informativa |

Exploratorio, posterior a E1-E7: cinco placebos adicionales bajo el límite (0,82–0,95), sensibilidad a anchos de banda (7,02–14,45), concentración en diciembre y desglose de la banda previa a la reforma (54 de 100 líneas entre 17.900 y 18.000 €). Suministros: B(18.150) de 1,45 (0,63–2,72) a 4,83 (3,68–6,32). Revisión independiente con ojos nuevos aplicada antes de la entrega.

**Defecto de diseño declarado.** El placebo de 20.000 € se fijó por encima del límite real, donde no puede haber líneas por construcción. Se mantiene como fallo y se añaden placebos válidos, rotulados como exploratorios.

## 5. Verificación medida

Se sembraron 20 alteraciones de una cifra por cada una de 3 ejecuciones (60 en total). El verificador detectó 60 de 60; el control, que solo busca el número en cualquier parte de los resultados, 50 de 60. En otra prueba, 60 intercambios de dos cifras válidas entre frases, **ninguno de los dos detectó ninguno**: la capa comprueba que cada cifra exista y sea correcta, no que esté en la frase adecuada. Esa revisión sigue siendo humana. Un verificador basado en literales tiene ventaja de partida en la primera prueba, por lo que el resultado no se presenta como comparación general entre métodos.

## 6. Limitaciones

- La unidad es la línea contable, no el contrato. Un contrato puede generar varias líneas.
- Antes de 2019 el dataset solo incluye líneas de al menos 3.000 €. Las métricas operan por encima de ese suelo.
- La franja de importes presupone el tipo general del 21 % de IVA, pero el filtro no identifica el IVA efectivo de cada operación. Puede incluir importes exentos o con otro tipo. Sin ese dato no es posible separar completamente su efecto ni equiparar la obligación contable con el valor estimado del contrato.
- El campo «objeto» es genérico y no hay departamento. Por eso la repetición es solo un indicio.
- No hay versión institucional recogida en esta entrega.
- Las bases definitivas se comprobaron el 9 de noviembre de 2026 en el Decreto Foral 73/2026, BOB n.º 141, de 27 de julio, documento I-865. La solicitud y la firma personales siguen pendientes; este paquete no acredita presentación.


La revisión añade `verificacion/verificar_revisado.py`: conserva las comprobaciones numéricas y vincula siete afirmaciones revisadas con su frase y magnitud. En siete intercambios dirigidos de dos cifras ya válidas, manteniendo ambas presentes en el texto, detectó siete; el control de literales globales detectó cero. Son pruebas de regresión de esas siete cláusulas, sin demostrar una tasa general de detección ni cubrir la colocación de cada cifra histórica. La comprobación original y sus resultados se conservan sin cambios en el archivo de partida.

## 7. Auditoría independiente de sensibilidad, 9 de noviembre de 2026

La auditoría es exploratoria: se fijó en `auditoria/ROBUSTNESS_PROTOCOL.md` después de ver los resultados originales, y antes de ejecutar estos cálculos. No convierte el análisis en un experimento causal ni en confirmación sobre datos nuevos. El original y su preregistro se conservan mediante hashes.

Se verificaron los SHA-256 de los 41 ficheros de contratos menores de la Diputación, la unicidad del ejercicio y el corte dentro de cada fichero y la selección del último corte acumulado. Se reprodujeron las 42.074 líneas y los recuentos de servicios: 1.105 en los 500 euros inferiores al límite y 0 en los siguientes. La razón exacta es 4 × 1.119 / 553 = 8,09403255.

Se agruparon por nombre de proveedor normalizado todas las líneas de servicios de 2014–2017 y 2019–2025: 4.281 grupos, sin nombres ausentes. Cada remuestreo conserva las líneas del proveedor en ambos periodos. Se ejecutaron 10.000 réplicas, semilla 20261109; ninguna tuvo denominadores sin soporte.

| Comprobación | Resultado |
|---|---|
| B(18.150), 2014–2017 | 2,40; intervalo por proveedor del 95 % [1,80; 3,15] |
| B(18.150), 2019–2025 | 8,09; intervalo por proveedor del 95 % [7,09; 9,26] |
| Diferencia posterior − anterior | 5,70; intervalo pareado por proveedor [4,43; 7,02] |
| Omitir un proveedor en cada cálculo | B posterior entre 8,01 y 8,21 |
| Omitir un ejercicio en cada cálculo | B posterior entre 7,64 y 8,44 |
| Unidad contable de 2019–2025 | 33.395 líneas y 33.395 identificadores ejercicio-expediente contable distintos |

Los intervalos dependen de un modelo hipotético de remuestreo de proveedores. No representan error de muestreo del recuento de este archivo completo. Los nombres pueden fragmentar una misma entidad o agrupar entidades distintas. Los identificadores contables tampoco acreditan el objeto jurídico ni la unidad completa del contrato. Los resultados agregados y el código están en `auditoria/ROBUSTNESS_RESULTS.json` y `auditoria/audit_robustness.py`; no se exportan nombres ni filas individuales.

## 8. Bases definitivas y límites de la entrega

Fuente oficial: [Decreto Foral 73/2026, documento I-865](https://www.bizkaia.eus/lehendakaritza/Bao_bob/2026/07/27/I-865_cas.pdf), 12 páginas, SHA-256 `b67d966564cbe53cb6df97a290d339d354e5acf86d65b5729e2cf8b36cef8236`.

La base 5 fija el cierre el 20 de noviembre de 2026 a las 13:00, hora de Madrid, y permite presentación presencial o electrónica. La base 6 pide procedencia y acceso a los datos y una descripción del proceso. Para la categoría c, la base 10 pondera propósito informativo 25 %, integración de datos 20 %, calidad periodística 20 %, fuentes 25 % e interés público 10 %. La base 18 atribuye al participante la responsabilidad sobre derechos de terceros. La base 19 exige que las personas premiadas asistan y presenten el trabajo, con representación justificada en los términos de la convocatoria. El texto no menciona expresamente la IA o el anonimato; su silencio no se presenta como autorización específica.

Asistencia de IA: Claude en la preparación; Codex en la auditoría, cálculos de sensibilidad y revisión. Autoría y responsabilidad editorial: Francisco Angulo de Lafuente. Falta incorporar una eventual versión de la Diputación, obtener la firma personal y conservar el justificante de presentación.
