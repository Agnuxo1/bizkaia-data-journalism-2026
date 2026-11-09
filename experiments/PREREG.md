# Preregistro — contratos menores DFB (escrito el 2026-11-08, antes de los cálculos confirmatorios)

Transparencia: antes de escribir esto se vio un histograma exploratorio 2014-2026 con cajas de 500 €,
que mostró el corte en 18.150 € y motivó la pregunta. Ese vistazo no es parte de la confirmación.
Sí es nuevo aquí: la separación por periodos, IFAS, los placebos y la repetición.

Pregunta: ¿los importes de los contratos menores de la DFB se ajustan al límite legal, y se mueven cuando la ley lo mueve?

Límites con IVA del 21 % (norma: TRLCSP art. 138.3 antes; LCSP 9/2017 art. 118 desde el 9-3-2018):
servicios y suministros 21.780 € → 18.150 €; obras 60.500 € → 48.400 €.
Periodos: PRE = 2014-2017; POST = 2019-2025; 2018 excluido por transición; 2026 parcial excluido de la confirmación.

Métrica B(L): densidad en [0,97L, L] dividida por densidad en [0,85L, 0,97L). Control a priori: B ≈ 1 sin efecto.
Intervalos: bootstrap percentil 95 %, 2.000 réplicas, semilla 20261108. Línea contable como unidad.

- E1 (salto). Servicios POST: B(18.150) > 2. Se rechaza con IC inferior ≤ 2.
- E2 (experimento natural). Servicios: B(18.150) POST > B(18.150) PRE y B(21.780) PRE > B(21.780) POST, con IC sin solape en ambos.
- E3 (réplica independiente). Mismo E2 en IFAS, entidad con su propio registro.
- E4 (placebos). B en límites falsos 16.000 € y 20.000 € en POST; debe estar en [0,5; 1,5]. Además 12.100 € (10.000 + IVA) como control de "número redondo": si B(12.100) iguala a B(18.150), el efecto no se distingue de redondeo.
- E5 (obras). B(48.400) POST y B(60.500) PRE; muestra pequeña, se informa aunque no sea concluyente.
- E6 (repetición). Pares adjudicatario × objeto × año con ≥ 2 líneas ≥ 0,9 L en POST: número y euros. Solo indicio; el "objeto" es un código presupuestario genérico.
- E7 (escala). Contratos menores frente a no menores y al capítulo 2 de gastos. Pone el fenómeno en proporción.

Reglas: no se atribuye ilegalidad, no se nombra adjudicatario alguno. Se publican también los negativos.
Los datos anteriores a 2019 solo incluyen líneas ≥ 3.000 €; todas las métricas operan por encima de ese suelo.
Se excluye "Contratos bases de datos y public." por régimen propio.
