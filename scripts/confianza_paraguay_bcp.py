"""ICC del BCP (Paraguay) cargado a mano desde notas de prensa (ABC Color, La Nación) que citan el dato mensual del BCP."""
import pandas as pd, numpy as np
F='final/'
S={'2021-03':46.0,'2021-12':55.9,'2022-01':56.9,'2022-02':50.8,'2022-03':45.8,'2022-12':52.4,'2023-01':57.5,'2023-02':52.8,'2023-03':52.1}
FUENTES={'2021-12':'abc.com.py 2022-02-14','2022-01':'abc.com.py 2022-02-14','2022-02':'abc.com.py 2022-03-14','2022-03':'lanacion.com.py 2022-04-08','2021-03':'lanacion.com.py 2022-04-08','2022-12':'lanacion.com.py 2023-02-15','2023-01':'lanacion.com.py 2023-02-15 / abc.com.py 2023-03-16','2023-02':'abc.com.py 2023-03-16','2023-03':'abc.com.py 2023-04-14'}
c=pd.read_csv(F+'confianza_consumidor_mensual.csv'); c=c[c.variable!='icc_bcp_paraguay']
n=pd.DataFrame([('PY',k,'icc_bcp_paraguay',v,'índice (0-100)','Banco Central del Paraguay, Índice de Confianza del Consumidor; transcripto a mano de '+FUENTES[k],'ABC 2023-04-14 da feb-2023=51,8 (inconsistente con 52,8 de otras dos notas; se usó 52,8)' if k=='2023-02' else '') for k,v in S.items()],columns=c.columns)
pd.concat([c,n]).to_csv(F+'confianza_consumidor_mensual.csv',index=False)
d=pd.Series(S); d.index=pd.PeriodIndex(d.index,freq='M')
def ccf(f):
    p=pd.Period(f,'M')-1
    w=d[(d.index<=p)&(d.index>p-3)]; w12=d[(d.index<=p-12)&(d.index>p-15)]
    if len(w)<2: return (np.nan,np.nan)
    return (w.mean(),(w.mean()-w12.mean()) if len(w12)>=2 else np.nan)
for nm in ['panel_modelo_eleccion','panel_modelo_region']:
    P=pd.read_csv(F+nm+'.csv'); m=(P.pais=='PY')
    r=[ccf(x) for x in P.loc[m,'fecha']]
    P.loc[m,'cc_3m']=[a for a,b in r]; P.loc[m,'cc_var12m']=[b for a,b in r]; P.loc[m,'cc_z']=np.nan
    P.loc[m,'cc_aproximacion']=pd.Series(['ICC_BCP_Paraguay_nota_prensa' if not np.isnan(a) else None for a,b in r],index=P.index[m])
    P.to_csv(F+nm+'.csv',index=False)
    if nm=='panel_modelo_eleccion': print(P[m][['id_eleccion','fecha','cc_3m','cc_var12m']].round(2).to_string())
