import pandas as pd, numpy as np, unicodedata
F='final/'
def norm(s): return ''.join(c for c in unicodedata.normalize('NFD',str(s).upper()) if unicodedata.category(c)!='Mn').strip()
p=pd.read_csv(F+'panel_modelo_region.csv')
# 1) pobreza relativa regional armonizada: percentil de la region dentro de su pais en cada eleccion-vuelta (1 = mas pobre)
def medida(r):
    k=r.pais
    if k=='AR': return r.eph_pobreza_rel60
    if k=='BR': return r.pnad_pobreza_rel60 if pd.notna(r.pnad_pobreza_rel60) else r.pnadc_tx_pobreza_nac
    if k=='CL': return r.pobreza_casen
    if k=='CO': return r.co_nbi
    if k=='PE': return -r.pe_gasto_rel_nacional_2019
    if k=='UY': return r.uy_nbi_ech_sc
p['pobrel_medida']=p.apply(medida,axis=1)
p['pobrel_pctrank']=p.groupby('id_eleccion').pobrel_medida.rank(pct=True)
p.loc[p.pobrel_medida.isna(),'pobrel_pctrank']=np.nan
# 2) voto a la izquierda por region (ideologia economica e_cont < -0.5) e ideologia media del voto
i=pd.read_csv(F+'ideologia_candidatos_continua.csv'); i['k']=i.candidato.map(norm); i['ey']=i.id_eleccion.str[:7]
r=pd.read_csv(F+'resultados_region.csv'); r['k']=r.opcion.map(lambda x: norm(str(x).split('|')[-1])); r['ey']=r.id_eleccion.str[:7]
m=r.merge(i[['ey','k','e_cont']].drop_duplicates(['ey','k']),on=['ey','k'],how='left')
# respaldo: emparejar por participacion nacional (opciones que son partidos/alianzas, ej. AR, UY, PE)
for e in m.id_eleccion.unique():
    s_=m[m.id_eleccion==e]
    vv=s_.votos.sum()
    if s_.loc[s_.e_cont.notna(),'votos'].sum()/vv>=0.8: continue
    ie=i[i.id_eleccion==e.replace('-PRES-2','-PRES-1')].sort_values('share_pct',ascending=False)
    o=s_.groupby('opcion').votos.sum().sort_values(ascending=False); o=100*o/o.sum()
    mp={}
    for (_,c) in ie.iterrows():
        d=(o-c.share_pct).abs()
        d=d[~d.index.isin(mp)]
        if len(d) and d.min()<=1.0: mp[d.idxmin()]=c.e_cont
    idx=m.id_eleccion==e
    m.loc[idx,'e_cont']=m.loc[idx,'opcion'].map(mp)
m['izq']=np.where(m.e_cont<-0.5,m.votos,0)
m['ide_w']=m.e_cont*m.votos
m['v_con']=np.where(m.e_cont.notna(),m.votos,0)
g=m.groupby(['id_eleccion','region_nivel1']).agg(izq=('izq','sum'),ide_w=('ide_w','sum'),v_con=('v_con','sum'),vv=('votos','sum')).reset_index()
g['cobertura_ideo']=g.v_con/g.vv
g['y_share_izquierda']=100*g.izq/g.vv
g['ideologia_voto_media']=g.ide_w/g.v_con
g.loc[g.cobertura_ideo<0.8,['y_share_izquierda','ideologia_voto_media']]=np.nan
g=g.rename(columns={'region_nivel1':'region'})[['id_eleccion','region','y_share_izquierda','ideologia_voto_media','cobertura_ideo']]
p=p.drop(columns=[c for c in g.columns if c in p and c not in('id_eleccion','region')]).merge(g,on=['id_eleccion','region'],how='left')
p.to_csv(F+'panel_modelo_region.csv',index=False)
print(p.groupby('pais')[['pobrel_pctrank','y_share_izquierda','ideologia_voto_media']].agg(lambda s:s.notna().mean()).round(2))
