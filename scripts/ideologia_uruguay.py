import pandas as pd, unicodedata, re
A='/mnt/user-data/attachments/fbc2a8cf-9f07-5c94-8ce1-557ba4094ca9/'
def nrm(t): return re.sub(r'[^a-z ]','',unicodedata.normalize('NFKD',str(t)).encode('ascii','ignore').decode().lower())
c=pd.read_csv('final/candidatos.csv'); c['share']=pd.to_numeric(c.share_nacional_pct,errors='coerce'); c['k']=c.candidato_o_formula.map(nrm)
m=pd.read_csv(A+'219a3d6b-MPDataset_MPDS2026a.csv',low_memory=False).copy()
m=m[(m.countryname=='Uruguay')&m.presvote.notna()]; m['econ_mf']=m.markeco-m.planeco; m['k']=m.candidatename.map(nrm)
vp=pd.read_csv('final/vparty_6paises_v2.csv'); vp=vp[vp.pais=='UY']; vp['socio_vp']=-(vp.v2palgbt+vp.v2parelig)/2
MV='manifesto_vparty_juicio'
R=[(2014,'vazquez','vazquez','Broad Front',-1,-1,MV,'Frente Amplio; V-Party e -1,33 / s -2,67; Manifesto econ -6,5. s -1 y no -2: como presidente vetó la despenalización del aborto en 2008 (conocimiento general).'),
(2014,'lacalle','lacalle','National Party',1,0,MV,'Partido Nacional; V-Party e +1,27 / s -0,60; Manifesto econ +2,2.'),
(2014,'bordaberry','bordaberry','Colorado',1,0,MV,'Partido Colorado; V-Party e +1,27 / s -1,51 (batllismo más laico); Manifesto econ -1,0. s 0 por juicio.'),
(2014,'mieres','mieres',None,0,0,MV,'Partido Independiente, centro socialdemócrata liberal; Manifesto econ +1,5; CHES PI 2020 e +0,2 / s -0,1.')]
rows=[]
for an,k,mk,vpk,e,s,niv,nota in R:
    g=c[(c.pais=='UY')&(c.anio==an)&(c.vuelta==1)&c.k.str.contains(k)]
    mm=m[m.k.str.contains(mk)]
    v=vp[(vp.year==an)&vp.v2paenname.str.contains(vpk,case=False,regex=False)] if vpk else vp.iloc[0:0]
    v=v[v.v2pariglef.notna()]; vv=v.iloc[0] if len(v) else None
    rows.append(dict(id_eleccion=f'UY-{an}-PRES-1',pais='UY',anio=an,candidato=g.candidato_o_formula.iloc[0] if len(g) else k,
      share_pct=round(g.share.sum(),2) if len(g) else None,eje_economico=e,eje_sociocultural=s,
      mf_rile=round(mm.rile.iloc[0],1) if len(mm) else None,mf_econ_markeco_menos_planeco=round(mm.econ_mf.iloc[0],1) if len(mm) else None,
      vp_econ=round(vv.v2pariglef,2) if vv is not None else None,vp_socio_idx=round(vv.socio_vp,2) if vv is not None else None,
      ches_econ_cont=None,ches_socio_cont=None,nivel_evidencia=niv,fuente='Manifesto MPDS2026a + V-Party v2 + juicio del analista',notas=nota,codificador='claude_v1'))
d=pd.DataFrame(rows); d.to_csv('final/ideologia_uruguay.csv',index=False)
print(d[['candidato','share_pct','eje_economico','eje_sociocultural','vp_econ','vp_socio_idx','mf_econ_markeco_menos_planeco']].to_string(index=False))
