import pandas as pd, numpy as np
d=pd.read_csv('eph/e.csv.gz',low_memory=False,usecols=['ola','REGION','PONDERA','IPCF'])
ip=pd.read_csv('final/ar_inflacion_mensual_2003_2026.csv'); ip['per']=pd.PeriodIndex(ip.periodo,freq='M'); ix=ip.set_index('per').indice_base_nov2003_100
WAVE={'2006T4':2006,'2010T4':2010,'2014T4':2014,'2018T4':2018,'2022T4':2022}
def idx(y): return ix[[pd.Period(f'{y}-10','M'),pd.Period(f'{y}-11','M'),pd.Period(f'{y}-12','M')]].mean()
base=idx(2018)
W={}
for ola,y in WAVE.items():
    g=d[(d.ola==ola)&(d.IPCF>0)&d.PONDERA.notna()&d.REGION.notna()]
    W[ola]=(g.IPCF.values*base/idx(y), g.PONDERA.values, y)
def tasa(L,ola):
    x,w,_=W[ola]; return 100*w[x<L].sum()/w.sum()
# anclas: pobreza 6.85 USD PPA 2017 del Banco Mundial en las olas post-2016 (años con IPC oficial confiable)
WB={'2018T4':12.5,'2022T4':13.9}
lo,hi=1,2e6
f=lambda L:sum((tasa(L,o)-WB[o])**2 for o in WB)
Ls=np.linspace(2000,60000,3000); L=Ls[np.argmin([f(l) for l in Ls])]
for _ in range(3):
    Ls=np.linspace(L-200,L+200,401); L=Ls[np.argmin([f(l) for l in Ls])]
WBA={'2006T4':19.9,'2010T4':13.6,'2014T4':11.7,'2018T4':12.5,'2022T4':13.9}
rows=[]
for o,(x,w,y) in W.items():
    rows.append(dict(ola=o,anio=y,pobreza_micro_685eq=round(tasa(L,o),1),pobreza_bm_685=WBA[o],diferencia_pp=round(tasa(L,o)-WBA[o],1),
                     ipc_idx_q4=round(idx(y),1),n=len(x)))
t=pd.DataFrame(rows); t['linea_2018T4_pesos']=round(L,0)
t['nota']='EPH (IPCF>0, PONDERA, urbano) deflactado con IPC empalmado (INDEC / San Luis 2007-2015 / INDEC 2016+); linea fija en pesos de 2018T4 calibrada contra BM 2018 y 2022'
t.to_csv('final/pobreza_argentina_micro_corregida.csv',index=False)
print(t.drop(columns='nota').to_string())
# sensibilidad: mismo calculo con IPC oficial intervenido? no disponible en archivo; reportar tasa con linea +-10%
for k in (0.9,1.0,1.1):
    print(k,{o:round(tasa(L*k,o),1) for o in W})
