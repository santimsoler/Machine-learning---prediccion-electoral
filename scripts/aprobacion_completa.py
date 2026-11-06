"""Aprobación completa: aprobacion_oficial (EAD / encuesta puntual 2019+) y, donde falta, aprobación Latinobarómetro
(rezago<=3 años) calibrada a la escala EAD con una regresión lineal estimada en las elecciones con ambas fuentes.
Crea aprobacion_oficial_completa y aprobacion_fuente_completa; no toca aprobacion_oficial."""
import pandas as pd, numpy as np
F='final/'
E=pd.read_csv(F+'panel_modelo_eleccion.csv').drop(columns=['aprobacion_oficial_completa','aprobacion_fuente_completa'],errors='ignore')
b=E[E.aprob_ead_ult.notna()&E.lb_aprob.notna()]
a1,a0=np.polyfit(b.lb_aprob,b.aprob_ead_ult,1)
print('calibración EAD = %.2f + %.3f*LB  (n=%d, r=%.2f)'%(a0,a1,len(b),b[['aprob_ead_ult','lb_aprob']].corr().iloc[0,1]))
WEB={'UY-2019-PRES-1':(37.0,'web_Equipos_sep2019'),'UY-2019-PRES-2':(37.0,'web_Equipos_sep2019'),'EC-2025-PRES-1':(51.0,'web_Cedatos_ago2024_ultimo_nacional'),'EC-2025-PRES-2':(51.0,'web_Cedatos_ago2024_ultimo_nacional'),'BO-2025-PRES-1':(19.5,'web_CB_Consultora_jul2025_imagen_positiva'),'EC-2021-PRES-1':(9.3,'web_Cedatos_salida_may2021'),'PY-2023-PRES-1':(12.0,'web_ranking_Datoworld_feb2023_fuente_debil'),'MX-2024-PRES-1':(60.0,'web_ElFinanciero_may2024'),'CR-2022-PRES-1':(18.0,'web_CIEP-UCR_2022_aprox_fuente_secundaria'),'CR-2026-PRES-1':(58.0,'web_CIEP-UCR_ene2026'),'PA-2024-PRES-1':(9.0,'web_GallupPanama_ene-feb2024')}
def f(r):
    if r.id_eleccion in WEB: return pd.Series(list(WEB[r.id_eleccion]))
    if pd.notna(r.aprobacion_oficial): return pd.Series([r.aprobacion_oficial,r.aprobacion_fuente])
    if pd.notna(r.lb_aprob) and r.lb_rezago_anios<=3: return pd.Series([round(a0+a1*r.lb_aprob,1),'LB_calibrada_rezago%d'%r.lb_rezago_anios])
    return pd.Series([np.nan,'sin_dato'])
E[['aprobacion_oficial_completa','aprobacion_fuente_completa']]=E.apply(f,axis=1)
E.to_csv(F+'panel_modelo_eleccion.csv',index=False)
R=pd.read_csv(F+'panel_modelo_region.csv').drop(columns=['aprobacion_oficial_completa','aprobacion_fuente_completa'],errors='ignore')
R=R.merge(E[['id_eleccion','aprobacion_oficial_completa','aprobacion_fuente_completa']],on='id_eleccion',how='left'); R.to_csv(F+'panel_modelo_region.csv',index=False)
print(E.aprobacion_fuente_completa.value_counts()); print(E[E.aprobacion_fuente_completa.str.startswith('LB')][['id_eleccion','lb_aprob','aprobacion_oficial_completa']])
print(E[E.aprobacion_oficial_completa.isna()].id_eleccion.tolist())
