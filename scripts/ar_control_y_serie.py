# 1) Control: provisorio (secciones) vs definitivo (provincias) en 2011, 2015 (1ª y 2ª) y 2019.
# 2) Serie provincial 1983-2023: definitivos 1983-2019 + 2023 (1ª y 2ª) desde provisorios sumados a provincia.
import csv, os
from collections import defaultdict
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SEC = os.path.join(S, 'out4', 'ar_presidencial_secciones_2011_2023.csv')
PRO = os.path.join(S, 'out4', 'ar_presidencial_provincias_1983_2019.csv')
OUT = os.path.join(S, 'out4', 'ar_presidencial_provincias_1983_2023.csv')
sec = list(csv.DictReader(open(SEC, encoding='utf-8'))); pro = list(csv.DictReader(open(PRO, encoding='utf-8')))
# --- control de cobertura: votos positivos provisorios / definitivos por provincia
pos_prov = defaultdict(int); seen = set()
for r in sec:
    k = (r['id_eleccion'], r['distrito_id'], r['seccion_id'])
    if k not in seen: seen.add(k); pos_prov[(r['id_eleccion'], r['distrito_id'])] += int(r['votos_positivos_seccion'])
pos_def = {}
for r in pro: pos_def[(r['id_eleccion'], r['distrito_id'])] = int(r['votos_positivos_distrito'])
print('Cobertura provisorio / definitivo (votos positivos):')
cob = {}
for e in ('AR-2011-PRES-1', 'AR-2015-PRES-1', 'AR-2015-PRES-2', 'AR-2019-PRES-1'):
    ks = [k for k in pos_def if k[0] == e]
    rat = {k[1]: pos_prov.get(k, 0) / pos_def[k] for k in ks}
    cob.update({(e, d): v for d, v in rat.items()})
    tot = sum(pos_prov.get(k, 0) for k in ks) / sum(pos_def[k] for k in ks)
    print(f'  {e}: país {tot:.4f} | provincias min {min(rat.values()):.4f} max {max(rat.values()):.4f}')
# --- serie provincial
COLS = list(pro[0].keys())
filas = list(pro)
ag = defaultdict(int); bl = defaultdict(int); nu = defaultdict(int); pos = defaultdict(int); el = defaultdict(int); emit = defaultdict(int)
nom = {}; dn = {}; seen = set(); fechas = {}
for r in sec:
    if not r['id_eleccion'].startswith('AR-2023'): continue
    e, d = r['id_eleccion'], r['distrito_id']
    ag[(e, d, r['agrupacion_nombre'])] += int(r['votos']); dn[(e, d)] = r['distrito_nombre']; fechas[e] = r['fecha']
    k = (e, d, r['seccion_id'])
    if k not in seen:
        seen.add(k); bl[(e, d)] += int(r['votos_blancos']); nu[(e, d)] += int(r['votos_nulos'])
        pos[(e, d)] += int(r['votos_positivos_seccion']); el[(e, d)] += int(r['electores_seccion'] or 0)
        emit[(e, d)] += int(r['votos_validos_seccion']) + int(r['votos_nulos']) + int(r['votos_otros_no_positivos'])
for (e, d, a), v in ag.items():
    filas.append(dict(id_eleccion=e, pais='AR', anio=2023, vuelta=int(e[-1]), fecha=fechas[e], recuento='provisorio',
        distrito_id=d, distrito_nombre=dn[(e, d)], agrupacion_nombre=a, formula='', votos=v, votos_blancos=bl[(e, d)],
        votos_nulos=nu[(e, d)], votos_positivos_distrito=pos[(e, d)], share_positivos=round(v / pos[(e, d)], 5),
        electores_distrito=el[(e, d)], total_votantes=emit[(e, d)], participacion=round(emit[(e, d)] / el[(e, d)], 4),
        diferencia_control='', estado_control='provisorio_sin_definitivo',
        fuente='DINE provisorios 2023 sumados a provincia'))
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(filas)
print('serie provincial: filas', len(filas), '| elecciones', sorted({r['id_eleccion'] for r in filas}))
# --- agrega a la base por sección la cobertura provincial del provisorio
for r in sec: r['cobertura_provisorio_provincia'] = round(cob[(r['id_eleccion'], r['distrito_id'])], 4) if (r['id_eleccion'], r['distrito_id']) in cob else ''
with open(SEC, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(sec[0].keys())); w.writeheader(); w.writerows(sec)
part = [float(r['participacion']) for r in sec if r['participacion']]
print('participación por sección: min', min(part), 'max', max(part), '| > 1:', sum(1 for p in part if p > 1))
