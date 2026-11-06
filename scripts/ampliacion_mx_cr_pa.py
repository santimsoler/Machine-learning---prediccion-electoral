"""Ampliación con México, Costa Rica y Panamá (capa nacional). Corre DESPUÉS de regional_bo_py_ideologia_pobreza.py y ANTES de
percepcion_economica_panel.py / aprobacion_completa.py / us_completar*.py / panel_modelo_completo.py (ver LEEME).
Entradas: data_ampliacion2/{nacional_mx_cr_pa.csv, macro_mx_cr_pa_raw.txt, lb_aprob_mx_cr_pa.csv, percep_lb_mx_cr_pa_1995_2017.csv},
ead/M-G et al CPS.tab, vp_cpd/ (V-Party), data_ampliacion/ches_la_2020_aggregate.csv. Idempotente."""
import pandas as pd, numpy as np, re, os
F='final/'; D='data_ampliacion/'; D2='data_ampliacion2/'
ISO={'MX':'MEX','CR':'CRI','PA':'PAN'}; ISO2=set(ISO.values())
# ---------------- 1. Macro / pobreza / fiscal (Banco Mundial + FMI, descargados por el usuario en Colab) ----------------
WBMAP={'SI.POV.UMIC':'pob_6.85usd','SI.POV.LMIC':'pob_3.65usd','SI.POV.GINI':'gini','NY.GDP.MKTP.KD.ZG':'crecimiento_pib',
 'NY.GDP.PCAP.KD.ZG':'crecimiento_pib_pc','FP.CPI.TOTL.ZG':'inflacion_ipc','SL.UEM.TOTL.ZS':'desempleo_oit','PA.NUS.FCRF':'tc_oficial_lcu_usd'}
wbr=[];cab=[];imf=[]
for l in open(D2+'macro_mx_cr_pa_raw.txt'):
    p=l.split()
    if len(p)<3: continue
    if p[0]=='IMF': code,iso,ser=p[1],p[2],p[3]
    else: code,iso,ser=p[0],p[1],p[2]
    for kv in ser.split(';'):
        y,v=kv.split(':'); y=int(y); v=float(v)
        if p[0]=='IMF': imf.append((iso,y,code,v))
        elif code=='BN.CAB.XOKA.GD.ZS': cab.append((iso,y,v))
        else: wbr.append((iso,y,WBMAP[code],v))
