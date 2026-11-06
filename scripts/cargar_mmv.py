# Presidencial Colombia 2018, 2022 y 2026 (archivos "mesa a mesa" del Observatorio Electoral RNEC).
# Se suman las mesas a municipio. Fechas: 2018 (27-05 y 17-06), 2022 (29-05 y 19-06), 2026 (31-05 y 21-06).
# 2026: estructura según "Estructuras Básicas (1808).pdf" incluido en el zip.
import os, csv, glob
from collections import defaultdict, Counter
import openpyxl
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
M = os.path.join(S, 'mmv')
OUT = os.path.join(S, 'out4', 'presidencial_2018_2022_2026.csv')
COLS = ['id_eleccion','pais','fecha','oficio','anio','codigo_depto_rnec','nombre_depto','codigo_muni_rnec',
        'nombre_muni','codigo_opcion','nombre_opcion','partido_codigo','partido_nombre','votos',
        'votos_blancos','votos_nulos','total_control','diferencia_control','estado_control','fuente',
        'circunscripcion','potencial_electoral']
ESP = {996: 'blanco', 997: 'nulo', 998: 'no_marcado'}

def salida(eid, fecha, anio, g, nom_c, par_c, nom_m, pot, fuente):
    filas = []
    for (dep, mun), d in g.items():
        for c, v in d.items():
            if c in ESP: continue
            filas.append(dict(id_eleccion=eid, pais='CO', fecha=fecha, oficio='presidencial', anio=anio,
                codigo_depto_rnec=dep, nombre_depto=nom_m.get((dep, mun), ('', ''))[0],
                codigo_muni_rnec=mun, nombre_muni=nom_m.get((dep, mun), ('', ''))[1],
                codigo_opcion=c, nombre_opcion=nom_c.get(c, ''), partido_codigo=par_c.get(c, ('', ''))[0],
                partido_nombre=par_c.get(c, ('', ''))[1], votos=v, votos_blancos=d.get(996, 0),
                votos_nulos=d.get(997, 0), total_control='', diferencia_control='', estado_control='sin_control',
                fuente=fuente, circunscripcion='', potencial_electoral=pot.get((dep, mun), '')))
    return filas

todas = []; resumen = {}
# ---------- 2018 (xlsx) ----------
def leer_xlsx(path, hoja):
    wb = openpyxl.load_workbook(path, read_only=True)
    it = wb[hoja].iter_rows(values_only=True); h = [str(x).strip() for x in next(it)]
    for r in it: yield dict(zip(h, r))
x1 = os.path.join(M, '..', 'mmv2018', 'MMV_NACIONAL_PRESIDENTE_2018_1v.xlsx')
x2 = os.path.join(M, '..', 'mmv2018', 'MMV_NACIONAL_PRESIDENTE_2018_2v.xlsx')
nom_m = {}; pot = defaultdict(int)
for r in leer_xlsx(x1, 'DIVIPOL'):
    k = (int(r['DEP']), int(r['MUN'])); nom_m[k] = (str(r['DEPARTAMENTO']).strip(), str(r['MUNICIPIO']).strip())
    pot[k] += int(r['HOMBRE'] or 0) + int(r['MUJERES'] or 0)
for eid, fecha, path, hoja in [('2018-PRES-1', '2018-05-27', x1, 'MMV ESCRUTINIO FINAL'),
                               ('2018-PRES-2', '2018-06-17', x2, 'MVV_Votación_Mesa_Mesa_2da Vuel')]:
    g = defaultdict(lambda: defaultdict(int)); nom_c = {}; par_c = {}
    for r in leer_xlsx(path, hoja):
        if r.get('DEP') is None: continue
        k = (int(r['DEP']), int(r['MUN'])); c = int(r.get('CODCAN', r.get('CAN')))
        g[k][c] += int(r['VOTOS'] or 0)
        nom_c[c] = str(r['CANDIDATO']).strip(); par_c[c] = (r['PAR'], str(r.get('PARTIDO', '') or '').strip())
    todas += salida(eid, fecha, 2018, g, nom_c, par_c, nom_m, pot, os.path.basename(path) + ' / ' + hoja)
    resumen[eid] = (len(g), Counter({nom_c.get(c, c): v for c, v in Counter({c: sum(d.get(c, 0) for d in g.values()) for c in nom_c}).items()}))
