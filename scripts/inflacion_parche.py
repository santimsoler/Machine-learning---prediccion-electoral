"""Completa inflación del año previo en 5 elecciones: AR (1989,1995,1999,2003) con IPC dic/dic del año previo (1988 387.7; 1994 3.9; 1998 0.7; 2002 40.9; la-voz-de-san-justo/INDEC)
y CL-1989 con IPC promedio 1989 de WDI (17.03). Marca inflacion_12m_previa_proxy=1 (no es la ventana de 12m previa exacta). bm_inflacion_ipc_tm1 se completa solo para esas filas."""
import pandas as pd, numpy as np
F='final/'
V={'AR-1989-PRES-1':387.7,'AR-1995-PRES-1':3.9,'AR-1999-PRES-1':0.7,'AR-2003-PRES-1':40.9,'CL-1989-PRES-1':17.03}
for nm in ['panel_modelo_eleccion','panel_modelo_region']:
    P=pd.read_csv(F+nm+'.csv').drop(columns=['inflacion_12m_previa_proxy'],errors='ignore'); P['inflacion_12m_previa_proxy']=0
    for k,v in V.items():
        m=(P.id_eleccion==k)
        for c in ['inflacion_12m_previa','bm_inflacion_ipc_tm1']:
            s=m&P[c].isna(); P.loc[s,c]=v
            if c=='inflacion_12m_previa': P.loc[s,'inflacion_12m_previa_proxy']=1
    P.to_csv(F+nm+'.csv',index=False)
    if nm=='panel_modelo_eleccion': print(P.inflacion_12m_previa.isna().sum(),P.bm_inflacion_ipc_tm1.isna().sum())
