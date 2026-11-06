# Codebook de ideología v2: puntaje continuo (2-nov-2026)

Escala común: -2 (izquierda / intervencionista / progresista) a +2 (derecha / liberal de mercado / conservador).
- eje_economico: -2 intervencionista ... +2 liberal de mercado.
- eje_sociocultural: -2 progresista ... +2 conservador.

## Cómo se construye `e_cont` / `s_cont`
Promedio ponderado de las fuentes disponibles para ese candidato-elección, todas llevadas a -2..+2:
| Fuente | Transformación | Peso | Cuándo se usa |
|---|---|---|---|
| Juicio del analista (v1, entero -2..+2, con fuente) | tal cual | 1 | siempre que exista |
| V-Party v2 (`v2pariglef`; socio = -(LGBT+religión)/2) | econ: valor/1,35; socio: valor/1,5; recorte a ±2 | 1 | partido del candidato en esa elección (hasta 2018) |
| CHES-LA 2020 (lrecon / galtan) | (x-5)/2,5 | 1 | solo elecciones 2018 en adelante (medición contemporánea) |
| Manifesto (markeco - planeco) | valor/6, recorte a ±2 | 0,5 | solo eje económico; no se usa en Colombia (correlación -0,22 con el juicio) |
Si el nivel de evidencia es `ches_la_partido` (Perú 2021, Uruguay), el puntaje es el valor CHES del partido sin redondear (el entero es solo su redondeo).

## Columnas
`e_cont`, `s_cont`: puntaje continuo. `e_ord`, `s_ord`: puntaje entero v1. `*_n_fuentes`: cuántas fuentes entran. `*_rango_entre_fuentes`: máx - mín entre fuentes (incertidumbre; vacío si hay una sola). `*_fuentes`: cuáles.

## Límites
- Con una sola fuente (solo juicio), el continuo coincide con el entero: no hay información extra. 50 de 180 filas están en ese caso en economía.
- CHES-LA y V-Party miden al partido, no al candidato.
- Las ponderaciones son una decisión del analista; conviene correr el modelo con variantes (solo juicio; sin Manifesto; sin juicio).
