# Presidencial Argentina 2011-2023 por sección (departamento/partido/comuna), desde los CSV provisorios
# de la DINE (estándar de preservación de resultados electorales). Recuento PROVISORIO.
import csv, io, os, zipfile, sys
from collections import defaultdict, Counter
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = os.path.join(S, 'ar')
OUT = os.path.join(S, 'out4', 'ar_presidencial_secciones_2011_2023.csv')
FUENTES = [  # id, fecha, zip, csv interno
    ('AR-2011-PRES-1', '2011-10-23', '2011_provisorios_generales.zip', '2011_Generales/ResultadosElectorales.csv'),
    ('AR-2015-PRES-1', '2015-10-25', '2015_provisorios_generales.zip', '2015_Generales/ResultadosElectorales.csv'),
    ('AR-2015-PRES-2', '2015-11-22', '2015_provisorios_ballotage.zip', '2015_Ballotage/ResultadosElectorales.csv'),
    ('AR-2019-PRES-1', '2019-10-27', '2019_provisorios_generales.zip', '2019_Generales/ResultadosElectorales.csv'),
    ('AR-2023-PRES-1', '2023-10-22', '2023_generales.zip', '2023_Generales/ResultadoElectorales_2023_Generales.csv'),
    ('AR-2023-PRES-2', '2023-11-19', '2023_segunda_vuelta.zip', '2023_segundavuelta/ResultadosElectorales_2023_SegundaVuelta.csv'),
]
COLS = ['id_eleccion','pais','anio','vuelta','fecha','recuento','distrito_id','distrito_nombre','seccion_id',
        'seccion_nombre','agrupacion_id','agrupacion_nombre','votos','votos_blancos','votos_nulos',
        'votos_otros_no_positivos','votos_positivos_seccion','votos_validos_seccion','share_positivos',
        'electores_seccion','mesas_seccion','participacion','fuente']
filas = []
for eid, fecha, zf, inner in FUENTES:
    pos = defaultdict(int); tipos = defaultdict(Counter); nombres = {}; electores = {}; dname = {}; sname = {}
    cargos = Counter()
    with zipfile.ZipFile(os.path.join(A, zf)) as z, z.open(inner) as fh:
        rd = csv.DictReader(io.TextIOWrapper(fh, encoding='utf-8-sig', errors='replace'))
        for r in rd:
            r = {k.lower(): v for k, v in r.items()}
            cn = (r['cargo_nombre'] or '').upper()
            cargos[cn] += 1
            if not cn.startswith('PRESIDENTE'): continue
            d = int(r['distrito_id']); s = int(r['seccion_id'])
            dname[d] = r['distrito_nombre'].strip(); sname[(d, s)] = r['seccion_nombre'].strip()
            mesa = (d, s, r['circuito_id'].strip(), r['mesa_id'].strip(), r['mesa_tipo'].strip())
            if r.get('mesa_electores', '').strip(): electores[mesa] = int(float(r['mesa_electores']))
            v = int(float(r['votos_cantidad'] or 0)); t = r['votos_tipo'].strip().upper()
            if t == 'POSITIVO':
                a = r['agrupacion_id'].strip().lstrip('0') or '0'
                pos[(d, s, a)] += v; nombres[a] = ' '.join(r['agrupacion_nombre'].split())
            else:
                tipos[(d, s)][t] += v
    el = defaultdict(int); me = Counter()
    for (d, s, *_), e in electores.items(): el[(d, s)] += e; me[(d, s)] += 1
    posec = defaultdict(int)
    for (d, s, a), v in pos.items(): posec[(d, s)] += v
    for (d, s, a), v in pos.items():
        tp = tipos[(d, s)]; bl = tp.get('EN BLANCO', 0); nu = tp.get('NULO', 0)
        otros = sum(x for k, x in tp.items() if k not in ('EN BLANCO', 'NULO'))
        val = posec[(d, s)] + bl; emit = val + nu + otros
        filas.append(dict(id_eleccion=eid, pais='AR', anio=int(eid[3:7]), vuelta=int(eid[-1]), fecha=fecha,
            recuento='provisorio', distrito_id=d, distrito_nombre=dname[d], seccion_id=s, seccion_nombre=sname[(d, s)],
            agrupacion_id=a, agrupacion_nombre=nombres[a], votos=v, votos_blancos=bl, votos_nulos=nu,
            votos_otros_no_positivos=otros, votos_positivos_seccion=posec[(d, s)], votos_validos_seccion=val,
            share_positivos=round(v / posec[(d, s)], 5) if posec[(d, s)] else '',
            electores_seccion=el.get((d, s), ''), mesas_seccion=me.get((d, s), ''),
            participacion=round(emit / el[(d, s)], 4) if el.get((d, s)) else '', fuente=f'DINE {zf} ({inner})'))
    tot = Counter(); 
    for (d, s, a), v in pos.items(): tot[nombres[a]] += v
    tti = Counter()
    for c in tipos.values(): tti.update(c)
    print(eid, '| secciones', len(posec), '| electores', sum(el.values()), '| cargos', [c for c in cargos if c.startswith('PRES')],
          '| no positivos', dict(tti), flush=True)
    for n, v in tot.most_common(4): print('     ', n, f'{v:,}', flush=True)
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(filas)
print('filas', len(filas))
