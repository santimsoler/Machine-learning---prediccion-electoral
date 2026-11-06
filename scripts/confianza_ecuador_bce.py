"""ICC-BCE Ecuador (ENEMDU, 5 ciudades). Valores extraídos del texto de los boletines mensuales del BCE (Colab del usuario, 5-nov-2026).
Solo meses con valor validado (rango 24-55). Meses sin dato quedan vacíos."""
import pandas as pd, numpy as np
F='final/'
S={'2010-10':42.3,'2010-11':43.3,'2010-12':41.5,'2011-08':39.4,'2011-09':41.1,'2011-11':41.2,'2011-12':44.9,'2012-01':43.0,'2012-02':43.4,'2012-04':43.6,'2012-05':44.2,'2012-06':44.2,'2012-07':44.2,'2012-08':43.8,'2012-09':43.2,'2012-10':43.6,'2012-11':41.4,'2012-12':48.7,'2013-01':45.8,'2013-02':45.1,'2013-04':46.3,'2013-07':46.4,'2013-08':45.5,'2013-10':45.5,'2013-11':47.1,'2013-12':50.6,
'2020-06':27.65,'2020-07':27.02,'2020-08':27.32,'2020-09':28.83,'2020-10':27.61,'2020-11':26.32,'2020-12':30.81,'2021-01':30.31,'2021-02':29.74,'2021-03':30.04,'2021-04':31.42,'2021-05':31.34,'2021-06':33.99,'2021-07':35.8,'2021-08':37.1,'2021-09':34.0,'2021-10':35.6,'2021-11':35.3,'2021-12':34.9,
'2022-01':36.0,'2022-02':35.6,'2022-03':36.7,'2022-04':36.1,'2022-05':37.2,'2022-06':35.8,'2022-07':36.0,'2022-08':36.2,'2022-09':36.6,'2022-10':35.59,'2022-11':35.1,'2022-12':36.7,'2023-01':36.5,'2023-02':35.3,'2023-03':35.74,'2023-04':35.49,'2023-05':34.41,'2023-06':35.33,'2023-07':35.57,'2023-08':35.0,'2023-09':35.7,'2023-10':35.5,'2023-11':36.1,'2023-12':37.6,
'2024-01':36.55,'2024-02':37.97,'2024-11':36.31,'2024-12':37.20,'2025-01':37.70,'2025-02':37.13}
# 2017: solo variaciones interanuales publicadas (nov-16 -5.2, dic-16 -2.2, ene-17 +0.5 vs un año antes; ene-17 con empalme de metodología)
YOY17=[-5.2,-2.2,0.5]
c=pd.read_csv(F+'confianza_consumidor_mensual.csv'); c=c[c.variable!='icc_bce_ecuador']
n=pd.DataFrame([('EC',k,'icc_bce_ecuador',v,'índice (0-100)','Banco Central del Ecuador, Índice de Confianza del Consumidor (ENEMDU, 5 ciudades); texto de boletines mensuales (extracción con Colab)','nivel global nacional') for k,v in S.items()],columns=c.columns)
pd.concat([c,n]).to_csv(F+'confianza_consumidor_mensual.csv',index=False)
d=pd.Series(S); d.index=pd.PeriodIndex(d.index,freq='M')
def ccf(f):
    p=pd.Period(f,'M')-1
    w=d[(d.index<=p)&(d.index>p-3)]; w12=d[(d.index<=p-12)&(d.index>p-15)]
    if len(w)<2: return pd.Series({'cc_3m':np.nan,'cc_var12m':np.nan,'cc_n_meses':len(w)})
    return pd.Series({'cc_3m':w.mean(),'cc_var12m':(w.mean()-w12.mean()) if len(w12)>=2 else np.nan,'cc_n_meses':len(w)})
for nm in ['panel_modelo_eleccion','panel_modelo_region']:
    P=pd.read_csv(F+nm+'.csv'); m=(P.pais=='EC')
    if m.sum()==0: continue
    for col in ['cc_aproximacion']:
        if col not in P: P[col]=np.nan
    fe=pd.to_datetime(P.loc[m,'fecha'])
    R=fe.apply(ccf); P.loc[m,'cc_3m']=R.cc_3m.values; P.loc[m,'cc_var12m']=R.cc_var12m.values; P.loc[m,'cc_z']=np.nan
    # 2017: solo variación interanual
    m17=m&(P.fecha=='2017-02-19'); P.loc[m17,'cc_var12m']=float(np.mean(YOY17))
    P.loc[m,'cc_aproximacion']=pd.Series(np.where(P.loc[m,'cc_3m'].notna()|P.loc[m,'cc_var12m'].notna(),'ICC_BCE_Ecuador_5ciudades_texto_boletin',None),index=P.index[m])
    P.to_csv(F+nm+'.csv',index=False)
    if nm=='panel_modelo_eleccion': print(P[m][['id_eleccion','fecha','cc_3m','cc_var12m','cc_aproximacion']].round(2).to_string())
