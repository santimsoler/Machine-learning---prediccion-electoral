import pandas as pd, numpy as np
F='final/'
# Gasto real promedio per capita mensual 2019 (soles constantes 2019, precios de Lima Metropolitana). INEI, Evolucion de la pobreza monetaria 2008-2019, cuadro I.1 (pag. 95). Nacional 2019 = 785; 2018 = 776
g19={'LIMA':942,'CALLAO':820,'TACNA':837,'LA LIBERTAD':786,'MOQUEGUA':949,'TUMBES':798,'ICA':914,'LAMBAYEQUE':902,'PIURA':715,'AREQUIPA':928,'ANCASH':736,'JUNIN':715,'CUSCO':676,'PUNO':571,'PASCO':540,'HUANUCO':614,'CAJAMARCA':562,'APURIMAC':568,'AYACUCHO':552,'HUANCAVELICA':480,'MADRE DE DIOS':804,'UCAYALI':619,'SAN MARTIN':657,'LORETO':546,'AMAZONAS':577}
g18={'LIMA':945,'CALLAO':812,'TACNA':839,'LA LIBERTAD':781,'MOQUEGUA':947,'TUMBES':810,'ICA':882,'LAMBAYEQUE':856,'PIURA':704,'AREQUIPA':895,'ANCASH':677,'JUNIN':709,'CUSCO':693,'PUNO':559,'PASCO':542,'HUANUCO':610,'CAJAMARCA':521,'APURIMAC':514,'AYACUCHO':549,'HUANCAVELICA':459,'MADRE DE DIOS':833,'UCAYALI':628,'SAN MARTIN':664,'LORETO':551,'AMAZONAS':561}
# Grupos de pobreza monetaria estadisticamente semejantes (INEI): 1 = mayor pobreza. Rango (%) del grupo.
G19={1:(34.4,39.4,['AYACUCHO','CAJAMARCA','HUANCAVELICA','PUNO']),2:(28.3,32.7,['AMAZONAS','APURIMAC','HUANUCO','LORETO','PASCO']),
     3:(21.9,25.3,['CUSCO','JUNIN','LA LIBERTAD','PIURA','SAN MARTIN']),
     4:(12.0,14.6,['ANCASH','AREQUIPA','LAMBAYEQUE','MADRE DE DIOS','MOQUEGUA','CALLAO','LIMA','TACNA','TUMBES','UCAYALI']),5:(1.3,3.9,['ICA'])}
G20={1:(41.4,45.9,['AYACUCHO','CAJAMARCA','HUANCAVELICA','HUANUCO','PASCO','PUNO']),
     2:(31.3,34.6,['AMAZONAS','ANCASH','APURIMAC','CUSCO','JUNIN','LA LIBERTAD','LORETO','PIURA','CALLAO','TUMBES']),
     3:(23.9,28.6,['LIMA','SAN MARTIN','TACNA','UCAYALI']),4:(15.1,19.5,['AREQUIPA','LAMBAYEQUE','MOQUEGUA']),5:(6.6,11.3,['ICA','MADRE DE DIOS'])}
rows=[]
for d in g19:
    r={'dpto':d,'gasto_real_pc_2019':g19[d],'gasto_real_pc_2018':g18[d],'gasto_rel_nacional_2019':g19[d]/785,'gasto_rel_nacional_2018':g18[d]/776}
    for tag,G in (('2019',G19),('2020',G20)):
        for k,(lo,hi,l) in G.items():
            if d in l: r[f'pobreza_grupo_{tag}']=k; r[f'pobreza_rango_min_{tag}']=lo; r[f'pobreza_rango_max_{tag}']=hi; r[f'pobreza_rango_medio_{tag}']=(lo+hi)/2
    rows.append(r)
t=pd.DataFrame(rows)
t['gasto_rel_pctrank_2019']=t.gasto_real_pc_2019.rank(pct=True)
t['fuente']='INEI, Evolucion de la pobreza monetaria 2008-2019 (cuadro I.1; grupos 2019); INEI NP 067-2021 (grupos 2020). Lima = departamento Lima (Provincia + Region)'
t.to_csv(F+'pobreza_peru_departamentos_inei.csv',index=False)
p=pd.read_csv(F+'panel_modelo_region.csv')
p=p.drop(columns=[c for c in p.columns if c.startswith('pe_')],errors='ignore')
q=t.drop(columns='fuente').rename(columns={'dpto':'_k'}); q.columns=['_k']+['pe_'+c for c in q.columns[1:]]
p['_k']=p.region.str.upper().str.strip()
p=p.merge(q,on='_k',how='left')
m=~((p.pais=='PE'))
for c in q.columns[1:]: p.loc[m,c]=np.nan
p=p.drop(columns='_k'); p.to_csv(F+'panel_modelo_region.csv',index=False)
c=p[p.pais=='PE'];print(c.groupby('anio').pe_gasto_rel_nacional_2019.count(),c[c.pe_gasto_rel_nacional_2019.isna()].region.tolist(),p.shape)
print(c[['region','y_share_oficialismo','pe_gasto_rel_nacional_2019','pe_pobreza_grupo_2019']].corr(numeric_only=True).round(2))
