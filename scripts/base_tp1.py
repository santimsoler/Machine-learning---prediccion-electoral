# Base TP1 (Big Data, ML e IA, FCE-UBA): alcaldes municipales Colombia 1997 -> 2000.
# Unidad: municipio. Target: el ganador de 2000 es de partido liberal o conservador (familia tradicional).
# Predictores: sólo datos de 1997 (anteriores a la elección objetivo, sin leakage).
import csv, re, sys, os
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dbfmini import read_dbf

S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CSV = os.path.join(S, 'out4', 'resultados_electorales_colombia.csv')
OUT = os.path.join(S, 'tp1', 'base_tp1_alcaldes_municipios.csv')
TRAD = re.compile(r'LIBERAL|CONSERV|\bPLC\b|\bPCC\b|\bLID\b')

def fam(nombre):
    return 1 if TRAD.search((nombre or '').upper()) else 0

def leer(eid):
    d = defaultdict(lambda: {'cand': [], 'dep_nom': '', 'mun_nom': '', 'valid_total': 0})
    with open(CSV, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['id_eleccion'] != eid: continue
            if int(r['codigo_opcion']) >= 900: continue   # 996-999: blancos, nulos, tarjetas, total
            dep = int(r['codigo_depto_rnec'])
            mun = int(r['codigo_muni_rnec'])
            mun = mun - dep*1000 if mun >= dep*1000 and mun > 999 else mun   # 1997: 1001 -> 1
            k = (dep, mun)
            d[k]['dep_nom'] = r['nombre_depto']; d[k]['mun_nom'] = r['nombre_muni']
            d[k]['cand'].append((int(r['votos'] or 0), r['nombre_opcion'], r['partido_nombre'], r['codigo_opcion']))
    return d

a97 = leer('1997-ALC'); a00 = leer('2000-ALC')

# Validación: el ganador por votos de 2000 debe coincidir con la marca ELEGIDO=S del DBF original
from collections import Counter as _C
import glob
DBF2000 = os.path.join(S, 'dbf2000', 'ALCAMUNI.DBF')
marca = {}
for r in read_dbf(DBF2000):
    if r['ELEGIDO'] == 'S':
        marca[(int(r['CODEPA']), int(r['CODMUN']))] = (r['NOMCAN'] + ' ' + r['APELLCAN']).strip()
coinciden = sum(1 for k in a00 if k in marca and sorted(a00[k]['cand'], reverse=True)[0][1].strip() == marca[k].strip())
print('validación 2000: municipios con marca S', len(marca), '| ganador por votos coincide con marca:', coinciden)
print('municipios 1997:', len(a97), ' 2000:', len(a00), ' en ambos:', len(set(a97) & set(a00)))

filas = []
for k in sorted(set(a97) & set(a00)):
    c97 = sorted(a97[k]['cand'], reverse=True)
    c00 = sorted(a00[k]['cand'], reverse=True)
    if not c97 or not c00 or sum(v for v,*_ in c97) == 0 or sum(v for v,*_ in c00) == 0:
        continue
    tot97 = sum(v for v,*_ in c97); tot00 = sum(v for v,*_ in c00)
    g97 = c97[0]; g00 = c00[0]
    trad97 = sum(v for v,_n,p,_c in c97 if fam(p))
    filas.append({
        'codigo_depto': k[0], 'nombre_depto': a00[k]['dep_nom'],
        'codigo_muni': k[0]*1000 + k[1], 'nombre_muni': a00[k]['mun_nom'],
        'y_ganador2000_tradicional': fam(g00[2]),
        'ganador2000_partido': g00[2], 'ganador2000_candidato': g00[1],
        'ganador1997_tradicional': fam(g97[2]),
        'ganador1997_partido': g97[2], 'ganador1997_candidato': g97[1],
        'votos_candidatos_1997': tot97,
        'n_candidatos_1997': len(c97),
        'share_tradicional_1997': round(trad97 / tot97, 4),
        'margen_1997': round((c97[0][0] - (c97[1][0] if len(c97) > 1 else 0)) / tot97, 4),
        'share_ganador_1997': round(g97[0] / tot97, 4),
        'votos_candidatos_2000': tot00,
        'share_ganador_2000': round(g00[0] / tot00, 4),
    })

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(filas[0].keys())); w.writeheader(); w.writerows(filas)
print('filas base:', len(filas))
print('y (tradicional 2000):', Counter(r['y_ganador2000_tradicional'] for r in filas))
print('tradicional 1997:', Counter(r['ganador1997_tradicional'] for r in filas))
