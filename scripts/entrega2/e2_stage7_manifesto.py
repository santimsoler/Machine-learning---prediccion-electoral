"""Etapa 7: cobertura del Manifesto Project (MPDS2026a) sobre las 76 elecciones y validación débil de la ideología codificada a mano.
Requiere subir MPDataset_MPDS2026a.csv a la carpeta de trabajo."""
import pandas as pd, numpy as np, re, os
ruta='MPDataset_MPDS2026a.csv'
if not os.path.exists(ruta): raise SystemExit('Subí MPDataset_MPDS2026a.csv (Manifesto Project) a esta carpeta para correr esta etapa.')
m=pd.read_csv(ruta,low_memory=False)
cc={'Argentina':'AR','Bolivia':'BO','Brazil':'BR','Chile':'CL','Colombia':'CO','Costa Rica':'CR','Ecuador':'EC','Mexico':'MX','Panama':'PA','Peru':'PE','Paraguay':'PY','Uruguay':'UY'}
m=m[m.countryname.isin(cc)].copy(); m['pais']=m.countryname.map(cc); m['anio']=(m.date//100).astype(int)
e=pd.read_csv('final/panel_modelo_eleccion.csv'); e1=e[e.vuelta==1]
filas=[]; hit=[]
for r in e1.itertuples():
    z=m[(m.pais==r.pais)&(m.anio==r.anio)]; filas.append(dict(id_eleccion=r.id_eleccion,pais=r.pais,anio=r.anio,n_programas=len(z)))
    f=str(r.familia_of).lower().strip()
    k=z[(z.partyabbrev.fillna('').str.lower()==f)|(z.partyname.fillna('').str.lower().str.contains(re.escape(f)) if len(f)>3 else False)]
    if len(k): hit.append((r.id_eleccion,k.rile.iloc[0],r.ideologia_of))
C=pd.DataFrame(filas); C['cubierta']=C.n_programas>0
print('Elecciones:',len(C),'| con >=1 programa:',int(C.cubierta.sum()),'| >=3:',int((C.n_programas>=3).sum()))
print('antes de 2000:',int(C[C.anio<2000].cubierta.sum()),'de',(C.anio<2000).sum(),'| 2000 en adelante:',int(C[C.anio>=2000].cubierta.sum()),'de',(C.anio>=2000).sum())
print(C.groupby('pais').agg(elecciones=('id_eleccion','count'),cubiertas=('cubierta','sum'),programas=('n_programas','sum')).T)
H=pd.DataFrame(hit,columns=['id','rile','ideologia_of']).dropna()
print('Programa del oficialismo identificable por nombre en',len(hit),'elecciones; corr(RILE, ideología codificada): pearson %.2f, spearman %.2f (n=%d)'%(H.corr(numeric_only=True).iloc[0,1],H.corr(method='spearman',numeric_only=True).iloc[0,1],len(H)))
