# Base presidencial Colombia 1998-2026: una fila por elección (vuelta) × municipio × candidato.
# Junta las cargas previas y normaliza códigos: codigo_muni = código RNEC del municipio (3 dígitos)
# y codigo_divipol = depto*1000 + muni. Agrega votos válidos (candidatos + blanco), share y participación.
import os, sys, csv
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dbfmini import read_dbf
from mdbmini import Mdb
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(S, 'out4', 'base_presidencial_colombia_1998_2026.csv')
FECHAS = {'1998-PRES-1': '1998-05-31', '1998-PRES-2': '1998-06-21', '2002-PRES-1': '2002-05-26',
          '2006-PRES-1': '2006-05-28'}
filas = []

def norm(dep, mun):
    dep, mun = int(dep), int(mun)
    return dep, (mun - dep*1000 if mun > 999 else mun)

# ---- 1998 y 2002: desde la tabla maestra (filas 996-999 excluidas) ----
pot02 = defaultdict(int)
db = Mdb(os.path.join(S, 'mdb2002', 'Estadistico2002.mdb')); cat = db.catalogo()
for r in db.filas(cat['divipol_presidente']):
    if not (r['cod_dpto'].isdigit() and r['cod_mpio'].isdigit()): continue   # filas de control ('ZZZ')
    pot02[(int(r['cod_dpto']), int(r['cod_mpio']))] += r['potencial'] or 0
for r in csv.DictReader(open(os.path.join(S, 'out4', 'resultados_electorales_colombia.csv'), encoding='utf-8')):
    if r['id_eleccion'] not in ('1998-PRES-1', '1998-PRES-2', '2002-PRES-1'): continue
    if int(r['codigo_opcion']) >= 900: continue
    dep, mun = norm(r['codigo_depto_rnec'], r['codigo_muni_rnec'])
    filas.append(dict(r, codigo_depto_rnec=dep, codigo_muni_rnec=mun,
                      potencial_electoral=''))   # padrón 2002 de divipol_presidente no confiable (Medellín suma 2,86 M): se omite

# ---- 2006: tb_votacion.dbf (corporación 03) + municipios_pre.dbf (padrón presidencial) ----
NOM06 = {1:'CARLOS ARTURO RINCON BARRETO',2:'ENRIQUE PAREJO GONZALEZ',3:'ALVARO URIBE VELEZ',4:'CARLOS GAVIRIA DIAZ',
         5:'HORACIO SERPA URIBE',6:'ALVARO LEYVA DURAN',7:'ANTANAS MOCKUS SIVICKAS'}
PAR06 = {}
for r in read_dbf(os.path.join(S, 'x2006', 'listas.dbf')):
    if r['CODI_COR'] == '03' and int(r['CODI_CAN']) < 900: PAR06[int(r['CODI_CAN'])] = (int(r['CODI_PAR']), r['MOVI_POL'].strip())
mun06 = {}; dep06 = {}
for r in read_dbf(os.path.join(S, 'x2006', 'municipios_pre.dbf')):
    mun06[(int(r['CODI_DEP']), int(r['CODI_MUN']))] = (r['NOMB_MUN'].strip(), int(r['POTE_TOT'] or 0))
for r in read_dbf(os.path.join(S, 'x2006', 'deptos_pre.dbf')):
    dep06[int(r['CODI_DEP'])] = r['NOMB_DEP'].strip()
g = defaultdict(lambda: defaultdict(int))
for r in read_dbf(os.path.join(S, 'x2006', 'tb_votacion.dbf')):
    if r['CODI_COR'] == '03': g[(int(r['CODI_DEP']), int(r['CODI_MUN']))][int(r['CODI_CAN'])] += int(r['VOTA_CAN'] or 0)
