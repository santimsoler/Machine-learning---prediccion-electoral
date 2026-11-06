import pandas as pd, numpy as np
F='final/'
lb=pd.read_csv(F+'percepcion_economica_latinobarometro.csv')
def f(r):
    y=r.fecha.year-1 if r.fecha.month<12 else r.fecha.year
    d=lb[(lb.pais==r.pais)&(lb.anio<=y)].sort_values('anio')
    return pd.Series({'percep_econ_lb':d.balance_percep_econ.iloc[-1],'percep_econ_lb_anio':d.anio.iloc[-1]}) if len(d) else pd.Series({'percep_econ_lb':np.nan,'percep_econ_lb_anio':np.nan})
for nm in ['panel_modelo_eleccion','panel_modelo_region']:
    P=pd.read_csv(F+nm+'.csv').drop(columns=['percep_econ_lb','percep_econ_lb_anio','percep_econ_lb_rezago_anios'],errors='ignore')
    k=P[['pais','fecha']].drop_duplicates().assign(fecha=lambda d:pd.to_datetime(d.fecha)); k=pd.concat([k,k.apply(f,axis=1)],axis=1); k['fecha']=k.fecha.dt.strftime('%Y-%m-%d')
    P=P.merge(k,on=['pais','fecha'],how='left'); P['percep_econ_lb_rezago_anios']=pd.to_datetime(P.fecha).dt.year-P.percep_econ_lb_anio
    P.to_csv(F+nm+'.csv',index=False)
