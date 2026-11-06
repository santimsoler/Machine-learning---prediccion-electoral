import pandas as pd, numpy as np, re, unicodedata
def nz(s):
    s=unicodedata.normalize('NFKD',str(s).replace('’',"'")).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z ]','',s).strip()
tab=pd.read_csv('cl/comunas_region.csv',dtype=str)
FIX={'Calera':'La Calera','Riconada':'Rinconada','Ránqui':'Ránquil','San Nico':'San Nicolás','Marichihue':'Marchihue','Coihaique':'Coyhaique','Aisén':'Aysén'}
tab['comuna']=tab.comuna.replace(FIX)
REG={'15':'Arica y Parinacota','01':'Tarapaca','02':'Antofagasta','03':'Atacama','04':'Coquimbo','05':'Valparaiso','06':'OHiggins','07':'Maule','16':'Nuble','08':'Biobio','09':'Araucania','14':'Los Rios','10':'Los Lagos','11':'Aysen','12':'Magallanes','13':'Metropolitana'}
tab['reg']=tab.cut.str[:2].map(REG)
key={nz(c):(r,cut) for c,r,cut in zip(tab.comuna,tab.reg,tab.cut)}
key[nz('Calera')]=key[nz('La Calera')]
def load(f,var):
    d=pd.read_csv(f,skipinitialspace=True); d=d.rename(columns={'Unidad territorial':'u'})
    for y in ['2011','2013','2015','2017','2020','2022','2024']: d[y]=pd.to_numeric(d[y].replace('-',np.nan),errors='coerce')
    return d
P,N=load('cl/bcn_pct.csv',''),load('cl/bcn_num.csv','')
def reg_of(u):
    m=re.match(r'^(.*?)(?: \(Región de(?:l| los| la)? ?(.*)\))?$',u); base,suf=m.group(1),m.group(2)
    k=nz(base)
    if k not in key:
        k2={nz('Aysen'):nz('Aisén')}.get(k)
        k=k2 if k2 in key else k
    if k not in key: return None,None
    r,cut=key[k]
    # antes de 2018 las comunas de Ñuble figuran sin sufijo (Biobío); con sufijo = Ñuble
    return r,cut
P['reg'],P['cut']=zip(*P.u.map(reg_of)); N['reg'],N['cut']=zip(*N.u.map(reg_of))
m_=None
print('sin región:',P[P.reg.isna()].u.tolist())
yrs=['2011','2013','2015','2017','2020','2022','2024']
m=P[['u','reg','cut']+yrs].merge(N[['u']+yrs],on='u',suffixes=('_p','_n'))
rows=[]
for (r),g in m.groupby('reg'):
    for y in yrs:
        v=g[[y+'_p',y+'_n']].dropna()
        if len(v)==0: continue
        v=v[v[y+'_p']>0]
        pop=(v[y+'_n']/(v[y+'_p']/100)); rows.append(dict(region=r,anio_casen=int(y),pobreza_ingresos_pct=100*v[y+'_n'].sum()/pop.sum(),poblacion_est=pop.sum(),n_comunas=len(v),n_comunas_region=g.cut.nunique()))
out=pd.DataFrame(rows)
# Biobío histórico (comunas de Ñuble incluidas) para elecciones con CASEN <=2015
for y in [2011,2013,2015]:
    a=out[(out.anio_casen==y)&out.region.isin(['Biobio','Nuble'])]
    pb=(a.pobreza_ingresos_pct*a.poblacion_est).sum()/a.poblacion_est.sum()
    out=pd.concat([out,pd.DataFrame([dict(region='Biobio historico (incl. Nuble)',anio_casen=y,pobreza_ingresos_pct=pb,poblacion_est=a.poblacion_est.sum(),n_comunas=a.n_comunas.sum(),n_comunas_region=a.n_comunas_region.sum())])])
nac=out[~out.region.str.contains('historico')].groupby('anio_casen').apply(lambda g:(g.pobreza_ingresos_pct*g.poblacion_est).sum()/g.poblacion_est.sum())
print('NACIONAL ponderado:',nac.round(1).to_dict())
out.to_csv('cl/pobreza_region_bcn.csv',index=False)
print(out.pivot(index='region',columns='anio_casen',values='pobreza_ingresos_pct').round(1).to_string())
print(out.pivot(index='region',columns='anio_casen',values='n_comunas').to_string())
