# Base presidencial Perú por distrito (ubigeo), 2006-2021. Fuente: ONPE, datos abiertos (resultados por mesa), agregados a distrito.
import csv, os, openpyxl
from collections import defaultdict, Counter
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.path.join(S, 'pe', 'src')
OUT = os.path.join(S, 'out4', 'pe_presidencial_distritos_2006_2021.csv')
ELE = [  # archivo, año, vuelta, fecha (calendario), nota de recuento
 ('EG2006', 2006, 1, '2006-04-09'), ('SEP2006', 2006, 2, '2006-06-04'),
 ('EG2011', 2011, 1, '2011-04-10'), ('SEP2011', 2011, 2, '2011-06-05'),
 ('EG2016', 2016, 1, '2016-04-10'), ('SEP2016', 2016, 2, '2016-06-05'),
 ('EG2021', 2021, 1, '2021-04-11'), ('SEP2021', 2021, 2, '2021-06-06')]
# partido -> candidato: sólo los verificados con totales nacionales (2021) o balotajes de 2 opciones (2006/2016: pendiente verificar contra lista JNE)
CAND = {'PARTIDO POLITICO NACIONAL PERU LIBRE': 'PEDRO CASTILLO TERRONES', 'FUERZA POPULAR': 'KEIKO FUJIMORI HIGUCHI',
        'UNION POR EL PERU': 'OLLANTA HUMALA TASSO', 'PARTIDO APRISTA PERUANO': 'ALAN GARCIA PEREZ',
        'PERUANOS POR EL KAMBIO': 'PEDRO PABLO KUCZYNSKI GODARD', 'GANA PERU': 'OLLANTA HUMALA TASSO', 'FUERZA 2011': 'KEIKO FUJIMORI HIGUCHI'}
def dicc(k):
    ws = openpyxl.load_workbook(os.path.join(P, 'd_' + k + '.xlsx'))['Variables']
    return {r[0]: r[1] for r in ws.iter_rows(min_row=2, values_only=True) if r[0] and r[0].startswith('VOTOS_P') and '*' not in str(r[1])}, \
           {r[0] for r in ws.iter_rows(min_row=2, values_only=True) if r[0] and r[0].startswith('VOTOS_P') and '*' in str(r[1])}
def filas_arch(k):
    if os.path.exists(os.path.join(P, k + '.csv')):
        rd = csv.DictReader(open(os.path.join(P, k + '.csv'), encoding='latin-1'), delimiter=';')
        for r in rd: yield {a: (b.strip('" ') if isinstance(b, str) else b) for a, b in r.items() if a}
    else:
        it = openpyxl.load_workbook(os.path.join(P, k + '.xlsx'), read_only=True).active.iter_rows(values_only=True)
        h = [str(x) for x in next(it)]
        for r in it:
            if r[0] is None: continue
            yield {a: ('' if b is None else str(b)) for a, b in zip(h, r)}
COLS = ['id_eleccion','pais','anio','vuelta','fecha','departamento','provincia','distrito','ubigeo','candidato','partido','votos',
        'votos_candidatos_distrito','votos_blancos','votos_nulos','votos_validos_distrito','share_validos','electores_distrito','votantes_distrito','participacion','mesas','mesas_no_contabilizadas','estado_control','fuente']
filas = []; resumen = []
for k, anio, vuelta, fecha in ELE:
    names, excl = dicc(k); eid = f'PE-{anio}-PRES-{vuelta}'
    A = defaultdict(lambda: defaultdict(int)); META = {}
    for r in filas_arch(k):
        u = r['UBIGEO'].zfill(6); META[u] = (r['DEPARTAMENTO'].strip(), r['PROVINCIA'].strip(), r['DISTRITO'].strip()); a = A[u]
        for c in names: a[c] += int(r.get(c) or 0)
        # agrupaciones excluidas (2016): sus votos ya están sumados a nulos por resolución JNE -> no se suman de nuevo
        for c in ('VOTOS_VB', 'VOTOS_VN', 'VOTOS_VI', 'N_CVAS', 'N_ELEC_HABIL'): a[c] += int(r.get(c) or 0)
        a['mesas'] += 1
        e = r['DESCRIP_ESTADO_ACTA'].upper()
        if any(x in e for x in ('NO INSTALADA', 'SIN INSTALAR', 'ANULAD', 'EN PROCESO')): a['sin'] += 1
    for u, a in A.items():
        cand = sum(a[c] for c in names); bl = a['VOTOS_VB']; nu = a['VOTOS_VN'] + a['VOTOS_VI']; val = cand + bl
        ok = (cand + bl + nu == a['N_CVAS'])
        for c, pn in names.items():
            filas.append(dict(id_eleccion=eid, pais='PE', anio=anio, vuelta=vuelta, fecha=fecha, departamento=META[u][0], provincia=META[u][1], distrito=META[u][2],
                ubigeo=u, candidato=CAND.get(pn, ''), partido=pn, votos=a[c], votos_candidatos_distrito=cand, votos_blancos=bl, votos_nulos=nu,
                votos_validos_distrito=val, share_validos=round(a[c] / val, 5) if val else '', electores_distrito=a['N_ELEC_HABIL'], votantes_distrito=a['N_CVAS'],
                participacion=round(a['N_CVAS'] / a['N_ELEC_HABIL'], 4) if a['N_ELEC_HABIL'] else '', mesas=a['mesas'], mesas_no_contabilizadas=a['sin'],
                estado_control='cuadra' if ok else 'no_cuadra', fuente='ONPE - datosabiertos.gob.pe'))
filas.sort(key=lambda r: (r['id_eleccion'], r['ubigeo'], -r['votos']))
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(filas)
print('filas', len(filas))
for k, anio, vuelta, fecha in ELE:
    eid = f'PE-{anio}-PRES-{vuelta}'; t = Counter(); u = set(); ctl = Counter(); seen = set()
    for r in filas:
        if r['id_eleccion'] != eid: continue
        t[r['partido']] += r['votos']; u.add(r['ubigeo'])
        if r['ubigeo'] not in seen: seen.add(r['ubigeo']); ctl[r['estado_control']] += 1
    print(eid, 'distritos', len(u), dict(ctl), [(p, f'{v:,}') for p, v in t.most_common(3)])