wb=pd.DataFrame(wbr,columns=['pais','anio','indicador','valor'])
# pobreza / gini
pob=pd.read_csv('wb/wdi_pobreza_gini.csv'); pob=pob[~pob.pais.isin(ISO2)]
pobn=wb[wb.indicador.isin(['pob_6.85usd','pob_3.65usd','gini'])]
pd.concat([pob,pobn[pob.columns]]).to_csv('wb/wdi_pobreza_gini.csv',index=False)
# macro anual
m0=pd.read_csv(F+'macro_anual_bm.csv'); m0=m0[~m0.pais.isin(ISO2)]
mm=wb[~wb.indicador.isin(['pob_6.85usd','pob_3.65usd','gini'])].rename(columns={'indicador':'variable','valor':'valor'}).copy()
mm['fuente']='Banco Mundial WDI'; mm['ultima_actualizacion']='2026-11-06'
pd.concat([m0,mm[m0.columns]]).to_csv(F+'macro_anual_bm.csv',index=False)
macro=mm.pivot_table(index=['pais','anio'],columns='variable',values='valor').reset_index()
# cuenta corriente WB verdadera
c0=pd.read_csv(F+'cuenta_corriente_wb.csv'); c0=c0[~c0.pais.isin(ISO)]
back={v:k for k,v in ISO.items()}
c1=pd.DataFrame(cab,columns=['pais','anio','cuenta_corriente_wb']); c1['pais']=c1.pais.map(back)
pd.concat([c0,c1]).to_csv(F+'cuenta_corriente_wb.csv',index=False)
# fiscal FMI: current_account (=saldo fiscal global GGXCNL, convención heredada de la base del usuario) y fiscal_primario (pb)
ex=pd.read_csv(D+'us_ca_fiscal_extra.csv'); ex=ex[~ex.pais.isin(ISO)]
im=pd.DataFrame(imf,columns=['pais','anio','code','valor']); im['pais']=im.pais.map(back)
im=im.pivot_table(index=['pais','anio'],columns='code',values='valor').reset_index().rename(columns={'GGXCNL_G01_GDP_PT':'current_account','pb':'fiscal_primario'})
pd.concat([ex,im[ex.columns]]).to_csv(D+'us_ca_fiscal_extra.csv',index=False)
# ---------------- 2. Elecciones nacionales ----------------
n=pd.read_csv(D2+'nacional_mx_cr_pa.csv')
n.loc[n.id_eleccion=='MX-2012-PRES-1','y_share_nacional']=26.03
n.loc[n.id_eleccion=='MX-2012-PRES-1','nota']='26,03 = % sobre votos válidos (el 25,41 del IFE es sobre el total con nulos; coherente con el resto de la serie)'
n['fecha']=pd.to_datetime(n.fecha); n['presidente_en_ejercicio']=n.presidente_en_ejercicio.str.replace(r'\s*\(.*\)','',regex=True)
n['estado_codificacion']='ampliacion2_codificacion_manual_sin_revision_analista'
n['nota_codificacion']=(n.partido_oficialismo.astype(str)+' ('+n.candidato_oficialista.astype(str)+'). '+n.nota.fillna('')).str.strip()
n=n[['id_eleccion','pais','anio','vuelta','fecha','presidente_en_ejercicio','oficialismo_va_por_reeleccion','y_share_nacional','oficialismo_dudoso','estado_codificacion','nota_codificacion']]
EYS={'MX':[1988,1994,2000,2006,2012,2018,2024],'CR':[1986,1990,1994,1998,2002,2006,2010,2014,2018,2022,2026],'PA':[1989,1994,1999,2004,2009,2014,2019,2024]}
# ---------------- 3. EAD y Latinobarómetro ----------------
ead=pd.read_csv('ead/M-G et al CPS.tab',sep='\t',low_memory=False)
ead=ead[ead.country_name.isin(['Mexico','Costa Rica','Panama'])].copy(); ead['pais']=ead.country_name.map({'Mexico':'MX','Costa Rica':'CR','Panama':'PA'}); ead['qtr']=pd.to_datetime(ead.qtr)
def ead_feat(p,f):
    d=ead[(ead.pais==p)&(ead.qtr<=f)].sort_values('qtr'); nan={'aprob_ead_ult':np.nan,'aprob_ead_media4':np.nan,'aprob_ead_gap_dias':np.nan,'inflacion_trim_ead':np.nan,'crec_trim_ead':np.nan}
    if d.empty: return pd.Series(nan)
    gap=(f-d.iloc[-1].qtr).days
    if gap>250: nan['aprob_ead_gap_dias']=gap; return pd.Series(nan)
    return pd.Series({'aprob_ead_ult':d.iloc[-1].Approval_Smoothed,'aprob_ead_media4':d.tail(4).Approval_Smoothed.mean(),'aprob_ead_gap_dias':gap,'inflacion_trim_ead':d.tail(4).q_inflation.mean(),'crec_trim_ead':d.tail(4).q_growth.mean()})
n=pd.concat([n,n.apply(lambda x:ead_feat(x.pais,x.fecha),axis=1)],axis=1)
n['aprobacion_oficial']=n.aprob_ead_ult; n['aprobacion_fuente']=np.where(n.aprob_ead_ult.notna(),'EAD','sin_dato')
lb=pd.read_csv(D2+'lb_aprob_mx_cr_pa.csv')
def lbf(p,f):
    y=f.year if f.month==12 else f.year-1
    d=lb[(lb.pais==p)&(lb.anio<=y)].sort_values('anio')
    return pd.Series({'lb_aprob':d.iloc[-1].aprueba_pct_sobre_respuestas,'lb_anio':d.iloc[-1].anio}) if len(d) else pd.Series({'lb_aprob':np.nan,'lb_anio':np.nan})
