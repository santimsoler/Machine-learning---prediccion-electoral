"""Etapa 4: conjunto de prueba (elecciones >= 2022), UNA sola vez. Modelo elegido en etapa 1 por regla fija: Ridge, set Base."""
import sys; sys.path.insert(0,'scripts')
import pandas as pd, numpy as np, e2_core as c, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
df=c.cargar(); rng=np.random.default_rng(0); res=[]; allp=[]; coefs={}
for muestra,f in [('todas',df.colapso>=0),('sin_colapsos',df.colapso==0)]:
    d=df[f].reset_index(drop=True); tr=np.where(d.fecha<c.CORTE_TEST)[0]; te=np.where(d.fecha>=c.CORTE_TEST)[0]
    y=d.y_share_nacional.values[te]
    for mod in ['Benchmark','Ridge']:
        p,hp=c.ajustar_predecir(d,mod,c.BASE,tr,te,d.fecha)
        e=np.abs(y-p); bs=[rng.choice(e,len(e)).mean() for _ in range(3000)]
        res.append(dict(muestra=muestra,modelo=mod,n=len(te),MAE=e.mean(),lo=np.percentile(bs,2.5),hi=np.percentile(bs,97.5),RMSE=np.sqrt(((y-p)**2).mean()),R2=1-((y-p)**2).sum()/((y-y.mean())**2).sum(),hp=str(hp)))
        allp.append(pd.DataFrame(dict(muestra=muestra,modelo=mod,id_eleccion=d.id_eleccion.values[te],y=y,pred=p,err=e)))
    # coeficientes del modelo final ajustado con todo el entrenamiento
    gs=c.GridSearchCV(c.pipe('Ridge',c.BASE),c.GRIDS['Ridge'],cv=c.cv_interno(d.fecha,tr),scoring='neg_mean_absolute_error').fit(d[c.BASE].iloc[tr],d.y_share_nacional.values[tr])
    coefs[muestra]=pd.Series(gs.best_estimator_[-1].coef_,index=c.BASE)
R=pd.DataFrame(res); P=pd.concat(allp); R.to_csv('modelos/e2_test_resultados.csv',index=False); P.to_csv('modelos/e2_test_predicciones.csv',index=False)
pd.DataFrame(coefs).to_csv('modelos/e2_coeficientes.csv')
print(R.round(2).to_string(index=False)); print(P[P.modelo=='Ridge'].sort_values('err',ascending=False).round(1).head(10).to_string(index=False))
