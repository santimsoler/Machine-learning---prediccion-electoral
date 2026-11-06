# Base nacional (eje principal): presidencia Colombia 1998 (1ª vuelta) -> 2002 (1ª vuelta), por municipio.
# Target: y_gano_uribe_2002 = 1 si el candidato más votado en el municipio en 2002 es Álvaro Uribe.
# Predictores: sólo 1998 (anterior). Partido Liberal (Serpa) y coalición de Pastrana se miden por separado.
import csv, os
from collections import defaultdict, Counter
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CSV = os.path.join(S, 'out4', 'resultados_electorales_colombia.csv')
OUT = os.path.join(S, 'tp1', 'base_nacional_presidencial_1998_2002.csv')

def key(r):
    d = int(r['codigo_depto_rnec']); m = int(r['codigo_muni_rnec'])
    return d, (m - d*1000 if m > 999 else m)

def leer(eid):
    t = defaultdict(lambda: {'cand': [], 'dep': '', 'mun': ''})
    for r in csv.DictReader(open(CSV, encoding='utf-8')):
        if r['id_eleccion'] != eid or int(r['codigo_opcion']) >= 900: continue
        k = key(r)
        t[k]['dep'] = r['nombre_depto']; t[k]['mun'] = r['nombre_muni']
        t[k]['cand'].append((int(r['votos'] or 0), r['nombre_opcion'].strip(), r['partido_nombre'].strip()))
    return t

p98 = leer('1998-PRES-1'); p02 = leer('2002-PRES-1')
ks = sorted(set(p98) & set(p02))
print('munis 1998:', len(p98), '2002:', len(p02), 'en ambos:', len(ks))
filas = []
for k in ks:
    c98 = sorted(p98[k]['cand'], reverse=True); c02 = sorted(p02[k]['cand'], reverse=True)
    t98 = sum(v for v,*_ in c98); t02 = sum(v for v,*_ in c02)
    if t98 == 0 or t02 == 0: continue
    g98, g02 = c98[0], c02[0]
    sh = lambda pred: sum(v for v,n,p in c98 if pred(n,p)) / t98
    filas.append({
        'codigo_depto': k[0], 'nombre_depto': p02[k]['dep'], 'codigo_muni': k[0]*1000 + k[1],
        'nombre_muni': p02[k]['mun'],
        'y_gano_uribe_2002': int(g02[1].startswith('ALVARO') and 'URIBE' in g02[1]),
        'ganador2002_candidato': g02[1], 'ganador2002_partido': g02[2],
        'ganador1998_candidato': g98[1], 'ganador1998_partido': g98[2],
        'votos_candidatos_1998': t98, 'n_candidatos_1998': len(c98),
        'share_liberal_1998': round(sh(lambda n,p: 'LIBERAL' in p.upper() or 'SERPA' in n.upper()), 4),
        'share_coalicion_1998': round(sh(lambda n,p: p.upper() == 'COALICION'), 4),
        'share_ganador_1998': round(g98[0] / t98, 4),
        'margen_1998': round((c98[0][0] - (c98[1][0] if len(c98) > 1 else 0)) / t98, 4),
        'votos_candidatos_2002': t02,
        'share_uribe_2002': round(sum(v for v,n,p in c02 if 'URIBE' in n) / t02, 4),
    })
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(filas[0].keys())); w.writeheader(); w.writerows(filas)
print('filas:', len(filas))
print('y_gano_uribe_2002:', Counter(r['y_gano_uribe_2002'] for r in filas))
print('ganador 2002 municipal:', Counter(r['ganador2002_candidato'] for r in filas).most_common(4))
print('ganador 1998 municipal:', Counter(r['ganador1998_candidato'] for r in filas).most_common(4))
