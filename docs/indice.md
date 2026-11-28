# Índice de ACO

> Generado por `scripts/indice.py` a partir de `docs/aco/sprints.toml` y
> de las fichas de `docs/aco/`. No se edita a mano: se regenera con
> `python scripts/indice.py`, y la CI comprueba que lo commiteado coincide
> con lo generado.

## Leyenda

- **—** significa «no consta», no «no tiene».
- **Estado:** `pendiente`, `en curso`, `en revisión`, `hecho` o
  `traspasado`. No se compara con el estado de la Issue en GitHub.
- **Caso de uso:** solo consta en los ACO que lo declaran en
  `sprints.toml`; «—» no significa que el ACO no atienda ningún caso.

## Tabla

| Caso de uso | ACO | Título | Sprint | Estado | Ficha | Issue |
| --- | --- | --- | --- | --- | --- | --- |
| — | 001 | Configuración del repositorio | — | hecho | [ACO-001](aco/ACO-001.md) | — |
| — | 006 | CI básica | — | hecho | [ACO-006](aco/ACO-006.md) | — |
| — | 007 | Esqueleto del backend (FastAPI) | — | hecho | [ACO-007](aco/ACO-007.md) | — |
| — | 011 | Keycloak local | S1 | hecho | [ACO-011](aco/ACO-011.md) | [#16](https://github.com/ACOMPAS-IA/acompas/issues/16) |
| — | 012 | Realm/configuración | S1 | hecho | [ACO-012](aco/ACO-012.md) | [#17](https://github.com/ACOMPAS-IA/acompas/issues/17) |
| — | 013 | OAuth2/OIDC | S1 | hecho | [ACO-013](aco/ACO-013.md) | [#18](https://github.com/ACOMPAS-IA/acompas/issues/18) |
| — | 014 | Validación JWT | S1 | hecho | [ACO-014](aco/ACO-014.md) | [#19](https://github.com/ACOMPAS-IA/acompas/issues/19) |
| — | 015 | Lista blanca del piloto | S1 | hecho | [ACO-015](aco/ACO-015.md) | [#20](https://github.com/ACOMPAS-IA/acompas/issues/20) |
| — | 016 | React bootstrap | S1 | hecho | [ACO-016](aco/ACO-016.md) | [#21](https://github.com/ACOMPAS-IA/acompas/issues/21) |
| — | 017 | Layout | S1 | hecho | [ACO-017](aco/ACO-017.md) | [#22](https://github.com/ACOMPAS-IA/acompas/issues/22) |
| — | 018 | Login | S1 | hecho | [ACO-018](aco/ACO-018.md) | [#23](https://github.com/ACOMPAS-IA/acompas/issues/23) |
| — | 019 | API client | S1 | hecho | [ACO-019](aco/ACO-019.md) | [#24](https://github.com/ACOMPAS-IA/acompas/issues/24) |
| — | 020 | Servicio anonimización | S1 | hecho | [ACO-020](aco/ACO-020.md) | [#25](https://github.com/ACOMPAS-IA/acompas/issues/25) |
| — | 021 | Presidio + MEDDOCAN | S1 | hecho | [ACO-021](aco/ACO-021.md) | [#26](https://github.com/ACOMPAS-IA/acompas/issues/26) |
| — | 022 | Etiquetado automático | S1 | hecho | [ACO-022](aco/ACO-022.md) | [#27](https://github.com/ACOMPAS-IA/acompas/issues/27) |
| — | 023 | Umbral de confianza | S1 | hecho | [ACO-023](aco/ACO-023.md) | [#28](https://github.com/ACOMPAS-IA/acompas/issues/28) |
| — | 024 | API anonimización | S1 | hecho | [ACO-024](aco/ACO-024.md) | [#29](https://github.com/ACOMPAS-IA/acompas/issues/29) |
| — | 025 | No persistencia del original | S1 | hecho | [ACO-025](aco/ACO-025.md) | [#30](https://github.com/ACOMPAS-IA/acompas/issues/30) |
| — | 026 | Tests anonimización | S1 | hecho | [ACO-026](aco/ACO-026.md) | [#31](https://github.com/ACOMPAS-IA/acompas/issues/31) |
| — | 027 | LLM Gateway v0 / encaje | S1 | hecho | [ACO-027](aco/ACO-027.md) | [#32](https://github.com/ACOMPAS-IA/acompas/issues/32) |
| — | 028 | Seguridad de API key | S1 | hecho | [ACO-028](aco/ACO-028.md) | [#33](https://github.com/ACOMPAS-IA/acompas/issues/33) |
| UC-05, UC-09 | 029 | System prompt v0 | S1 | hecho | [ACO-029](aco/ACO-029.md) | [#34](https://github.com/ACOMPAS-IA/acompas/issues/34) |
| — | 030 | Conversación sobre documento | S1 | hecho | [ACO-030](aco/ACO-030.md) | [#35](https://github.com/ACOMPAS-IA/acompas/issues/35) |
| — | 031 | Disclaimer | S1 | hecho | [ACO-031](aco/ACO-031.md) | [#36](https://github.com/ACOMPAS-IA/acompas/issues/36) |
| — | 032 | Flujo E2E | S1 | hecho | [ACO-032](aco/ACO-032.md) | [#37](https://github.com/ACOMPAS-IA/acompas/issues/37) |
| — | 033 | Tests E2E | S2 | traspasado | [ACO-033](aco/ACO-033.md) | [#38](https://github.com/ACOMPAS-IA/acompas/issues/38) |
| — | 034 | Imagen del backend con PyTorch en CPU y modelos precargados | S2 | hecho | [ACO-034](aco/ACO-034.md) | [#159](https://github.com/ACOMPAS-IA/acompas/issues/159) |
| — | 035 | OCR local y Nivel 2: validación reforzada de entidades y documento ilegible | S2 | en curso | [ACO-035](aco/ACO-035.md) | [#204](https://github.com/ACOMPAS-IA/acompas/issues/204) |
| — | 037 | Métricas de cobertura de la anonimización | S2 | en curso | [ACO-037](aco/ACO-037.md) | [#221](https://github.com/ACOMPAS-IA/acompas/issues/221) |
| — | 041 | Prompt v1: historial no fiable | S2 | pendiente | [ACO-041](aco/ACO-041.md) | [#185](https://github.com/ACOMPAS-IA/acompas/issues/185) |
| — | 047 | Fixture `authenticated_user` en `conftest.py` | S2 | hecho | [ACO-047](aco/ACO-047.md) | [#110](https://github.com/ACOMPAS-IA/acompas/issues/110) |
| — | 051 | Datos sintéticos para demo | S1 | hecho | [ACO-051](aco/ACO-051.md) | [#8](https://github.com/ACOMPAS-IA/acompas/issues/8) |
| — | 052 | Casos de prueba | S1 | hecho | [ACO-052](aco/ACO-052.md) | [#39](https://github.com/ACOMPAS-IA/acompas/issues/39) |
| — | 053 | Seguridad transversal: lista negra, rotación y renovación de tokens | S2 | pendiente | [ACO-053](aco/ACO-053.md) | [#186](https://github.com/ACOMPAS-IA/acompas/issues/186) |

## Limitaciones

- El Documento Operativo no está en el repositorio: si cambia sin que nadie
  actualice `sprints.toml`, el índice no lo detecta.
- El estado es el de `sprints.toml`; no se compara con el de la Issue en
  GitHub.
- Solo aparecen los ACO con ficha en `docs/aco/`. La lista completa vive en
  el Documento Operativo, así que un ACO sin ficha y sin entrada no se
  detecta.
