# Presidencial Colombia 2014 (1ª y 2ª vuelta) por municipio.
# Fuente: setupEstadisticas2014-v2.exe (CD 2014 RNEC) -> bloque LZMA de Inno Setup -> bases SQLite.
# db_0 = 1ª vuelta (25-05-2014), db_1 = 2ª vuelta (15-06-2014), según la tabla 'parametros' de cada base.
# Datos por mesa (tablas votacion_XX, una por departamento); se suman a municipio.
import os, sqlite3, csv
from collections import defaultdict, Counter
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BASES = {'2014-PRES-1': ('x2014db/db_0.sqlite', '2014-05-25'), '2014-PRES-2': ('x2014db/db_1.sqlite', '2014-06-15')}
OUT = os.path.join(S, 'out4', 'presidencial_2014.csv')
COLS = ['id_eleccion','pais','fecha','oficio','anio','codigo_depto_rnec','nombre_depto','codigo_muni_rnec',
        'nombre_muni','codigo_opcion','nombre_opcion','partido_codigo','partido_nombre','votos',
        'votos_blancos','votos_nulos','total_control','diferencia_control','estado_control','fuente',
        'circunscripcion','potencial_electoral']
filas = []
for eid, (rel, fecha) in BASES.items():
    con = sqlite3.connect(f'file:{os.path.join(S, rel)}?mode=ro', uri=True)
    fecha_db = con.execute("select valor from parametros where descripcion='Fecha Eleccion'").fetchone()[0]
    tabs = [r[0] for r in con.execute("select name from sqlite_master where type='table' and name like 'votacion_%'")]
    g = defaultdict(lambda: defaultdict(int)); nom = {}; par = {}; nmun = {}
    for t in tabs:
        for dep, ddep, mun, dmun, p, dp, c, dc, v in con.execute(
                f'select depto, desc_depto, mpio, desc_mpio, partido, desc_partido, candidato, desc_candidato, votos from {t}'):
            g[(dep, mun)][c] += v or 0
            nom[c] = (dc or '').strip(); par[c] = (p, (dp or '').strip()); nmun[(dep, mun)] = (ddep.strip(), dmun.strip())
    # Control: suma de mesas por departamento y candidato = tabla x_resum_dpto_XX de la misma base
    dif_dep = {}
    for t in tabs:
        dd = t.split('_')[1]
        m = dict(con.execute(f'select candidato, sum(votos) from {t} group by candidato'))
        r = dict(con.execute(f'select candidato, sum(votos) from x_resum_dpto_{dd} group by candidato'))
        dif_dep[int(dd)] = sum(abs(m.get(c, 0) - r.get(c, 0)) for c in set(m) | set(r))
    print(eid, 'departamentos que no cuadran:', [d for d, v in dif_dep.items() if v])
    nac = Counter()
    for (dep, mun), d in g.items():
        for c, v in d.items():
            nac[c] += v
            if c in (996, 997, 998): continue
            filas.append(dict(id_eleccion=eid, pais='CO', fecha=fecha, oficio='presidencial', anio=2014,
                codigo_depto_rnec=dep, nombre_depto=nmun[(dep, mun)][0], codigo_muni_rnec=mun,
                nombre_muni=nmun[(dep, mun)][1], codigo_opcion=c, nombre_opcion=nom[c],
                partido_codigo=par[c][0], partido_nombre=par[c][1], votos=v,
                votos_blancos=d.get(996, 0), votos_nulos=d.get(997, 0), total_control='',
                diferencia_control=dif_dep[dep], estado_control='cuadra_depto' if dif_dep[dep] == 0 else 'no_cuadra_depto',
                fuente='setupEstadisticas2014-v2.exe (CD 2014 RNEC), SQLite por mesa', circunscripcion='',
                potencial_electoral=''))
    print(eid, 'fecha en base:', fecha_db, '| municipios:', len(g), '| tablas:', len(tabs))
    for c, v in nac.most_common(): print('   ', c, nom.get(c), v)
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(filas)
print('filas', len(filas))
