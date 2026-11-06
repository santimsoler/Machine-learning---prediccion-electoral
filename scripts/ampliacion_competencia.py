"""Competencia, ideología y familia partidaria para BO/PY/EC (replica features_competencia.py). Corre DESPUÉS de ampliacion_nacional.py."""
import pandas as pd, numpy as np, re
F='final/'; D='data_ampliacion/'
vp=pd.read_csv(D+'vparty_bo_py_ec.csv'); ch=pd.read_csv(D+'ches_la_2020_aggregate.csv',encoding='latin1').set_index('party_id')
PAIS={'Bolivia':'BO','Paraguay':'PY','Ecuador':'EC'}; vp['pais']=vp.country_name.map(PAIS)
# (eid, candidato, familia, share_o_votos, es_of, tag_ideologia)
C=[]
def add(eid,rows,of): 
    for nm,fam,sh,tag in rows: C.append((eid,nm,fam,sh,int(nm==of),tag))
add('BO-1993',[('Sánchez de Lozada (MNR)','MNR',35.56,'V:MNR'),('Banzer (AP)','ADN',21.05,'V:AP'),('Palenque (CONDEPA)','CONDEPA',14.29,'V:CONDEPA'),('Fernández (UCS)','UCS',13.77,'V:UCS'),('Araníbar (MBL)','OTROS',5.36,'V:MBL'),('Ancalle (ARBOL)','OTROS',1.87,''),('Justiniano (ASD)','OTROS',1.84,''),('Serrate (VR-9)','OTROS',1.28,''),('Serrate Paz (FSB)','OTROS',1.27,''),('Cárdenas (Eje Pachakuti)','OTROS',1.10,''),('Velasco (IU)','OTROS',0.98,''),('Untoja (MKN)','OTROS',0.77,'')],'Banzer (AP)')
add('BO-1997',[('Banzer (ADN)','ADN',22.26,'V:ADN'),('Durán (MNR)','MNR',18.20,'V:MNR'),('Loza (CONDEPA)','CONDEPA',17.16,'V:CONDEPA'),('Paz Zamora (MIR)','MIR',16.77,'V:MIR'),('Kuljis (UCS)','UCS',16.11,'V:UCS'),('Véliz (IU)','OTROS',3.71,''),('Urioste (MBL)','OTROS',3.09,'V:MBL'),('Justiniano (VSB)','OTROS',1.39,'')],'Durán (MNR)')
add('BO-2002',[('Sánchez de Lozada (MNR)','MNR',22.46,'V:MNR'),('Morales (MAS)','MAS',20.94,'V:MAS'),('Reyes Villa (NFR)','NFR',20.91,'V:NFR'),('Paz Zamora (MIR)','MIR',16.32,'V:MIR'),('Quispe (MIP)','OTROS',6.09,''),('Fernández (UCS-FSB)','UCS',5.51,'V:UCS'),('MacLean (ADN)','ADN',3.40,'W:ADN'),('Costa (PLJ)','OTROS',2.72,'')],'MacLean (ADN)')
# Bolivia 2005-2025 desde la suma departamental
b=pd.read_csv(D+'bo_reg_largo.csv'); b=b[b.region!='Exterior'] if 'region' in b.columns else b[b.dep!='Exterior']
b=b.rename(columns={'dep':'region'}) if 'dep' in b.columns else b
BOF={'MAS-IPSP':('MAS',None),'PODEMOS':('PODEMOS','V:Podemos'),'NFR':('NFR','V:NFR'),'UN':('UN','V:UN'),'MNR':('MNR','V:MNR'),'PPB-CN':('PPB','V:PPB-CN'),'UN-CP':('UN','V:UN'),'UD':('UN','V:UN'),'PDC':('PDC','V:PDC'),'CC':('CC','V:CC'),'Creemos':('CREEMOS','C:5105'),'FPV':('OTROS','C:5106'),'Libre':('LIBRE','J:1.0:eju_bretel_2025'),'Unidad':('UN','C:5104'),'Alianza Popular':('OTROS','J:-1.5:eju_bretel_2025'),'APB Super':('OTROS','')}
MAST={'2005':'V:MAS','2009':'V:MAS','2014':'V:MAS','2019':'V:MAS','2020':'V:MAS|C:5101','2025-1':'C:5101','2025-2':'C:5101'}
for k,g in b.groupby('clave'):
    if k=='2025-2': continue
    s=g.groupby('cand').votos.sum(); rows=[]
    for cand,v in s.items():
        m_=re.search(r'\((.*)\)',cand); party=m_.group(1) if m_ else cand; fam,tag=BOF.get(party,('OTROS',''))
        if party=='MAS-IPSP': tag=MAST[k]
        if k=='2025-1' and party=='PDC': tag='J:1.0:lanacion_2025'
        rows.append((cand,fam,100*v/s.sum(),tag))
    ofc={'2009':'Morales (MAS-IPSP)','2014':'Morales (MAS-IPSP)','2019':'Morales (MAS-IPSP)','2025-1':'Del Castillo (MAS-IPSP)'}.get(k)
    add('BO-'+k[:4],rows,ofc)
