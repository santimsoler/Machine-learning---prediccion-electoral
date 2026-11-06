"""Completa us_gdp_real_crec_tm1 y us_ner_var_tm1 con Banco Mundial (equivalentes exactos a las series del usuario: corr=1.0 en el solapamiento).
current_account y fiscal_primario: ver data_ampliacion/us_ca_fiscal_extra.csv (opcional; pais,anio,current_account,fiscal_primario)."""
import pandas as pd, numpy as np, os
F='final/'
B=pd.read_csv(F+'macro_anual_bm.csv'); T=B[B.variable=='tc_oficial_lcu_usd'].pivot(index='anio',columns='pais',values='valor')
G=B[B.variable=='crecimiento_pib'].pivot(index='anio',columns='pais',values='valor')
iso={'AR':'ARG','BR':'BRA','CL':'CHL','CO':'COL','PE':'PER','UY':'URY','BO':'BOL','PY':'PRY','EC':'ECU','MX':'MEX','CR':'CRI','PA':'PAN'}
X=F and 'data_ampliacion/us_ca_fiscal_extra.csv'
ex=pd.read_csv(X) if os.path.exists(X) else None
def fix(r):
    y=r.fecha.year-1 if r.fecha.month<12 else r.fecha.year; c=iso[r.pais]; o={}
    if pd.isna(r.us_gdp_real_crec_tm1) and c in G and y in G.index: o['us_gdp_real_crec_tm1']=G.loc[y,c]
    if pd.isna(r.us_ner_var_tm1) and c in T and y in T.index and y-1 in T.index and T.loc[y-1,c]>0: o['us_ner_var_tm1']=(T.loc[y,c]/T.loc[y-1,c]-1)*100
    if ex is not None:
        e=ex[(ex.pais==r.pais)&(ex.anio==y)]
        for k in ['current_account','fiscal_primario']:
            if pd.isna(r['us_'+k+'_tm1']) and len(e) and pd.notna(e[k].iloc[0]): o['us_'+k+'_tm1']=e[k].iloc[0]
    return pd.Series(o,dtype=float)
for nm in ['panel_modelo_eleccion','panel_modelo_region']:
    P=pd.read_csv(F+nm+'.csv'); D=P.copy(); D['fecha']=pd.to_datetime(D.fecha)
    for c in ['us_current_account_tm1','us_fiscal_primario_tm1','us_gdp_real_crec_tm1','us_ner_var_tm1']:
        if c not in D: D[c]=np.nan
    u=D.drop_duplicates(['pais','fecha'])
    fx=u.apply(fix,axis=1); fx[['pais','fecha']]=u[['pais','fecha']]
    for c in [c for c in fx.columns if c.startswith('us_')]:
        m=D[['pais','fecha']].merge(fx[['pais','fecha',c]],on=['pais','fecha'],how='left')[c].values
        P[c]=P[c].fillna(pd.Series(m,index=P.index))
    P.to_csv(F+nm+'.csv',index=False)
    if nm=='panel_modelo_eleccion': print(P[[c for c in P.columns if c.startswith('us_')]].isna().sum())
