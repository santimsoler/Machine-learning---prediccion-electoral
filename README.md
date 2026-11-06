# Principales determinantes del voto en Latinoamérica

Base de datos y código del trabajo final del seminario **Big Data, Machine Learning e Inteligencia Artificial** (M73, Maestría en Economía Aplicada, FCE-UBA).

**Pregunta:** ¿cuánto del voto al oficialismo en elecciones presidenciales latinoamericanas se explica por la aprobación del presidente, la economía, la pobreza, la competencia y la ideología? La unidad de análisis es la elección-vuelta; la heterogeneidad regional es un complemento.

## Contenido del dataset (versión actual)
- **12 países:** Argentina, Bolivia, Brasil, Chile, Colombia, Costa Rica, Ecuador, México, Panamá, Paraguay, Perú y Uruguay.
- **102 elecciones-vuelta** (76 elecciones país-año; 1989–2026). Variable a predecir: `y_share_nacional` = % de votos válidos del oficialismo.
- **Panel regional:** 1.617 filas (región × elección) con `y_share_oficialismo` y variables regionales (voto a la izquierda, ideología media del voto, pobreza relativa). Cobertura regional parcial en Bolivia, Paraguay, Costa Rica y México; Ecuador y Panamá solo a nivel nacional.

## Archivos principales (`data/`)
| Archivo | Descripción |
|---|---|
| `panel_modelo_eleccion.csv` | Panel por elección-vuelta (102 filas, 73 columnas), con valores faltantes sin imputar |
| `panel_modelo_completo.csv` | Versión para modelar: 28 predictores sin celdas vacías (imputación por mediana del país), con indicadores `<variable>_imp` |
| `panel_modelo_region.csv` | Panel por región y elección (1.617 filas, 147 columnas) |
| `LEEME.md` | Documentación de cada fuente, regla de construcción, advertencias y casos dudosos |
| `candidatos_ampliacion.csv`, `competencia_ampliacion.csv` | Candidatos, ideología y medidas de competencia de BO, PY, EC, MX, CR y PA |
| `insumos/` | Archivos auxiliares de la ampliación (Banco Mundial, tablas por estado/provincia, Latinobarómetro procesado) |

Leer primero `data/LEEME.md`: describe los casos dudosos (oficialismo ambiguo), las variables imputadas y los límites de cada fuente.

## Fuentes
Resultados electorales de organismos oficiales y Wikipedia; aprobación presidencial (Executive Approval Database y encuestas puntuales), Latinobarómetro (aprobación y percepción económica), Banco Mundial/WDI y FMI (macro, pobreza, fiscal), V-Party y CHES-LA (ideología de partidos), y fuentes nacionales de pobreza regional (INE, DANE, INEI, CASEN, UDAPE, IBGE/IPEA, EPH).

## Código (`scripts/`)
Los scripts se corrieron sobre una carpeta de trabajo con `final/`, `data_ampliacion/`, `data_ampliacion2/`, `wb/`, y los insumos crudos (Latinobarómetro, EAD, V-Party, CHES-LA) que **no** se incluyen por tamaño y licencia. Sirven como documentación reproducible de cada paso. Orden de la ampliación a 12 países:

1. `ampliacion_nacional.py` → `ampliacion_competencia.py` → `ampliacion_regional_py.py` → `percepcion_economica_panel.py` → `confianza_ecuador_bce.py` → `confianza_paraguay_bcp.py` → `regional_bo_py_ideologia_pobreza.py` (Bolivia, Paraguay, Ecuador)
2. `lb_agregar_2018_2023.py`, luego `bash scripts/run_post_mx_cr_pa.sh` (México, Costa Rica, Panamá, aprobación completa, variables `us_*`, inflación, mandato, panel completo y filas regionales de Costa Rica y México)

## Limitaciones conocidas
- Aprobación sin dato real en 5 elecciones (CL-1989, BO-1993, BO-1997, PY-1993, PY-1998); se imputa en `panel_modelo_completo`.
- Candidatos menores de varias elecciones de Costa Rica, Panamá y México 1994 con porcentajes aproximados; juicios de ideología marcados como pendientes (Costa Rica 2022 y 2026, Panamá 2019 y 2024).
- Sin regional para Ecuador, Panamá, Costa Rica 2018 (segunda vuelta), 2022 y 2026; sin pobreza regional de México y Costa Rica.
- 8 elecciones con oficialismo dudoso (`oficialismo_dudoso = 1`).
