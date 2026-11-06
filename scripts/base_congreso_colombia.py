# Base Congreso Colombia 1998-2014: votos por partido (lista + voto preferente) por municipio,
# corporación (SEN, CAM) y circunscripción. Robustez del eje presidencial.
import os, sys, csv, glob, sqlite3
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dbfmini import read_dbf
from mdbmini import Mdb
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(S, 'out4', 'base_congreso_colombia_1998_2014.csv')
ESP = {996, 997, 998, 999}
# acumulador: (eleccion, corp, circ, dep, mun, partido) -> votos ; nombres y especiales aparte
V = defaultdict(int); PN = {}; MN = {}; DN = {}; BL = defaultdict(int); NU = defaultdict(int); EST = {}; FUENTE = {}
FECHA = {'1998': '1998-03-08', '2002': '2002-03-10', '2006': '2006-03-12', '2010': '2010-03-14', '2014': '2014-03-09'}

def arregla(t):
    """Corrige textos UTF-8 leídos como Latin-1 (ej. 'DEMOCRÃ\x81TICO' -> 'DEMOCRÁTICO')."""
    try:
        return t.encode('latin-1').decode('utf-8') if 'Ã' in t else t
    except UnicodeError:
        return t

def norm(dep, mun):
    dep, mun = int(dep), int(mun)
    return dep, (mun - dep*1000 if mun > 999 else mun)

# ---------- 1998 y 2002: tabla maestra (por lista) ----------
ESP98 = {'CAM': [297, 298, 299, 300], 'SEN': [897, 898, 899, 900]}
T98 = defaultdict(lambda: [0, 0, 0, 0])
for r in csv.DictReader(open(os.path.join(S, 'out4', 'resultados_electorales_colombia.csv'), encoding='utf-8')):
    eid = r['id_eleccion']
    if eid not in ('1998-SEN', '1998-CAM', '2002-SEN', '2002-CAM'): continue
    anio, corp = eid.split('-')
    dep, mun = norm(r['codigo_depto_rnec'], r['codigo_muni_rnec'])
    cod = int(r['codigo_opcion'])
    # 1998: los códigos 297-300 (Cámara) y 897-900 (Senado) son blanco, nulos, no marcados y total del municipio
    if anio == '1998' and cod in ESP98[corp]:
        T98[(corp, dep, mun)][ESP98[corp].index(cod)] = int(r['votos'] or 0)
        MN[(anio, dep, mun)] = r['nombre_muni']; DN[(anio, dep)] = r['nombre_depto']
        continue
    if cod >= 900: continue
    circ = r['circunscripcion'] or ('0' if corp == 'SEN' else '1')
    pc = int(float(r['partido_codigo'] or -1))
    k = (anio, corp, circ, dep, mun, pc)
    V[k] += int(r['votos'] or 0); PN[(anio, corp, pc)] = r['partido_nombre'].strip()
    MN[(anio, dep, mun)] = r['nombre_muni']; DN[(anio, dep)] = r['nombre_depto']
    BL[(anio, corp, dep, mun)] = int(r['votos_blancos'] or 0); NU[(anio, corp, dep, mun)] = int(r['votos_nulos'] or 0)
    prev = EST.get(k, 'cuadra'); e = r['estado_control']
    EST[k] = 'no_cuadra' if 'no_cuadra' in (prev, e) else ('sin_control' if 'sin_control' in (prev, e) else 'cuadra')
    FUENTE[(anio, corp)] = r['fuente']

# control municipal 1998: listas + blanco + nulos + no marcados = total
sum98 = defaultdict(int)
for (anio, corp, circ, dep, mun, p), v in V.items():
    if anio == '1998': sum98[(corp, dep, mun)] += v
for (corp, dep, mun), (b, n, nm, t) in T98.items():
    BL[('1998', corp, dep, mun)] = b; NU[('1998', corp, dep, mun)] = n
    ok = t and sum98[(corp, dep, mun)] + b + n + nm == t
    EST[('1998', corp, dep, mun)] = 'cuadra' if ok else ('sin_control' if not t else 'no_cuadra')
