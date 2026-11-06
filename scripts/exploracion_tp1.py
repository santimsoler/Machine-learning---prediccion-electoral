# Exploración de la base TP1: filas, columnas, faltantes, tipos y distribución del target.
import csv, os, sys
from collections import Counter
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BASE = os.path.join(S, 'tp1', 'base_tp1_alcaldes_municipios.csv')
rows = list(csv.DictReader(open(BASE, encoding='utf-8')))
cols = list(rows[0].keys())
print(f'Filas: {len(rows)}  Columnas: {len(cols)}')
print('\n| Columna | Tipo | Faltantes | Ejemplo |\n|---|---|---|---|')
for c in cols:
    vals = [r[c] for r in rows]
    falt = sum(1 for v in vals if v == '')
    nums = [v for v in vals if v != '']
    try:
        [float(v) for v in nums]; tipo = 'numérica'
    except ValueError:
        tipo = 'texto'
    print(f'| {c} | {tipo} | {falt} | {vals[0]} |')
y = Counter(r['y_ganador2000_tradicional'] for r in rows)
print('\nTarget y_ganador2000_tradicional:', dict(y), f"({100*y['1']/len(rows):.1f}% = 1)")
print('Benchmark mayoría (predecir siempre 1): exactitud', f"{100*y['1']/len(rows):.1f}%")
print('\nPredictores (1997):')
for c in ['share_tradicional_1997', 'margen_1997', 'n_candidatos_1997', 'ganador1997_tradicional']:
    v = [float(r[c]) for r in rows]
    print(f'  {c}: min {min(v):.3f}  media {sum(v)/len(v):.3f}  max {max(v):.3f}')
