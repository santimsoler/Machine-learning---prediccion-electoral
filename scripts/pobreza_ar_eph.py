import pandas as pd, numpy as np, re, unicodedata
def nz(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().upper().strip()
    return re.sub(r'\s+',' ',s)
d=pd.read_csv('eph/e.csv.gz',low_memory=False)
RG={1:'GBA',40:'NOA',41:'NEA',42:'Cuyo',43:'Pampeana',44:'Patagonia'}
def wq(x,w,q):
    o=np.argsort(x.values); xs=x.values[o]; cw=np.cumsum(w.values[o]); return xs[np.searchsorted(cw,q*cw[-1])]
rows=[]
for ola,g in d.groupby('ola'):
    v=g[(g.IPCF>0)&g.PONDERA.notna()&g.REGION.notna()].copy(); w=v.PONDERA
    med=wq(v.IPCF,w,.5); q1=wq(v.IPCF,w,.2)
    v['reg']=v.REGION.map(RG)
    for r,x in list(v.groupby('reg'))+[('NACIONAL(urbano)',v)]:
        ww=x.PONDERA; s=ww.sum()
        rows.append(dict(ola=ola,region=r,rel50=100*ww[x.IPCF<.5*med].sum()/s,rel60=100*ww[x.IPCF<.6*med].sum()/s,
          cuota_quintil1=100*ww[x.IPCF<=q1].sum()/s,ingreso_mediano_rel=wq(x.IPCF,ww,.5)/med,n_personas=len(x),
          pct_ipcf_cero_excluido=100*(1-len(x)/len(g[g.REGION==x.REGION.iloc[0]])) if r!='NACIONAL(urbano)' else 100*(1-len(v)/len(g))))
t=pd.DataFrame(rows)
t['fuente']='EPH INDEC (individual, PONDERA); espejo github.com/holatam/data; IPCF>0; cálculo propio'
t.to_csv('final/pobreza_relativa_argentina_eph.csv',index=False)
print(t.pivot(index='region',columns='ola',values='rel50').round(1)); print(t.pivot(index='region',columns='ola',values='ingreso_mediano_rel').round(2))
# merge panel
AR={'GBA':['CABA','CAPITAL FEDERAL','CIUDAD AUTONOMA DE BUENOS AIRES'],
 'Pampeana':['BUENOS AIRES','BS AS','CORDOBA','ENTRE RIOS','LA PAMPA','SANTA FE'],
 'Cuyo':['MENDOZA','SAN JUAN','SAN LUIS'],
 'NOA':['JUJUY','SALTA','TUCUMAN','CATAMARCA','LA RIOJA','SANTIAGO DEL ESTERO','S. DEL ESTERO'],
 'NEA':['CHACO','CORRIENTES','FORMOSA','MISIONES'],
 'Patagonia':['CHUBUT','NEUQUEN','RIO NEGRO','SANTA CRUZ','TIERRA DEL FUEGO','TIERRA DEL FUEGO, ANTARTIDA E ISLAS DEL ATLANTICO SUR']}
inv={nz(v):k for k,vs in AR.items() for v in vs}
OLA={1995:'1996O1',1999:'1998O2',2003:'2002O2',2007:'2006T4',2011:'2010T4',2015:'2014T4',2019:'2018T4',2023:'2022T4'}
r=pd.read_csv('final/panel_modelo_region.csv')
r=r.drop(columns=[c for c in r.columns if c.startswith('eph_')])
T=t.set_index(['ola','region'])
cols={'eph_pobreza_rel50':'rel50','eph_pobreza_rel60':'rel60','eph_cuota_quintil1':'cuota_quintil1','eph_ingreso_mediano_rel':'ingreso_mediano_rel'}
new={k:[] for k in list(cols)+['eph_ola','eph_region']}
for p,a,rg in zip(r.pais,r.anio,r.region):
    reg=inv.get(nz(rg)) if p=='AR' else None; ola=OLA.get(a)
    if reg is None or ola is None:
        for k in new: new[k].append(np.nan)
        continue
    for k,c in cols.items(): new[k].append(T.loc[(ola,reg),c])
    new['eph_ola'].append(ola); new['eph_region'].append(reg)
r=pd.concat([r,pd.DataFrame(new,index=r.index)],axis=1); r.to_csv('final/panel_modelo_region.csv',index=False)
c=r[(r.pais=='AR')&(r.vuelta==1)]
print(c.groupby('anio').eph_pobreza_rel50.agg(['count','mean']).round(1))