for k in [k for k in EST if len(k) == 6 and k[0] == '1998']: del EST[k]
FUENTE[('1998', 'CAM')] = 'rcama.dbf + LISTACAM.DBF (CD 1997-1998 RNEC)'
FUENTE[('1998', 'SEN')] = 'resusena.dbf + LISTASEN.DBF (CD 1997-1998 RNEC)'

# ---------- 2006: tb_votacion.dbf (01 Senado, 02 Cámara), control municipal con fila 999 ----------
nom06 = {}
for r in read_dbf(os.path.join(S, 'x2006', 'listas.dbf')):
    if r['CODI_COR'] in ('01', '02') and r['MOVI_POL'].strip():
        nom06.setdefault((r['CODI_COR'], int(r['CODI_PAR'])), r['MOVI_POL'].strip())
for r in read_dbf(os.path.join(S, 'x2006', 'municipios.dbf')):
    MN[('2006', int(r['CODI_DEP']), int(r['CODI_MUN']))] = r['NOMB_MUN'].strip()
for r in read_dbf(os.path.join(S, 'x2006', 'deptos.dbf')):
    DN[('2006', int(r['CODI_DEP']))] = r['NOMB_DEP'].strip()
tot06 = defaultdict(lambda: defaultdict(int))
for r in read_dbf(os.path.join(S, 'x2006', 'tb_votacion.dbf')):
    if r['CODI_COR'] not in ('01', '02'): continue
    corp = 'SEN' if r['CODI_COR'] == '01' else 'CAM'
    dep, mun = int(r['CODI_DEP']), int(r['CODI_MUN']); par = int(r['CODI_PAR']); v = int(r['VOTA_CAN'] or 0)
    tot06[(corp, dep, mun)][par] += v
    if par in ESP: continue
    k = ('2006', corp, r['CODI_CIR'], dep, mun, par)
    V[k] += v; PN[('2006', corp, par)] = nom06.get((r['CODI_COR'], par), '')
for (corp, dep, mun), d in tot06.items():
    BL[('2006', corp, dep, mun)] = d.get(996, 0); NU[('2006', corp, dep, mun)] = d.get(997, 0)
    dif = sum(v for p, v in d.items() if p not in ESP) + d.get(996, 0) + d.get(997, 0) + d.get(998, 0) - d.get(999, 0)
    EST[('2006', corp, dep, mun)] = 'cuadra' if d.get(999, 0) and dif == 0 else ('sin_control' if not d.get(999, 0) else 'no_cuadra')
FUENTE[('2006', 'SEN')] = FUENTE[('2006', 'CAM')] = 'tb_votacion.dbf (CD 2006 RNEC)'

# ---------- 2010: bases Access (corp 1 Senado, 2 Cámara), control por departamento ----------
FILES = os.path.join(S, 'x2010', 'files'); DEP_NAC = {}; PART10 = {}
dbs = []
for f in sorted(glob.glob(os.path.join(FILES, '_*'))):
    if open(f, 'rb').read(20)[4:19] != b'Standard Jet DB': continue
    db = Mdb(f); cat = db.catalogo(); dbs.append((db, cat))
    if 'RESUMEN_NACIONAL' in cat:
        for r in db.filas(cat['DEPARTAMENTOS']):
            if r['ID'] > 0: DEP_NAC[r['ID'] % 10_000_000] = r
    if 'PARTIDOS' in cat:
        for r in db.filas(cat['PARTIDOS']): PART10[r['CODIGO']] = r['NOMBRE'].strip()
