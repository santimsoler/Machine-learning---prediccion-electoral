import pandas as pd,glob,re
B='lb/'
V={'2002':'p18no2','2003':'p24st','2004':'p46st','2005':'p29st','2006':'p43st','2007':'p32sta','2008':'p32st_a','2009':'p68st_a','2010':'P59ST_A','2011':'P36ST','2013':'P38STGBS','2015':'P48STGBS','2016':'P16STGBS','2017':'P17STGBSC'}
ISO={'68':'BO','600':'PY','218':'EC','32':'AR','76':'BR','152':'CL','170':'CO','604':'PE','858':'UY'}
NAME={'bolivia':'BO','paraguay':'PY','ecuador':'EC','argentina':'AR','brazil':'BR','brasil':'BR','chile':'CL','colombia':'CO','peru':'PE','perã\x83âº':'PE','uruguay':'UY'}
rows=[];audit=[]
for y,v in V.items():
    f=[x for x in glob.glob(f'{B}y{y}/*.dta') if re.search(r'esp',x.lower()) or y=='2013'][0]
    r=pd.io.stata.StataReader(f); vl=r.value_labels(); r=pd.io.stata.StataReader(f)
    d=pd.read_stata(f,convert_categoricals=False)
    col={c.lower():c for c in d.columns}
    vc=col[v.lower()]
    # etiqueta de valores de la variable
    lab=pd.io.stata.StataReader(f)
    lab.read(convert_categoricals=False); 
    lblname=lab._lbllist[list(d.columns).index(vc)]
    m=vl.get(lblname,{})
    audit.append((y,vc,m))
    pais=d[col['idenpa']].astype(str).str.strip()
    # país: ISO numérico o nombre
    def cc(x):
        if x in ISO: return ISO[x]
        try: return ISO.get(str(int(float(x))))
        except: return None
    pm=pais.map(cc)
    if pm.isna().all():
        pl=lab.value_labels().get(lab._lbllist[list(d.columns).index(col['idenpa'])],{})
        pm=d[col['idenpa']].map(lambda k: NAME.get(str(pl.get(k,'')).lower()))
    w=d[col['wt']].fillna(1)
    x=d[vc]
    ap=[k for k,t in m.items() if str(t).lower().startswith('aprueba')]
    na=[k for k,t in m.items() if str(t).lower().startswith('no aprueba') or str(t).lower().startswith('desaprueba')]
    if not ap: ap=[1]; na=[2]
    for p in ISO.values():
        s=(pm==p)
        a=w[s&x.isin(ap)].sum(); n=w[s&x.isin(na)].sum(); tot=w[s].sum()
        if a+n>0: rows.append((p,int(y),round(100*a/(a+n),1),round(100*a/tot,1),int(s.sum())))
for a in audit: print(a)
o=pd.DataFrame(rows,columns=['pais','anio','aprueba_pct_sobre_respuestas','aprueba_pct_sobre_total','n_encuestados'])
o['fuente']='Latinobarómetro (bases .dta oficiales aportadas por el usuario), pregunta aprobación gestión del gobierno'
o.to_csv('out/lb_ampliacion_raw.csv',index=False)
print(o.pivot(index='anio',columns='pais',values='aprueba_pct_sobre_respuestas'))

# ---- 2018, 2020, 2023 (archivos R, leídos con scripts/rread.py) ----
import sys; sys.path.insert(0,'scripts'); import rread
ISOI={68:'BO',600:'PY',218:'EC',32:'AR',76:'BR',152:'CL',170:'CO',604:'PE',858:'UY'}
extra=[]
def calc(df,var,y):
    for code,p in ISOI.items():
        s=df[df['idenpa']==code]; a=(s['wt']*(s[var]==1)).sum(); n=(s['wt']*(s[var]==2)).sum(); t=s['wt'].sum()
        if a+n>0: extra.append((p,y,round(100*a/(a+n),1),round(100*a/t,1),len(s)))
o18=rread.load('lb/y2018/Latinobarometro_2018_Eng_R_v20190303.rds'); d18,_=rread.to_df(o18); d18.columns=[c.lower() for c in d18.columns]
calc(d18,'p20stgbsc',2018)
for y,path,var in [(2020,'lb/y2020/Latinobarometro_2020_Eng_Rdata_v1_0.rdata','p17stgbs'),(2023,'lb/y2023/Latinobarometro_2023_Eng_Rdata_v1_0.rdata','P15STGBS')]:
    oo=rread.load_multi(path); k=[k for k in oo if k and k.startswith('Latino')][0]
    d,_=rread.to_df(oo[k]); calc(d,var,y)
e=pd.DataFrame(extra,columns=o.columns[:5])
e['fuente']='Latinobarómetro (archivo R aportado por el usuario); variable '+'P20STGBSC (2018), p17stgbs (2020, identificada por orden/plausibilidad), P15STGBS (2023)'
o=pd.concat([o,e]).sort_values(['pais','anio'])
o.to_csv('out/lb_ampliacion_raw.csv',index=False)
print(o.pivot(index='anio',columns='pais',values='aprueba_pct_sobre_respuestas'))
