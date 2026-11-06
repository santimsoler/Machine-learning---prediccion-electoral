import pandas as pd, numpy as np, sys
sys.path.insert(0,'scripts')
import re, unicodedata
def nz(s): return re.sub(r'[^A-Z ]','',unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().upper()).strip()
def reg(n):
    n=nz(n)
    if 'EXTRANJERO' in n: return None
    for k,v in [('ARICA','Arica y Parinacota'),('TARAPACA','Tarapaca'),('ANTOFAGASTA','Antofagasta'),('ATACAMA','Atacama'),('COQUIMBO','Coquimbo'),('VALPARAISO','Valparaiso'),('HIGGINS','OHiggins'),('MAULE','Maule'),('NUBLE','Nuble'),('BIOBIO','Biobio'),('ARAUCANIA','Araucania'),('LOS RIOS','Los Rios'),('LOS LAGOS','Los Lagos'),('AISEN','Aysen'),('AYSEN','Aysen'),('MAGALLANES','Magallanes'),('METROPOLITANA','Metropolitana')]:
        if k in n: return v
r=pd.read_csv('final/panel_modelo_region.csv')
r=r.drop(columns=[c for c in ['pobreza_casen','pobreza_casen_comparable','pobreza_casen_anio','pobreza_casen_metodo','pobreza_casen_rel'] if c in r])
new=pd.read_csv('final/pobreza_chile_region_casen_2011_2024.csv')
mid=pd.read_csv('final/pobreza_chile_casen_1990_2006_metodologia2013.csv')
m13=pd.read_csv('final/pobreza_casen_region.csv').set_index('region_casen').pobreza_ingresos_metod2013
nac_new=new[~new.region.str.contains('historico')].groupby('anio_casen').apply(lambda g:(g.pobreza_ingresos*g.poblacion_est).sum()/g.poblacion_est.sum()).to_dict()
nac_new['2024c']=4.89
OLA={1989:1990,1993:1992,1999:1998,2005:2003,2009:2006,2013:2011,2017:2015,2021:2020,2025:2024}
out=[]
for p,a,rg in zip(r.pais,r.anio,r.region):
    g=reg(rg)
    if p!='CL' or a not in OLA or g is None: out.append((np.nan,np.nan,np.nan,'',np.nan)); continue
    y=OLA[a]
    if y in (1990,1992,1998,2003,2006):
        x=mid[(mid.region==g)&(mid.anio_casen==y)]; nat=mid[(mid.region=='NACIONAL')&(mid.anio_casen==y)].pobreza_ingresos.iloc[0]
        v=x.pobreza_ingresos.iloc[0] if len(x) else np.nan
        out.append((v,v,v/nat if v==v else np.nan,'metodología 2013',y)); continue
    gg='Biobio historico (incl. Nuble)' if (g=='Biobio' and y<=2015) else g
    x=new[(new.region==gg)&(new.anio_casen==y)]; v=x.pobreza_ingresos.iloc[0] if len(x) else np.nan
    if y==2024:
        vc=m13.get(g,np.nan); out.append((v,vc,vc/nac_new['2024c'],'2024 (línea nueva); comparable=metodología 2013',y))
    else:
        out.append((v,v,v/nac_new[y],'metodología 2013',y))
o=pd.DataFrame(out,columns=['pobreza_casen','pobreza_casen_comparable','pobreza_casen_rel','pobreza_casen_metodo','pobreza_casen_anio'],index=r.index)
r=pd.concat([r,o],axis=1); r.to_csv('final/panel_modelo_region.csv',index=False)
c=r[r.pais=='CL']; print(c.groupby('anio')[['pobreza_casen','pobreza_casen_comparable','pobreza_casen_rel']].agg(['count','mean']).round(2))
