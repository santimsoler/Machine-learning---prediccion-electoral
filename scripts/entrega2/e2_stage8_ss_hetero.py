"""Etapa 8 (solo entrenamiento): (a) proxy de sudden stop en los dos años previos al año electoral; (b) efectos económicos distintos en Argentina / por país."""
import sys; sys.path.insert(0,'scripts')
import pandas as pd, numpy as np, e2_core as c
df=c.cargar(); rng=np.random.default_rng(0)
w=pd.read_csv('final/macro_panel_ss.csv').set_index(['pais','anio'])
def ventana(r,col,f=max):
    v=[w[col].get((r.pais,y),np.nan) for y in (r.anio-2,r.anio-1)]; v=[x for x in v if pd.notna(x)]; return f(v) if v else np.nan
df['ss2']=[ventana(r,'ss') for r in df.itertuples()]
df['dep2']=[np.log1p(max(ventana(r,'depre'),0)/100) if pd.notna(ventana(r,'depre')) else np.nan for r in df.itertuples()]
df['dca2']=[ventana(r,'dca') for r in df.itertuples()]
df['AR']=(df.pais=='AR').astype(int)
df['AR_infl']=df.AR*df.bm_inflacion_ipc_tm1; df['AR_fisc']=df.AR*df.us_current_account_tm1; df['AR_aprob']=df.AR*df.aprobacion_oficial_completa
GR=[p for p,n in df[df.vuelta==1].pais.value_counts().items() if n>=6]   # países con >=6 elecciones
for p in GR:
    df[f'{p}_infl']=(df.pais==p)*df.bm_inflacion_ipc_tm1; df[f'{p}_fisc']=(df.pais==p)*df.us_current_account_tm1
B=c.BASE
S={'Base':B,'Base + sudden stop (proxy, 2 años previos)':B+['ss2'],'Base + máxima depreciación (2 años previos)':B+['dep2'],'Base + ambas':B+['ss2','dep2'],
   'Base + Argentina (dummy)':B+['AR'],'Base + AR e interacciones con inflación y saldo fiscal':B+['AR','AR_infl','AR_fisc'],
   'Base + AR e interacciones con inflación, saldo fiscal y aprobación':B+['AR','AR_infl','AR_fisc','AR_aprob'],
   'Base + pendientes económicas por país (>=6 elecciones)':B+[f'{p}_{k}' for p in GR for k in ('infl','fisc')]}
out=[]; print('países con >=6 elecciones:',GR)
print('años con proxy en ventana (elecciones):',int((df.ss2==1).sum()),'de',int(df.ss2.notna().sum()),'| entrenamiento:',int(((df.ss2==1)&(df.fecha<c.CORTE_TEST)).sum()))
for muestra,f in [('todas',df.colapso>=0),('sin_colapsos',df.colapso==0)]:
    d=df[f].reset_index(drop=True); tr=np.where(d.fecha<c.CORTE_TEST)[0]; R0=None
    for n,cols in S.items():
        R,m,_=c.validacion_externa(d,'Ridge',cols,tr)
        if R0 is None: R0=R
        dif=(R.set_index('id_eleccion').err-R0.set_index('id_eleccion').err).values; bs=[rng.choice(dif,len(dif)).mean() for _ in range(2000)]
        out.append(dict(muestra=muestra,modelo=n,MAE=m['MAE_pool'],R2=m['R2'],d_vs_base=dif.mean(),lo=np.percentile(bs,2.5),hi=np.percentile(bs,97.5)))
        print(f'{muestra:13s} {n:68s} MAE {m["MAE_pool"]:.2f} Δ {dif.mean():+.2f} [{np.percentile(bs,2.5):+.2f},{np.percentile(bs,97.5):+.2f}]',flush=True)
pd.DataFrame(out).to_csv('modelos/e2_ss_hetero.csv',index=False)
# descriptivo: sudden stop vs voto (entrenamiento, primeras vueltas) y por país
tr=df[(df.fecha<c.CORTE_TEST)&(df.vuelta==1)]
print('\nVoto medio del oficialismo (1ª vuelta, entrenamiento) con/sin proxy de sudden stop en ventana:'); print(tr.groupby('ss2').y_share_nacional.agg(['count','mean','median']).round(1))
print('\nCorrelación de Spearman dentro de cada país (entrenamiento, 1ª vuelta, n>=6):')
rows=[]
for p in GR:
    z=tr[tr.pais==p]; r={'pais':p,'n':len(z)}
    for v in ['bm_inflacion_ipc_tm1','us_current_account_tm1','bm_crecimiento_pib_tm1','aprobacion_oficial_completa']:
        q=z[[v,'y_share_nacional']].dropna(); r[v]=q.corr(method='spearman').iloc[0,1] if len(q)>=5 else np.nan
    rows.append(r)
T=pd.DataFrame(rows); T.to_csv('modelos/e2_corr_por_pais.csv',index=False); print(T.round(2).to_string(index=False))
# interacción Argentina: OLS con variables estandarizadas, IC por bootstrap de elecciones (entrenamiento)
d=df[df.fecha<c.CORTE_TEST].copy(); cols=B+['AR','AR_infl','AR_fisc']; X=d[cols].copy()
X=X.fillna(X.median()); mu,sd=X.mean(),X.std().replace(0,1); Z=((X-mu)/sd).values; y=d.y_share_nacional.values
def ols(Z,y):
    A=np.c_[np.ones(len(Z)),Z]; return np.linalg.lstsq(A,y,rcond=None)[0][1:]
b0=ols(Z,y); bs=np.array([ols(Z[i],y[i]) for i in (rng.integers(0,len(y),len(y)) for _ in range(2000))])
T2=pd.DataFrame({'coef':b0,'lo':np.percentile(bs,2.5,axis=0),'hi':np.percentile(bs,97.5,axis=0)},index=cols); T2.to_csv('modelos/e2_interaccion_AR.csv'); print('\nOLS estandarizado con interacciones de Argentina (n=%d):'%len(y)); print(T2.round(2).to_string())
