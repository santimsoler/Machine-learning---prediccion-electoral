"""Ampliación del panel con Bolivia, Paraguay y Ecuador (capa nacional + regional Bolivia).
Entradas: data_ampliacion/*, ead/M-G et al CPS.tab. Idempotente: parte de final_bak/ (panel original de 6 países)."""
import pandas as pd, numpy as np, re
F='final/'; D='data_ampliacion/'
ISO={'BO':'BOL','PY':'PRY','EC':'ECU'}
# ---------------- 1. Banco Mundial ----------------
wb=pd.read_csv(D+'wb_bol_pry_ecu.csv')
rows=[]
for l in open(D+'wb_crecimiento_bol_pry_ecu.txt'):
    m=re.match(r'^(BOL|PRY|ECU),(\d{4}),(crecimiento_pib),(-?[\d.]+)$',l.strip())
    if m: rows.append((m[1],int(m[2]),m[3],float(m[4])))
wb=wb[pd.to_numeric(wb.anio,errors='coerce').notna()].copy()
wb['anio']=wb.anio.astype(int); wb['valor']=wb.valor.astype(float)
wb=pd.concat([wb.dropna(),pd.DataFrame(rows,columns=wb.columns)]).drop_duplicates(['pais','anio','indicador'])
wb=wb[wb.pais.isin(ISO.values())]
pob0=pd.read_csv('final_bak/wdi_pobreza_gini.csv'); pob0=pob0[~pob0.pais.isin(ISO.values())]
pobw=wb[wb.indicador.isin(['pob_6.85usd','pob_3.65usd','gini'])]
pd.concat([pob0,pobw]).to_csv('wb/wdi_pobreza_gini.csv',index=False)
m0=pd.read_csv('final_bak/macro_anual_bm.csv'); m0=m0[~m0.pais.isin(ISO.values())]
mm=wb[~wb.indicador.isin(['pob_6.85usd','pob_3.65usd','gini'])].rename(columns={'indicador':'variable','valor':'valor'})
mm['variable']=mm.variable.replace({'tc_oficial_lcu_usd':'tc_oficial_lcu_usd'}); mm['fuente']='Banco Mundial WDI'; mm['ultima_actualizacion']='2026-11-04'
pd.concat([m0,mm[m0.columns]]).to_csv(F+'macro_anual_bm.csv',index=False)
macro=mm.pivot_table(index=['pais','anio'],columns='variable',values='valor').reset_index()
# ---------------- 2. Elecciones nacionales (codificación manual) ----------------
# (id, pais, anio, vuelta, fecha, presidente, reeleccion, y_share, dudoso, nota)
N=[
('BO',1993,1,'1993-06-06','Paz Zamora',0,21.05,0,'Acuerdo Patriótico (Oscar Zamora, MIR-ADN)'),
('BO',1997,1,'1997-06-01','Sánchez de Lozada',0,18.20,0,'MNR (Juan Carlos Durán)'),
('BO',2002,1,'2002-06-30','Quiroga',0,3.40,1,'ADN (Ronald MacLean); Quiroga había asumido tras la renuncia de Banzer y no fue candidato'),
('BO',2009,1,'2009-12-06','Morales',1,64.22,0,'MAS-IPSP'),
('BO',2014,1,'2014-10-12','Morales',1,61.36,0,'MAS-IPSP'),
('BO',2019,1,'2019-10-20','Morales',1,47.08,0,'MAS-IPSP'),
('BO',2025,1,'2025-08-17','Arce',0,3.19,1,'MAS-IPSP (Eduardo del Castillo); Arce no fue candidato y el MAS se fracturó; share = suma departamental'),
('PY',1993,1,'1993-05-09','Rodríguez',0,41.63,0,'ANR-Colorado (Wasmosy); % sobre votos positivos calculado (la tabla fuente da 39,91 sobre el total con blancos/nulos)'),
('PY',1998,1,'1998-05-10','Wasmosy',0,55.35,0,'ANR-Colorado (Cubas Grau)'),
('PY',2003,1,'2003-04-27','González Macchi',0,38.30,0,'ANR-Colorado (Duarte Frutos); % sobre votos positivos calculado (oficial s/ total: 37,1)'),
('PY',2008,1,'2008-04-20','Duarte Frutos',0,30.82,0,'ANR-Colorado (Blanca Ovelar); % sobre votos positivos calculado desde votos (la tabla fuente da 31,02 con denominador inconsistente)'),
('PY',2013,1,'2013-04-21','Franco',0,39.09,0,'PLRA (Efraín Alegre), partido del presidente; % sobre votos positivos calculado (la tabla da 37,11 sobre el total con blancos/nulos)'),
('PY',2018,1,'2018-04-22','Cartes',0,48.96,0,'ANR-Colorado (Abdo Benítez)'),
('PY',2023,1,'2023-04-30','Abdo Benítez',0,42.74,0,'ANR-Colorado (Peña)'),
('EC',2009,1,'2009-04-26','Correa',1,51.99,0,'Alianza PAIS'),
('EC',2013,1,'2013-02-17','Correa',1,57.17,0,'Alianza PAIS'),
('EC',2017,1,'2017-02-19','Correa',0,39.36,0,'Alianza PAIS (Lenín Moreno)'),
('EC',2017,2,'2017-04-02','Correa',0,51.16,0,'Alianza PAIS (Lenín Moreno)'),
('EC',2021,1,'2021-02-07','Moreno',0,1.54,1,'Alianza PAIS (Ximena Peña), partido de Moreno, que se distanció de él; Moreno no declaró apoyo explícito a ningún candidato. Peña apoyó a Arauz en el balotaje'),
('EC',2025,1,'2025-02-09','Noboa',1,44.17,0,'ADN (Daniel Noboa)'),
('EC',2025,2,'2025-04-13','Noboa',1,55.63,0,'ADN (Daniel Noboa)'),
]
n=pd.DataFrame(N,columns=['pais','anio','vuelta','fecha','presidente_en_ejercicio','oficialismo_va_por_reeleccion','y_share_nacional','oficialismo_dudoso','nota_codificacion'])
n['id_eleccion']=n.pais+'-'+n.anio.astype(str)+'-PRES-'+n.vuelta.astype(str); n['fecha']=pd.to_datetime(n.fecha)
n['estado_codificacion']='ampliacion_codificacion_manual_wikipedia_PDBA_sin_revision_analista'
# todas las elecciones (incluye sin oficialista) para calcular mandatos
EY={'BO':[1993,1997,2002,2005,2009,2014,2019,2020,2025],'PY':[1993,1998,2003,2008,2013,2018,2023],'EC':[1996,1998,2002,2006,2009,2013,2017,2021,2023,2025]}
# ---------------- 3. Aprobación EAD y Latinobarómetro ----------------
ead=pd.read_csv('ead/M-G et al CPS.tab',sep='\t',low_memory=False)
ead=ead[ead.country_name.isin(['Bolivia','Ecuador','Paraguay'])].copy(); ead['pais']=ead.country_name.map({'Bolivia':'BO','Ecuador':'EC','Paraguay':'PY'})
ead['qtr']=pd.to_datetime(ead.qtr)
def ead_feat(p,f):
    d=ead[(ead.pais==p)&(ead.qtr<=f)].sort_values('qtr'); nan={'aprob_ead_ult':np.nan,'aprob_ead_media4':np.nan,'aprob_ead_gap_dias':np.nan,'inflacion_trim_ead':np.nan,'crec_trim_ead':np.nan}
    if d.empty: return pd.Series(nan)
    gap=(f-d.iloc[-1].qtr).days
    if gap>250: nan['aprob_ead_gap_dias']=gap; return pd.Series(nan)
    return pd.Series({'aprob_ead_ult':d.iloc[-1].Approval_Smoothed,'aprob_ead_media4':d.tail(4).Approval_Smoothed.mean(),'aprob_ead_gap_dias':gap,'inflacion_trim_ead':d.tail(4).q_inflation.mean(),'crec_trim_ead':d.tail(4).q_growth.mean()})
