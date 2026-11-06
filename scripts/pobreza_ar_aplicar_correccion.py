# Se ejecuta DESPUES de pobreza_wb_nacional.py. Reemplaza la pobreza nacional de Argentina por la estimacion con microdatos EPH + IPC empalmado donde ambos extremos del mandato son comparables.
import pandas as pd, numpy as np
F='final/'
m=pd.read_csv(F+'pobreza_argentina_micro_corregida.csv').set_index('anio').pobreza_micro_685eq
ELE={2011:(2010,2006),2015:(2014,2010),2019:(2018,2014),2023:(2022,2018)}   # eleccion -> (año fin, año inicio)
def aplicar(p):
    for c in ['pobnac_685_tm1_bm_original','d_pobnac_685_mandato_bm_original','pobnac_correccion_micro']:
        if c in p.columns: p=p.drop(columns=c)
    p['pobnac_685_tm1_bm_original']=p['pobnac_685_tm1']; p['d_pobnac_685_mandato_bm_original']=p['d_pobnac_685_mandato']
    p['pobnac_correccion_micro']=pd.Series([None]*len(p),dtype=object)
    for a,(fin,ini) in ELE.items():
        k=(p.pais=='AR')&(p.anio==a)
        p.loc[k,'pobnac_685_tm1']=m[fin]; p.loc[k,'pobnac_685_eleccion_prev']=m[ini]; p.loc[k,'d_pobnac_685_mandato']=round(m[fin]-m[ini],2)
        p.loc[k,'pobnac_685_tm1_tipo']='microdatos_EPH'; p.loc[k,'pobnac_correccion_micro']='EPH_microdatos_IPC_empalmado'
    return p
for f in ['panel_modelo_region.csv','panel_modelo_eleccion.csv','pobreza_nacional_bm_por_eleccion.csv']:
    p=pd.read_csv(F+f)
    if f.startswith('pobreza_nacional'): 
        p=p.rename(columns={}) 
    p=aplicar(p); p.to_csv(F+f,index=False)
e=pd.read_csv(F+'panel_modelo_eleccion.csv')
print(e[(e.pais=='AR')][['anio','pobnac_685_tm1','pobnac_685_tm1_bm_original','d_pobnac_685_mandato','d_pobnac_685_mandato_bm_original','pobnac_correccion_micro']].round(1).to_string())