for (dep, mun), d in g.items():
    dif = sum(v for c, v in d.items() if c < 900) + d.get(996, 0) + d.get(997, 0) + d.get(998, 0) - d.get(999, 0)
    for c, v in d.items():
        if c >= 900: continue
        filas.append(dict(id_eleccion='2006-PRES-1', pais='CO', fecha='2006-05-28', oficio='presidencial', anio='2006',
            codigo_depto_rnec=dep, nombre_depto=dep06.get(dep, ''), codigo_muni_rnec=mun,
            nombre_muni=mun06.get((dep, mun), ('', ''))[0], codigo_opcion=c, nombre_opcion=NOM06[c],
            partido_codigo=PAR06.get(c, ('', ''))[0], partido_nombre=PAR06.get(c, ('', ''))[1], votos=v,
            votos_blancos=d.get(996, 0), votos_nulos=d.get(997, 0), total_control=d.get(999, 0),
            diferencia_control=dif, estado_control='cuadra' if dif == 0 and d.get(999, 0) else ('sin_control' if not d.get(999, 0) else 'no_cuadra'),
            fuente='tb_votacion.dbf corporación 03 (CD 2006 RNEC)', circunscripcion='',
            potencial_electoral=mun06.get((dep, mun), ('', ''))[1]))

# ---- 2010, 2014, 2018, 2022, 2026: cargas propias ----
for f in ['presidencial_2010.csv', 'presidencial_2014.csv', 'presidencial_2018_2022_2026.csv']:
    for r in csv.DictReader(open(os.path.join(S, 'out4', f), encoding='utf-8')):
        dep, mun = norm(r['codigo_depto_rnec'], r['codigo_muni_rnec'])
        filas.append(dict(r, codigo_depto_rnec=dep, codigo_muni_rnec=mun))

# ---- variables derivadas por municipio y elección ----
validos = defaultdict(int); blanc = {}
for r in filas:
    k = (r['id_eleccion'], r['codigo_depto_rnec'], r['codigo_muni_rnec'])
    validos[k] += int(r['votos'] or 0); blanc[k] = int(r['votos_blancos'] or 0)
COLS = ['id_eleccion','anio','vuelta','fecha','codigo_depto','nombre_depto','codigo_muni','codigo_divipol',
        'nombre_muni','codigo_opcion','nombre_opcion','partido_codigo','partido_nombre','votos',
        'votos_blancos','votos_nulos','votos_validos_muni','share_validos','potencial_electoral',
        'participacion','estado_control','fuente']
out = []
for r in filas:
    k = (r['id_eleccion'], r['codigo_depto_rnec'], r['codigo_muni_rnec'])
    val = validos[k] + blanc[k]
    pot = int(r['potencial_electoral']) if str(r.get('potencial_electoral', '')).strip() not in ('', 'None') else None
    emit = val + int(r['votos_nulos'] or 0)
    out.append({'id_eleccion': r['id_eleccion'], 'anio': int(r['id_eleccion'][:4]), 'vuelta': int(r['id_eleccion'][-1]),
        'fecha': FECHAS.get(r['id_eleccion'], r['fecha']), 'codigo_depto': r['codigo_depto_rnec'],
        'nombre_depto': r['nombre_depto'], 'codigo_muni': r['codigo_muni_rnec'],
        'codigo_divipol': int(r['codigo_depto_rnec'])*1000 + int(r['codigo_muni_rnec']),
        'nombre_muni': r['nombre_muni'], 'codigo_opcion': r['codigo_opcion'], 'nombre_opcion': r['nombre_opcion'],
        'partido_codigo': r['partido_codigo'], 'partido_nombre': r['partido_nombre'], 'votos': r['votos'],
        'votos_blancos': r['votos_blancos'], 'votos_nulos': r['votos_nulos'], 'votos_validos_muni': val,
        'share_validos': round(int(r['votos'] or 0) / val, 5) if val else '',
        'potencial_electoral': pot if pot else '',
        'participacion': round(emit / pot, 4) if pot else '',
        'estado_control': r['estado_control'], 'fuente': r['fuente']})
out.sort(key=lambda r: (r['id_eleccion'], r['codigo_depto'], r['codigo_muni'], -int(r['votos'] or 0)))
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(out)
print('filas', len(out))
res = defaultdict(lambda: [set(), Counter(), Counter(), 0])
for r in out:
    x = res[r['id_eleccion']]; x[0].add(r['codigo_divipol']); x[1][r['estado_control']] += 1
    x[2][r['nombre_opcion']] += int(r['votos'] or 0); x[3] += 1 if r['potencial_electoral'] != '' else 0
for e in sorted(res):
    m, est, tot, conpot = res[e]
    top = tot.most_common(2)
    print(f"{e}: municipios {len(m)} | filas {sum(est.values())} | control {dict(est)} | con padrón {conpot} | {top[0][0]} {top[0][1]:,} / {top[1][0]} {top[1][1]:,}")
