"""Voto regional a la izquierda, ideología media del voto y pobreza relativa regional para Bolivia (2009-2025) y Paraguay 2023.
Pobreza Bolivia: UDAPE, pobreza moderada por departamento (EH), 2011-2018. Pobreza Paraguay: data_ampliacion/py_pobreza_departamento.csv (opcional; columnas region,valor,medida,anio)."""
import pandas as pd, numpy as np, csv, re, os
F='final/'; D='data_ampliacion/'
c=pd.read_csv(F+'candidatos_ampliacion.csv')
# ---------- votos por candidato y región ----------
b=pd.read_csv(D+'bo_reg_largo.csv'); b=b[(b.dep!='Exterior')&(b.clave.isin(['2009','2014','2019','2025-1']))]
b['id_eleccion']='BO-'+b.clave.str[:4]+'-PRES-1'; b=b.rename(columns={'dep':'region','cand':'candidato'})[['id_eleccion','region','candidato','votos']]
def num(t):
    t=t.strip().replace(' ','')
    if re.fullmatch(r'\d{1,3}\.\d{3}',t): t=t.replace('.','')
    return float(t)
NOM=['Peña (ANR)','Alegre (Concertación)','Cubas (Cruzada Nacional)','Acevedo (Nueva República)','Chilavert','Otros']
rows=[]
for p in csv.reader(open(D+'paraguay_2023_regional.txt',encoding='utf-8')):
    if len(p)<17 or p[0].startswith('Fuente'): continue
    reg=p[0].replace('P. Hayes','Presidente Hayes')
    for k,i in enumerate((1,3,5,7,9,11)): rows.append(('PY-2023-PRES-1',reg,NOM[k],num(p[i])))
py=pd.DataFrame(rows,columns=b.columns)
v=pd.concat([b,py]).merge(c[['id_eleccion','candidato','e_cont']].assign(id_eleccion=lambda d:d.id_eleccion+'-PRES-1'),on=['id_eleccion','candidato'],how='left')
v['izq']=np.where(v.e_cont<-0.5,v.votos,0); v['ide_w']=v.e_cont*v.votos; v['v_con']=np.where(v.e_cont.notna(),v.votos,0)
g=v.groupby(['id_eleccion','region']).agg(izq=('izq','sum'),ide_w=('ide_w','sum'),v_con=('v_con','sum'),vv=('votos','sum')).reset_index()
g['cobertura_ideo']=g.v_con/g.vv; g['y_share_izquierda']=100*g.izq/g.vv; g['ideologia_voto_media']=g.ide_w/g.v_con
g.loc[g.cobertura_ideo<0.8,['y_share_izquierda','ideologia_voto_media']]=np.nan
# ---------- pobreza ----------
UD={'Chuquisaca':{2011:64.8,2013:58.0,2018:47.4},'La Paz':{2011:44.7,2013:43.5,2018:37.6},'Cochabamba':{2011:43.4,2013:41.1,2018:32.9},'Oruro':{2011:47.9,2013:31.3,2018:33.8},'Potosí':{2011:65.8,2013:57.3,2018:52.0},'Tarija':{2011:42.7,2013:19.7,2018:28.8},'Santa Cruz':{2011:35.6,2013:28.2,2018:26.1},'Beni':{2011:48.1,2013:41.5,2018:39.9},'Pando':{2011:40.1,2013:35.6,2018:32.1}}
AN={'BO-2009-PRES-1':2011,'BO-2014-PRES-1':2013,'BO-2019-PRES-1':2018,'BO-2025-PRES-1':2018}
pob=[]
for e,a in AN.items():
    for r,s in UD.items(): pob.append((e,r,s[a],'pobreza_moderada_UDAPE_EH',a))
pf=D+'py_pobreza_departamento.csv'
if os.path.exists(pf):
    q=pd.read_csv(pf)
    for _,r in q.iterrows(): pob.append(('PY-2023-PRES-1',r.region,r.valor,r.medida,r.anio))
pob=pd.DataFrame(pob,columns=['id_eleccion','region','pobrel_medida','pobrel_medida_nombre','pobrel_anio_dato'])
pob['pobrel_pctrank']=pob.groupby('id_eleccion').pobrel_medida.rank(pct=True)
# ---------- escribir ----------
R=pd.read_csv(F+'panel_modelo_region.csv')
cols=['y_share_izquierda','ideologia_voto_media','cobertura_ideo','pobrel_medida','pobrel_pctrank']
for k in ['pobrel_medida_nombre','pobrel_anio_dato']:
    if k not in R: R[k]=pd.Series([None]*len(R),dtype=object)
for df,cs in [(g,['y_share_izquierda','ideologia_voto_media','cobertura_ideo']),(pob,['pobrel_medida','pobrel_pctrank','pobrel_medida_nombre','pobrel_anio_dato'])]:
    K=R[['id_eleccion','region']].merge(df[['id_eleccion','region']+cs],on=['id_eleccion','region'],how='left')
    m=R.pais.isin(['BO','PY']).values
    for k in cs: R.loc[m,k]=K.loc[m,k].values
R.to_csv(F+'panel_modelo_region.csv',index=False)
x=R[R.pais.isin(['BO','PY'])].groupby('id_eleccion')[['y_share_oficialismo','y_share_izquierda','cobertura_ideo','pobrel_pctrank']].agg(lambda s:s.notna().mean()).round(2); print(x)
for e,d in R[R.pais.isin(['BO','PY'])].groupby('id_eleccion'):
    z=d[['pobrel_pctrank','y_share_oficialismo','y_share_izquierda']].dropna()
    if len(z)>4: print(e,len(z),'r(pob,of)=',round(z.corr().loc['pobrel_pctrank','y_share_oficialismo'],2),'r(pob,izq)=',round(z.corr().loc['pobrel_pctrank','y_share_izquierda'],2) if z.y_share_izquierda.notna().all() else '')
