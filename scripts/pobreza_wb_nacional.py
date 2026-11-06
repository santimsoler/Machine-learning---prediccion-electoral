import pandas as pd, numpy as np
F='final/'
w=pd.read_csv('wb/wdi_pobreza_gini.csv')
ISO={'AR':'ARG','BR':'BRA','CL':'CHL','CO':'COL','PE':'PER','UY':'URY'}
IND={'pob_6.85usd':'pobnac_685','pob_3.65usd':'pobnac_365'}
el=pd.read_csv(F+'elecciones.csv'); ey={p:sorted(set(g.anio)) for p,g in el.groupby('pais')}
def serie(iso,ind):
    s=w[(w.pais==iso)&(w.indicador==ind)].set_index('anio').valor.sort_index(); return s
def val(s,y):
    """valor en el anio y: observado, o interpolacion lineal entre anios observados; si y supera el ultimo observado en 1 anio, usa el ultimo"""
    if y in s.index: return s[y],y,'observado'
    if y<s.index.min(): return np.nan,np.nan,'fuera_de_rango'
    if y>s.index.max():
        if y-s.index.max()<=1: return s[s.index.max()],s.index.max(),'ultimo_disponible'
        return np.nan,np.nan,'fuera_de_rango'
    a=s[s.index<y]; b=s[s.index>y]; ya,yb=a.index.max(),b.index.min()
    return a[ya]+(b[yb]-a[ya])*(y-ya)/(yb-ya),y,'interpolado'
rows=[]
for p,yrs in ey.items():
    for i,y in enumerate(yrs):
        r={'pais':p,'anio':y}
        for ind,nm in IND.items():
            s=serie(ISO[p],ind)
            fin,afin,tfin=val(s,y-1)
            r[nm+'_tm1']=fin; r[nm+'_tm1_tipo']=tfin
            if i>0:
                ini,_,tini=val(s,yrs[i-1]-1)
                r[nm+'_eleccion_prev']=ini; r['d_'+nm+'_mandato']=fin-ini if pd.notna(fin) and pd.notna(ini) else np.nan
                r[nm+'_ini_tipo']=tini
        rows.append(r)
t=pd.DataFrame(rows); t['anios_mandato']=t.groupby('pais').anio.diff()
t['fuente_pobnac']='Banco Mundial WDI (SI.POV.UMIC 6.85 USD y SI.POV.LMIC 3.65 USD, PPA 2017); anios sin encuesta interpolados linealmente'
t.to_csv(F+'pobreza_nacional_bm_por_eleccion.csv',index=False)
keep=['pais','anio','pobnac_685_tm1','pobnac_685_tm1_tipo','pobnac_685_eleccion_prev','d_pobnac_685_mandato','pobnac_365_tm1','d_pobnac_365_mandato','anios_mandato']
for f in ['panel_modelo_region.csv','panel_modelo_eleccion.csv']:
    p=pd.read_csv(F+f); p=p.drop(columns=[c for c in p.columns if c in keep[2:] ],errors='ignore')
    p=p.merge(t[keep],on=['pais','anio'],how='left'); p.to_csv(F+f,index=False)
    print(f,p.shape)
e=pd.read_csv(F+'panel_modelo_eleccion.csv')
print(e.groupby('pais').agg(n=('anio','size'),cobertura_delta=('d_pobnac_685_mandato','count')).to_string())
print(t[['pais','anio','pobnac_685_tm1','pobnac_685_tm1_tipo','d_pobnac_685_mandato']].round(1).to_string())