n=pd.concat([n,n.apply(lambda x:lbf(x.pais,x.fecha),axis=1)],axis=1); n['lb_rezago_anios']=n.fecha.dt.year-n.lb_anio
# percepción económica LB 1995-2017 (las de 2018-2023 ya están en el archivo)
pe=pd.read_csv(F+'percepcion_economica_latinobarometro.csv'); pn=pd.read_csv(D2+'percep_lb_mx_cr_pa_1995_2017.csv')
pe=pe[~(pe.pais.isin(ISO)&(pe.anio<2018))]; pd.concat([pe,pn]).sort_values(['pais','anio']).to_csv(F+'percepcion_economica_latinobarometro.csv',index=False)
# ---------------- 4. Macro y pobreza por elección ----------------
def mac(p,f):
    y=f.year-1 if f.month<12 else f.year
    s=macro[(macro.pais==ISO[p])&(macro.anio==y)]
    g=lambda c: s[c].iloc[0] if len(s) and c in s and pd.notna(s[c].iloc[0]) else np.nan
    return pd.Series({'bm_crecimiento_pib_tm1':g('crecimiento_pib'),'bm_inflacion_ipc_tm1':g('inflacion_ipc'),'bm_desempleo_oit_tm1':g('desempleo_oit'),'inflacion_12m_previa':g('inflacion_ipc'),'inflacion_fuente':'Banco Mundial WDI (año previo)'})
n=pd.concat([n,n.apply(lambda x:mac(x.pais,x.fecha),axis=1)],axis=1)
def serie(iso,ind): return wb[(wb.pais==iso)&(wb.indicador==ind)].set_index('anio').valor.sort_index()
def val(s,y):
    if y in s.index: return s[y],'observado'
    if len(s)==0 or y<s.index.min(): return np.nan,'fuera_de_rango'
    if y>s.index.max(): return (s[s.index.max()],'ultimo_disponible') if y-s.index.max()<=1 else (np.nan,'fuera_de_rango')
    a=s[s.index<y]; b=s[s.index>y]; ya,yb=a.index.max(),b.index.min()
    return a[ya]+(b[yb]-a[ya])*(y-ya)/(yb-ya),'interpolado'
pr=[]
for p,yrs in EYS.items():
    for i,y in enumerate(yrs):
        r={'pais':p,'anio':y,'anios_mandato':(y-yrs[i-1]) if i else np.nan}
        for ind,nm in [('pob_6.85usd','685'),('pob_3.65usd','365')]:
            s=serie(ISO[p],ind); fin,t=val(s,y-1); r[f'pobnac_{nm}_tm1']=fin; r[f'pobnac_{nm}_tm1_tipo']=t
            if i:
                ini,_=val(s,yrs[i-1]-1); r[f'pobnac_{nm}_eleccion_prev']=ini; r[f'd_pobnac_{nm}_mandato']=fin-ini if pd.notna(fin) and pd.notna(ini) else np.nan
        pr.append(r)
pr=pd.DataFrame(pr)
n=n.merge(pr[['pais','anio','anios_mandato','pobnac_685_tm1','pobnac_685_tm1_tipo','pobnac_685_eleccion_prev','d_pobnac_685_mandato','pobnac_365_tm1','d_pobnac_365_mandato']],on=['pais','anio'],how='left')
n['anio_c']=(n.anio-2000)/10; n['pre2000']=(n.anio<2000).astype(int); n['ampliacion']=2
# ---------------- 5. Candidatos, competencia e ideología ----------------
vp=pd.read_csv('vp_cpd/CPD_V-Party_CSV_v2/V-Dem-CPD-Party-V2.csv',usecols=['country_name','year','v2pashname','v2pariglef'],low_memory=False)
vp['pais']=vp.country_name.map({'Mexico':'MX','Costa Rica':'CR','Panama':'PA'}); vp=vp[vp.pais.notna()]
ch=pd.read_csv(D+'ches_la_2020_aggregate.csv',encoding='latin1').set_index('party_id')
C=[]
def add(eid,rows,of):
    for nm,fam,sh,tag in rows: C.append((eid,nm,fam,sh,int(nm==of),tag))
