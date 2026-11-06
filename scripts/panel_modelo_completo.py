"""Arma final/panel_modelo_completo.csv: núcleo de predictores sin faltantes.
Reglas: (1) bm_inflacion_ipc_tm1 faltante (AR 2007-15, INDEC) <- inflacion_12m_previa; (2) resto: mediana del país (ventana: otras elecciones del mismo país), si no hay, mediana global.
Cada variable imputada tiene un indicador <var>_imp (1 = imputada). No se incluyen cc_* (confianza del consumidor) ni las series trimestrales EAD por cobertura incompleta."""
import pandas as pd, numpy as np
F='final/'
P=pd.read_csv(F+'panel_modelo_eleccion.csv')
ID=['id_eleccion','pais','anio','vuelta','fecha','ampliacion','y_share_nacional','oficialismo_dudoso']
X=['oficialismo_va_por_reeleccion','ideologia_of','aprobacion_oficial_completa','percep_econ_lb',
   'bm_crecimiento_pib_tm1','bm_inflacion_ipc_tm1','bm_desempleo_oit_tm1','inflacion_12m_previa',
   'us_current_account_tm1','us_fiscal_primario_tm1','us_gdp_real_crec_tm1','us_ner_var_tm1','us_cuenta_corriente_wb_tm1',
   'enc','n_cand_5pct','hhi_top1','n_fuertes_cercanos','share_fuertes_cercanos','of_tradicional','pre2000','anio_c',
   'pobnac_685_tm1','pobnac_365_tm1','d_pobnac_685_mandato','d_pobnac_365_mandato','anios_mandato','of_top2_eleccion_previa','of_n_top2_previas']
D=P[ID+X].copy()
m=D.bm_inflacion_ipc_tm1.isna(); D.loc[m,'bm_inflacion_ipc_tm1']=D.loc[m,'inflacion_12m_previa']
for c in X:
    na=D[c].isna()
    if c=='bm_inflacion_ipc_tm1': na=P.bm_inflacion_ipc_tm1.isna()
    D[c+'_imp']=na.astype(int)
    if D[c].isna().any():
        med_p=D.groupby('pais')[c].transform('median'); D[c]=D[c].fillna(med_p).fillna(D[c].median())
imp=[c for c in D.columns if c.endswith('_imp')]
D=D.drop(columns=[c for c in imp if D[c].sum()==0])
D.to_csv(F+'panel_modelo_completo.csv',index=False)
print(D.shape, D.isna().sum().sum(), 'celdas faltantes')
print(D[[c for c in D.columns if c.endswith('_imp')]].sum().to_string())
