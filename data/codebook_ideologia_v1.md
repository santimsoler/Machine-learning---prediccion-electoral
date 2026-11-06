# Codebook de ideología v1 (borrador)
Unidad: candidato/fórmula en cada elección (no el partido en general). Dos ejes, escala entera de -2 a +2 más "NA" si no hay información.

## eje_economico (intervención del Estado en la economía)
- -2 intervencionista fuerte: propiedad estatal de sectores estratégicos, controles de precios/cambio, fuerte redistribución, rechazo al ajuste fiscal.
- -1 intervencionista moderado: Estado regula y redistribuye con mercado como base.
- 0 centro / mixto o programa sin definiciones económicas.
- +1 liberal moderado: apertura, disciplina fiscal, privatizaciones parciales, Estado subsidiario.
- +2 liberal fuerte: reducción drástica del gasto y los impuestos, desregulación, privatizaciones amplias.

## eje_sociocultural (valores)
- -2 progresista fuerte: aborto legal, matrimonio igualitario, diversidad de género, secularismo pleno.
- -1 progresista moderado.
- 0 centro / sin definiciones.
- +1 conservador moderado.
- +2 conservador fuerte: oposición al aborto y al matrimonio igualitario, orden y valores religiosos, mano dura.

## Reglas
1. Se puntúa lo que el candidato dice y propone en esa elección (plataforma, declaraciones, propuestas), no lo que hizo en el gobierno.
2. Cada puntaje lleva fuente (plataforma, entrevista o dataset de expertos) en fuente_ideologia y version_codebook = v1.
3. Si hay puntajes de expertos (V-Party, Manifesto Project, PELA), se anotan en columnas aparte y se compara contra el puntaje propio; no se pisan.
4. Sin evidencia: NA. Nada se completa de memoria.
5. Dos codificaciones independientes por candidato cuando sea posible; los desacuerdos de más de 1 punto se revisan.
## Orden de trabajo
Primero oficialismo y los dos más votados de cada elección; después el resto con más de 3% de votos.
