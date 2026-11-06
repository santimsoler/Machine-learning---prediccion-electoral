import pandas as pd, numpy as np
A='/mnt/user-data/attachments/fbc2a8cf-9f07-5c94-8ce1-557ba4094ca9/'
f='final/'
cl=lambda x,a=-2,b=2: None if pd.isna(x) else float(max(a,min(b,x)))
rows=[]
for fn in ['ideologia_brasil','ideologia_chile_colombia','ideologia_peru','ideologia_uruguay','ideologia_recientes']:
    d=pd.read_csv(f+fn+'.csv')
    for c in ['mf_econ_markeco_menos_planeco','vp_econ','vp_socio_idx','ches_econ_cont','ches_socio_cont']:
        if c not in d: d[c]=np.nan
    d['_src']=fn; rows.append(d[['id_eleccion','pais','anio','candidato','share_pct','eje_economico','eje_sociocultural','mf_econ_markeco_menos_planeco','vp_econ','vp_socio_idx','ches_econ_cont','ches_socio_cont','nivel_evidencia','notas','_src']])
# Argentina
ag=pd.read_csv(f+'candidatos_ar_agrupado.csv'); ag=ag[ag.vuelta==1].copy()
ch=pd.read_csv(A+'f1c2292b-ches_la_2020_aggregate_level_v01.csv',encoding='latin-1').set_index(['country_abb','party_abb'])
chmap={('AR-2019','alberto fernandez'):'FT',('AR-2019','mauricio macri'):'JC',('AR-2019','roberto lavagna'):'CF',('AR-2019','nicolas del cano'):'FI'}
ar=pd.DataFrame(dict(id_eleccion=ag.id_eleccion,pais='AR',anio=ag.anio,candidato=ag.formula.fillna(ag.clave),share_pct=ag.share,
  eje_economico=ag.eje_economico_propio,eje_sociocultural=ag.eje_sociocultural_propio,
  mf_econ_markeco_menos_planeco=ag.mf_markeco-ag.mf_planeco,vp_econ=np.nan,vp_socio_idx=np.nan,nivel_evidencia=ag.nivel_evidencia_econ,notas='',_src='candidatos_ar_agrupado'))
ar['ches_socio_cont']=[ (ch.loc[('AR',chmap[(i[:7],k)])].galtan-5)/2.5 if (i[:7],k) in chmap else np.nan for i,k in zip(ag.id_eleccion,ag.clave)]
ar['ches_econ_cont']=[ (ch.loc[('AR',chmap[(i[:7],k)])].lrecon-5)/2.5 if (i[:7],k) in chmap else np.nan for i,k in zip(ag.id_eleccion,ag.clave)]
ar=ar[ar.share_pct>=2.5]
D=pd.concat(rows+[ar],ignore_index=True)
# V-Party 2019 de Uruguay como segunda fuente (partido), valores de vparty_6paises_v2.csv
vpu=pd.read_csv(f+'vparty_6paises_v2.csv'); vpu=vpu[(vpu.pais=='UY')&(vpu.year==2019)]
vpu=vpu.assign(socio=-(vpu.v2palgbt+vpu.v2parelig)/2)
pm={'Martínez':'Broad Front','Lacalle':'National Party','Talvi':'Colorado','Manini':'Open Cabildo'}
for k,pn in pm.items():
    r0=vpu[vpu.v2paenname.str.contains(pn)].iloc[0]
    msk=(D.id_eleccion=='UY-2019-PRES-1')&D.candidato.str.contains(k)
    D.loc[msk,'vp_econ']=r0.v2pariglef; D.loc[msk,'vp_socio_idx']=r0.socio
D=D.rename(columns={'eje_economico':'e_ord','eje_sociocultural':'s_ord'})
out=[]
for r in D.itertuples():
    base_ches=(r.nivel_evidencia=='ches_la_partido')
    def build(ordv,vp,ches,mf,vp_scale,anio):
        src={}
        if base_ches:
            if pd.notna(ches): src['ches']=(cl(ches),1.0)
            if pd.notna(vp): src['vparty']=(cl(vp/vp_scale),1.0)
        else:
            if pd.notna(ordv): src['juicio']=(float(ordv),1.0)
            if pd.notna(vp): src['vparty']=(cl(vp/vp_scale),1.0)
            if pd.notna(ches) and anio>=2018: src['ches']=(cl(ches),1.0)
            if mf is not None and pd.notna(mf) and r.pais!='CO': src['manifesto']=(cl(mf/6.0),0.5)
        if not src: return (np.nan,0,np.nan,'')
        w=np.array([v[1] for v in src.values()]); x=np.array([v[0] for v in src.values()])
        mean=float((w*x).sum()/w.sum()); disp=float(x.max()-x.min()) if len(x)>1 else np.nan
        return (round(mean,2),len(src),round(disp,2) if len(x)>1 else np.nan,'+'.join(src))
    e=build(r.e_ord,r.vp_econ,r.ches_econ_cont,r.mf_econ_markeco_menos_planeco,1.35,r.anio)
    s=build(r.s_ord,r.vp_socio_idx,r.ches_socio_cont,None,1.5,r.anio)
    out.append(dict(id_eleccion=r.id_eleccion,pais=r.pais,anio=r.anio,candidato=r.candidato,share_pct=r.share_pct,
      e_cont=e[0],e_ord=r.e_ord,e_n_fuentes=e[1],e_rango_entre_fuentes=e[2],e_fuentes=e[3],
      s_cont=s[0],s_ord=r.s_ord,s_n_fuentes=s[1],s_rango_entre_fuentes=s[2],s_fuentes=s[3],
      nivel_evidencia=r.nivel_evidencia,notas=r.notas))
O=pd.DataFrame(out).sort_values(['pais','anio','share_pct'],ascending=[True,True,False])
O.to_csv(f+'ideologia_candidatos_continua.csv',index=False)
pd.set_option('display.width',220)
print(len(O),'filas;', O.e_cont.notna().sum(),'con e_cont;',O.s_cont.notna().sum(),'con s_cont')
print(O.groupby('e_n_fuentes').size().to_dict())
print('corr e',O[['e_cont','e_ord']].corr().iloc[0,1].round(3),'corr s',O[['s_cont','s_ord']].corr().iloc[0,1].round(3))
print('valores distintos e_cont:',O.e_cont.nunique(),'vs e_ord:',O.e_ord.nunique())
sel=O[O.candidato.str.contains('FUJIMORI|MATTHEI|KAST|BORIC|LULA|BOLSONARO|MILEI|ESPRIELLA|CEPEDA|ORSI|LACALLE|Fujimori|Matthei|Lula|Kast|Sánchez|MILEI|Bullrich|PETRO',regex=True)&(O.anio>=2017)]
print(sel[['id_eleccion','candidato','e_ord','e_cont','e_fuentes','s_ord','s_cont','s_fuentes']].to_string(index=False))
