import pandas as pd, unicodedata, re
A='/mnt/user-data/attachments/fbc2a8cf-9f07-5c94-8ce1-557ba4094ca9/'
def nrm(t): return re.sub(r'[^a-z ]','',unicodedata.normalize('NFKD',str(t)).encode('ascii','ignore').decode().lower())
c=pd.read_csv('final/candidatos.csv'); c['share']=pd.to_numeric(c.share_nacional_pct,errors='coerce'); c['k']=c.candidato_o_formula.map(nrm)
m=pd.read_csv(A+'219a3d6b-MPDataset_MPDS2026a.csv',low_memory=False).copy()
m=m[(m.countryname=='Peru')&m.presvote.notna()]; m['anio']=pd.to_datetime(m.edate,dayfirst=True).dt.year; m['econ_mf']=m.markeco-m.planeco; m['k']=m.candidatename.map(nrm)
vp=pd.read_csv('final/vparty_6paises_v2.csv'); vp=vp[vp.pais=='PE']; vp['socio_vp']=-(vp.v2palgbt+vp.v2parelig)/2
ch=pd.read_csv(A+'f1c2292b-ches_la_2020_aggregate_level_v01.csv',encoding='latin-1').set_index(['country_abb','party_abb'])
MV='manifesto_vparty_juicio'; CG='conocimiento_general_verificar'
# anio, clave_cand, clave_mf, texto en v2paenname, partido CHES, e, s, nivel, nota
R=[
(2006,'ollanta','humala','Union for Peru','UPP',-2,1,MV,'nacionalista radical (renegociar contratos, nacionalizar); Manifesto econ -3,9 (el más bajo del año); V-Party UPP e -1,20. s por conocimiento general (etnocacerismo).'),
(2006,'garcia','garcia','Aprista','APRA',1,1,MV,'giro promercado respecto a los 80; V-Party APRA e +1,82; CHES APRA 2020 s +1,0.'),
(2006,'flores','flores','National Unity','PPC',1,1,MV,'PPC liberal-conservadora; V-Party UN e +1,68; CHES PPC 2020 e +1,16 / s +1,32.'),
(2006,'chavez','chavez','Alliance for the Future','FP',1,2,MV,'fujimorismo; V-Party AF e +1,58; s por CHES FP (+1,6).'),
(2006,'paniagua','paniagua','Center Front',None,0,0,MV,'centro; V-Party FDC e +0,60 / s +0,10.'),
(2006,'lay',None,None,None,None,2,CG,'Restauración Nacional (evangélico); económico NA.'),
(2011,'humala','humala','Peruvian Nationalist',None,-1,0,MV,'moderó la "Gran Transformación" a la "Hoja de ruta"; Manifesto econ -3,8; V-Party PNP e -0,95.'),
(2011,'fujimori','fujimori','Popular Force 2011','FP',1,2,MV,'V-Party FP e +2,03 / s +1,52; se mantiene +1 económico como en 2016 y 2021 (CHES FP e +1,12).'),
(2011,'kuczynski','kuczynski','Gran Cambio',None,1,0,MV,'tecnócrata promercado; V-Party Alianza por el Gran Cambio e +0,73; s por conocimiento general (liberal moderado).'),
(2011,'toledo','toledo','Posible',None,1,0,MV,'ex presidente promercado; V-Party Alianza Perú Posible e +1,26.'),
(2011,'castaneda','castaneda','Solidarity',None,1,0,MV,'Solidaridad Nacional; V-Party SN e +0,90.'),
(2016,'fujimori','fujimori','Popular Force',None,1,2,MV,'V-Party FP e +2,02 / s +1,62; CHES FP 2021 e +1,12 / s +1,6.'),
(2016,'kuczynski','kuczynski','Peruvians for Change',None,1,0,MV,'V-Party PPK e +1,42 / s -0,80; Manifesto econ -0,5. s 0 por juicio (liberal moderado, no progresista).'),
(2016,'mendoza','mendoza','Broad Front','FA',-2,-1,MV,'Frente Amplio; V-Party e -1,95 / s -1,71. En 2021 (Juntos por el Perú, CHES) queda en -1: discrepancia de fuente entre partidos.'),
(2016,'barnechea','barnechea','Popular Action','AP',0,0,MV,'Acción Popular; V-Party AP e +0,48; CHES AP 2020 s +0,69.'),
(2016,'garcia','garcia','Popular Alliance','APRA',1,1,MV,'Alianza Popular (APRA-PPC); V-Party e +0,93; CHES APRA s +1,0.'),
(2016,'santos',None,None,None,-2,None,CG,'Gregorio Santos (Democracia Directa), izquierda regional; sociocultural NA.'),
]
rows=[]
for an,k,mk,vpk,chp,e,s,niv,nota in R:
    g=c[(c.pais=='PE')&(c.anio==an)&(c.vuelta==1)&c.k.str.contains(k)]
    mm=m[(m.anio==an)&m.k.str.contains(mk)] if mk else m.iloc[0:0]
    v=vp[(vp.year==an)&(vp.v2paenname.fillna('')+' '+vp.v2paorname.fillna('')+' '+vp.v2pashname.fillna('')).str.contains(vpk,case=False,regex=False)] if vpk else vp.iloc[0:0]
    v=v[v.v2pariglef.notna()]
    vv=v.iloc[0] if len(v) else None
    chk=('PE',chp) in ch.index if chp else False
    rows.append(dict(id_eleccion=f'PE-{an}-PRES-1',pais='PE',anio=an,candidato=g.candidato_o_formula.iloc[0] if len(g) else k,
      share_pct=round(g.share.sum(),2) if len(g) else None,eje_economico=e,eje_sociocultural=s,
      mf_rile=round(mm.rile.iloc[0],1) if len(mm) and pd.notna(mm.rile.iloc[0]) else None,
      mf_econ_markeco_menos_planeco=round(mm.econ_mf.iloc[0],1) if len(mm) and pd.notna(mm.econ_mf.iloc[0]) else None,
      vp_econ=round(vv.v2pariglef,2) if vv is not None else None,vp_socio_idx=round(vv.socio_vp,2) if vv is not None else None,
      ches_econ_cont=round((ch.loc[('PE',chp)].lrecon-5)/2.5,2) if chk else None,ches_socio_cont=round((ch.loc[('PE',chp)].galtan-5)/2.5,2) if chk else None,
      nivel_evidencia=niv,fuente='Manifesto MPDS2026a + V-Party v2 + CHES-LA 2020/21 (cuando existe) + juicio del analista',notas=nota,codificador='claude_v1'))
d=pd.DataFrame(rows); d.to_csv('final/ideologia_peru.csv',index=False)
pd.set_option('display.width',250)
print(d[['id_eleccion','candidato','share_pct','eje_economico','eje_sociocultural','vp_econ','mf_econ_markeco_menos_planeco','nivel_evidencia']].to_string(index=False))
for e,gg in d.groupby('id_eleccion'): print(e,'econ',round(gg.share_pct[gg.eje_economico.notna()].sum(),1),'socio',round(gg.share_pct[gg.eje_sociocultural.notna()].sum(),1))
