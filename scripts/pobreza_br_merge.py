import pandas as pd, numpy as np
t=pd.read_csv('final/pobreza_relativa_brasil_pnad.csv').set_index(['ola','uf'])
OLA={2002:2001,2006:2005,2010:2009,2014:2013}
r=pd.read_csv('final/panel_modelo_region.csv')
r=r.drop(columns=[c for c in r.columns if c.startswith('pnad_')])
cols={'pnad_pobreza_rel50':'rel50','pnad_pobreza_rel60':'rel60','pnad_cuota_quintil1':'cuota_quintil1','pnad_ingreso_mediano_rel':'ingreso_mediano_rel'}
new={k:[] for k in list(cols)+['pnad_ola']}
for p,a,rg in zip(r.pais,r.anio,r.region):
    o=OLA.get(a)
    if p!='BR' or o is None or (o,rg) not in t.index:
        for k in new: new[k].append(np.nan)
        continue
    for k,c in cols.items(): new[k].append(t.loc[(o,rg),c])
    new['pnad_ola'].append(o)
r=pd.concat([r,pd.DataFrame(new,index=r.index)],axis=1); r.to_csv('final/panel_modelo_region.csv',index=False)
print(r[r.pais=='BR'].groupby('anio').pnad_pobreza_rel50.agg(['count','mean']).round(1))