n=pd.concat([n,n.apply(lambda x:ead_feat(x.pais,x.fecha),axis=1)],axis=1)
n['aprobacion_oficial']=n.aprob_ead_ult; n['aprobacion_fuente']=np.where(n.aprob_ead_ult.notna(),'EAD','sin_dato')
lb=pd.read_csv(D+'lb_ampliacion_raw.csv'); lb=lb[lb.pais.isin(ISO)]
def lbf(p,f):
    y=f.year if f.month==12 else f.year-1
    d=lb[(lb.pais==p)&(lb.anio<=y)].sort_values('anio')
    return pd.Series({'lb_aprob':d.iloc[-1].aprueba_pct_sobre_respuestas,'lb_anio':d.iloc[-1].anio}) if len(d) else pd.Series({'lb_aprob':np.nan,'lb_anio':np.nan})
n=pd.concat([n,n.apply(lambda x:lbf(x.pais,x.fecha),axis=1)],axis=1); n['lb_rezago_anios']=n.fecha.dt.year-n.lb_anio
# ---------------- 4. Macro y pobreza ----------------
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
for p,yrs in EY.items():
    for i,y in enumerate(yrs):
        r={'pais':p,'anio':y,'anios_mandato':(y-yrs[i-1]) if i else np.nan}
        for ind,nm in [('pob_6.85usd','685'),('pob_3.65usd','365')]:
            s=serie(ISO[p],ind); fin,t=val(s,y-1); r[f'pobnac_{nm}_tm1']=fin; r[f'pobnac_{nm}_tm1_tipo']=t
            if i:
                ini,_=val(s,yrs[i-1]-1); r[f'pobnac_{nm}_eleccion_prev']=ini; r[f'd_pobnac_{nm}_mandato']=fin-ini if pd.notna(fin) and pd.notna(ini) else np.nan
        pr.append(r)
