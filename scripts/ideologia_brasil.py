import pandas as pd
A='/mnt/user-data/attachments/fbc2a8cf-9f07-5c94-8ce1-557ba4094ca9/'
c=pd.read_csv('final/candidatos.csv'); c['share']=pd.to_numeric(c.share_nacional_pct,errors='coerce')
m=pd.read_csv(A+'219a3d6b-MPDataset_MPDS2026a.csv',low_memory=False)
m=m[(m.countryname=='Brazil')&m.presvote.notna()].copy(); m['anio']=pd.to_datetime(m.edate,dayfirst=True).dt.year; m['econ_mf']=m.markeco-m.planeco
vp=pd.read_csv('final/vparty_6paises_v2.csv'); vp=vp[vp.pais=='BR']; vp['socio_vp']=-(vp.v2palgbt+vp.v2parelig)/2
ch=pd.read_csv(A+'f1c2292b-ches_la_2020_aggregate_level_v01.csv',encoding='latin-1').set_index(['country_abb','party_abb'])
VPD='V-Party v2 (partido-elección)'; MFD='Manifesto MPDS2026a (plataforma del candidato)'
CG='conocimiento_general_verificar'; MV='manifesto_vparty_juicio'
# anio, clave candidato (candidatos.csv), clave manifesto, partido V-Party, partido CHES, e, s, nivel, nota
R=[
(2002,'LULA','Luiz','PT','PT',-1,-1,MV,'Carta ao Povo Brasileiro: moderación; PT progresista en lo social.'),
(2002,'SERRA','Serra','PSDB','PSDB',1,0,MV,'PSDB centro-derecha económica; centro en lo social.'),
(2002,'GAROTINHO','Gartinho','PSB',None,-1,1,CG,'populismo de izquierda; evangélico (s por conocimiento general).'),
(2002,'CIRO','Ciro','PPS',None,-1,-1,MV,'desarrollismo; centro-izquierda.'),
(2006,'LULA','Luiz','PT','PT',-1,-1,MV,'continuidad; Bolsa Família.'),
(2006,'ALCKMIN','Alckmin','PSDB','PSDB',1,0,MV,'PSDB; católico (apoyo Opus Dei) no se refleja en el partido.'),
(2006,'HELOÍSA','Heliosa','PSOL',None,-2,0,CG,'izquierda radical; católica y contraria al aborto (s 0 por eso, no por el partido).'),
(2010,'DILMA','Dilma','PT','PT',-1,0,CG,'en 2010 se retractó públicamente sobre el aborto bajo presión evangélica (conocimiento general).'),
(2010,'SERRA','Serra','PSDB','PSDB',1,1,CG,'campaña 2010 con discurso antiaborto (conocimiento general).'),
(2010,'MARINA','Marina','PV',None,0,1,CG,'evangélica (Asamblea de Dios), ambientalista; Manifesto trad. discrepa (-3.8): señal débil.'),
(2014,'DILMA','Dilma','PT','PT',-1,0,CG,'reelección; moderó posición sobre aborto.'),
(2014,'AÉCIO','Aécio','PSDB','PSDB',1,0,MV,'PSDB; Manifesto econ +3.5.'),
(2014,'MARINA','Marina','PSB',None,0,1,CG,'asesores de mercado (autonomía BCB) pero programa verde; retiró pauta LGBT en 2014 (conocimiento general).'),
(2018,'BOLSONARO','Bolsonaro','PSL','PSL',2,2,MV,'programa Guedes (privatizar todo); Manifesto econ +23; CHES-LA 2020 (Jair): +1,52 / +1,92.'),
(2018,'HADDAD','Haddad','PT','PT',-2,-1,MV,'programa "revogaço" (teto de gasto y reforma laboral); Manifesto econ -5,7, el más bajo de 2018.'),
(2018,'CIRO','Ciro','PDT','PDT',-1,-1,MV,'desarrollismo estatal.'),
(2018,'ALCKMIN','Alckmin','PSDB','PSDB',1,0,MV,'Manifesto econ +7,8.'),
(2018,'AMOÊDO','NOVO','NOVO',None,2,0,CG,'liberal-libertario (conocimiento general).'),
(2022,'LULA','Luiz','PT','PT',-1,-1,MV,'CHES-LA 2020 PT: -0,95 / -1,28.'),
(2022,'BOLSONARO','Bolsonaro','PL','JB',1,2,MV,'Auxílio Brasil sube el gasto; Guedes liberal. CHES-LA 2020 (Jair): +1,52 / +1,92; Manifesto econ +5,9, trad. +5,3.'),
(2022,'TEBET','Simone','MDB','MDB',0,0,MV,'centro liberal-socio; CHES MDB 2020: +0,1 / +0,3.'),
(2022,'CIRO','Ciro','PDT','PDT',-1,-1,CG,'repite perfil 2018.'),
]
rows=[]
for an,k,mk,vpp,chp,e,s,niv,nota in R:
    g=c[(c.pais=='BR')&(c.anio==an)&(c.vuelta==1)&c.candidato_o_formula.fillna('').str.contains(k,case=False)]
    mm=m[(m.anio==an)&m.candidatename.fillna('').str.contains(mk,case=False)|(m.anio==an)&m.partyname.fillna('').str.contains(mk,case=False)]
    v=vp[(vp.year==an)&(vp.v2pashname.str.upper().str.contains(vpp.upper().replace('NOVO','ZZZ')) if vpp else False)] if vpp else pd.DataFrame()
    rows.append(dict(id_eleccion=f'BR-{an}-PRES-1',pais='BR',anio=an,candidato=g.candidato_o_formula.iloc[0] if len(g) else k,
      partido=g.partido_o_coalicion.iloc[0] if len(g) else None,share_pct=round(g.share.sum(),2) if len(g) else None,
      eje_economico=e,eje_sociocultural=s,
      mf_rile=mm.rile.iloc[0] if len(mm) else None,mf_econ_markeco_menos_planeco=round(mm.econ_mf.iloc[0],1) if len(mm) else None,
      vp_econ=v.v2pariglef.iloc[0] if len(v) else None,vp_socio_idx=round(v.socio_vp.iloc[0],2) if len(v) else None,
      ches_econ_cont=round((ch.loc[('BR',chp)].lrecon-5)/2.5,2) if chp and ('BR',chp) in ch.index else None,
      ches_socio_cont=round((ch.loc[('BR',chp)].galtan-5)/2.5,2) if chp and ('BR',chp) in ch.index else None,
      nivel_evidencia=niv,fuente=MFD+' + '+VPD+' + CHES-LA 2020 (cuando existe) + juicio del analista',notas=nota,codificador='claude_v1'))
d=pd.DataFrame(rows); d.to_csv('final/ideologia_brasil.csv',index=False)
pd.set_option('display.width',250)
print(d[['anio','candidato','share_pct','eje_economico','eje_sociocultural','mf_econ_markeco_menos_planeco','vp_econ','vp_socio_idx','ches_econ_cont','nivel_evidencia']].to_string(index=False))