# Paraguay (votos -> % de positivos)
def pct(rows,tot=None):
    t=tot or sum(r[2] for r in rows); return [(a,b,100*c/t,d) for a,b,c,d in rows]
add('PY-1993',pct([('Wasmosy (ANR)','ANR',468213,'V:ANR-PC'),('Laíno (PLRA)','PLRA',376868,'V:PLRA'),('Caballero (PEN)','PEN',271421,'V:PEN'),('Canese (CDS)','OTROS',1998,''),('Zapag (PL)','OTROS',1155,''),('Arce (PT)','OTROS',2025,''),('Bader (PNS)','OTROS',850,''),('Cazal (APN)','OTROS',1091,''),('Prieto (MPSP)','OTROS',1042,'')]),'Wasmosy (ANR)')
add('PY-1998',[('Cubas (ANR)','ANR',55.35,'V:ANR-PC'),('Laíno (PLRA-PEN)','PLRA',43.88,'V:PLRA'),('Campos (PRF)','OTROS',0.51,''),('Bader (UNC)','OTROS',0.26,'')],'Cubas (ANR)')
add('PY-2003',pct([('Duarte (ANR)','ANR',573562,'V:ANR-PC'),('Franco (PLRA)','PLRA',369863,'V:PLRA'),('Fadul (PPQ)','PPQ',328598,'V:PPQ'),('Sánchez (UNACE)','UNACE',207964,'V:UNACE'),('Abente (PEN)','PEN',8741,'V:PEN'),('Zayas (PPL)','OTROS',4549,''),('Hellmers (FDI)','OTROS',1364,''),('Notario (PHP)','OTROS',1194,''),('Almada (PFA)','OTROS',1441,'')]),'Duarte (ANR)')
add('PY-2008',pct([('Ovelar (ANR)','ANR',540553,'V:ANR-PC'),('Lugo (APC)','PLRA',774968,'V:PLRA'),('Oviedo (UNACE)','UNACE',386571,'V:UNACE'),('Fadul (PPQ)','PPQ',41004,'V:PPQ'),('Martínez (PHP)','OTROS',5852,''),('López (PT)','OTROS',2288,''),('Galeano (MTP)','OTROS',2788,'')]),'Ovelar (ANR)')
add('PY-2013',pct([('Cartes (ANR)','ANR',1104976,'V:ANR-PC'),('Alegre (PLRA)','PLRA',890451,'V:PLRA'),('Ferreiro (Avanza País)','OTROS',145618,''),('Frente Guasú','FG',73864,'V:GF'),('Carrizosa (PPQ)','PPQ',27026,'V:PPQ'),('Oviedo (UNACE)','UNACE',19416,'V:UNACE'),('Otros','OTROS',4264+3925+3011+2767+2416,'')],2277734),'Alegre (PLRA)')
add('PY-2018',[('Abdo (ANR)','ANR',48.96,'V:ANR-PC|C:5801'),('Alegre (GANAR)','PLRA',45.08,'V:GANAR|C:5802'),('Ybáñez (Verde)','OTROS',3.24,''),('Anzoátegui','OTROS',0.60,''),('Galeano','OTROS',0.38,''),('Benítez','OTROS',0.36,''),('Almada','OTROS',0.33,'')],'Abdo (ANR)')
add('PY-2023',[('Peña (ANR)','ANR',42.74,'C:5801'),('Alegre (Concertación)','PLRA',27.48,'C:5802'),('Cubas (Cruzada Nacional)','CRUZADA',22.91,'C:5807'),('Acevedo (Nueva República)','OTROS',1.36,''),('Chilavert','OTROS',0.80,''),('Talavera','OTROS',0.57,'')],'Peña (ANR)')
# Ecuador
add('EC-1996',[('Bucaram (PRE)','PRE',26.28,'V:PRE'),('Nebot (PSC)','PSC',27.17,'V:PSC'),('Ehlers (Pachakutik-NP)','OTROS',20.61,'V:MUPP-NP'),('Paz (DP)','DP',13.48,'V:UDC/DP'),('Vargas (APRE)','OTROS',4.93,'V:PAPRE'),('Noboa (PLRE-FRA)','OTROS',3.02,'V:PLR/FRA Alli...'),('Castelló (MPD)','OTROS',2.35,'V:MPD')],None)
add('EC-1998',[('Mahuad (DP)','DP',34.92,'V:UDC/DP'),('Noboa (PRE-APRE-UPL)','PRE',26.61,'V:PRE'),('Borja (ID)','ID',16.12,'V:ID'),('Ehlers (Nuevo País)','OTROS',14.75,'V:MUPP-NP'),('Arteaga (MIRA)','OTROS',5.07,''),('Lima (MPD)','OTROS',2.53,'V:MPD')],None)
add('EC-2002',[('Gutiérrez (PSP-MUPP)','PSP',20.43,'V:PSP'),('Noboa (PRIAN)','PRIAN',18.23,'V:PRIAN'),('Roldós (RP)','OTROS',15.43,''),('Borja (ID)','ID',14.04,'V:ID'),('Neira (PSC)','PSC',12.18,'V:PSC'),('Bucaram (PRE)','PRE',11.86,'V:PRE'),('Velázquez (TSI)','OTROS',3.73,''),('Juez (PLRE)','OTROS',1.76,''),('Alarcón (PL)','OTROS',1.23,'V:PL'),('Hurtado (MPS)','OTROS',1.07,'V:MPS')],None)
add('EC-2006',[('Noboa (PRIAN)','PRIAN',26.83,'V:PRIAN'),('Correa (PAIS)','CORREISMO',22.84,'V:PAIS'),('Gutiérrez (PSP)','PSP',17.42,'V:PSP'),('Roldós (ID-RED)','ID',14.84,'V:ID'),('Viteri (PSC)','PSC',9.63,'V:PSC'),('Macas (MUPP-NP)','OTROS',2.19,'V:MUPP-NP'),('Rosero (PRE)','PRE',2.08,'V:PRE'),('Proaño (MRD)','OTROS',1.42,''),('Villacís (MPD)','OTROS',1.33,'V:MPD')],None)
add('EC-2009',[('Correa (PAIS)','CORREISMO',51.99,'V:PAIS'),('Gutiérrez (PSP)','PSP',28.24,'V:PSP'),('Noboa (PRIAN)','PRIAN',11.40,'V:PRIAN'),('Roldós (RED)','OTROS',4.33,''),('Sagnay (MTM)','OTROS',1.57,''),('Jácome (MTF)','OTROS',1.35,''),('Delgado (MITS)','OTROS',0.63,'')],'Correa (PAIS)')
add('EC-2013',[('Correa (PAIS)','CORREISMO',57.17,'V:PAIS'),('Lasso (CREO)','CREO',22.68,'V:CREO'),('Gutiérrez (PSP)','PSP',6.73,'V:PSP'),('Rodas (SUMA)','OTROS',3.90,''),('Noboa (PRIAN)','PRIAN',3.72,'V:PRIAN'),('Acosta (MPD-MUPP)','OTROS',3.26,'V:Multinationa...'),('Wray (Ruptura 25)','OTROS',1.31,''),('Zavala (PRE)','PRE',1.23,'V:PRE')],'Correa (PAIS)')
add('EC-2017',[('Moreno (PAIS)','CORREISMO',39.36,'V:PAIS'),('Lasso (CREO-SUMA)','CREO',28.09,'V:CREO'),('Viteri (PSC)','PSC',16.32,'V:PSC'),('Moncayo (ID-UP-MUPP)','ID',6.71,'V:ID'),('Bucaram (Fuerza Ecuador)','PRE',4.82,''),('Espinel (FCS)','OTROS',3.18,''),('Zuquilanda (PSP)','PSP',0.77,'V:PSP')],'Moreno (PAIS)')
add('EC-2021',[('Arauz (UNES)','CORREISMO',32.72,'J:-1.5:voz_us_2023_correismo_izquierda'),('Lasso (CREO-PSC)','CREO',19.74,'C:5602'),('Peña (Alianza PAIS)','PAIS_MORENO',1.54,'C:5601'),('Pérez (Pachakutik)','OTROS',19.39,'C:5608'),('Hervas (ID)','ID',15.68,'C:5606'),('Freile (Amigo)','OTROS',2.08,''),('Romero (Avanza)','OTROS',1.86,'C:5609'),('Gutiérrez (PSP)','PSP',1.78,'C:5607')],'Peña (Alianza PAIS)')
add('EC-2023',[('González (RC)','CORREISMO',33.61,'J:-1.5:voz_us_2023'),('Noboa (ADN)','ADN',23.47,'J:0.5:cidob_2023_ambiguo'),('Zurita (Construye)','OTROS',16.37,''),('Topic (País sin Miedo)','OTROS',14.67,'J:1.5:energy_daily_2023'),('Sonnenholzner (Actuemos)','OTROS',7.06,''),('Pérez (UP-PSE)','OTROS',3.97,'C:5608'),('Hervas (RETO)','OTROS',0.49,'')],None)
add('EC-2025',[('Noboa (ADN)','ADN',44.17,'J:0.5:cidob_2023_ambiguo'),('González (RC-RETO)','CORREISMO',44.00,'J:-1.5:voz_us_2023'),('Iza (Pachakutik)','OTROS',5.25,'C:5608'),('González (PSP)','PSP',2.69,'C:5607'),('Kronfle (PSC)','PSC',0.71,'C:5604'),('Granja (PSE)','OTROS',0.53,''),('Jairala (CD)','OTROS',0.40,'')],'Noboa (ADN)')
c=pd.DataFrame(C,columns=['id_eleccion','candidato','familia','share','es_oficialismo','tag'])
c['pais']=c.id_eleccion.str[:2]; c['anio']=c.id_eleccion.str[3:].astype(int)
# ---------- ideología ----------
def vsc(pais,short,anio,win=3):
    d=vp[(vp.pais==pais)&(vp.v2pashname==short)]
    if d.empty: return np.nan
    d=d.assign(dist=(d.year-anio).abs()).sort_values('dist'); r=d.iloc[0]
    return np.nan if r.dist>win else float(np.clip(r.v2pariglef/1.35,-2,2))
