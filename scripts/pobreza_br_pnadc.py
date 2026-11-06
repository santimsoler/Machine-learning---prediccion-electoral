import pandas as pd, numpy as np
e=pd.read_csv('final/brasil_ipea_estados.csv'); n=pd.read_csv('final/brasil_ipea_nacional.csv').rename(columns={'VALVALOR':'nac'})
UFN={'Rondônia':'RO','Acre':'AC','Amazonas':'AM','Roraima':'RR','Pará':'PA','Amapá':'AP','Tocantins':'TO','Maranhão':'MA','Piauí':'PI','Ceará':'CE','Rio Grande do Norte':'RN','Paraíba':'PB','Pernambuco':'PE','Alagoas':'AL','Sergipe':'SE','Bahia':'BA','Minas Gerais':'MG','Espírito Santo':'ES','Rio de Janeiro':'RJ','São Paulo':'SP','Paraná':'PR','Santa Catarina':'SC','Rio Grande do Sul':'RS','Mato Grosso do Sul':'MS','Mato Grosso':'MT','Goiás':'GO','Distrito Federal':'DF'}
e['uf']=e.TERNOME.map(UFN); print('sin mapear:',e[e.uf.isna()].TERNOME.unique())
m=e.merge(n,on=['serie','anio'],how='left'); m['rel']=m.VALVALOR/m.nac
P=m.pivot_table(index=['uf','anio'],columns='serie',values=['VALVALOR','rel'])
# consistencia con la PNAD 2013 calculada de microdatos (mediana relativa)
pn=pd.read_csv('final/pobreza_relativa_brasil_pnad.csv'); a=pn[(pn.ola==2013)&(pn.uf!='NACIONAL')].set_index('uf').ingreso_mediano_rel
b=P.xs(2013,level='anio')[('rel','SIS_RDPCMEDIANO')]
print('corr mediana relativa PNAD(micro) vs SIS 2013:',round(a.corr(b),3), ' dif media abs:',round((a-b).abs().mean(),3))
OLA={2014:2013,2018:2017,2022:2021,2026:2025}   # año de la última PNAD Contínua anual previa
r=pd.read_csv('final/panel_modelo_region.csv'); r=r.drop(columns=[c for c in r.columns if c.startswith('pnadc_')])
cols={'pnadc_tx_pobreza_nac':('VALVALOR','PNADCA_TXPNUF'),'pnadc_tx_pobreza_nac_rel':('rel','PNADCA_TXPNUF'),'pnadc_tx_pobreza_int':('VALVALOR','PNADCA_TXPIUF'),
      'pnadc_gini':('VALVALOR','PNADCA_GINIUF'),'pnadc_rdpc40':('VALVALOR','SIS_RDPC40'),'pnadc_ingreso_mediano_rel':('rel','SIS_RDPCMEDIANO')}
new={k:[] for k in list(cols)+['pnadc_anio']}
for p,a_,rg in zip(r.pais,r.anio,r.region):
    y=OLA.get(a_)
    if p!='BR' or y is None or (rg,y) not in P.index:
        for k in new: new[k].append(np.nan); 
        continue
    for k,c in cols.items():
        v=P.loc[(rg,y),c]
        if np.isnan(v) and y==2025 and 'MEDIANO' in c[1]: v=P.loc[(rg,2024),c]   # SIS llega a 2024
        new[k].append(v)
    new['pnadc_anio'].append(y)
r=pd.concat([r,pd.DataFrame(new,index=r.index)],axis=1)
# completar pnad_ingreso_mediano_rel con SIS donde no hay PNAD (2018+)
m_=r.pais.eq('BR')&r.pnad_ingreso_mediano_rel.isna()&r.pnadc_ingreso_mediano_rel.notna()
r.loc[m_,'pnad_ingreso_mediano_rel']=r.loc[m_,'pnadc_ingreso_mediano_rel']
r.to_csv('final/panel_modelo_region.csv',index=False)
c=r[(r.pais=='BR')]
print(c.groupby('anio')[['pnad_pobreza_rel50','pnad_ingreso_mediano_rel','pnadc_tx_pobreza_nac_rel','pnadc_gini']].count())