pr=pd.DataFrame(pr)
n=n.merge(pr[['pais','anio','anios_mandato','pobnac_685_tm1','pobnac_685_tm1_tipo','pobnac_685_eleccion_prev','d_pobnac_685_mandato','pobnac_365_tm1','d_pobnac_365_mandato']],on=['pais','anio'],how='left')
n['anio_c']=(n.anio-2000)/10; n['pre2000']=(n.anio<2000).astype(int)
n['ampliacion']=1
# ---------------- 5. Regional Bolivia ----------------
rr=[]
for l in open(D+'bolivia_regional_votos.txt'):
    p=l.rstrip('\n').split(',')
    if len(p)>=4 and re.match(r'^\d{4}(-\d)?$',p[0]) and p[-1].strip().isdigit(): rr.append((p[0],p[1],','.join(p[2:-1]),int(p[-1])))
b=pd.DataFrame(rr,columns=['clave','region','cand','votos']); b=b[b.region!='Exterior']
OF={'2009':'MAS-IPSP','2014':'MAS-IPSP','2019':'MAS-IPSP','2025-1':'MAS-IPSP'}
reg=[]
for k,mk in OF.items():
    g=b[b.clave==k]; yr=int(k[:4]); iid=f'BO-{yr}-PRES-1'
    for rg,h in g.groupby('region'):
        tot=h.votos.sum(); of=h[h.cand.str.contains(mk)].votos.sum(); otros=h[~h.cand.str.contains(mk)].groupby('cand').votos.sum().max()
        reg.append({'id_eleccion':iid,'region':rg,'votos_validos':tot,'y_share_oficialismo':100*of/tot,'y_gana_region':int(of>otros)})
reg=pd.DataFrame(reg).merge(n.drop(columns=['nota_codificacion']),on='id_eleccion',how='left')
reg['y_desvio_regional']=reg.y_share_oficialismo-reg.y_share_nacional
# ---------------- 6. Unir a los paneles originales ----------------
e0=pd.read_csv('final_bak/panel_modelo_eleccion.csv'); e0['ampliacion']=0
r0=pd.read_csv('final_bak/panel_modelo_region.csv'); r0['ampliacion']=0
def fecha_fmt(df): df['fecha']=pd.to_datetime(df.fecha).dt.strftime('%Y-%m-%d'); return df
E=fecha_fmt(pd.concat([e0,n.drop(columns=['nota_codificacion'])],ignore_index=True)); R=fecha_fmt(pd.concat([r0,reg],ignore_index=True))
E.to_csv(F+'panel_modelo_eleccion.csv',index=False); R.to_csv(F+'panel_modelo_region.csv',index=False)
n[['id_eleccion','pais','anio','vuelta','fecha','presidente_en_ejercicio','y_share_nacional','oficialismo_dudoso','nota_codificacion']].assign(fecha=lambda d:d.fecha.dt.strftime('%Y-%m-%d')).to_csv(F+'ampliacion_codificacion_oficialismo.csv',index=False)
print(E.shape,R.shape)
print(n[['id_eleccion','y_share_nacional','aprob_ead_ult','aprob_ead_gap_dias','lb_aprob','lb_anio','bm_crecimiento_pib_tm1','bm_inflacion_ipc_tm1','pobnac_685_tm1','d_pobnac_685_mandato']].round(1).to_string())
print(reg.groupby('id_eleccion').size())
