import pandas as pd, numpy as np
d=pd.concat([pd.read_csv('br/p2.csv.gz',dtype={'UF':str}),pd.read_csv('br/p1.csv.gz',dtype={'UF':str})])
UF={'11':'RO','12':'AC','13':'AM','14':'RR','15':'PA','16':'AP','17':'TO','21':'MA','22':'PI','23':'CE','24':'RN','25':'PB','26':'PE','27':'AL','28':'SE','29':'BA','31':'MG','32':'ES','33':'RJ','35':'SP','41':'PR','42':'SC','43':'RS','50':'MS','51':'MT','52':'GO','53':'DF'}
def wq(x,w,q):
    o=np.argsort(x.values); xs=x.values[o]; cw=np.cumsum(w.values[o]); return xs[np.searchsorted(cw,q*cw[-1])]
rows=[]
for ola,g in d.groupby('ola'):
    v=g[(g.V0401<6)&(g.ing_pc_V0401_lt6>0)&g.V4729.notna()].copy(); v['uf']=v.UF.map(UF)
    med=wq(v.ing_pc_V0401_lt6,v.V4729,.5); q1=wq(v.ing_pc_V0401_lt6,v.V4729,.2)
    tot=g[(g.V0401<6)&g.V4729.notna()]
    for r,x in list(v.groupby('uf'))+[('NACIONAL',v)]:
        w=x.V4729; s=w.sum(); i=x.ing_pc_V0401_lt6
        n_all=len(tot[tot.UF.map(UF)==r]) if r!='NACIONAL' else len(tot)
        rows.append(dict(ola=int(ola),uf=r,rel50=100*w[i<.5*med].sum()/s,rel60=100*w[i<.6*med].sum()/s,cuota_quintil1=100*w[i<=q1].sum()/s,
          ingreso_mediano_rel=wq(i,w,.5)/med,n_personas=len(x),pct_ingreso_cero_o_ausente_excluido=100*(1-len(x)/n_all)))
t=pd.DataFrame(rows); t['fuente']='IBGE PNAD microdatos (ftp.ibge.gov.br); ingreso mensual domiciliar V4721 / integrantes V0401<6; peso V4729; ingreso>0; cálculo propio'
t.to_csv('final/pobreza_relativa_brasil_pnad.csv',index=False)
print(t.pivot(index='uf',columns='ola',values='rel50').round(1).sort_values(2013).iloc[[0,1,2,-3,-2,-1]])
print(t[t.uf=='NACIONAL'][['ola','rel50','n_personas','pct_ingreso_cero_o_ausente_excluido']].round(1))
r=pd.read_csv('final/panel_modelo_region.csv'); print(sorted(r[r.pais=='BR'].anio.unique()), r[r.pais=='BR'].region.unique()[:30])
