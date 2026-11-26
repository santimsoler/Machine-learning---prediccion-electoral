"""Descarga de los artículos de Wikipedia (es) de cada elección, filtro de secciones previas a la votación y conteo de un diccionario de 16 temas.
Genera texto_conteos.csv. Correr en Colab (necesita acceso a es.wikipedia.org)."""
import requests, re, time, collections, random, pandas as pd

ELECCIONES = {
 'AR':[1989,1995,1999,2003,2007,2011,2015,2019,2023],
 'BO':[1993,1997,2002,2009,2014,2019,2025],
 'BR':[2002,2006,2010,2014,2018,2022,2026],
 'CL':[1989,1993,1999,2005,2009,2013,2017,2021,2025],
 'CO':[1998,2006,2010,2014,2026],
 'CR':[1990,1994,1998,2002,2006,2010,2014,2018,2022,2026],
 'EC':[2009,2013,2017,2021,2025],
 'MX':[1994,2000,2006,2012,2018,2024],
 'PA':[1994,1999,2004,2009,2014,2019,2024],
 'PE':[2021],
 'PY':[1993,1998,2003,2008,2013,2018,2023],
 'UY':[2014,2019,2024],
}
NOMBRE = {'AR':'Argentina','BO':'Bolivia','BR':'Brasil','CL':'Chile','CO':'Colombia','CR':'Costa Rica','EC':'Ecuador',
          'MX':'México','PA':'Panamá','PE':'Perú','PY':'Paraguay','UY':'Uruguay'}
API = 'https://es.wikipedia.org/w/api.php'
HDR = {'User-Agent':'TP-MEA-UBA-electoral/1.0 (trabajo academico, FCE-UBA)'}

def api(params):
    for _ in range(4):
        try:
            r = requests.get(API, params={**params,'format':'json'}, headers=HDR, timeout=30)
            if r.status_code == 200: return r.json()
        except Exception: pass
        time.sleep(2)
    return {}

def texto(titulo):
    j = api({'action':'query','prop':'extracts','explaintext':1,'exsectionformat':'wiki','redirects':1,'titles':titulo})
    pg = list(j.get('query',{}).get('pages',{}).values())
    if not pg or 'missing' in pg[0] or not pg[0].get('extract'): return None, None
    return pg[0]['title'], pg[0]['extract']

def candidatos_titulo(p, a):
    P = NOMBRE[p]; anios = [str(a), f'{a}-{a+1}']
    for y in anios:
        for t in ['Elecciones presidenciales de','Elecciones generales de','Elecciones federales de','Elección presidencial de','Elecciones presidenciales y legislativas de']:
            yield f'{t} {P} de {y}'

def buscar(p, a):
    for ti in candidatos_titulo(p, a):
        t, ext = texto(ti)
        if ext and len(ext.split()) > 80: return t, ext, 'directo'
    for q in [f'elecciones presidenciales {NOMBRE[p]} {a}', f'elección presidencial {NOMBRE[p]} {a}', f'elecciones generales {NOMBRE[p]} {a}']:
        j = api({'action':'query','list':'search','srsearch':q,'srlimit':8})
        for h in j.get('query',{}).get('search',[]):
            ti = h['title']; l = ti.lower()
            if (l.startswith('elecci') and (str(a) in ti) and NOMBRE[p].lower() in l
                and 'parlamentaria' not in l and 'legislativa' not in l and 'municipal' not in l and 'regional' not in l):
                t, ext = texto(ti)
                if ext and len(ext.split()) > 80 and 'estatal' not in t.lower(): return t, ext, 'búsqueda'
    return None, None, 'no encontrado'

ALLOW = re.compile(r'(antecedente|contexto|trasfondo|sistema electoral|reglas|legislaci|regulaci|candidat|definici[oó]n|campa[ñn]a|encuesta|sondeo|primaria|apoyo|alianza|coalici|partidos|cronograma|calendario|propuesta|debate|desarrollo|etapa|cuestiones|temas|organizaci|inscripci)', re.I)
DENY  = re.compile(r'(resultado|escrutinio|primera vuelta|segunda vuelta|balotaje|ballottage|por (regi|prov|depart|cant)|elecciones generales|presidente y|presidenciales$|elecci[oó]n presidencial$|parlament|legislativ|consecuencia|reacciones|an[aá]lisis|tras |v[eé]ase|referencias|enlaces|notas|bibliograf|fuentes|gobernador|estatal|senador|diputad|investidura|posesi)', re.I)
def secciones(ext):
    partes = re.split(r'\n(={2,})\s*(.+?)\s*\1\s*\n', ext); out = []; top_ok = False
    for i in range(1, len(partes)-2, 3):
        nivel, tit, cuerpo = len(partes[i]), partes[i+1].strip(), partes[i+2].strip()
        if nivel == 2: top_ok = bool(ALLOW.search(tit)) and not DENY.search(tit); ok = top_ok
        else: ok = top_ok and not DENY.search(tit)
        out.append((tit, cuerpo, ok))
    return out

