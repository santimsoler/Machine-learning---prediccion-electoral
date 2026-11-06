# Panel nacional presidencial: Colombia 2002 (1ª vuelta) -> 2006 (1ª vuelta), por municipio.
# Fuente 2006: tb_votacion.dbf (CODI_COR='03'), CD 2006 RNEC. Fuente 2002: tabla maestra (out4).
# Predictores: sólo 2002. Target: y_gano_uribe_2006.
import csv, os, sys
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dbfmini import read_dbf
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
MAESTRA = os.path.join(S, 'out4', 'resultados_electorales_colombia.csv')
DBF06 = os.path.join(S, 'x2006', 'tb_votacion.dbf')
OUT = os.path.join(S, 'tp1', 'base_nacional_presidencial_2002_2006.csv')
NOM06 = {1:'RINCON BARRETO CARLOS ARTURO',2:'PAREJO GONZALEZ ENRIQUE',3:'URIBE VELEZ ALVARO',4:'GAVIRIA DIAZ CARLOS',
         5:'SERPA URIBE HORACIO',6:'LEYVA DURAN ALVARO',7:'MOCKUS SIVICKAS ANTANAS'}
PAR06 = {1:'MOVIMIENTO COMUNAL Y COMUNITARIO',2:'MOVIMIENTO RECONSTRUCCION DEMOCRATICA',3:'PRIMERO COLOMBIA',
         4:'POLO DEMOCRATICO ALTERNATIVO',5:'PARTIDO LIBERAL COLOMBIANO',6:'MOVIMIENTO NACIONAL DE RECONCILIACION',7:'ALIANZA SOCIAL INDIGENA'}

def k_dbf(r): return int(r['CODI_DEP']), int(r['CODI_MUN'])
def k_m(r):
    d = int(r['codigo_depto_rnec']); m = int(r['codigo_muni_rnec'])
    return d, (m - d*1000 if m > 999 else m)

# 2006
g06 = defaultdict(lambda: defaultdict(int)); nom06 = {}
for r in read_dbf(DBF06):
    if r['CODI_COR'] != '03': continue
    k = k_dbf(r); c = int(r['CODI_CAN'])
    g06[k][c] += int(r['VOTA_CAN'] or 0)
# 2002
g02 = defaultdict(lambda: {'cand': [], 'dep': '', 'mun': ''})
for r in csv.DictReader(open(MAESTRA, encoding='utf-8')):
    if r['id_eleccion'] != '2002-PRES-1' or int(r['codigo_opcion']) >= 900: continue
    k = k_m(r); g02[k]['dep'] = r['nombre_depto']; g02[k]['mun'] = r['nombre_muni']
    g02[k]['cand'].append((int(r['votos'] or 0), r['nombre_opcion'].strip(), r['partido_nombre'].strip()))

filas = []
for k in sorted(set(g06) & set(g02)):
    d06 = g06[k]
    c06 = {c: v for c, v in d06.items() if c < 900}
    t06 = d06.get(999, 0)
    if t06 == 0 or not c06: continue
    ganador06 = max(c06, key=c06.get)
    c02 = sorted(g02[k]['cand'], reverse=True)
    t02 = sum(v for v, *_ in c02)
    if t02 == 0: continue
    g = c02[0]
    sh = lambda pred: sum(v for v, n, p in c02 if pred(n, p)) / t02
    filas.append({
        'codigo_depto': k[0], 'nombre_depto': g02[k]['dep'], 'codigo_muni': k[0]*1000 + k[1],
        'nombre_muni': g02[k]['mun'],
        'y_gano_uribe_2006': int(ganador06 == 3),
        'ganador2006_candidato': NOM06[ganador06], 'ganador2006_partido': PAR06[ganador06],
        'ganador2002_candidato': g[1], 'ganador2002_partido': g[2],
        'votos_candidatos_2002': t02, 'n_candidatos_2002': len(c02),
        'share_uribe_2002': round(sh(lambda n, p: 'URIBE' in n), 4),
        'share_liberal_2002': round(sh(lambda n, p: 'LIBERAL' in p.upper() or 'SERPA' in n.upper()), 4),
        'share_ganador_2002': round(g[0] / t02, 4),
        'margen_2002': round((c02[0][0] - (c02[1][0] if len(c02) > 1 else 0)) / t02, 4),
        'votos_candidatos_2006': sum(c06.values()),
        'share_uribe_2006': round(c06.get(3, 0) / sum(c06.values()), 4),
    })
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(filas[0].keys())); w.writeheader(); w.writerows(filas)
print('filas', len(filas))
print('y_gano_uribe_2006', Counter(r['y_gano_uribe_2006'] for r in filas))
print('ganador 2006', Counter(r['ganador2006_candidato'] for r in filas).most_common(4))