bad10 = Counter()
for db, cat in dbs:
    if 'RESUMEN_NACIONAL' in cat or 'MUNICIPIOS' not in cat: continue
    mun = {r['ID']: r for r in db.filas(cat['MUNICIPIOS'])}
    dep = {r['ID']: r for r in db.filas(cat['DEPARTAMENTOS'])} if 'DEPARTAMENTOS' in cat else \
          {m['DEPARTAMENTO']: DEP_NAC[m['DEPARTAMENTO'] % 10_000_000] for m in mun.values()}
    cpar = {(r['CORPORACION'], r['CODIGO']): r['PARTIDO'] for r in db.filas(cat['CANDIDATOS'])}
    g = defaultdict(int)   # (corp, circ, mid, cand) -> votos
    if 'RESUMEN_MUNICIPIOS' in cat:
        for r in db.filas(cat['RESUMEN_MUNICIPIOS']):
            if r['CORPORACION'] in (1, 2): g[(r['CORPORACION'], r['CIRCUNS'], r['MUNICIPIO'], r['CANDIDATO'])] += r['VOTACION'] or 0
    else:
        mesa = {r['ID']: r['PUESTO'] for r in db.filas(cat['MESAS'])}
        puesto = {r['ID']: r['ZONA'] for r in db.filas(cat['PUESTOS'])}
        zona = {r['ID']: r['MUNICIPIO'] for r in db.filas(cat['ZONAS'])}
        for r in db.filas(cat['RESUMEN_MESAS']):
            if r['CORPORACION'] in (1, 2):
                g[(r['CORPORACION'], r['CIRCUNS'], zona[puesto[mesa[r['MESA']]]], r['CANDIDATO'])] += r['VOTACION'] or 0
    # control: suma por departamento y candidato vs RESUMEN_DEPARTAMENTOS
    sm = defaultdict(int); rd = defaultdict(int)
    for (corp, circ, mid, c), v in g.items(): sm[(corp, mun[mid]['DEPARTAMENTO'] , c)] += v
    for r in db.filas(cat['RESUMEN_DEPARTAMENTOS']):
        if r['CORPORACION'] in (1, 2): rd[(r['CORPORACION'], r['DEPARTAMENTO'], r['CANDIDATO'])] += r['VOTACION'] or 0
    depbad = {k[:2] for k in set(sm) | set(rd) if sm.get(k, 0) != rd.get(k, 0)}
    bad10['no'] += len(depbad); bad10['si'] += len({k[:2] for k in sm} - depbad)
    for (corp, circ, mid, c), v in g.items():
        m = mun[mid]; dp = dep[m['DEPARTAMENTO']]; cs = 'SEN' if corp == 1 else 'CAM'
        d_, m_ = int(dp['CODIGO']), int(m['CODIGO'])
        MN[('2010', d_, m_)] = m['DESCRIPCION'].strip(); DN[('2010', d_)] = dp['DESCRIPCION'].strip()
        EST[('2010', cs, d_, m_)] = 'municipal_incompleto' if (corp, m['DEPARTAMENTO']) in depbad else 'cuadra_depto'
        if c in ('996', '997', '998'):
            if c == '996': BL[('2010', cs, d_, m_)] += v
            if c == '997': NU[('2010', cs, d_, m_)] += v
            continue
        p = cpar.get((corp, c))
        if p is None: continue
        V[('2010', cs, str(circ), d_, m_, p)] += v; PN[('2010', cs, p)] = PART10.get(p, '')
FUENTE[('2010', 'SEN')] = FUENTE[('2010', 'CAM')] = 'ConVotoEst_1.msi (CD 2010 RNEC)'
print('2010 control depto:', dict(bad10))

