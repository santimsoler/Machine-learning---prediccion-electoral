import pandas as pd,numpy as np
F='final/'
r=pd.read_csv(F+'resultados_region.csv'); e=pd.read_csv(F+'elecciones.csv',dtype=str)
c=pd.read_csv(F+'candidatos_unificado.csv'); ead=pd.read_csv(F+'aprobacion_presidencial_ead.csv',parse_dates=['trimestre_inicio'])
p19=pd.read_csv(F+'aprobacion_presidencial_post2019.csv'); lb=pd.read_csv(F+'aprobacion_gobierno_latinobarometro.csv')
cc=pd.read_csv(F+'confianza_consumidor_mensual.csv'); bm=pd.read_csv(F+'macro_anual_bm.csv'); us=pd.read_csv(F+'macro_anual_usuario_base_final.csv')
# ---------- target ----------
r['votos']=pd.to_numeric(r.votos,errors='coerce')
g=r.groupby(['id_eleccion','pais','anio','region_nivel1'])
t=g.apply(lambda d:pd.Series({
  'votos_validos':d.votos_validos_region.iloc[0],
  'votos_oficialismo':d.loc[d.es_oficialismo==1,'votos'].sum(),
  'max_otro':d.loc[d.es_oficialismo!=1,'votos'].max(),
  'hay_oficialismo':int((d.es_oficialismo==1).any())}),include_groups=False).reset_index()
t=t[t.hay_oficialismo==1].copy()
t['y_share_oficialismo']=100*t.votos_oficialismo/t.votos_validos
t['y_gana_region']=(t.votos_oficialismo>t.max_otro).astype(int)
nat=t.groupby('id_eleccion').apply(lambda d:100*d.votos_oficialismo.sum()/d.votos_validos.sum(),include_groups=False).rename('y_share_nacional')
t=t.merge(nat,on='id_eleccion'); t['y_desvio_regional']=t.y_share_oficialismo-t.y_share_nacional
t=t.merge(e[['id_eleccion','vuelta','fecha','presidente_en_ejercicio','oficialismo_va_por_reeleccion','estado_codificacion']],on='id_eleccion')
t['fecha']=pd.to_datetime(t.fecha); t['vuelta']=t.vuelta.astype(int)
t['oficialismo_va_por_reeleccion']=pd.to_numeric(t.oficialismo_va_por_reeleccion)
t['oficialismo_dudoso']=t.estado_codificacion.str.startswith('dudoso').astype(int)
# ---------- ideología del candidato oficialista ----------
co=c[c.es_oficialismo==1].groupby('id_eleccion').agg(ideologia_of=('e_cont','mean'),ideologia_of_n=('e_cont','count')).reset_index()
t=t.merge(co,on='id_eleccion',how='left')
# ---------- aprobación EAD (hasta 2019) ----------
def ead_feat(pais,fecha):
    d=ead[(ead.pais==pais)&(ead.trimestre_inicio<=fecha)].sort_values('trimestre_inicio')
    if d.empty: return pd.Series({'aprob_ead_ult':np.nan,'aprob_ead_media4':np.nan,'aprob_ead_gap_dias':np.nan,'inflacion_trim_ead':np.nan,'crec_trim_ead':np.nan})
    last=d.iloc[-1]; gap=(fecha-last.trimestre_inicio).days
    if gap>250: return pd.Series({'aprob_ead_ult':np.nan,'aprob_ead_media4':np.nan,'aprob_ead_gap_dias':gap,'inflacion_trim_ead':np.nan,'crec_trim_ead':np.nan})
    return pd.Series({'aprob_ead_ult':last.aprobacion_suavizada_pct,'aprob_ead_media4':d.tail(4).aprobacion_suavizada_pct.mean(),'aprob_ead_gap_dias':gap,'inflacion_trim_ead':d.tail(4).inflacion_trimestral.mean(),'crec_trim_ead':d.tail(4).crecimiento_trimestral.mean()})
el=t[['id_eleccion','pais','fecha']].drop_duplicates()
el=pd.concat([el.reset_index(drop=True),el.apply(lambda x:ead_feat(x.pais,x.fecha),axis=1).reset_index(drop=True)],axis=1)
# ---------- aprobación puntual 2019+ ----------
p19['base']=p19.id_eleccion
el['base']=el.id_eleccion.str[:7]
el=el.merge(p19[['base','encuestadora','aprobacion_pct','desaprobacion_pct','dias_a_primera_vuelta']].rename(columns={'encuestadora':'aprob_p19_encuestadora','aprobacion_pct':'aprob_p19','desaprobacion_pct':'desaprob_p19','dias_a_primera_vuelta':'aprob_p19_dias'}),on='base',how='left')
el['aprobacion_oficial']=el.aprob_ead_ult.fillna(el.aprob_p19)
el['aprobacion_fuente']=np.where(el.aprob_ead_ult.notna(),'EAD',np.where(el.aprob_p19.notna(),'encuesta_puntual_2019+','sin_dato'))
# ---------- Latinobarómetro: ola más reciente de año < año de elección (diciembre: año actual) ----------
def lbf(pais,fecha):
    y=fecha.year if fecha.month==12 else fecha.year-1
    d=lb[(lb.pais==pais)&(lb.anio<=y)].sort_values('anio')
    if d.empty: return pd.Series({'lb_aprob':np.nan,'lb_anio':np.nan})
    return pd.Series({'lb_aprob':d.iloc[-1].aprueba_pct_sobre_respuestas,'lb_anio':d.iloc[-1].anio})
