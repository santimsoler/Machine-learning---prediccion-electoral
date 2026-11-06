# Base presidencial Chile 1989-2025 por comuna (y "EXTRANJERO" como unidad aparte desde 2017).
# Fuentes Servel: serie 1989-2017 por comuna (definitivos), 2021 por mesa (Tricel), 2025 1ª vuelta por mesa (preliminares).
import openpyxl, os, csv, re, unicodedata, datetime
from collections import defaultdict, Counter
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
C = os.path.join(S, 'cl'); OUT = os.path.join(S, 'out4', 'cl_presidencial_comunas_1989_2025.csv')
def n(t): return ' '.join(unicodedata.normalize('NFKD', str(t or '')).encode('ascii', 'ignore').decode().upper().split())
def esp(c):
    c = n(c)
    if 'NULO' in c: return 'nulos'
    if 'BLANCO' in c and 'PROMOTOR' not in c: return 'blancos'
    return None
V = defaultdict(int); PAR = {}; FECHA = {}; REC = {}; ELEC = defaultdict(int); NOMC = {}; REG = {}
def add(eid, reg, com, cand, partido, votos):
    if isinstance(votos, str) and not votos.strip().isdigit(): return   # filas de subtotal con fórmula
    k = (eid, n(com)); REG[k] = n(reg); NOMC[k] = str(com).strip()
    V[k + (n(cand),)] += int(votos or 0)
    if partido: PAR[(eid, n(cand))] = partido

# --- 1989-2017 (definitivos, por comuna)
it = openpyxl.load_workbook(os.path.join(C, 'chile_presidenciales_1989_2017.xlsx'), read_only=True).active.iter_rows(values_only=True)
h = [str(x) for x in next(it)]; ix = {k: i for i, k in enumerate(h)}
for r in it:
    if r[0] is None: continue
    anio = int(r[ix['Año de Elección']]); vot = n(r[ix['Votación Presidencial']])
    vuelta = 2 if 'SEGUNDA' in vot else 1
    fe = r[ix['Fecha de Elección']]
    if vuelta == 2 and isinstance(fe, datetime.datetime) and fe.month == 1: anio -= 1   # 2ª vuelta en enero: ciclo del año anterior
    eid = f'CL-{anio}-PRES-{vuelta}'
    FECHA[eid] = r[ix['Fecha de Elección']].date().isoformat() if isinstance(r[ix['Fecha de Elección']], datetime.datetime) else str(r[ix['Fecha de Elección']])
    REC[eid] = 'definitivo (Servel 1989-2017)'
    add(eid, r[ix['Región']], r[ix['Comuna']], r[ix['Candidato (a)']], r[ix['Sigla Partido']] or r[ix['Partido']], r[ix['Votos Totales']])
# --- 2017 extranjero
it = openpyxl.load_workbook(os.path.join(C, 'chile_presidencial_2017_extranjero.xlsx'), read_only=True).active.iter_rows(values_only=True)
h = [str(x) for x in next(it)]; ix = {k: i for i, k in enumerate(h)}
for r in it:
    if r[0] is None: continue
    vuelta = 2 if 'SEGUNDA' in n(r[ix['Votación Presidencial']]) else 1
    votos = next((r[i] for i, k in enumerate(h) if 'Votos' in k), 0)
    add(f'CL-2017-PRES-{vuelta}', 'EXTRANJERO', 'EXTRANJERO', r[ix['Candidato (a)']], None, votos)
# --- 2021 (Tricel, por mesa) + control con hoja TOTAL
CONTROL = {}
for vuelta, f, fecha in [(1, 'chile_presidencial_2021_1v_mesa.xlsx', '2021-11-21'), (2, 'chile_presidencial_2021_2v_mesa.xlsx', '2021-12-19')]:
    eid = f'CL-2021-PRES-{vuelta}'; FECHA[eid] = fecha; REC[eid] = 'definitivo (Tricel), por mesa'
    wb = openpyxl.load_workbook(os.path.join(C, f), read_only=True)
    for sh in ('CHILE', 'EXTRANJERO'):
        it = wb[sh].iter_rows(values_only=True); h = [str(x) for x in next(it)]; ix = {k: i for i, k in enumerate(h)}
        mesas = {}
        for r in it:
            if r[ix['Candidato']] is None: continue
            reg = r[ix['Región']] if sh == 'CHILE' else 'EXTRANJERO'; com = r[ix['Comuna']] if sh == 'CHILE' else 'EXTRANJERO'
            add(eid, reg, com, r[ix['Candidato']], None, r[ix['Votos TRICEL']])
            e_ = re.sub(r'\D', '', str(r[ix['Electores']] or ''))
            if e_: mesas[(n(com), r[ix['Circ. Electoral']], r[ix['Local']], str(r[ix['Mesas Fusionadas']]))] = int(e_)
        for (com, *_), e in mesas.items(): ELEC[(eid, com)] += e
    tot = wb['TOTAL'].iter_rows(values_only=True); next(tot)
    CONTROL[eid] = {n(r[1]): (r[2] or 0) + (r[3] or 0) for r in tot if r[1] and isinstance(r[2], (int, float))}