# ---- diccionario: raíces (regex) agrupadas por tema ----
DIC = {
 'crisis':   ['crisis','recesi','inflaci','hiperinflaci','desempleo','desocupaci','pobreza','devaluaci','default','ajuste','deuda','estanflaci','corralito'],
 'corrup':   ['corrupci','esc[aá]ndalo','soborn','coima','imputad','procesad','denunci','malversaci'],
 'protesta': ['protest','huelga','paro','movilizaci','estallido','manifestaci','cacerol','bloque','descontent','malestar','disturbio','saqueo'],
 'insegur':  ['inseguridad','violenci','narco','delincuen','crimin','homicid','pandill'],
 'continu':  ['continuidad','reelecci','oficialis','sucesor','delf[ií]n','heredero'],
 'cambio':   ['cambio','alternancia','outsider','antipol','antisistema','renovaci'],
 'polariz':  ['polariz','antagonis','grieta','enfrentamiento','confrontaci'],
 'fragm':    ['fragment','divisi[oó]n','dividid','ruptura','fractura','interna','disidente','coalici'],
 'favorito': ['favorit','ventaja','encuesta','sondeo','popularidad','aprobaci','lideraba','liderazgo'],
 'bonanza':  ['crecimiento','bonanza','estabilidad','auge','prosperidad','recuperaci'],
 'izq':      ['izquierd','socialis','progresis','populis','bolivarian'],
 'der':      ['derecha','conservador','liberal','neoliberal','mercado'],
 'regimen':  ['dictadura','transici[oó]n','golpe','militar','autoritari'],
 'reforma':  ['reforma','constituci','enmienda','destituci','renuncia','inhabilit','juicio pol'],
 'pandemia': ['pandemia','covid'],
 'FUGA':     ['gan[oó]\\b','ganador','victoria','derrot','result[oó] electo','fue electo','elegido presidente','triunf'],
}
def contar(tp):
    t = tp.lower()
    return {tema: sum(len(re.findall(r'\b'+r, t)) for r in raices) for tema, raices in DIC.items()}

log = []; filas = []; corpus = collections.Counter(); kw = {}
for pais, anios in ELECCIONES.items():
    for a in anios:
        titulo, ext, how = buscar(pais, a)
        id_ = f'{pais}-{a}-PRES-1'
        if not ext:
            print('NO ENCONTRADO', pais, a); continue
        previas = [(t, c) for t, c, ok in secciones(ext) if ok]
        tp = '\n\n'.join(c for _, c in previas)
        f = dict(id_eleccion=id_, n_total=len(ext.split()), n_prev=len(tp.split()), n_secc=len(previas)); f.update(contar(tp)); filas.append(f)
        corpus.update(w for w in re.findall(r'[a-záéíóúñ]{6,}', tp.lower()))
        for tema in ['corrupci','crisis','protest']:
            m = re.search(r'.{0,110}\b'+tema+r'.{0,110}', tp.replace('\n',' '), re.I)
            if m: kw.setdefault(tema, []).append((id_, m.group(0)))
        log.append(f'{id_}|{titulo[-22:]}|{how[:3]}|prev={len(tp.split())}|nsec={len(previas)}')
        time.sleep(0.3)

df = pd.DataFrame(filas)
print('=====INICIO_CSV=====')
print(df.to_csv(index=False))
print('=====FIN_CSV=====')
print('articulos con texto:', len(df), 'de 76 | mediana palabras previas:', df.n_prev.median())
print('\n'.join(log))
print('\n=== PALABRAS MÁS FRECUENTES ===')
print(', '.join(f'{w}:{n}' for w, n in corpus.most_common(30)))
print('\n=== CONTEXTOS PARA VALIDAR ===')
random.seed(1)
for tema, lst in kw.items():
    for id_, frag in random.sample(lst, min(3, len(lst))): print(f'[{tema}] {id_}: ...{frag[:200]}...')

df.to_csv('texto_conteos.csv', index=False)