# ---------- 2014: SQLite db_2 (corp 1 Senado, 2 Cámara), control por departamento ----------
con = sqlite3.connect('file:' + os.path.join(S, 'x2014db', 'db_2.sqlite') + '?mode=ro', uri=True)
tabs = [r[0] for r in con.execute("select name from sqlite_master where type='table' and name like 'votacion_%'")]
# nombres de partido desde el catálogo partpoli (los textos de votacion_XX vienen con acentos dañados)
PP14 = {c: ''.join(ch for ch in (n or '') if ch.isprintable()).strip() for c, n in con.execute('select papocopa, paponomb from partpoli')}
bad14 = Counter()
for t in tabs:
    dd = t.split('_')[1]
    rows = con.execute(f'select corp, circunscripcion, depto, desc_depto, mpio, desc_mpio, partido, desc_partido, sum(votos) '
                       f'from {t} where corp in (1,2) group by corp, circunscripcion, depto, mpio, partido').fetchall()
    m = dict(((c, p), v) for c, p, v in con.execute(f'select corp, candidato, sum(votos) from {t} where corp in (1,2) group by corp, candidato'))
    r_ = dict(((c, p), v) for c, p, v in con.execute(f'select corp, candidato, sum(votos) from x_resum_dpto_{dd} where corp in (1,2) group by corp, candidato'))
    okc = {c: all(m.get(k, 0) == r_.get(k, 0) for k in set(m) | set(r_) if k[0] == c) for c in (1, 2)}
    for c in (1, 2): bad14['si' if okc[c] else 'no'] += 1
    for corp, circ, dep, ddep, mun, dmun, par, dpar, v in rows:
        cs = 'SEN' if corp == 1 else 'CAM'
        MN[('2014', dep, mun)] = dmun.strip(); DN[('2014', dep)] = ddep.strip()
        EST[('2014', cs, dep, mun)] = 'cuadra_depto' if okc[corp] else 'no_cuadra_depto'
        if par in (996, 997, 998):
            if par == 996: BL[('2014', cs, dep, mun)] += v
            if par == 997: NU[('2014', cs, dep, mun)] += v
            continue
        V[('2014', cs, str(circ), dep, mun, par)] += v; PN[('2014', cs, par)] = PP14.get(par) or arregla((dpar or '').strip(' .'))
FUENTE[('2014', 'SEN')] = FUENTE[('2014', 'CAM')] = 'setupEstadisticas2014-v2.exe -> SQLite (CD 2014 RNEC)'
print('2014 control depto:', dict(bad14))

# ---------- salida ----------
val = defaultdict(int)
for (anio, corp, circ, dep, mun, p), v in V.items(): val[(anio, corp, dep, mun)] += v
COLS = ['id_eleccion','anio','fecha','corporacion','circunscripcion','codigo_depto','nombre_depto','codigo_muni',
        'codigo_divipol','nombre_muni','partido_codigo','partido_nombre','votos_partido','votos_blancos',
        'votos_nulos','votos_validos_muni','share_validos','estado_control','fuente']
out = []
for (anio, corp, circ, dep, mun, p), v in V.items():
    vv = val[(anio, corp, dep, mun)] + BL.get((anio, corp, dep, mun), 0)
    est = EST.get((anio, corp, circ, dep, mun, p)) or EST.get((anio, corp, dep, mun), 'sin_control')
    out.append({'id_eleccion': f'{anio}-{corp}', 'anio': anio, 'fecha': FECHA[anio], 'corporacion': corp,
        'circunscripcion': circ, 'codigo_depto': dep, 'nombre_depto': DN.get((anio, dep), ''), 'codigo_muni': mun,
        'codigo_divipol': dep*1000 + mun, 'nombre_muni': MN.get((anio, dep, mun), ''), 'partido_codigo': p,
        'partido_nombre': PN.get((anio, corp, p), ''), 'votos_partido': v,
        'votos_blancos': BL.get((anio, corp, dep, mun), 0), 'votos_nulos': NU.get((anio, corp, dep, mun), 0),
        'votos_validos_muni': vv, 'share_validos': round(v / vv, 5) if vv else '',
        'estado_control': est, 'fuente': FUENTE[(anio, corp)]})
out.sort(key=lambda r: (r['id_eleccion'], r['codigo_depto'], r['codigo_muni'], -r['votos_partido']))
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(out)
print('filas', len(out))
res = defaultdict(lambda: [set(), Counter(), Counter()])
for r in out:
    x = res[r['id_eleccion']]; x[0].add(r['codigo_divipol']); x[1][r['estado_control']] += 1; x[2][r['partido_nombre'][:35]] += r['votos_partido']
for e in sorted(res):
    m, est, tot = res[e]
    print(f"{e}: municipios {len(m)} | filas {sum(est.values())} | {dict(est)} | total {sum(tot.values()):,} | top {tot.most_common(2)}")