def ideo(r):
    vals=[];src=[]
    for t in str(r.tag).split('|'):
        if t.startswith('V:') and r.anio<=2019:
            v=vsc(r.pais,t[2:],r.anio)
            if pd.notna(v): vals.append(v); src.append('vparty')
        elif t.startswith('C:') and r.anio>=2018:
            vals.append((ch.loc[int(t[2:]),'lrecon']-5)/2.5); src.append('ches_la2020')
        elif t.startswith('W:'):
            v=vsc(r.pais,t[2:],r.anio,5)
            if pd.notna(v): vals.append(v); src.append('vparty_ventana5')
        elif t.startswith('J:'): q=t.split(':'); vals.append(float(q[1])); src.append('web:'+(q[2] if len(q)>2 else 'sin_cita'))
    return pd.Series({'e_cont':np.mean(vals) if vals else np.nan,'e_n_fuentes':len(vals),'e_fuentes':'+'.join(src)})
c=pd.concat([c,c.apply(ideo,axis=1)],axis=1)
c.drop(columns=['pais','anio']).to_csv(F+'candidatos_ampliacion.csv',index=False)
# ---------- features por elección ----------
rows=[]
for eid,d in c.groupby('id_eleccion',sort=False):
    s=d.share/d.share.sum()*100; d=d.assign(s=s)
    of=d[d.es_oficialismo==1]; ideo_of=of.e_cont.mean() if len(of) else np.nan
    oth=d[(d.es_oficialismo!=1)&(d.s>=5)]
    cerc=oth[(oth.e_cont-ideo_of).abs()<=1.0] if pd.notna(ideo_of) else oth.iloc[0:0]
    top2=d.sort_values('s',ascending=False).head(2).familia.tolist()
    rows.append(dict(id_eleccion=eid,enc=1/((s/100)**2).sum(),n_cand_1pct=int((s>=1).sum()),n_cand_5pct=int((s>=5).sum()),hhi_top1=s.max(),
      n_fuertes_cercanos=len(cerc) if pd.notna(ideo_of) else np.nan,share_fuertes_cercanos=cerc.s.sum() if pd.notna(ideo_of) else np.nan,
      cobertura_ideologia=oth.e_cont.notna().mean() if len(oth) else np.nan,familia_of=of.familia.iloc[0] if len(of) else None,top2_familias='|'.join(top2),
      ideologia_of=ideo_of if pd.notna(ideo_of) else np.nan,ideologia_of_n=int(of.e_n_fuentes.iloc[0]) if len(of) else np.nan))
