import pandas as pd, unicodedata, re
A='/mnt/user-data/attachments/fbc2a8cf-9f07-5c94-8ce1-557ba4094ca9/'
def nrm(t): return re.sub(r'[^a-z ]','',unicodedata.normalize('NFKD',str(t)).encode('ascii','ignore').decode().lower())
c=pd.read_csv('final/candidatos.csv'); c['share']=pd.to_numeric(c.share_nacional_pct,errors='coerce'); c['k']=c.candidato_o_formula.map(nrm)
m=pd.read_csv(A+'219a3d6b-MPDataset_MPDS2026a.csv',low_memory=False).copy()
m=m[m.presvote.notna()]; m['anio']=pd.to_datetime(m.edate,dayfirst=True).dt.year; m['econ_mf']=m.markeco-m.planeco; m['k']=m.candidatename.map(nrm)
vp=pd.read_csv('final/vparty_6paises_v2.csv'); vp['socio_vp']=-(vp.v2palgbt+vp.v2parelig)/2
ch=pd.read_csv(A+'f1c2292b-ches_la_2020_aggregate_level_v01.csv',encoding='latin-1').set_index(['country_abb','party_abb'])
MV='manifesto_vparty_juicio'; CG='conocimiento_general_verificar'
CLV={'1989':'', }
# pais, anio, clave_cand, clave_mf, partido_vp, partido_ches, e, s, nivel, nota
R=[
('CL',1989,'aylwin','aylwin','PDC','PDC',0,1,MV,'Concertación: economía de mercado con "deuda social"; DC católica.'),
('CL',1989,'buchi','buchi','UDI',None,2,2,MV,'ex ministro de Hacienda de Pinochet; Manifesto econ +8,7. V-Party con UDI como proxy.'),
('CL',1989,'errazuriz','errazuriz',None,None,0,0,CG,'empresario independiente de centro (conocimiento general).'),
('CL',1993,'frei','frei','PDC','PDC',0,1,MV,'continuidad Concertación.'),
('CL',1993,'alessandri','alessandri','UDI','UDI',2,2,MV,'Manifesto econ +13,9.'),
('CL',1993,'pinera','',None,None,2,1,CG,'José Piñera: arquitecto del sistema de AFP, libertario (conocimiento general).'),
('CL',1993,'max','',None,None,-1,-2,CG,'Manfred Max-Neef: ecologista de izquierda humanista (conocimiento general).'),
('CL',1993,'pizarro','',None,None,-2,-1,CG,'Eugenio Pizarro: izquierda (conocimiento general).'),
('CL',1999,'lagos','lagos','PPD','PPD',-1,-1,MV,'Concertación, PS-PPD; Manifesto econ -4,1.'),
('CL',1999,'lavin','lavin','UDI','UDI',1,2,MV,'campaña "cambio" de derecha social; Manifesto econ +2,1.'),
('CL',1999,'marin','',None,None,-2,-1,CG,'Gladys Marín, PC (conocimiento general); V-Party PC 2013: e -2,31.'),
('CL',2005,'bachelet','bachelet','PS','PS',-1,-1,MV,'Manifesto econ -8,3.'),
('CL',2005,'pinera','pinera','RN','RN',1,1,MV,'Manifesto econ +0,8; V-Party RN +1,67.'),
('CL',2005,'lavin','lavin','UDI','UDI',2,2,MV,'V-Party UDI +2,62 (Manifesto econ -0,7, atípico).'),
('CL',2005,'hirsch','hirsch','PH','HUM',-2,-2,MV,'Manifesto econ -13,7; V-Party PH e -2,67 / s -2,96.'),
('CL',2009,'pinera','pinera','RN','RN',1,1,MV,'Coalición por el Cambio.'),
('CL',2009,'frei','frei','PDC','PDC',0,0,MV,'Manifesto econ -8,3 pero V-Party PDC ~0.'),
('CL',2009,'enriquez','enriquez',None,None,-1,-1,MV,'MEO: Manifesto econ -9,2.'),
('CL',2009,'arrate','arrate','PC','PC',-2,-1,MV,'Juntos Podemos; V-Party PC.'),
('CL',2013,'bachelet','bachelet','PS','PS',-1,-1,MV,'Nueva Mayoría con PC: reforma tributaria y educativa; Manifesto econ -5,6. Se mantiene -1 (centro-izquierda moderada).'),
('CL',2013,'matthei','matthei','UDI','UDI',1,1,MV,'Se la codifica igual que en 2025 (ala moderada de la UDI); V-Party UDI +2,62/+2,0 como contraste. Manifesto econ -9,6 es atípico.'),
('CL',2013,'enriquez','enriquez',None,None,-1,-1,MV,'Manifesto econ -18,5.'),
('CL',2013,'parisi','',None,None,0,None,CG,'populista independiente; sociocultural NA.'),
('CL',2017,'pinera','pinera','RN','RN',1,1,MV,'Manifesto econ +1,0.'),
('CL',2017,'guillier','guillier','PS','PS',-1,-1,MV,'Manifesto econ -6,5.'),
('CL',2017,'sanchez','sanchez','DR','RD',-2,-2,MV,'Frente Amplio; V-Party DR e -2,09 / s -2,70.'),
('CL',2017,'kast','kast',None,None,2,2,CG,'candidato independiente; programa liberal en economía y conservador en valores (conocimiento general; Manifesto econ -2,2, poco informativo).'),
('CL',2017,'goic','goic','PDC','PDC',0,0,MV,'Manifesto econ -4,2.'),
('CL',2017,'enriquez','enriquez',None,None,-1,-1,MV,'PRO.'),
('CL',2021,'kast','kast',None,None,2,2,CG,'Manifesto rile +3, econ -3,7 (documento moderado). Coherente con 2017 y 2025.'),
('CL',2021,'boric','boric','DR','RD',-2,-2,MV,'Manifesto econ -6,0; V-Party Frente Amplio 2017.'),
('CL',2021,'parisi','parisi',None,None,0,None,CG,'Manifesto econ -2,6.'),
('CL',2021,'sichel','sichel',None,None,1,0,CG,'centroderecha moderado; Manifesto econ -6,5 (atípico).'),
('CL',2021,'provoste','provoste','PDC','PDC',-1,0,MV,'Nuevo Pacto Social; Manifesto econ -5,8.'),
('CL',2021,'enriquez','enriquez',None,None,-1,-1,MV,'Manifesto econ -8,4.'),
('CO',1998,'serpa','serpa','PLC','PLC',0,0,MV,'Partido Liberal; V-Party PLC ~0.'),
('CO',1998,'pastrana','pastrana','PCC','PCC',1,1,MV,'Gran Alianza por el Cambio; Manifesto econ +1,5; V-Party PCC +2,34.'),
('CO',1998,'sanin','sanin',None,None,1,1,CG,'Noemí Sanín (conocimiento general).'),
('CO',2002,r'alvaro\s+uribe','uribe',None,None,1,1,CG,'Primero Colombia, seguridad democrática (conocimiento general; Manifesto atípico).'),
('CO',2002,'serpa','serpa','PLC','PLC',0,0,MV,'V-Party PLC.'),
('CO',2002,'garzon','garzon','PDA','PDA',-2,-1,MV,'Polo Democrático; V-Party PDA e -2,6.'),
('CO',2002,'sanin','sanin',None,None,1,1,CG,'Sí Colombia.'),
('CO',2006,r'alvaro\s+uribe','uribe',None,None,1,1,CG,'reelección.'),
('CO',2006,'gaviria','gaviria','PDA','PDA',-2,-1,MV,'V-Party PDA e -2,60 / s -1,83.'),
('CO',2006,'serpa','serpa','PLC','PLC',0,0,MV,'V-Party PLC.'),
('CO',2010,'santos','santos','Partido-U','U',1,0,MV,'Tercera vía promercado; V-Party Partido de la U +0,14.'),
('CO',2010,'mockus','mockus',None,None,0,-1,CG,'Partido Verde, centro progresista (conocimiento general).'),
('CO',2010,'vargas','vargas','CR','RCP',1,0,MV,'Cambio Radical; V-Party CR e +1,78.'),
('CO',2010,'petro','petro','PDA','PDA',-2,-1,MV,'V-Party PDA e -2,33 / s -2,16; se codifica s -1 como en 2018 y 2022.'),
('CO',2010,'sanin','sanin','PCC','PCC',1,1,MV,'Partido Conservador.'),
('CO',2010,'pardo','pardo','PLC','PLC',0,0,MV,'Partido Liberal.'),
('CO',2014,'zuluaga','zuluaga','CD','CD',2,1,MV,'Centro Democrático; V-Party CD +2,68 / +1,59.'),
('CO',2014,'santos','santos','Partido-U','U',1,0,MV,'V-Party Partido de la U +0,80.'),
('CO',2014,'ramirez','ramirez','PCC','PCC',1,1,MV,'Partido Conservador (candidata moderada); V-Party PCC e +2,36.'),
('CO',2014,'lopez','lopez','PDA','PDA',-2,-1,MV,'PDA-UP; Manifesto rile -39.'),
('CO',2014,'penalosa','penalosa','AV','AV',1,-1,CG,'Alianza Verde; Peñalosa es promercado en lo económico (conocimiento general).'),
('CO',2018,'duque','duque','CD','ID',1,1,MV,'Manifesto econ +4,9; CHES-LA 2020 (Duque presidente): +1,4 / +1,36.'),
('CO',2018,'petro','petro','AV','DEC',-1,-1,MV,'Lista de la Decencia; CHES DEC e -0,76 / s -1,08; Manifesto econ -0,7.'),
('CO',2018,'fajardo','fajardo','AV','AV',0,-1,MV,'Coalición Colombia; V-Party AV e -0,64 / s -1,81.'),
('CO',2018,'vargas','vargas','CR','RCP',1,0,MV,'V-Party CR +1,57.'),
]
rows=[]
for P,an,k,mk,vpp,chp,e,s,niv,nota in R:
    g=c[(c.pais==P)&(c.anio==an)&(c.vuelta==1)&c.k.str.contains(k)]
    N={'CL':'Chile','CO':'Colombia'}[P]
    mm=m[(m.countryname==N)&(m.anio==an)&m.k.str.contains(mk)] if mk else m.iloc[0:0]
    if mk=='uribe': mm=mm[mm.k.str.contains('alvaro')]
    v=vp[(vp.pais==P)&(vp.year==an)&(vp.v2pashname==vpp)] if vpp else vp.iloc[0:0]
    vv=v.iloc[0] if len(v) else None
    # si no hay fila V-Party del año exacto, usar el año anterior más cercano
    if vpp and vv is None:
        w=vp[(vp.pais==P)&(vp.v2pashname==vpp)&(vp.year<=an)].sort_values('year')
        vv=w.iloc[-1] if len(w) else None
    chk=(P,chp) in ch.index if chp else False
    rows.append(dict(id_eleccion=f'{P}-{an}-PRES-1',pais=P,anio=an,candidato=g.candidato_o_formula.iloc[0] if len(g) else k,
      share_pct=round(g.share.sum(),2) if len(g) else None,eje_economico=e,eje_sociocultural=s,
      mf_rile=round(mm.rile.iloc[0],1) if len(mm) and pd.notna(mm.rile.iloc[0]) else None,
      mf_econ_markeco_menos_planeco=round(mm.econ_mf.iloc[0],1) if len(mm) and pd.notna(mm.econ_mf.iloc[0]) else None,
      vp_econ=round(vv.v2pariglef,2) if vv is not None else None,vp_socio_idx=round(vv.socio_vp,2) if vv is not None else None,vp_anio=int(vv.year) if vv is not None else None,
      ches_econ_cont=round((ch.loc[(P,chp)].lrecon-5)/2.5,2) if chk else None,ches_socio_cont=round((ch.loc[(P,chp)].galtan-5)/2.5,2) if chk else None,
      nivel_evidencia=niv,fuente='Manifesto MPDS2026a + V-Party v2 + CHES-LA 2020 (cuando existe) + juicio del analista',notas=nota,codificador='claude_v1'))
d=pd.DataFrame(rows); d.to_csv('final/ideologia_chile_colombia.csv',index=False)
pd.set_option('display.width',250)
print(d[['id_eleccion','candidato','share_pct','eje_economico','eje_sociocultural','nivel_evidencia']].to_string(index=False))
print(d[d.share_pct.isna()][['id_eleccion','candidato']])
for e,gg in d.groupby('id_eleccion'): print(e,round(gg.share_pct.sum(),1),end=' | ')
