import pandas as pd, numpy as np
F='final/'
t=open('wb/salida_colab.txt',encoding='utf-8').read().split('\n')
i=[k for k,l in enumerate(t) if l.startswith('periodo,exp_economia_12m')][0]
M={'Ene':1,'Feb':2,'Mar':3,'Abr':4,'May':5,'Jun':6,'Jul':7,'Ago':8,'Sep':9,'Oct':10,'Nov':11,'Dic':12}
rows=[]
for l in t[i+1:]:
    if not l.strip(): break
    per,a,b=l.split(','); m,y=per.split('.'); P=f'{int(y)}-{M[m]:02d}'
    for var,v in (('bcrp_exp_economia_12m',a),('bcrp_exp_sector_12m',b)):
        if v!='n.d.': rows.append(('PE',P,var,float(v),'indice','BCRP, Gerencia Central de Estudios Economicos (BCRPData PD37981AM / PD39752AM)','Expectativas EMPRESARIALES a 12 meses, no de consumidores: aproximacion'))
n=pd.DataFrame(rows,columns=['pais','periodo','variable','valor','unidad','fuente','notas'])
c=pd.read_csv(F+'confianza_consumidor_mensual.csv'); c=c[~((c.pais=='PE')&c.variable.str.startswith('bcrp'))]
pd.concat([c,n]).to_csv(F+'confianza_consumidor_mensual.csv',index=False)
d=n[n.variable=='bcrp_exp_economia_12m'].copy(); d['per']=pd.PeriodIndex(d.periodo,freq='M'); d=d.set_index('per').valor
def cc(fecha):
    p=pd.Period(fecha,'M')-1
    w=d[(d.index<=p)&(d.index>p-3)]; w12=d[(d.index<=p-12)&(d.index>p-15)]; h=d[d.index<=p]
    return w.mean(), (w.mean()-w12.mean()) if len(w12)>=2 else np.nan, (w.mean()-h.mean())/h.std()
for f in ['panel_modelo_region.csv','panel_modelo_eleccion.csv']:
    p=pd.read_csv(F+f)
    p['cc_aproximacion']=pd.Series([None]*len(p),dtype=object)
    m=p.pais=='PE'
    if f=='panel_modelo_region.csv': fe=pd.to_datetime(p.loc[m,'fecha'])
    else: fe=pd.to_datetime(p.loc[m,'fecha'])
    vals=[cc(x) for x in fe]
    p.loc[m,'cc_3m']=[v[0] for v in vals]; p.loc[m,'cc_var12m']=[v[1] for v in vals]; p.loc[m,'cc_z']=[v[2] for v in vals]
    p.loc[m,'cc_aproximacion']='expectativas_empresariales_BCRP'
    p.to_csv(F+f,index=False)
    print(f, p[m][['id_eleccion','fecha','cc_3m','cc_var12m','cc_z']].drop_duplicates().round(2).to_string())
p=pd.read_csv(F+'panel_modelo_region.csv'); print(p.groupby('pais').cc_3m.apply(lambda s:s.notna().mean()).round(2).to_dict())
