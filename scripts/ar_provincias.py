# Presidencial Argentina 1983-2019 por provincia, desde los xlsx de resultados DEFINITIVOS de la DINE.
# Una hoja por distrito: fórmulas/agrupaciones con votos, más positivos, blancos, nulos, votantes y electores.
import openpyxl, os, re, csv, unicodedata
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = os.path.join(S, 'ar')
OUT = os.path.join(S, 'out4', 'ar_presidencial_provincias_1983_2019.csv')
ARCH = [('AR-1983-PRES-1','1983-10-30','1983_presidente.xlsx'), ('AR-1989-PRES-1','1989-05-14','1989_presidente.xlsx'),
        ('AR-1995-PRES-1','1995-05-14','1995_presidente.xlsx'), ('AR-1999-PRES-1','1999-10-24','1999_presidente.xlsx'),
        ('AR-2003-PRES-1','2003-04-27','2003_presidente.xlsx'), ('AR-2007-PRES-1','2007-10-28','2007_presidente.xlsx'),
        ('AR-2011-PRES-1','2011-10-23','2011_presidente_generales.xlsx'), ('AR-2015-PRES-1','2015-10-25','2015_presidente_generales.xlsx'),
        ('AR-2015-PRES-2','2015-11-22','2015_presidente_segunda_vuelta.xlsx'), ('AR-2019-PRES-1','2019-10-27','2019_presidente_x_distrito.xlsx')]
# Códigos de distrito DINE (los mismos de los CSV provisorios)
DIST = {'CIUDAD AUTONOMA DE BUENOS AIRES':1,'CABA':1,'CAPITAL FEDERAL':1,'BUENOS AIRES':2,'BS AS':2,'CATAMARCA':3,'CORDOBA':4,
        'CORRIENTES':5,'CHACO':6,'CHUBUT':7,'ENTRE RIOS':8,'FORMOSA':9,'JUJUY':10,'LA PAMPA':11,'LA RIOJA':12,'MENDOZA':13,
        'MISIONES':14,'NEUQUEN':15,'RIO NEGRO':16,'SALTA':17,'SAN JUAN':18,'SAN LUIS':19,'SANTA CRUZ':20,'SANTA FE':21,
        'SANTIAGO DEL ESTERO':22,'S DEL ESTERO':22,'TUCUMAN':23,'TIERRA DEL FUEGO':24,'TIERRA DEL FUEGO, ANTARTIDA E ISLAS DEL ATLANTICO SUR':24}
def norm(t): return ' '.join(unicodedata.normalize('NFKD', str(t)).encode('ascii','ignore').decode().upper().replace('.', ' ').split())
def num(x):
    if isinstance(x, (int, float)): return x
    try: return float(str(x).replace('.', '').replace(',', '.'))
    except: return None
filas = []; problemas = []
for eid, fecha, f in ARCH:
    wb = openpyxl.load_workbook(os.path.join(A, f), data_only=True, read_only=True)
    for sh in wb.sheetnames:
        key = norm(sh)
        d = DIST.get(key) or next((v for k, v in DIST.items() if key.startswith(k)), None)
        if d is None: continue   # hoja nacional u otras
        rows = [list(r) for r in wb[sh].iter_rows(values_only=True)]
        electores = None; hdr = None; vcol = acol = None; agr = []; esp = {}
        for i, r in enumerate(rows):
            txt = [norm(x) if x is not None else '' for x in r]
            if any(t.startswith('ELECTORES') and ('INSCRIPTOS' in t or 'HABILES' in t) for t in txt):
                electores = next((num(x) for x in r[1:] if num(x)), None)
            if hdr is None and any('AGRUPACION' in t for t in txt) and any(t == 'VOTOS' for t in txt):
                hdr = i; acol = next(j for j, t in enumerate(txt) if 'AGRUPACION' in t); vcol = txt.index('VOTOS'); continue
            if hdr is not None and i > hdr:
                lab = ' '.join(t for t in txt if t and not t.replace(' ', '').isdigit())
                v = num(r[vcol]) if vcol < len(r) else None
                for k in ('VOTOS POSITIVOS', 'VOTOS EN BLANCO', 'VOTOS NULOS', 'VOTOS ANULADOS', 'TOTAL DE VOTANTES', 'VOTOS RECURRIDOS', 'VOTOS IMPUGNADOS', 'DIFERENCIA DE ACTAS'):
                    if k in lab: esp[k] = v; break
                else:
                    if 'TOTAL' in lab and v: esp.setdefault('TOTAL DE VOTANTES', v)
                    elif r[acol] and v is not None and 'VOTOS POSITIVOS' not in esp:
                        form = r[0] if acol != 0 and isinstance(r[0], str) else ''
                        agr.append((str(r[acol]).strip(), (form or '').strip(), int(v)))
        pos = esp.get('VOTOS POSITIVOS'); bl = esp.get('VOTOS EN BLANCO') or 0
        nu = (esp.get('VOTOS NULOS') or 0) + (esp.get('VOTOS ANULADOS') or 0)
        sum_ag = sum(v for *_, v in agr)
        dif = (sum_ag - pos) if pos else ''
        if pos and dif != 0: problemas.append((eid, sh, sum_ag, pos))
        for a, form, v in agr:
            filas.append(dict(id_eleccion=eid, pais='AR', anio=int(eid[3:7]), vuelta=int(eid[-1]), fecha=fecha,
                recuento='definitivo', distrito_id=d, distrito_nombre=sh.strip(), agrupacion_nombre=a, formula=form,
                votos=v, votos_blancos=int(bl), votos_nulos=int(nu), votos_positivos_distrito=int(pos) if pos else '',
                share_positivos=round(v / pos, 5) if pos else '', electores_distrito=int(electores) if electores else '',
                total_votantes=int(esp['TOTAL DE VOTANTES']) if esp.get('TOTAL DE VOTANTES') else '',
                participacion=round(esp['TOTAL DE VOTANTES'] / electores, 4) if electores and esp.get('TOTAL DE VOTANTES') else '',
                diferencia_control=dif, estado_control='cuadra' if dif == 0 else ('sin_control' if dif == '' else 'no_cuadra'),
                fuente=f'DINE {f} (definitivos), hoja {sh}'))
COLS = list(filas[0].keys())
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(filas)
from collections import Counter, defaultdict
print('filas', len(filas))
for eid, *_ in ARCH:
    fs = [r for r in filas if r['id_eleccion'] == eid]
    tot = Counter()
    for r in fs: tot[r['agrupacion_nombre'][:45]] += r['votos']
    print(eid, '| distritos', len({r['distrito_id'] for r in fs}), '| control', dict(Counter(r['estado_control'] for r in fs)),
          '| con electores', sum(1 for r in fs if r['electores_distrito'] != ''), '|', tot.most_common(2))
print('problemas (suma agrupaciones != positivos):', len(problemas), problemas[:10])
