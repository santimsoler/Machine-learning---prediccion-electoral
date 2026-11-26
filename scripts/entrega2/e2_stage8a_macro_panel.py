"""Panel macro anual por país (12 países) y proxy de sudden stop; se guarda en final/macro_panel_ss.csv.
Usa macro_anual_bm.csv (Banco Mundial) y cuenta_corriente_wb.csv (descargados del repositorio). No hay datos de flujos de capital: es una proxy de ajuste externo forzado."""
import pandas as pd
a=pd.read_csv('final/macro_anual_bm.csv'); cc=pd.read_csv('final/cuenta_corriente_wb.csv')
m={'ARG':'AR','BOL':'BO','BRA':'BR','CHL':'CL','COL':'CO','CRI':'CR','ECU':'EC','MEX':'MX','PAN':'PA','PER':'PE','PRY':'PY','URY':'UY'}
a['pais']=a.pais.map(m)
w=a.pivot_table(index=['pais','anio'],columns='variable',values='valor').reset_index().merge(cc.rename(columns={'cuenta_corriente_wb':'ca'}),on=['pais','anio'],how='left').sort_values(['pais','anio'])
w['dca']=w.groupby('pais').ca.diff(); w['dg']=w.groupby('pais').crecimiento_pib.diff(); w['depre']=w.groupby('pais').tc_oficial_lcu_usd.pct_change()*100
w['ss']=((w.dca>=3)&((w.crecimiento_pib<=0)|(w.dg<=-3))).astype(int)   # umbrales fijados antes de ver resultados
w.to_csv('final/macro_panel_ss.csv',index=False); print(int(w.ss.sum()),'años-país con proxy de',len(w))
