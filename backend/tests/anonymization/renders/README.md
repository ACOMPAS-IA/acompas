# Renders de calibración (ACO-035)

Documentos sintéticos de ACO-051 en las tres formas de entrega de
ADR-023:25. Los `_escaneo.pdf` y `_foto.jpg` pasan por OCR; los
`_capa.pdf` son el control del extractor y no deben tocar Tesseract.

| Dato | Valor |
| --- | --- |
| Fuente | `DejaVuSans.ttf` |
| reportlab | 5.1.1 |
| Resolución | 300 ppp (2480×3508 px) |

Versión calibrada: tesseract 5.5.0.
Si la CI instala otra, avisa y la tabla se rehace (ADR-023:30).

Tiempos medidos **por página** y en arranque en frío, en la CPU de
desarrollo (i7-3770): 3,41 s el escaneo del informe, 2,62 s el de la
analítica y 3,29 s el de la carta; 2,62 s, 2,33 s y 3,20 s las tres
fotos. El objetivo de ADR-023:27-31 es ≤3 s por página y lo superan
tres de los seis; la medición que cuenta se repite en el servidor de
destino.

Los escaneos son PDF de una o dos páginas. Las fotos son un único JPG
con el documento entero, en cuerpo menor para que quepa en una página.

Se regeneran con:

```
cd backend
python -m tests.anonymization.renders.generate --readme
```

## Hashes

| Fichero | SHA-256 |
| --- | --- |
| `informe_patologia_01_escaneo.pdf` | `9657d6a77bc1131cb0833d07e5313e4741acaa8177866a8c5b8411e8d94d04f1` |
| `informe_patologia_01_foto.jpg` | `03f2570ef779fa2c33f4fa95929bcb6add8627fb19f66423c3f67e490f5612ae` |
| `informe_patologia_01_capa.pdf` | `81e79f13f1dca539f3cae7287f1a349532a0a749f8b9d53f2bee02841ada8e38` |
| `analitica_01_escaneo.pdf` | `e78d9bbb4a0feba1384e2b2c5642279077a86cf295f331b93ea79c21ac6b1730` |
| `analitica_01_foto.jpg` | `e691c808980bfdfc469d43ef119d2df2d4ad4968655ae2b6b5ad5017dd0687cc` |
| `analitica_01_capa.pdf` | `6999ba0753fa684597bc6cf8ef8283b2b286ab75ad5872dbfb7d16d634c53ac3` |
| `carta_oncologia_01_escaneo.pdf` | `dcbce71d771032b3bcd6470276200e2b0cd2477eee44645f94c9c56045621a76` |
| `carta_oncologia_01_foto.jpg` | `4c0c74f807e2be32dbe435920a43a3a76d55c98aa95308700ff7fd4d04df46cf` |
| `carta_oncologia_01_capa.pdf` | `248281f175012fe21e76c2fe7179f954d78e7f954fd0a97400dc503bd53a9597` |
