import pandas as pd
M={32:'AR',68:'BO',76:'BR',152:'CL',170:'CO',188:'CR',214:'DO',218:'EC',222:'SV',320:'GT',340:'HN',484:'MX',558:'NI',591:'PA',600:'PY',604:'PE',858:'UY',862:'VE'}
n=pd.read_csv('data_ampliacion/lb_2018_2020_2023.csv'); n['pais']=n.idenpa.map(M)
n=n.rename(columns={'pct_buena':'pct_buena_muy_buena','pct_mala':'pct_mala_muy_mala','percep':'balance_percep_econ'})[['pais','anio','pct_buena_muy_buena','pct_mala_muy_mala','balance_percep_econ','n']]
f='final/percepcion_economica_latinobarometro.csv'
o=pd.read_csv(f); o=o[o.anio<2018]
pd.concat([o,n]).sort_values(['pais','anio']).to_csv(f,index=False)
