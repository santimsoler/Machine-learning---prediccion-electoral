# Presidencial Colombia 2010 (1ª y 2ª vuelta) por municipio, desde ConVotoEst_1.msi (CD 2010 RNEC).
# El MSI trae 35 bases Access (una por departamento + nacional). Corporación 4 = 1ª vuelta, 9 = 2ª vuelta.
# Fechas (verificadas en el aplicativo): 30-05-2010 y 20-06-2010.
# Control: suma de municipios por departamento y candidato = RESUMEN_DEPARTAMENTOS de la misma base.
import os, sys, glob, csv
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mdbmini import Mdb
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FILES = os.path.join(S, 'x2010', 'files')
OUT = os.path.join(S, 'out4', 'presidencial_2010.csv')
CORP = {4: ('2010-PRES-1', '2010-05-30'), 9: ('2010-PRES-2', '2010-06-20')}
COLS = ['id_eleccion','pais','fecha','oficio','anio','codigo_depto_rnec','nombre_depto','codigo_muni_rnec',
        'nombre_muni','codigo_opcion','nombre_opcion','partido_codigo','partido_nombre','votos',
        'votos_blancos','votos_nulos','total_control','diferencia_control','estado_control','fuente',
        'circunscripcion','potencial_electoral']
filas = []; control = Counter(); nac = defaultdict(int)
# Departamentos desde la base nacional (para bases departamentales sin tabla DEPARTAMENTOS).
# Los ID llevan un prefijo por elección (0, 10.000.000 o 50.000.000): se compara el resto.
DEP_NAC = {}
for f in glob.glob(os.path.join(FILES, '_*')):
    if open(f, 'rb').read(20)[4:19] != b'Standard Jet DB': continue
    db = Mdb(f); cat = db.catalogo()
    if 'RESUMEN_NACIONAL' in cat:
        for r in db.filas(cat['DEPARTAMENTOS']):
            if r['ID'] > 0: DEP_NAC[r['ID'] % 10_000_000] = r
for f in sorted(glob.glob(os.path.join(FILES, '_*'))):
    if open(f, 'rb').read(20)[4:19] != b'Standard Jet DB': continue
    db = Mdb(f); cat = db.catalogo()
    if 'RESUMEN_NACIONAL' in cat or 'MUNICIPIOS' not in cat: continue
    mun = {r['ID']: r for r in db.filas(cat['MUNICIPIOS'])}
    if 'DEPARTAMENTOS' in cat:
        dep = {r['ID']: r for r in db.filas(cat['DEPARTAMENTOS'])}
    else:
        dep = {m['DEPARTAMENTO']: DEP_NAC[m['DEPARTAMENTO'] % 10_000_000] for m in mun.values()}
    cand = {(r['CORPORACION'], r['CODIGO']): r['NOMBRE'].strip() for r in db.filas(cat['CANDIDATOS'])}
    g = defaultdict(lambda: defaultdict(int))
    if 'RESUMEN_MUNICIPIOS' in cat:
        nivel = 'RESUMEN_MUNICIPIOS'
        for r in db.filas(cat['RESUMEN_MUNICIPIOS']):
            if r['CORPORACION'] in CORP:
                g[(r['CORPORACION'], r['MUNICIPIO'])][r['CANDIDATO']] += r['VOTACION'] or 0
    else:   # sin resumen municipal: se suma desde las mesas (mesa -> puesto -> zona -> municipio)
        nivel = 'RESUMEN_MESAS'
        mesa = {r['ID']: r['PUESTO'] for r in db.filas(cat['MESAS'])}
        puesto = {r['ID']: r['ZONA'] for r in db.filas(cat['PUESTOS'])}
        zona = {r['ID']: r['MUNICIPIO'] for r in db.filas(cat['ZONAS'])}
        for r in db.filas(cat['RESUMEN_MESAS']):
            if r['CORPORACION'] in CORP:
                mid = zona[puesto[mesa[r['MESA']]]]
                g[(r['CORPORACION'], mid)][r['CANDIDATO']] += r['VOTACION'] or 0
    # control departamental
    rd = defaultdict(int); sm = defaultdict(int)
    for r in db.filas(cat['RESUMEN_DEPARTAMENTOS']):
        if r['CORPORACION'] in CORP: rd[(r['CORPORACION'], r['DEPARTAMENTO'], r['CANDIDATO'])] += r['VOTACION'] or 0
    for (corp, mid), d in g.items():
        m = mun[mid]; dp = dep[m['DEPARTAMENTO']]
        for c, v in d.items(): sm[(corp, m['DEPARTAMENTO'], c)] += v
    dif_dep = {k: sm.get(k, 0) - rd.get(k, 0) for k in set(sm) | set(rd)}
    for k, v in dif_dep.items(): control['cuadra' if v == 0 else 'no_cuadra'] += 1
    for (corp, mid), d in g.items():
        m = mun[mid]; dp = dep[m['DEPARTAMENTO']]
        eid, fecha = CORP[corp]
        dif_d = sum(abs(dif_dep.get((corp, m['DEPARTAMENTO'], c), 0)) for c in d)
        for c, v in d.items():
            nac[(corp, c)] += v
            if c in ('996', '997', '998'): continue
            filas.append(dict(id_eleccion=eid, pais='CO', fecha=fecha, oficio='presidencial', anio=2010,
                codigo_depto_rnec=dp['CODIGO'], nombre_depto=dp['DESCRIPCION'].strip(),
                codigo_muni_rnec=m['CODIGO'], nombre_muni=m['DESCRIPCION'].strip(),
                codigo_opcion=c, nombre_opcion=cand.get((corp, c), ''), partido_codigo='', partido_nombre='',
                votos=v, votos_blancos=d.get('996', 0), votos_nulos=d.get('997', 0),
                total_control='', diferencia_control=dif_d,
                estado_control='cuadra_depto' if dif_d == 0 else 'no_cuadra_depto',
                fuente='ConVotoEst_1.msi (CD 2010 RNEC), ' + nivel, circunscripcion='',
                potencial_electoral=(m['POVOMUJE'] or 0) + (m['POVOHOMB'] or 0)))
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(filas)
print('filas', len(filas), Counter(r['id_eleccion'] for r in filas))
print('control depto x candidato:', dict(control))
print('municipios:', {e: len({(r['codigo_depto_rnec'], r['codigo_muni_rnec']) for r in filas if r['id_eleccion']==e}) for e in ('2010-PRES-1','2010-PRES-2')})
names = {}
for r in filas: names[r['codigo_opcion']] = r['nombre_opcion']
for (corp, c), v in sorted(nac.items()): print(CORP[corp][0], c, names.get(c, c), v)
