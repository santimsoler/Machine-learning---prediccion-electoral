import pandas as pd, re, unicodedata
from difflib import SequenceMatcher
def n(t): return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',unicodedata.normalize('NFKD',str(t)).encode('ascii','ignore').decode().lower())).strip()
FIX={'almarira':'altamira'}
c=pd.read_csv('final/candidatos.csv'); a=c[c.pais=='AR'].copy()
def clave(x):
    if pd.isna(x): return 'sin formula (listas provinciales/menores)'
    k=n(re.split(r'\s*[-–]\s*',str(x))[0])
    k=FIX.get(k,k)
    k=re.sub(r'(gutierreza|closeo)$','',k).strip()
    return k
a['clave']=a.candidato_o_formula.map(clave)
for col in ['votos_nacionales','share_nacional_pct']: a[col]=pd.to_numeric(a[col],errors='coerce')
def first(s): 
    s=s.dropna(); return s.value_counts().index[0] if len(s) else None
g=a.groupby(['id_eleccion','clave']).agg(anio=('anio','first'),vuelta=('vuelta','first'),
   formula=('candidato_o_formula',first),n_listas=('clave','size'),
   partidos=('partido_o_coalicion',lambda s:' | '.join(sorted(set(s.astype(str)))[:4])),
   votos=('votos_nacionales','sum'),share=('share_nacional_pct','sum'),
   es_oficialismo=('es_oficialismo','max'),va_por_reeleccion=('va_por_reeleccion','max')).reset_index()
g['share']=g.share.round(3)
# puntajes propios
ev=pd.read_csv('final/ideologia_evidencia.csv')
def tok(s): return set(t for t in n(s).split() if len(t)>=3 and t not in ('del','los','las'))
def ev_for(row,eje):
    e=ev[(ev.elecciones==row.id_eleccion.rsplit('-PRES',1)[0])&(ev.eje==eje)]
    kt=tok(row.clave) 
    hits=[r for _,r in e.iterrows() if kt and kt<=tok(r.candidato.split(' - ')[0]) or (kt and tok(r.candidato.split(' - ')[0])<=kt and tok(r.candidato.split(' - ')[0]))]
    return hits[0] if len(hits)>=1 else None
for eje,col in [('economico','eje_economico_propio'),('sociocultural','eje_sociocultural_propio')]:
    vals=[];niv=[]
    for _,r in g.iterrows():
        h=ev_for(r,eje)
        vals.append(h.valor if h is not None else None); niv.append(h.nivel_evidencia if h is not None else None)
    g[col]=vals
    if eje=='economico': g['nivel_evidencia_econ']=niv
# manifesto
ex=pd.read_csv('final/ideologia_externa.csv'); mf=ex[(ex.fuente=='manifesto')&(ex.pais=='AR')]
w=mf.pivot_table(index=['anio','candidato'],columns='variable',values='valor').reset_index()
vt=mf.drop_duplicates(['anio','candidato'])[['anio','candidato','voto_pct']]
w=w.merge(vt,on=['anio','candidato'])
w['kt']=w.candidato.map(tok)
def mfm(r):
    kt=tok(r.clave); x=w[(w.anio==r.anio)&w.kt.map(lambda t:bool(kt) and any(SequenceMatcher(None,a,b).ratio()>=0.85 for a in kt for b in t))]
    return x.iloc[0][['candidato','rile','markeco','planeco','welfare','voto_pct']].rename({'candidato':'mf_candidato','rile':'mf_rile','markeco':'mf_markeco','planeco':'mf_planeco','welfare':'mf_welfare','voto_pct':'mf_voto_pct'}) if len(x) else pd.Series(dtype=float)
g=g.join(g.apply(mfm,axis=1))
g=g.sort_values(['id_eleccion','share'],ascending=[True,False])
g.to_csv('final/candidatos_ar_agrupado.csv',index=False)
for e,x in g.groupby('id_eleccion'):
    print('\n==',e,'suma share',round(x.share.sum(),2),'| listas',x.n_listas.sum())
    print(x.head(8)[['clave','n_listas','share','eje_economico_propio','eje_sociocultural_propio','mf_candidato','mf_voto_pct','mf_rile']].to_string(index=False))