# ---------- 2022 (csv con nombres) ----------
for eid, fecha, path in [('2022-PRES-1', '2022-05-29', glob.glob(os.path.join(M, '*2022_1v*', '*.csv'))[0]),
                         ('2022-PRES-2', '2022-06-19', glob.glob(os.path.join(M, '*2022_2v*', '*.csv'))[0])]:
    g = defaultdict(lambda: defaultdict(int)); nom_c = {}; par_c = {}; nm = {}
    with open(path, encoding='latin-1', newline='') as fh:
        for r in csv.DictReader(fh, delimiter=';'):
            if r['CORCODIGO'] != '01': continue
            k = (int(r['DEP']), int(r['MUN'])); c = int(r['CAN'])
            g[k][c] += int(r['VOTOS'] or 0)
            nom_c[c] = r['CANNOMBRE'].strip(' .'); par_c[c] = (int(r['PAR']), r['PARNOMBRE'].strip())
            nm[k] = (r['DEPNOMBRE'].strip(), r['MUNNOMBRE'].strip())
    todas += salida(eid, fecha, 2022, g, nom_c, par_c, nm, {}, os.path.basename(path))
    resumen[eid] = (len(g), Counter({nom_c[c]: sum(d.get(c, 0) for d in g.values()) for c in nom_c}))
# ---------- 2026 (escrutinio codificado + archivos básicos) ----------
def fijo(linea, anchos):
    out, p = [], 0
    for a in anchos: out.append(linea[p:p+a]); p += a
    return out
for eid, fecha, sub, bas in [('2026-PRES-1', '2026-05-31', '4cea55b3*/MMV_Presidente1V_2026/MMV_Presidente1V_2026', 'basicos2026_1'),
                             ('2026-PRES-2', '2026-06-21', '0790a112*/MMV_Presidente2V_2026', 'basicos2026_2')]:
    d0 = glob.glob(os.path.join(M, sub))[0]; b = os.path.join(M, bas)
    nom_c = {}; par_c = {}; partidos = {}
    for l in open(glob.glob(os.path.join(b, 'PARTIDOS_*'))[0], encoding='latin-1'):
        if l.strip(): partidos[int(l[:5])] = l[5:205].strip()
    for l in open(glob.glob(os.path.join(b, 'CANDIDATOS_*'))[0], encoding='latin-1'):
        if not l.strip(): continue
        corp, circ, dep, mun, com, par, can, tipo, nomb, apel = fijo(l, [3,1,2,3,2,5,3,1,50,50])
        nom_c[int(can)] = (nomb.strip() + ' ' + apel.strip()).strip(); par_c[int(can)] = (int(par), partidos.get(int(par), ''))
    nom_m = {}; pot = defaultdict(int)
    for l in open(glob.glob(os.path.join(b, 'DIVIPOL_*'))[0], encoding='latin-1'):
        if not l.strip(): continue
        dep, mun, zon, pue, ndep, nmun, npue, ind, ph, pm, mes = fijo(l, [2,3,2,2,12,30,40,1,8,8,6])
        k = (int(dep), int(mun)); nom_m[k] = (ndep.strip(), nmun.strip()); pot[k] += int(ph) + int(pm)
    g = defaultdict(lambda: defaultdict(int))
    with open(os.path.join(d0, '_ficheros_MMV_4_MMV_9999_ESCRUTINIO.csv'), encoding='latin-1') as fh:
        for l in fh:
            p = l.strip().split(';')
            if len(p) < 12 or p[0] != '9999': continue
            k = (int(p[1]), int(p[2])); c = int(p[10])
            g[k][c] += int(p[11])
    todas += salida(eid, fecha, 2026, g, nom_c, par_c, nom_m, pot, '_ficheros_MMV_4_MMV_9999_ESCRUTINIO.csv + archivos básicos (RNEC)')
    tot = Counter()
    for d in g.values():
        for c, v in d.items(): tot[nom_c.get(c, ESP.get(c, c))] += v
    resumen[eid] = (len(g), tot)
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(todas)
print('filas', len(todas))
for e, (n, tot) in resumen.items():
    print(e, 'municipios', n); [print('    ', k, v) for k, v in tot.most_common(6)]
