"""Etapa 6: modelo aparte para segundas vueltas (con la 1a vuelta como predictor) y modelo aparte de primeras vueltas, frente al modelo conjunto.
Validación: ventana expansiva por año (2010-2021) sobre elecciones de entrenamiento; la prueba (>=2022) NO se usa para elegir."""
import sys; sys.path.insert(0,'scripts')
import pandas as pd, numpy as np, e2_core as c
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
df=c.cargar(); rng=np.random.default_rng(0)
R2COLS=['r1_share','aprobacion_oficial_completa','fp_prev1','oficialismo_va_por_reeleccion']
def mod_r2(kind):
    if kind=='OLS_r1': return Pipeline([('imp',SimpleImputer(strategy='median')),('m',LinearRegression())]), ['r1_share']
    if kind=='Ridge_r1+3': return Pipeline([('imp',SimpleImputer(strategy='median')),('sc',StandardScaler()),('m',RidgeCV(alphas=np.logspace(-1,3,15)))]), R2COLS
def cv_r2(d, kind, desde=2010, hasta=2021, minimo=6):
    rows=[]; f=d.fecha
    for a in range(desde,hasta+1):
        va=np.where((f.dt.year==a)&(d.vuelta==2))[0]
        if len(va)==0: continue
        ini=f.iloc[np.where(f.dt.year==a)[0]].min(); tr=np.where((f<ini)&(d.vuelta==2))[0]
        if len(tr)<minimo: continue
        y=d.y_share_nacional.values
        if kind=='Benchmark_R2': p=np.repeat(y[tr].mean(),len(va))
        elif kind=='y2=y1': p=d.r1_share.values[va]
        else:
            m,cols=mod_r2(kind); m.fit(d[cols].iloc[tr],y[tr]); p=m.predict(d[cols].iloc[va])
        rows+= [(d.id_eleccion[i],a,y[i],pi) for i,pi in zip(va,p)]
    R=pd.DataFrame(rows,columns=['id_eleccion','bloque','y','pred']); R['err']=(R.y-R.pred).abs(); return R
res=[]
for muestra,filt in [('todas',df.colapso>=0),('sin_colapsos',df.colapso==0)]:
    d=df[filt].reset_index(drop=True); tr=np.where(d.fecha<c.CORTE_TEST)[0]
    # modelos conjuntos: predicciones de la etapa 1 (misma validación) restringidas a R2
    for nom,cols in [('Conjunto Ridge Base',c.BASE),('Conjunto Ridge Base+R1',c.BASE+['r1_share'])]:
        R,m,_=c.validacion_externa(d,'Ridge',cols,tr); R['vuelta']=R.id_eleccion.str[-1].astype(int)
        z=R[R.vuelta==2]; res.append(dict(muestra=muestra,vuelta='R2',modelo=nom,n=len(z),MAE=z.err.mean(),RMSE=np.sqrt(((z.y-z.pred)**2).mean())))
        z=R[R.vuelta==1]; res.append(dict(muestra=muestra,vuelta='R1',modelo=nom,n=len(z),MAE=z.err.mean(),RMSE=np.sqrt(((z.y-z.pred)**2).mean())))
        if nom=='Conjunto Ridge Base': Rj=R.copy()
    for kind in ['Benchmark_R2','y2=y1','OLS_r1','Ridge_r1+3']:
        R=cv_r2(d,kind); res.append(dict(muestra=muestra,vuelta='R2',modelo='Aparte '+kind,n=len(R),MAE=R.err.mean(),RMSE=np.sqrt(((R.y-R.pred)**2).mean())))
        if kind=='OLS_r1': Ro=R.copy()
    # modelo aparte de 1a vuelta: Ridge solo con R1 (sin 'vuelta' ni r1)
    d1=d[d.vuelta==1].reset_index(drop=True); t1=np.where(d1.fecha<c.CORTE_TEST)[0]
    cols1=[x for x in c.BASE if x!='vuelta']
    R,m,_=c.validacion_externa(d1,'Ridge',cols1,t1); res.append(dict(muestra=muestra,vuelta='R1',modelo='Aparte Ridge solo R1',n=len(R),MAE=R.err.mean(),RMSE=np.sqrt(((R.y-R.pred)**2).mean())))
    # diferencia pareada R2: aparte OLS_r1 vs conjunto Base (mismas elecciones)
    a=Ro.set_index('id_eleccion').err; b=Rj.set_index('id_eleccion').err; k=a.index.intersection(b.index); dif=(a[k]-b[k]).values
    bs=[rng.choice(dif,len(dif)).mean() for _ in range(3000)]
    print(muestra,'R2 aparte OLS_r1 - conjunto Base: ',round(dif.mean(),2),np.percentile(bs,[2.5,97.5]).round(2),'n=',len(k))
R=pd.DataFrame(res); R.to_csv('modelos/e2_segunda_vuelta.csv',index=False); print(R.round(2).to_string(index=False))
# coeficientes del modelo R2 simple ajustado con todas las R2 de entrenamiento
d=df.copy(); t=d[(d.vuelta==2)&(d.fecha<c.CORTE_TEST)]; z=t[['r1_share','y_share_nacional']].dropna(); lr=LinearRegression().fit(z[['r1_share']],z.y_share_nacional)
print('R2 train n=',len(z),'y2 = %.1f + %.2f*y1'%(lr.intercept_,lr.coef_[0]),' corr',round(z.corr().iloc[0,1],2))
