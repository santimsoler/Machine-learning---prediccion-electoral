import pandas as pd, numpy as np, unicodedata
F='final/'
# MIDES (indicador "Porcentaje de personas con al menos una NBI segun departamento (sin calefaccion). Total pais"), fuente INE-ECH. Anios 2013, 2018, 2021
D={'MONTEVIDEO':(15.6,11.2,9.6),'ARTIGAS':(23.8,21.8,21.7),'CANELONES':(21.1,15.7,11.9),'CERRO LARGO':(24,20.4,24.3),'COLONIA':(15.4,9.9,9.4),
'DURAZNO':(26.6,20.4,9.6),'FLORES':(21.8,9.2,2.6),'FLORIDA':(22.9,15.2,7.4),'LAVALLEJA':(19.1,14.6,19.8),'MALDONADO':(16.6,9.7,8.2),
'PAYSANDU':(25.5,22.5,16.5),'RIO NEGRO':(28.7,26,10.6),'RIVERA':(28,14.2,10.6),'ROCHA':(22.6,18.2,17.4),'SALTO':(31.9,26.6,23.5),
'SAN JOSE':(24.4,12,15.7),'SORIANO':(21.3,16.6,15.5),'TACUAREMBO':(32,16,15.9),'TREINTA Y TRES':(26.3,20.3,22.3)}
NAC=(20.1,14.4,12.2)
rows=[]
for d,v in D.items():
    for yr,x,n in zip((2013,2018,2021),v,NAC): rows.append((d,yr,x,n))
t=pd.DataFrame(rows,columns=['dpto','anio_ech','uy_nbi_ech_sc','nbi_nacional'])
t['uy_nbi_ech_sc_rel']=t.uy_nbi_ech_sc/t.nbi_nacional
t['uy_nbi_ech_sc_z']=t.groupby('anio_ech').uy_nbi_ech_sc.transform(lambda s:(s-s.mean())/s.std())
t['uy_nbi_ech_sc_pctrank']=t.groupby('anio_ech').uy_nbi_ech_sc.rank(pct=True)
t['fuente']='MIDES indicador 8031 (INE, ECH): % personas con al menos una NBI por departamento, sin calefaccion'
t.to_csv(F+'nbi_uruguay_departamentos_ech_mides.csv',index=False)
def key(s): return unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().upper().strip().replace('_',' ')
p=pd.read_csv(F+'panel_modelo_region.csv')
p=p.drop(columns=[c for c in p.columns if c.startswith('uy_')],errors='ignore')
p['_k']=p.region.map(key); OLA={2014:2013,2019:2018,2024:2021}
p['_a']=p.anio.map(OLA)
q=t.drop(columns=['fuente','nbi_nacional']).rename(columns={'dpto':'_k','anio_ech':'_a'})
p=p.merge(q,on=['_k','_a'],how='left')
p['uy_nbi_ola']=np.where(p.pais=='UY',p._a,np.nan)
for c in [x for x in p.columns if x.startswith('uy_') and x!='uy_nbi_ola']: p.loc[p.pais!='UY',c]=np.nan
p=p.drop(columns=['_k','_a']); p.to_csv(F+'panel_modelo_region.csv',index=False)
u=p[p.pais=='UY'];print(u.groupby('anio').uy_nbi_ech_sc.count(),u[u.uy_nbi_ech_sc.isna()].region.unique(),p.shape)
print(u[u.vuelta==1].groupby('anio').apply(lambda g:g[['y_share_oficialismo','uy_nbi_ech_sc']].corr().iloc[0,1]).round(2).to_dict())
