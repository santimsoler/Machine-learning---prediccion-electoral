"""Percepción de la situación económica actual del país (Latinobarómetro), 9 países, 1995-2017 (+2018/2020/2023 si hay .rds/.rdata)."""
import pandas as pd, numpy as np, glob, re, os
B='lb/'
V={'1995':'p1','1996':'p1','1997':'sp1','1998':'sp1','2000':'P1ST','2001':'p1st','2002':'p2sta','2003':'p1st','2004':'p2st','2005':'p2st','2006':'p2st','2007':'p100st','2008':'p4st','2009':'p3st_a','2010':'P3ST_A','2011':'P3ST_A','2013':'P3STGBS','2015':'P3STGBS','2016':'P4STGBS','2017':'P4STGBSC'}
ISO={'484':'MX','188':'CR','591':'PA'}
NAME={'mexico':'MX','méxico':'MX','mã©xico':'MX','costa rica':'CR','panama':'PA','panamá':'PA','panamã¡':'PA'}
def norm(t): return str(t).encode('latin1','ignore').decode('utf8','ignore').lower() if 'Ã' in str(t) else str(t).lower()
def clasif(t):
    t=norm(t).strip()
    if t.startswith('muy buena'): return 'mb'
    if t.startswith('buena'): return 'b'
    if t.startswith('muy mala'): return 'mm'
    if t.startswith('mala'): return 'm'
    if t.startswith('regular') or 'ni buena' in t: return 'r'
    return None
rows=[]
for y,v in V.items():
    fs=[x for x in glob.glob(f'{B}y{y}/*.dta') if re.search(r'esp',x.lower()) or y=='2013'] or glob.glob(f'{B}y{y}/*.dta')
    f=fs[0]; rd=pd.io.stata.StataReader(f); vl=rd.value_labels()
    rd=pd.io.stata.StataReader(f); d=rd.read(convert_categoricals=False)
    col={c.lower():c for c in d.columns}; vc=col[v.lower()]
    lbl=rd._lbllist[list(d.columns).index(vc)]; m=vl.get(lbl,{})
    cl={k:clasif(t) for k,t in m.items()}
    ic=next(k for k in ('idenpa','pais') if k in col); wc=next((k for k in ('wt','pondera','ponder') if k in col),None)
    pais=d[col[ic]]
    def cc(x):
        try: return ISO.get(str(int(float(x))))
        except: return None
    pm=pais.map(cc)
    if pm.isna().all():
        pl=vl.get(rd._lbllist[list(d.columns).index(col[ic])],{}); pm=pais.map(lambda k: NAME.get(norm(pl.get(k,''))))
    w=d[col[wc]].fillna(1) if wc else pd.Series(1,index=d.index)
    cat=d[vc].map(cl)
    for p in ISO.values():
        s=(pm==p)&cat.notna()
        if s.sum()<100: continue
        sh=lambda k: 100*w[s&(cat==k)].sum()/w[s].sum()
        buena=sh('mb')+sh('b'); mala=sh('mm')+sh('m')
        rows.append((p,int(y),round(buena,1),round(mala,1),round(buena-mala,1),int(s.sum())))
o=pd.DataFrame(rows,columns=['pais','anio','pct_buena_muy_buena','pct_mala_muy_mala','balance_percep_econ','n']).sort_values(['pais','anio'])
o.to_csv('data_ampliacion2/percep_lb_mx_cr_pa_1995_2017.csv',index=False)
print(o.pivot(index='anio',columns='pais',values='balance_percep_econ').round(0).to_string())