E=pd.DataFrame(rows); E['pais']=E.id_eleccion.str[:2]; E['anio']=E.id_eleccion.str[3:].astype(int); E=E.sort_values(['pais','anio'])
prev=[];cnt=[]
for p,d in E.groupby('pais'):
    hist=[]
    for i,r in d.iterrows():
        f=r.familia_of if isinstance(r.familia_of,str) else None
        prev.append((i,(int(f in hist[-1]) if hist and f else np.nan)))
        cnt.append((i,(sum(1 for h in hist if f in h) if hist and f else np.nan))); hist.append(r.top2_familias.split('|'))
E['of_top2_eleccion_previa']=pd.Series(dict(prev)); E['of_n_top2_previas']=pd.Series(dict(cnt))
TRAD={'BO':['MNR','ADN','MIR'],'PY':['ANR','PLRA'],'EC':['PSC','ID','DP','PRE']}
E['of_tradicional']=E.apply(lambda r:(int(r.familia_of in TRAD[r.pais]) if isinstance(r.familia_of,str) else np.nan),axis=1)
E['pre2000']=(E.anio<2000).astype(int); E['of_tradicional_x_pre2000']=E.of_tradicional*E.pre2000; E['anio_c']=(E.anio-2000)/10
E.to_csv(F+'competencia_ampliacion.csv',index=False)
# ---------- escribir en los paneles ----------
tr=pd.read_csv(F+'partidos_tradicionales.csv'); tr=tr[~tr.pais.isin(TRAD)]
pd.concat([tr,pd.DataFrame([(p,f) for p,l in TRAD.items() for f in l],columns=tr.columns)]).to_csv(F+'partidos_tradicionales.csv',index=False)
cols=['enc','n_cand_1pct','n_cand_5pct','hhi_top1','n_fuertes_cercanos','share_fuertes_cercanos','cobertura_ideologia','familia_of','top2_familias','of_top2_eleccion_previa','of_n_top2_previas','of_tradicional','pre2000','of_tradicional_x_pre2000','anio_c','ideologia_of','ideologia_of_n']
for f in ['panel_modelo_eleccion','panel_modelo_region']:
    P=pd.read_csv(F+f+'.csv'); m=P.ampliacion==1
    K=P[m][['pais','anio']].merge(E[['pais','anio']+cols],on=['pais','anio'],how='left')
    for col in cols: P.loc[m,col]=K[col].values
    P.to_csv(F+f+'.csv',index=False)
print(E[['id_eleccion','familia_of','ideologia_of','enc','n_cand_5pct','hhi_top1','n_fuertes_cercanos','cobertura_ideologia','of_tradicional','of_n_top2_previas']].round(2).to_string())
