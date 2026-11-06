"""Completa us_cuenta_corriente_wb_tm1 (cuenta corriente real, % PIB, WDI BN.CAB.XOKA.GD.ZS) desde final/cuenta_corriente_wb.csv (año previo; dic -> mismo año)."""
import pandas as pd
F='final/'; c=pd.read_csv(F+'cuenta_corriente_wb.csv').set_index(['pais','anio']).cuenta_corriente_wb
for nm in ['panel_modelo_eleccion','panel_modelo_region']:
    P=pd.read_csv(F+nm+'.csv'); d=pd.to_datetime(P.fecha); y=d.dt.year.where(d.dt.month==12,d.dt.year-1)
    v=pd.Series([c.get((p,a)) for p,a in zip(P.pais,y)],index=P.index,dtype=float)
    if 'us_cuenta_corriente_wb_tm1' not in P: P['us_cuenta_corriente_wb_tm1']=float('nan')
    P['us_cuenta_corriente_wb_tm1']=P.us_cuenta_corriente_wb_tm1.fillna(v); P.to_csv(F+nm+'.csv',index=False)
    if nm=='panel_modelo_eleccion': print(P[P.us_cuenta_corriente_wb_tm1.isna()].id_eleccion.tolist())
