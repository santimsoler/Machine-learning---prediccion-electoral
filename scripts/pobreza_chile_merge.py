import pandas as pd, numpy as np, unicodedata, re
def nz(s): return re.sub(r'[^A-Z ]','',unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().upper()).strip()
r=pd.read_csv('final/panel_modelo_region.csv')
for c in ['pobreza_casen','pobreza_casen_comparable','pobreza_casen_anio']:
    if c in r: r=r.drop(columns=c)
b=pd.read_csv('final/pobreza_chile_region_casen_2011_2024.csv')
m13=pd.read_csv('final/pobreza_casen_region.csv').set_index('region_casen').pobreza_ingresos_metod2013
OLA={2013:2011,2017:2015,2021:2020,2025:2024}   # última CASEN publicada antes de la elección
def reg(n,anio):
    n=nz(n)
    if 'EXTRANJERO' in n: return None
    for k,v in [('ARICA','Arica y Parinacota'),('TARAPACA','Tarapaca'),('ANTOFAGASTA','Antofagasta'),('ATACAMA','Atacama'),('COQUIMBO','Coquimbo'),('VALPARAISO','Valparaiso'),('HIGGINS','OHiggins'),('MAULE','Maule'),('NUBLE','Nuble'),('BIOBIO','Biobio'),('ARAUCANIA','Araucania'),('LOS RIOS','Los Rios'),('LOS LAGOS','Los Lagos'),('AISEN','Aysen'),('AYSEN','Aysen'),('MAGALLANES','Magallanes'),('METROPOLITANA','Metropolitana')]:
        if k in n: return v
v1,v2,v3=[],[],[]
for p,a,rg in zip(r.pais,r.anio,r.region):
    if p!='CL' or a not in OLA or reg(rg,a) is None: v1.append(np.nan);v2.append(np.nan);v3.append(np.nan);continue
    y=OLA[a]; g=reg(rg,a)
    if g=='Biobio' and y<=2015: g='Biobio historico (incl. Nuble)'
    x=b[(b.region==g)&(b.anio_casen==y)]
    val=x.pobreza_ingresos.iloc[0] if len(x) else np.nan
    v1.append(val); v3.append(y)
    v2.append(m13.get(g.replace('Biobio historico (incl. Nuble)','Biobio'),np.nan) if y==2024 else val)
r['pobreza_casen']=v1; r['pobreza_casen_comparable']=v2; r['pobreza_casen_anio']=v3
r.to_csv('final/panel_modelo_region.csv',index=False)
c=r[r.pais=='CL']; print(c.groupby('anio')[['pobreza_casen','pobreza_casen_comparable']].agg(['count','mean']).round(1))
