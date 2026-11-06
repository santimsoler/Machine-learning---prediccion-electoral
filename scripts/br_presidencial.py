# Base presidencial Brasil 2002-2026 por municipio y turno (TSE, datos abiertos, vía API CKAN).
# Control: suma de votos nominales de candidatos = QT_TOTAL_VOTOS_VALIDOS del detalle de apuración.
import csv, os, glob
from collections import defaultdict, Counter
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
B = os.path.join(S, 'br'); OUT = os.path.join(S, 'out4', 'br_presidencial_municipios_2002_2026.csv')
COLS = ['id_eleccion','pais','anio','vuelta','uf','cd_municipio_tse','nm_municipio','nr_candidato','nm_candidato',
        'sg_partido','votos','votos_validos_muni','share_validos','votos_brancos','votos_nulos','aptos',
        'comparecimento','participacion','diferencia_control','estado_control','fuente']
filas = []
for anio in range(2002, 2027, 4):
    fv = os.path.join(B, f'br_{anio}_votos_municipio.csv'); fd = os.path.join(B, f'br_{anio}_detalle_municipio.csv')
    if not os.path.exists(fv): continue
    det = {}
    for r in csv.DictReader(open(fd, encoding='utf-8')):
        det[(r['turno'], r['uf'], int(r['cd_municipio']))] = r
    v = defaultdict(int); info = {}
    for r in csv.DictReader(open(fv, encoding='utf-8')):
        k = (r['turno'], r['uf'], int(r['cd_municipio']))
        v[k + (r['nr_candidato'],)] += int(r['votos']); info[k + (r['nr_candidato'],)] = r
    sumv = defaultdict(int)
    for k, x in v.items(): sumv[k[:3]] += x
    for k, x in v.items():
        m = k[:3]; d = det.get(m); r = info[k]
        val = int(d['QT_TOTAL_VOTOS_VALIDOS']) if d else None
        dif = sumv[m] - val if d else ''
        apt = int(d['QT_APTOS']) if d else None; comp = int(d['QT_COMPARECIMENTO']) if d else None
        filas.append(dict(id_eleccion=f'BR-{anio}-PRES-{k[0]}', pais='BR', anio=anio, vuelta=int(k[0]), uf=k[1],
            cd_municipio_tse=k[2], nm_municipio=r['nm_municipio'], nr_candidato=k[3], nm_candidato=r['nm_urna_candidato'],
            sg_partido=r['sg_partido'], votos=x, votos_validos_muni=val if val is not None else '',
            share_validos=round(x / val, 5) if val else '', votos_brancos=d['QT_VOTOS_BRANCOS'] if d else '',
            votos_nulos=d['QT_TOTAL_VOTOS_NULOS'] if d else '', aptos=apt if apt is not None else '',
            comparecimento=comp if comp is not None else '', participacion=round(comp / apt, 4) if apt else '',
            diferencia_control=dif, estado_control=('cuadra' if dif == 0 else 'no_cuadra') if d else 'sin_control',
            fuente='TSE dadosabertos: votação nominal + detalhe da apuração por município e zona'))
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(filas)
print('filas', len(filas))
res = defaultdict(lambda: [set(), Counter(), Counter()])
for r in filas:
    x = res[r['id_eleccion']]; x[0].add((r['uf'], r['cd_municipio_tse'])); x[1][r['estado_control']] += 1; x[2][r['nm_candidato']] += r['votos']
for e in sorted(res):
    m, est, tot = res[e]
    print(f'{e}: municipios {len(m)} | {dict(est)} | ' + ' / '.join(f'{n} {v:,}' for n, v in tot.most_common(3)))
