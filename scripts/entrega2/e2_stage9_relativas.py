"""Etapa 9 (solo entrenamiento): variables económicas relativas al promedio histórico del propio país (sin mirar el futuro)."""
import sys; sys.path.insert(0,'scripts')
import pandas as pd, numpy as np, e2_core as c
df=c.cargar(); w=pd.read_csv('final/macro_panel_ss.csv'); w['linf']=np.sign(w.inflacion_ipc)*np.log1p(w.inflacion_ipc.abs()); rng=np.random.default_rng(0)
def rel(r,col):
    z=w[(w.pais==r.pais)]; v=z[z.anio==r.anio-1][col]; h=z[z.anio<=r.anio-2][col].dropna()
    return (v.iloc[0]-h.mean()) if len(v) and pd.notna(v.iloc[0]) and len(h)>=3 else np.nan
for k,col in [('g_rel','crecimiento_pib'),('infl_rel','linf'),('ca_rel','ca')]: df[k]=[rel(r,col) for r in df.itertuples()]
B=c.BASE; econ=['bm_inflacion_ipc_tm1','us_current_account_tm1']
S={'Base':B,'Base + 3 variables relativas al país':B+['g_rel','infl_rel','ca_rel'],'Base + crecimiento relativo':B+['g_rel'],'Base sin economía en niveles + relativas':[x for x in B if x not in econ]+['g_rel','infl_rel','ca_rel']}
out=[]
for muestra,f in [('todas',df.colapso>=0),('sin_colapsos',df.colapso==0)]:
    d=df[f].reset_index(drop=True); tr=np.where(d.fecha<c.CORTE_TEST)[0]; R0=None
    for n,cols in S.items():
        R,m,_=c.validacion_externa(d,'Ridge',cols,tr)
        if R0 is None: R0=R
        dif=(R.set_index('id_eleccion').err-R0.set_index('id_eleccion').err).values; bs=[rng.choice(dif,len(dif)).mean() for _ in range(2000)]
        out.append(dict(muestra=muestra,modelo=n,MAE=m['MAE_pool'],d_vs_base=dif.mean(),lo=np.percentile(bs,2.5),hi=np.percentile(bs,97.5)))
        print(f'{muestra:13s} {n[:60]:60s} MAE {m["MAE_pool"]:.2f} Δ {dif.mean():+.2f} [{np.percentile(bs,2.5):+.2f},{np.percentile(bs,97.5):+.2f}]',flush=True)
pd.DataFrame(out).to_csv('modelos/e2_relativas.csv',index=False)
