import pandas as pd,unicodedata,re
nz=lambda s:''.join(c for c in unicodedata.normalize('NFD',str(s).upper()) if unicodedata.category(c)!='Mn')
tok=lambda s:{t for t in re.findall(r'[A-Z]+',nz(s)) if len(t)>2 and t not in('DEL','LOS','LAS','PARTIDO','FRENTE')}
# 1) oficialismo verificado (2-nov-2026)
OV={
'CL-1989':('dudoso_regimen_militar_Buchi_candidato_derecha_pro_regimen_no_verificado_con_fuente','—'),
'CL-2021':('verificado_apoyo_explicito_Pinera_24horas_2021-08-10_y_RN_Evopoli_PRI_Emol_2021-10-26',''),
'CL-2025':('verificado_apoyo_explicito_Boric_a_Jara_BioBio_y_TheClinic_2025-07-04',''),
'PE-2021':('dudoso_candidato_del_partido_del_presidente_Guzman_se_desmarca_sensibilidad_recomendada',''),
'PE-2026':('sin_oficialista_identificado_Balcazar_Peru_Libre_interino_desde_2026-02-18_sin_endoso_hallado',''),
}
for g in ['CL-1993','CL-1999','CL-2005','CL-2009','CL-2013','CL-2017']:
    OV[g]=('coalicion_gobernante_confirmada_por_usuario_2026-11-02_sin_cita_por_eleccion','')
e=pd.read_csv('final/elecciones.csv',keep_default_na=False,dtype=str)
for k,(est,_) in OV.items():
    m=e.id_eleccion.str.startswith(k); e.loc[m,'estado_codificacion']=est
m=e.id_eleccion.str.startswith('PE-2026')
e.loc[m,['presidente_en_ejercicio','partido_oficialismo','palabras_clave_opcion_oficialista','oficialismo_va_por_reeleccion']]=['Balcázar (interino, Perú Libre)','Perú Libre','','0']
e.to_csv('final/elecciones.csv',index=False)
# 2) unificada
c=pd.read_csv('final/candidatos.csv');c.loc[(c.id_eleccion=='UY-2024-PRES-2')&(c.candidato_o_formula=='DelgadoRipoll'),'candidato_o_formula']='Álvaro Delgado';c.loc[(c.id_eleccion=='UY-2024-PRES-2')&(c.candidato_o_formula=='OrsiCosse'),'candidato_o_formula']='Yamandú Orsi';k=pd.read_csv('final/ideologia_candidatos_continua.csv')
k['t']=k.candidato.map(tok)
cols=['e_cont','e_ord','e_n_fuentes','e_fuentes','s_cont','s_ord','s_n_fuentes','s_fuentes','nivel_evidencia']
out=[]
for i,r in c.iterrows():
    cand=k[(k.pais==r.pais)&(k.anio==r.anio)]
    t=tok(str(r.candidato_o_formula)+' '+str(r.partido_o_coalicion)); best=None;bs=0
    if t:
        for j,q in cand.iterrows():
            if not q.t: continue
            s=len(t&q.t)/min(len(t),len(q.t))
            if s>bs: bs,best=s,q
    d={x:(best[x] if best is not None and bs>=0.5 else None) for x in cols}
    d['match_score']=round(bs,2) if best is not None and bs>=0.5 else None
    out.append(d)
u=pd.concat([c.drop(columns=['eje_economico','eje_sociocultural','fuente_ideologia','version_codebook']),pd.DataFrame(out)],axis=1)
u.to_csv('final/candidatos_unificado.csv',index=False)
cov=u.assign(ok=u.e_cont.notna()*u.share_nacional_pct).groupby(['pais','anio','vuelta']).apply(lambda g:g.ok.sum()).reset_index(name='cob')
print(u.groupby('pais').apply(lambda g:(g.e_cont.notna()*g.share_nacional_pct).sum()/g.share_nacional_pct.sum()))
print(cov[cov.cob<80].to_string())