el=pd.concat([el,el.apply(lambda x:lbf(x.pais,x.fecha),axis=1)],axis=1)
el['lb_rezago_anios']=el.fecha.dt.year-el.lb_anio
# ---------- confianza del consumidor (valor medio 3 meses previos y cambio vs 12 meses antes) ----------
CCV={'AR':'icc_nacional','CL':'ipec','CO':'confianza_consumidor_ocde','BR':'confianza_consumidor_ocde'}
def ccf(pais,fecha):
    if pais not in CCV: return pd.Series({'cc_3m':np.nan,'cc_var12m':np.nan,'cc_z':np.nan})
    d=cc[(cc.pais==pais)&(cc.variable==CCV[pais])].copy(); d['per']=pd.PeriodIndex(d.periodo,freq='M'); d=d.set_index('per').valor
    p=pd.Period(fecha,'M')-1  # último mes completo previo
    w=d[(d.index<=p)&(d.index>p-3)]
    w12=d[(d.index<=p-12)&(d.index>p-15)]
    if len(w)<2: return pd.Series({'cc_3m':np.nan,'cc_var12m':np.nan,'cc_z':np.nan})
    hist=d[d.index<=p]; z=(w.mean()-hist.mean())/hist.std() if len(hist)>24 else np.nan
    return pd.Series({'cc_3m':w.mean(),'cc_var12m':(w.mean()-w12.mean()) if len(w12)>=2 else np.nan,'cc_z':z})
el=pd.concat([el,el.apply(lambda x:ccf(x.pais,x.fecha),axis=1)],axis=1)
# ---------- macro anual: año previo ----------
iso={'AR':'ARG','BR':'BRA','CL':'CHL','CO':'COL','PE':'PER','UY':'URY'}
bmw=bm.pivot_table(index=['pais','anio'],columns='variable',values='valor').reset_index()
uw=us.pivot_table(index=['pais','anio'],columns='variable',values='valor').reset_index()
print(sorted(set(us.pais))[:8], sorted(set(bm.pais))[:8])
def macro(pais,fecha):
    y=fecha.year-1 if fecha.month<12 else fecha.year
    out={}
    for col in ['crecimiento_pib','inflacion_ipc','desempleo_oit']:
        s=bmw[(bmw.pais==iso[pais])&(bmw.anio==y)]
        out['bm_'+col+'_tm1']=s[col].iloc[0] if len(s) and col in s else np.nan
    for col in ['current_account','fiscal_primario']:
        s=uw[(uw.pais.isin([pais,iso[pais]]))&(uw.anio==y)]
        out['us_'+col+'_tm1']=s[col].iloc[0] if len(s) else np.nan
    s0=uw[(uw.pais.isin([pais,iso[pais]]))&(uw.anio==y)]; s1=uw[(uw.pais.isin([pais,iso[pais]]))&(uw.anio==y-1)]
    out['us_gdp_real_crec_tm1']=(s0.gdp_real.iloc[0]/s1.gdp_real.iloc[0]-1)*100 if len(s0) and len(s1) else np.nan
    out['us_ner_var_tm1']=(s0.ner.iloc[0]/s1.ner.iloc[0]-1)*100 if len(s0) and len(s1) else np.nan
    return pd.Series(out)
el=pd.concat([el,el.apply(lambda x:macro(x.pais,x.fecha),axis=1)],axis=1)
arinf=pd.read_csv(F+'ar_inflacion_mensual_2003_2026.csv'); arinf['per']=pd.PeriodIndex(arinf.periodo,freq='M'); arinf=arinf.set_index('per').indice_base_nov2003_100
def inf(pais,fecha,bmv):
    if pais!='AR': return bmv
    p=pd.Period(fecha,'M')-1
    try: return (arinf[p]/arinf[p-12]-1)*100
    except KeyError: return np.nan
el['inflacion_12m_previa']=el.apply(lambda x:inf(x.pais,x.fecha,x.bm_inflacion_ipc_tm1),axis=1)
el['inflacion_fuente']=np.where(el.pais=='AR','serie empalmada del usuario (INDEC/IPC)','Banco Mundial WDI (año previo)')
keep=[c for c in el.columns if c not in('pais','fecha','base')]
panel=t.merge(el[keep],on='id_eleccion')
panel=panel.drop(columns=['votos_oficialismo','max_otro','hay_oficialismo']).rename(columns={'region_nivel1':'region'})
panel.to_csv(F+'panel_modelo_region.csv',index=False)
nat=panel.groupby('id_eleccion').first().reset_index()
nat.drop(columns=['region','votos_validos','y_share_oficialismo','y_gana_region','y_desvio_regional']).to_csv(F+'panel_modelo_eleccion.csv',index=False)
print(panel.shape, nat.shape)
print(nat[['id_eleccion','y_share_nacional','aprobacion_oficial','aprobacion_fuente','lb_aprob','lb_rezago_anios','cc_3m','bm_crecimiento_pib_tm1','bm_inflacion_ipc_tm1','us_gdp_real_crec_tm1','ideologia_of']].round(1).to_string())