# --- 2025 1ª y 2ª vuelta (preliminares, por mesa)
TOT25 = defaultdict(int)
for eid, fch, d in [('CL-2025-PRES-1', '2025-11-16', 'p2025'), ('CL-2025-PRES-2', '2025-12-14', 'p2025_2v')]:
  FECHA[eid] = fch; REC[eid] = 'preliminar, por mesa'
  for f, ext in [(d + '/PRELIMINARES_PRESIDENTE_DE_LA_REPUBLICA_En_Chile.xlsx', False), (d + '/PRELIMINARES_PRESIDENTE_DE_LA_REPUBLICA_En_Extranjero.xlsx', True)]:
    it = openpyxl.load_workbook(os.path.join(C, f), read_only=True).active.iter_rows(values_only=True)
    h = [str(x) for x in next(it)]; ix = {k: i for i, k in enumerate(h)}; vcol = ix.get('votos_preliminares', ix.get('votos'))
    mesas = {}
    for r in it:
        if r[0] is None: continue
        com = 'EXTRANJERO' if ext else r[ix['comuna']]; reg = 'EXTRANJERO' if ext else r[ix['region']]
        cand = n(r[ix['nombre_candidato']])
        if cand.startswith('TOTAL'):
            if 'VALIDAMENTE' in cand: TOT25[(eid, n(com))] += int(r[vcol] or 0)
            continue
        add(eid, reg, com, r[ix['nombre_candidato']], r[ix['partido']], r[vcol])
        mesas[(n(com), r[ix['cod_mesa']])] = int(r[ix.get('electores', ix.get('electores_mesa'))] or 0)
    for (com, _), e in mesas.items(): ELEC[(eid, com)] += e

# --- salida por comuna
tot_c = defaultdict(int); bl = defaultdict(int); nu = defaultdict(int)
for (eid, com, cand), v in V.items():
    t = esp(cand)
    if t == 'blancos': bl[(eid, com)] += v
    elif t == 'nulos': nu[(eid, com)] += v
    else: tot_c[(eid, com)] += v
COLS = ['id_eleccion','pais','anio','vuelta','fecha','recuento','region','comuna','candidato','partido','votos',
        'votos_candidatos_comuna','votos_blancos','votos_nulos','votos_validos_comuna','share_validos','electores_comuna','participacion','estado_control','fuente']
filas = []
for (eid, com, cand), v in V.items():
    if esp(cand): continue
    val = tot_c[(eid, com)] + bl[(eid, com)]; el = ELEC.get((eid, com))
    filas.append(dict(id_eleccion=eid, pais='CL', anio=int(eid[3:7]), vuelta=int(eid[-1]), fecha=FECHA[eid], recuento=REC[eid],
        region=REG[(eid, com)], comuna=NOMC[(eid, com)], candidato=cand, partido=PAR.get((eid, cand), ''), votos=v,
        votos_candidatos_comuna=tot_c[(eid, com)], votos_blancos=bl[(eid, com)], votos_nulos=nu[(eid, com)],
        votos_validos_comuna=val, share_validos=round(v / val, 5) if val else '', electores_comuna=el or '',
        participacion=round((val + nu[(eid, com)]) / el, 4) if el else '',
        estado_control=('cuadra_total_nacional' if eid.startswith('CL-2021') else
                        (('cuadra' if TOT25.get((eid, com)) in (tot_c[(eid, com)] + bl[(eid, com)], tot_c[(eid, com)]) else 'no_cuadra') if eid.startswith('CL-2025') else 'sin_control')),
        fuente='Servel'))
filas.sort(key=lambda r: (r['id_eleccion'], r['region'], r['comuna'], -r['votos']))
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(filas)
print('filas', len(filas))
res = defaultdict(Counter); com = defaultdict(set)
for r in filas: res[r['id_eleccion']][r['candidato']] += r['votos']; com[r['id_eleccion']].add(r['comuna'])
for e in sorted(res):
    print(f"{e} ({FECHA[e]}, {REC[e]}): comunas {len(com[e])} | " + ' / '.join(f'{k} {v:,}' for k, v in res[e].most_common(3)))
print('2025 control por comuna:', Counter(r['estado_control'] for r in filas if r['id_eleccion'].startswith('CL-2025')))
for e, ctl in CONTROL.items():
    nb = {k: v for k, v in res[e].items()}
    dif = {k: nb.get(k, 0) - v for k, v in ctl.items() if not esp(k)}
    print('control', e, 'diferencias por candidato vs hoja TOTAL:', {k: d for k, d in dif.items() if d})
