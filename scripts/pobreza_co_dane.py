import pandas as pd, numpy as np, unicodedata, re, warnings
warnings.filterwarnings('ignore')
D='co/'; F='final/'
def key(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().upper().strip()
    s=re.sub(r'[^A-Z ]',' ',s); s=re.sub(r'\s+',' ',s).strip()
    M={'BOGOTA D C':'BOGOTA','BOGOTA':'BOGOTA','STAFE DE BOGOTA D C':'BOGOTA','VALLE DEL CAUCA':'VALLE','N DE SANTANDER':'NORTE DE SANTANDER',
       'NORTE DE SAN':'NORTE DE SANTANDER','SAN ANDRES Y PROVIDENCIA':'SAN ANDRES','ARCHIPIELAGO DE SAN ANDRES':'SAN ANDRES','GUAJIRA':'LA GUAJIRA',
       'BOLIVAR 1':'BOLIVAR','CAUCA 1':'CAUCA','CORDOBA 1 3':'CORDOBA','CHOCO 2':'CHOCO','NARI O':'NARINO'}
    if s.startswith('NARI'): return 'NARINO'
    return M.get(s,s)
rows=[]
# NBI 1993: bloques por departamento, fila TOTAL; Bogota una sola fila
a=pd.read_excel(D+'nbi_1993.xlsx',header=None)
cur=None
for _,r in a.iterrows():
    if pd.notna(r[0]) and pd.isna(r[1]) and pd.isna(r[2]) and isinstance(r[0],str) and r.index.size and cur is not None or (pd.notna(r[0]) and isinstance(r[0],str) and pd.isna(r[1]) and pd.isna(r[2]) and pd.isna(r[3])):
        cur=r[0]
    if cur and str(r[2]).strip().upper()=='TOTAL' and pd.notna(r[3]): rows.append(('1993',key(cur),float(r[3]),np.nan))
    if cur and key(cur)=='BOGOTA' and str(r[2]).strip()=='Bogotá': rows.append(('1993','BOGOTA',float(r[3]),np.nan))
# NBI 2005
b=pd.read_excel(D+'nbi_2005.xlsx','Departamentos',header=None)
for _,r in b.iloc[6:].iterrows():
    if pd.isna(r[1]) or str(r[0]).startswith('Fuente') or str(r[1]).startswith('TOTAL'): continue
    try: rows.append(('2005',key(r[1]),float(r[30]),float(r[32])))
    except: pass
# NBI 2018 (hoja Departamento, actualizacion feb-2021)
c=pd.read_excel(D+'nbi_2018.xlsx','Departamento',header=None)
for _,r in c.iloc[10:].iterrows():
    if pd.isna(r[1]) or 'TOTAL' in str(r[1]): continue
    try: rows.append(('2018',key(r[1]),float(r[2]),float(r[3])))
    except: pass
nbi=pd.DataFrame(rows,columns=['ola','dpto','nbi','miseria']).drop_duplicates(['ola','dpto'])
nbi=nbi[nbi.dpto.isin(set(nbi[nbi.ola=='1993'].dpto))].copy()
nbi['nbi_z']=nbi.groupby('ola').nbi.transform(lambda s:(s-s.mean())/s.std())
nbi['nbi_pctrank']=nbi.groupby('ola').nbi.rank(pct=True)
# Pobreza monetaria 2024
xl=pd.ExcelFile(D+'pm_2024.xlsx')
def hoja(s,col):
    d=xl.parse(s,header=None).iloc[11:36,:5]; d.columns=['dpto','y2021','y2022','y2023','y2024']
    d=d[d.dpto.notna()]; d['dpto']=d.dpto.map(key); return d[['dpto','y2024']].rename(columns={'y2024':col})
pm=hoja('Pobreza Monetaria Act.Met.','co_pobreza_monetaria_2024').merge(hoja('Gini','co_gini_2024'),on='dpto').merge(hoja('Ingpc Act.Met.','co_ingpc_2024'),on='dpto')
nac=pm[pm.dpto=='TOTAL NACIONAL'].iloc[0]
pm['co_pobreza_monetaria_rel']=pm.co_pobreza_monetaria_2024/nac.co_pobreza_monetaria_2024
pm['co_ingpc_rel']=pm.co_ingpc_2024/nac.co_ingpc_2024
pm=pm[pm.dpto!='TOTAL NACIONAL']
OLA={1998:'1993',2006:'2005',2010:'2005',2014:'2005',2026:'2018'}
out=nbi.copy(); out['fuente']='DANE censos NBI'
out.to_csv(F+'pobreza_colombia_nbi_dane.csv',index=False)
pm['fuente']='DANE GEIH pobreza monetaria departamental 2024 (act. metodologica)'
pm.to_csv(F+'pobreza_colombia_monetaria_2024_dane.csv',index=False)
p=pd.read_csv(F+'panel_modelo_region.csv')
p=p.drop(columns=[c for c in p.columns if c.startswith('co_')],errors='ignore')
p['_k']=p.region.map(key); p['_ola']=p.anio.map(OLA)
m=p.pais.eq('CO')
n=nbi.rename(columns={'nbi':'co_nbi','miseria':'co_nbi_miseria','nbi_z':'co_nbi_z','nbi_pctrank':'co_nbi_pctrank','ola':'_ola','dpto':'_k'})
p=p.merge(n,on=['_k','_ola'],how='left')
for c in ['co_nbi','co_nbi_miseria','co_nbi_z','co_nbi_pctrank']: p.loc[~m,c]=np.nan
p['co_nbi_ola']=np.where(m,p._ola,None)
q=pm.drop(columns='fuente').rename(columns={'dpto':'_k'})
p=p.merge(q,on='_k',how='left')
for c in q.columns[1:]: p.loc[~(m&(p.anio==2026)),c]=np.nan
p=p.drop(columns=['_k','_ola'])
p.to_csv(F+'panel_modelo_region.csv',index=False)
c=p[p.pais=='CO']
print(c.groupby('anio').agg(n=('region','count'),nbi=('co_nbi','count'),pm=('co_pobreza_monetaria_2024','count')))
print(c[c.co_nbi.isna()].region.unique())
print(sorted(set(nbi[nbi.ola=='1993'].dpto)),len(nbi[nbi.ola=='1993']),len(nbi[nbi.ola=='2005']),len(nbi[nbi.ola=='2018']))
print(c[(c.anio==2026)&(c.vuelta==1)][['region','y_share_oficialismo','co_nbi','co_pobreza_monetaria_2024','co_ingpc_rel']].sort_values('co_nbi').to_string())