# ---- México ----
add('MX-1994',[('Zedillo (PRI)','PRI',50.13,'V:PRI'),('Fernández de Cevallos (PAN)','PAN',26.69,'V:PAN'),('Cárdenas (PRD)','PRD',17.07,'V:PRD'),('Soto (PT)','OTROS',2.75,''),('González Torres (PVEM)','OTROS',0.94,''),('Álvarez (PDM)','OTROS',0.95,''),('Aguilar (PFCRN)','OTROS',0.77,''),('Lombardo (PPS)','OTROS',0.47,'')],'Zedillo (PRI)')
add('MX-2000',[('Labastida (PRI)','PRI',36.11,'V:PRI'),('Fox (PAN-PVEM)','PAN',42.52,'V:PAN'),('Cárdenas (PRD-PT)','PRD',16.64,'V:PRD'),('Camacho (PCD)','OTROS',1.58,''),('Rincón Gallardo (DS)','OTROS',1.57,''),('Muñoz (PARM)','OTROS',0.42,'')],'Labastida (PRI)')
add('MX-2006',[('Calderón (PAN)','PAN',35.89,'V:PAN'),('López Obrador (PRD-PT-MC)','PRD',35.31,'V:PRD'),('Madrazo (PRI-PVEM)','PRI',22.26,'V:PRI'),('Mercado (Alternativa)','OTROS',2.70,''),('Campa (PNA)','OTROS',0.96,'')],'Calderón (PAN)')
add('MX-2012',[('Peña Nieto (PRI-PVEM)','PRI',38.21,'V:PRI'),('López Obrador (PRD-PT-MC)','PRD',31.59,'V:PRD'),('Vázquez Mota (PAN)','PAN',25.41,'V:PAN'),('Quadri (PNA)','OTROS',2.30,'')],'Vázquez Mota (PAN)')
add('MX-2018',[('López Obrador (Morena-PT-PES)','MORENA',53.19,'V:MORENA|C:5701'),('Anaya (PAN-PRD-MC)','PAN',22.27,'V:PAN|C:5702'),('Meade (PRI-PVEM-PNA)','PRI',16.40,'V:PRI|C:5703'),('Rodríguez Calderón (indep.)','OTROS',5.23,'')],'Meade (PRI-PVEM-PNA)')
add('MX-2024',[('Sheinbaum (Morena-PT-PVEM)','MORENA',59.76,'C:5701'),('Gálvez (PAN-PRI-PRD)','PAN',27.45,'C:5702'),('Máynez (MC)','MC',10.32,'C:5706')],'Sheinbaum (Morena-PT-PVEM)')
# ---- Costa Rica ----
add('CR-1990',[('Calderón (PUSC)','PUSC',51.5,'V:PUSC'),('Castillo (PLN)','PLN',47.2,'V:PLN'),('Otros','OTROS',1.3,'')],'Castillo (PLN)')
add('CR-1994',[('Figueres (PLN)','PLN',49.69,'V:PLN'),('Rodríguez (PUSC)','PUSC',47.74,'V:PUSC'),('De la Cruz (FD)','OTROS',2.0,'V:FD'),('Otros','OTROS',0.57,'')],'Rodríguez (PUSC)')
add('CR-1998',[('Rodríguez (PUSC)','PUSC',46.96,'V:PUSC'),('Corrales (PLN)','PLN',44.56,'V:PLN'),('Fuerza Democrática','OTROS',3.0,'V:FD'),('Otros-a','OTROS',2.74,''),('Otros-b','OTROS',2.74,'')],'Corrales (PLN)')
add('CR-2002',[('Pacheco (PUSC)','PUSC',38.58,'V:PUSC'),('Araya (PLN)','PLN',31.05,'V:PLN'),('Solís (PAC)','PAC',26.2,'V:PAC'),('Guevara (ML)','OTROS',1.7,'V:PML'),('Otros','OTROS',2.47,'')],'Pacheco (PUSC)')
add('CR-2006',[('Arias (PLN)','PLN',40.92,'V:PLN'),('Solís (PAC)','PAC',39.80,'V:PAC'),('Guevara (ML)','OTROS',8.48,'V:PML'),('Toledo (PUSC)','PUSC',3.55,'V:PUSC'),('Otros-a','OTROS',1.8,''),('Otros-b','OTROS',1.8,''),('Otros-c','OTROS',1.8,''),('Otros-d','OTROS',1.85,'')],'Toledo (PUSC)')
add('CR-2010',[('Chinchilla (PLN)','PLN',46.91,'V:PLN'),('Solís (PAC)','PAC',25.1,'V:PAC'),('Guevara (ML)','OTROS',20.9,'V:PML'),('Fishman (PUSC)','PUSC',3.9,'V:PUSC'),('Otros','OTROS',3.19,'')],'Chinchilla (PLN)')
add('CR-2014',[('Solís (PAC)','PAC',30.64,'V:PAC'),('Araya (PLN)','PLN',29.71,'V:PLN'),('Villalta (FA)','OTROS',17.09,'V:FA'),('Guevara (ML)','OTROS',11.3,'V:PML'),('Hernández (PUSC)','PUSC',6.0,'V:PUSC'),('Avendaño (PRN)','OTROS',1.6,'V:PRN'),('Otros','OTROS',3.66,'')],'Araya (PLN)')
add('CR-2018',[('Alvarado Muñoz (PRN)','PRN',24.99,'V:PRN'),('Alvarado Quesada (PAC)','PAC',21.63,'V:PAC'),('Álvarez (PLN)','PLN',18.6,'V:PLN'),('Piza (PUSC)','PUSC',16.0,'V:PUSC'),('Castro (PIN)','OTROS',9.5,'V:PIN'),('Otros-a','OTROS',4.64,''),('Otros-b','OTROS',4.64,'')],'Alvarado Quesada (PAC)')
add('CR-2022',[('Figueres (PLN)','PLN',27.2,'C:5501'),('Chaves (PPSD)','PPSD',16.8,'J:1.0:juicio_analista_populismo_derecha_pendiente'),('Alvarado (Nueva República)','PRN',14.7,'C:5502'),('Feinzaig (PLP)','OTROS',12.4,'C:5508'),('Saborío (PUSC)','PUSC',12.4,'C:5504'),('Villalta (FA)','OTROS',8.7,'C:5507'),('Ramos (PAC)','PAC',0.66,'C:5503'),('Otros-a','OTROS',2.5,''),('Otros-b','OTROS',2.5,''),('Otros-c','OTROS',2.3,'')],'Ramos (PAC)')
add('CR-2026',[('Fernández (PPSO)','PPSO',48.30,'J:1.0:juicio_analista_continuidad_Chaves_pendiente'),('Ramos (PLN)','PLN',33.44,'C:5501'),('Dobles (CAC)','OTROS',4.85,'J:-0.5:juicio_analista_pendiente'),('Robles (FA)','OTROS',3.76,'C:5507'),('Hidalgo (PUSC)','PUSC',2.79,'C:5504'),('Otros','OTROS',6.86,'')],'Fernández (PPSO)')
# ---- Panamá ----
add('PA-1994',[('Pérez Balladares (PRD)','PRD',33.3,'V:PRD'),('Moscoso (Arnulfista)','PANAMENISTA',29.09,'V:PPA'),('Blades (MPT)','OTROS',17.13,'J:-0.5:juicio_analista_pendiente'),('Carles (otros)','OTROS',15.9,''),('Lewis Galindo (Solidaridad)','SOLIDARIDAD',1.73,'V:PS'),('Otros','OTROS',2.85,'')],'Lewis Galindo (Solidaridad)')
add('PA-1999',[('Moscoso (Arnulfista)','PANAMENISTA',44.8,'V:PPA'),('Torrijos (PRD)','PRD',37.82,'V:PRD'),('Vallarino (Unión por Panamá)','OTROS',17.4,'V:MOLIRENA')],'Torrijos (PRD)')
add('PA-2004',[('Torrijos (PRD)','PRD',47.44,'V:PRD'),('Endara (Solidaridad)','SOLIDARIDAD',30.92,'V:PS'),('Alemán (Arnulfista)','PANAMENISTA',16.38,'V:PPA'),('Martinelli (CD)','CD',5.3,'V:CD')],'Alemán (Arnulfista)')
add('PA-2009',[('Martinelli (CD-Panameñista)','CD',60.03,'V:CD'),('Herrera (PRD)','PRD',37.65,'V:PRD'),('Endara (Solidaridad)','SOLIDARIDAD',2.32,'')],'Herrera (PRD)')
add('PA-2014',[('Varela (Panameñista)','PANAMENISTA',39.07,'V:PPA'),('Arias (CD)','CD',31.38,'V:CD'),('Navarro (PRD)','PRD',28.14,'V:PRD'),('Otros','OTROS',1.41,'')],'Arias (CD)')
add('PA-2019',[('Cortizo (PRD)','PRD',33.35,'V:PRD'),('Roux (CD)','CD',31.00,'V:CD'),('Lombana (indep.)','OTROS',18.78,'J:0.0:juicio_analista_independiente_pendiente'),('Blandón (Panameñista)','PANAMENISTA',10.84,'V:PPA'),('Gómez (indep.)','OTROS',4.77,''),('Méndez (FAD)','OTROS',0.69,'J:-2.0:juicio_analista_pendiente'),('Ameglio (indep.)','OTROS',0.58,'')],'Blandón (Panameñista)')
add('PA-2024',[('Mulino (RM)','OTROS',34.23,'J:1.0:juicio_analista_RM_derecha_pendiente'),('Lombana (MOCA)','OTROS',24.59,'J:0.0:juicio_analista_independiente_pendiente'),('Torrijos (PP)','OTROS',16.03,'J:-0.5:juicio_analista_pendiente'),('Roux (CD-Panameñista)','CD',11.38,'W:CD'),('Rodríguez (indep.)','OTROS',6.61,''),('Carrizo (PRD)','PRD',5.88,'W:PRD'),('Gordón (indep.)','OTROS',1.08,'J:-1.5:juicio_analista_pendiente'),('Arrocha (indep.)','OTROS',0.20,'')],'Carrizo (PRD)')
c=pd.DataFrame(C,columns=['id_eleccion','candidato','familia','share','es_oficialismo','tag'])
c['pais']=c.id_eleccion.str[:2]; c['anio']=c.id_eleccion.str[3:].astype(int)
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
c0=pd.read_csv(F+'candidatos_ampliacion.csv'); c0=c0[~c0.id_eleccion.str[:2].isin(ISO)]
pd.concat([c0,c.drop(columns=['pais','anio'])]).to_csv(F+'candidatos_ampliacion.csv',index=False)
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
TRAD={'MX':['PRI','PAN','PRD'],'CR':['PLN','PUSC'],'PA':['PRD','PANAMENISTA']}
E['of_tradicional']=E.apply(lambda r:(int(r.familia_of in TRAD[r.pais]) if isinstance(r.familia_of,str) else np.nan),axis=1)
E['of_tradicional_x_pre2000']=E.of_tradicional*(E.anio<2000)
E0=pd.read_csv(F+'competencia_ampliacion.csv'); E0=E0[~E0.pais.isin(ISO)]
pd.concat([E0,E]).to_csv(F+'competencia_ampliacion.csv',index=False)
tr=pd.read_csv(F+'partidos_tradicionales.csv'); tr=tr[~tr.pais.isin(TRAD)]
pd.concat([tr,pd.DataFrame([(p,f) for p,l in TRAD.items() for f in l],columns=tr.columns)]).to_csv(F+'partidos_tradicionales.csv',index=False)
cols=['enc','n_cand_1pct','n_cand_5pct','hhi_top1','n_fuertes_cercanos','share_fuertes_cercanos','cobertura_ideologia','familia_of','top2_familias','of_top2_eleccion_previa','of_n_top2_previas','of_tradicional','of_tradicional_x_pre2000','ideologia_of','ideologia_of_n']
n=n.merge(E[['pais','anio']+cols],on=['pais','anio'],how='left')
# ---------------- 6. Unir al panel ----------------
P=pd.read_csv(F+'panel_modelo_eleccion.csv'); P=P[~P.pais.isin(ISO)]
n=n.drop(columns=['nota_codificacion']); n['fecha']=n.fecha.dt.strftime('%Y-%m-%d')
out=pd.concat([P,n],ignore_index=True); out.to_csv(F+'panel_modelo_eleccion.csv',index=False)
n[['id_eleccion','pais','anio','vuelta','fecha','presidente_en_ejercicio','y_share_nacional','oficialismo_dudoso']].to_csv(F+'ampliacion2_codificacion_oficialismo.csv',index=False)
print(out.shape)
print(n[['id_eleccion','y_share_nacional','familia_of','ideologia_of','enc','n_cand_5pct','hhi_top1','n_fuertes_cercanos','of_tradicional','of_n_top2_previas','aprob_ead_ult','aprob_ead_gap_dias','lb_aprob','lb_anio','bm_crecimiento_pib_tm1','bm_inflacion_ipc_tm1','pobnac_685_tm1','d_pobnac_685_mandato']].round(2).to_string())
