import pandas as pd
F='final/'
E=pd.read_csv(F+'competencia_por_eleccion.csv').drop(columns=['pais','anio']); E['base']=E.id_eleccion.str[:7]; E=E.drop(columns=['id_eleccion'])
for f in ['panel_modelo_region','panel_modelo_eleccion']:
    P=pd.read_csv(F+f+'.csv').drop(columns=[c for c in E.columns if c!='base' and c in pd.read_csv(F+f+'.csv',nrows=1).columns]); P['base']=P.id_eleccion.str[:7]
    P=P.merge(E,on='base',how='left').drop(columns=['base']); P.to_csv(F+f+'.csv',index=False); print(f,P.shape)
N=pd.read_csv(F+'panel_modelo_eleccion.csv'); v=N[N.vuelta==1]
print(v.groupby(['pre2000','of_tradicional']).y_share_nacional.agg(['mean','count']).round(1))
print(v.groupby('oficialismo_va_por_reeleccion').y_share_nacional.agg(['mean','count']).round(1))
print(v[['y_share_nacional','enc','n_cand_5pct','share_fuertes_cercanos','n_fuertes_cercanos','aprobacion_oficial']].corr().round(2).iloc[0])
