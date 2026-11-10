# Strict JSON compatibility export

This additive export makes the historical public aggregate artifact readable by RFC 8259 JSON consumers. It replaces 24 non-finite `NaN` literals with `null`. The pinned original remains unchanged.

- Source: [historical resultados.json](https://github.com/Agnuxo1/bizkaia-data-journalism-2026/blob/7cae90a8e13b7ed76daeecbfe8d69c45ff305223/verificacion/resultados.json), Git blob `8fb61884f846bd3dec2294c76a09f02e22bc5374`, SHA-256 `a6f91605f10a57ac7111ca0112c58573150a1371d9e263fb774faa41f2041da5`.
- Derived file: [resultados.rfc8259.json](resultados.rfc8259.json), 10,000 bytes, SHA-256 `9bbabfcc33f3b048fbc3f1fb8f3ef46e754ab79f00f7d3a7c4bb21db7c2c4669`.
- The [manifest](nonfinite-conversion-manifest.json) identifies all 24 JSON pointers and the source-to-export binding.

`null` preserves the fact that the source contained a non-finite value. It does not mean zero, an imputed estimate, a finite confidence interval, or a newly established cause of missingness. Consumers must handle these fields as unavailable values.

Every finite value, its spelling, strings, keys, ordering, array positions and all bytes outside the replaced tokens are preserved. This is a serialization repair of a historical artifact. It does not recompute the statistical analysis, reconcile historical estimates with the later revised PDFs, validate the underlying CSVs or change the article's conclusions. A public source archive is separate from an official competition submission.

Reproduce the derived JSON using Python 3 and the pinned original downloaded above:

```sh
python json_nonfinite_to_null.py original-resultados.json reproduced.json reproduced-manifest.json
```

The command refuses to overwrite existing outputs and has no network access or third-party dependencies. The reproduced JSON has the hash above; a newly created manifest records that run's inputs and outputs.

The new transformation code is licensed under Apache-2.0. Existing mixed source terms remain applicable to the historical aggregates, article and figures. This folder does not relicense upstream material or modify the original project documentation, figures, credits or history.

<!-- author-background:start -->
## Author background

**Francisco Angulo de Lafuente**, independent AI researcher · [ORCID](https://orcid.org/0009-0001-1634-7063) · [arXiv](https://arxiv.org/a/angulodelafuente_f_1.html) · [Google Scholar](https://scholar.google.com/citations?user=6nOpJ9IAAAAJ) · [ResearchGate](https://www.researchgate.net/profile/Francisco-Angulo-Lafuente-3) · [Figshare](https://figshare.com/authors/Francisco_Angulo_de_Lafuente/22601234) · [Wikipedia](https://es.wikipedia.org/wiki/Francisco_Angulo_de_Lafuente)

Earlier research at ECOFA focused on biotechnology for clean energy and on second-generation biofuels obtained by microbiological processing of organic waste. Two Spanish patents document that work:

- **ES 2273594 B1**, *Process for obtaining fuels from organic waste*. Filed 5 September 2005, grant published 16 February 2008. [OEPM](https://www.oepm.es/pdf/ES/0000/000/02/27/35/ES-2273594_B1.pdf) · [Google Patents](https://patents.google.com/patent/ES2273594B1/en)
- **ES 2341194 B1**, *Method for obtaining paraffin by a biological process with microorganisms from organic matter, and its refining for use as fuel*. Filed 11 September 2007, grant published 26 April 2011. Also published as EP2196519 and WO2009034217. [OEPM](https://www.oepm.es/pdf/ES/0000/000/02/34/11/ES-2341194_B1.pdf) · [Google Patents](https://patents.google.com/patent/ES2341194B1/en)

These are historical publication and grant records under the inventor name Francisco Angulo Lafuente, and both have since lapsed. They are cited as evidence of a research trajectory and make no statement about current enforceability.
<!-- author-background:end -->
