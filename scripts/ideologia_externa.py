import pandas as pd, unicodedata, re, numpy as np
A='/mnt/user-data/attachments/fbc2a8cf-9f07-5c94-8ce1-557ba4094ca9/'
PM={'Argentina':'AR','Brazil':'BR','Chile':'CL','Colombia':'CO','Peru':'PE','Uruguay':'UY'}
def n(t): return re.sub(r'[^a-z ]','',unicodedata.normalize('NFKD',str(t)).encode('ascii','ignore').decode().lower())
out=[]
# 1) Manifesto: nivel candidato presidencial
m=pd.read_csv(A+'219a3d6b-MPDataset_MPDS2026a.csv',low_memory=False)
m=m[m.countryname.isin(PM)&m.presvote.notna()].copy()
m['pais']=m.countryname.map(PM); m['anio']=pd.to_datetime(m.edate,dayfirst=True).dt.year
for _,r in m.iterrows():
    for v in ['rile','markeco','planeco','welfare','per601','per602','per603','per604','per605','per606','per607','per608','per705']:
        if v in m.columns and pd.notna(r[v]):
            out.append(('manifesto',r.pais,r.anio,r.candidatename,r.partyname,v,r[v],r.presvote,'candidato'))
# 2) CHES-LA 2020: partidos y presidentes
c=pd.read_csv(A+'f1c2292b-ches_la_2020_aggregate_level_v01.csv',encoding='latin-1')
c=c[c.country_abb.isin(PM.values())]
for _,r in c.iterrows():
    for v in ['lrecon','galtan','lrgen','redistribution','sociallifestyle','religious_principles','immigrate_policy','ethnic_minorities','crime']:
        if pd.notna(r[v]):
            out.append(('ches_la_2020',r.country_abb,2020,r.party if r.president==1 else None,r.party,v,r[v],None,'presidente' if r.president==1 else 'partido'))
# 3) V-Party
v=pd.read_csv('final/vparty_6paises_v2.csv')
for _,r in v.iterrows():
    for k in ['v2pariglef','v2palgbt','v2parelig','v2paimmig','v2paculsup']:
        if pd.notna(r[k]):
            out.append(('vparty_v2',r.pais,int(r.year),None,r.v2paenname,k,r[k],r.v2pavote,'partido'))
d=pd.DataFrame(out,columns=['fuente','pais','anio','candidato','partido','variable','valor','voto_pct','nivel'])
d.to_csv('final/ideologia_externa.csv',index=False)
print(d.groupby(['fuente','nivel']).size())
# validacion contra nuestro eje economico
ev=pd.read_csv('final/ideologia_evidencia.csv'); ev=ev[ev.eje=='economico']
mm=m.copy(); mm['k']=mm.candidatename.map(n)
rows=[]
for _,r in ev.iterrows():
    anio=int(r.elecciones.split('-')[1]); pais=r.elecciones.split('-')[0]
    toks=[t for t in n(r.candidato.split(' - ')[0]).split() if len(t)>3]
    g=mm[(mm.pais==pais)&(mm.anio==anio)]
    hit=g[g.k.apply(lambda s:any(t in s for t in toks[-2:]))]
    if len(hit)==1:
        rows.append((r.elecciones,r.candidato.split(' - ')[0],r.valor,hit.iloc[0].rile,hit.iloc[0].markeco,hit.iloc[0].planeco,r.nivel_evidencia))
val=pd.DataFrame(rows,columns=['elec','cand','nuestro_econ','rile','markeco','planeco','nivel'])
print(val.to_string())
print(len(val), 'corr rile', val[['nuestro_econ','rile']].corr(method='spearman').iloc[0,1])
val['mk_menos_plan']=val.markeco-val.planeco
print('corr markeco-planeco', val[['nuestro_econ','mk_menos_plan']].corr(method='spearman').iloc[0,1])
val.to_csv('final/validacion_manifesto_vs_nuestro.csv',index=False)
