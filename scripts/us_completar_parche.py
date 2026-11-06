"""Parche final de us_*: (1) TC y PIB 1985-1992 de WDI (PA.NUS.FCRF, NY.GDP.MKTP.KD.ZG) para AR/CL/PY donde la base BM no tenía;
(2) saldo primario 2025 (aún no publicado por el FMI) = arrastre del valor 2024, con us_fiscal_primario_arrastre=1."""
import pandas as pd, numpy as np
F='final/'
TC={'PRY':{1985:306.667,1986:339.167,1987:550,1988:550,1989:1056.217,1990:1229.808,1991:1325.183,1992:1500.258,1993:1744.346,1994:1904.761,1995:1963.019,1996:2056.812,1997:2177.863,1998:2726.49,1999:3119.073,2000:3486.353,2001:4105.925,2002:5716.258,2003:6424.339,2004:5974.578,2005:6177.935,2006:5635.094,2007:5032.712,2008:4363.292,2009:4966.682,2010:4758.43,2011:4193.802,2012:4421.659,2013:4303.883},
    'CHL':{1987:219.407,1988:245.012,1989:266.954}}
PIB={'ARG':{1988:-1.09},'CHL':{1988:7.351,1989:10.358}}
iso={'AR':'ARG','CL':'CHL','PY':'PRY'}
IMF24={'BR':2.1,'CO':-1.9,'CL':-1.6,'CR':1.1,'PA':-4.5}  # pb 2024 (FMI) para arrastre a 2025
for nm in ['panel_modelo_eleccion','panel_modelo_region']:
    P=pd.read_csv(F+nm+'.csv').drop(columns=['us_fiscal_primario_arrastre'],errors='ignore'); P['us_fiscal_primario_arrastre']=0
    for i,r in P.iterrows():
        d=pd.to_datetime(r.fecha); y=d.year-1 if d.month<12 else d.year; c=iso.get(r.pais)
        if pd.isna(r.us_ner_var_tm1) and c in TC and y in TC[c] and y-1 in TC[c]: P.at[i,'us_ner_var_tm1']=(TC[c][y]/TC[c][y-1]-1)*100
        if pd.isna(r.us_gdp_real_crec_tm1) and c in PIB and y in PIB[c]: P.at[i,'us_gdp_real_crec_tm1']=PIB[c][y]
        if pd.isna(r.us_fiscal_primario_tm1) and y==2025 and r.pais in IMF24: P.at[i,'us_fiscal_primario_tm1']=IMF24[r.pais]; P.at[i,'us_fiscal_primario_arrastre']=1
    P.to_csv(F+nm+'.csv',index=False)
    if nm=='panel_modelo_eleccion':
        for c in [c for c in P.columns if c.startswith('us_') and c!='us_fiscal_primario_arrastre']: print(c,P[P[c].isna()].id_eleccion.tolist())
