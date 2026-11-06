import pandas as pd
A='/mnt/user-data/attachments/fbc2a8cf-9f07-5c94-8ce1-557ba4094ca9/'
base=pd.read_csv('final/confianza_consumidor_mensual.csv')
base=base[base.pais.isin(['CO','BR'])].rename(columns={'confianza_consumidor':'valor'})
base['variable']='confianza_consumidor_ocde'
base=base[['pais','periodo','variable','valor','unidad','fuente','notas']]
rows=[]
M={'ene':1,'feb':2,'mar':3,'abr':4,'may':5,'jun':6,'jul':7,'ago':8,'sep':9,'set':9,'oct':10,'nov':11,'dic':12}
def per(x):
    if isinstance(x,str):
        m,y=x.strip().lower().replace('.','').split('-'); return '%04d-%02d'%(2000+int(y),M[m[:3]])
    return pd.Timestamp(x).strftime('%Y-%m')
# Argentina: Di Tella ICC (convertido de .xls a .xlsx con LibreOffice)
d=pd.read_excel('lb/icc.xlsx',sheet_name='Desagregación por subíndices',header=None,skiprows=3)
for _,r in d.iterrows():
    if pd.isna(r[0]): continue
    p=per(r[0])
    for col,v in [(1,'icc_situacion_personal'),(3,'icc_situacion_macro'),(5,'icc_bienes_durables'),(7,'icc_nacional')]:
        if pd.notna(r[col]): rows.append(('AR',p,v,float(r[col]),'índice (0-100)','Universidad Torcuato Di Tella, ICC (archivo Serie_ICC_10-26.xls aportado por el usuario)',''))
d=pd.read_excel('lb/icc.xlsx',sheet_name='Desagregación por regiones',header=None,skiprows=3)
for _,r in d.iterrows():
    if pd.isna(r[0]) or pd.isna(r[7]): continue
    p=per(r[0])
    if p<'2001-03': rows.append(('AR',p,'icc_nacional',float(r[7]),'índice (0-100)','UTDT ICC (hoja regiones)',''))
# Chile: IPEC (Banco Central de Chile, Adimark/GfK)
c=pd.read_excel(A+'820e1462-EXE_IPEC_01_M2.xlsx',sheet_name='Cuadro',header=None,skiprows=3)
names=['ipec_personal_actual','ipec_pais_actual','ipec_pais_12m','ipec_pais_5a','ipec_expectativas_consumo','ipec']
for _,r in c.iterrows():
    try: p=per(r[0])
    except Exception: continue
    for i,n in enumerate(names,1):
        if pd.notna(r[i]): rows.append(('CL',p,n,float(r[i]),'índice (0-100)','Banco Central de Chile, base estadística (IPEC Adimark/GfK), archivo EXE_IPEC_01_M2.xlsx aportado por el usuario',''))
add=pd.DataFrame(rows,columns=base.columns)
out=pd.concat([base,add]).drop_duplicates(['pais','periodo','variable']).sort_values(['pais','variable','periodo'])
out.to_csv('final/confianza_consumidor_mensual.csv',index=False)
print(out.groupby(['pais','variable']).periodo.agg(['min','max','count']))
