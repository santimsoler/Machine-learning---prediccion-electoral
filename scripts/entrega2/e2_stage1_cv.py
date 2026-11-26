"""Etapa 1: validación en ventana expansiva SOLO con elecciones de entrenamiento (< 2022). No toca el conjunto de prueba."""
import sys; sys.path.insert(0,'scripts')
import pandas as pd, numpy as np, time
import e2_core as c
df = c.cargar()
res = []; preds = []
SETS = {'Base':c.BASE, 'Base+R1':c.BASE+['r1_share'], 'Amplio+R1':c.AMPLIO+['r1_share']}
MODELOS = {'Base':['Ridge','ElasticNet','RandomForest','GradBoost'], 'Base+R1':['Ridge','ElasticNet','RandomForest','GradBoost'],
           'Amplio+R1':['Ridge','RandomForest','GradBoost']}
for muestra, filtro in [('todas', df.colapso>=0), ('sin_colapsos', df.colapso==0)]:
    d = df[filtro].reset_index(drop=True)
    tr = np.where(d.fecha < c.CORTE_TEST)[0]
    t0=time.time()
    R, m, _ = c.validacion_externa(d, 'Benchmark', c.BASE, tr)
    res.append(dict(muestra=muestra, set='-', modelo='Benchmark', **m)); R.assign(muestra=muestra, set='-', modelo='Benchmark').pipe(preds.append)
    for s, cols in SETS.items():
        for mod in MODELOS[s]:
            R, m, hp = c.validacion_externa(d, mod, cols, tr)
            res.append(dict(muestra=muestra, set=s, modelo=mod, **m)); preds.append(R.assign(muestra=muestra, set=s, modelo=mod))
            print(muestra, s, mod, {k:round(v,2) for k,v in m.items()}, f'{time.time()-t0:.0f}s', flush=True)
            pd.DataFrame(res).to_csv('modelos/e2_cv_resultados.csv', index=False)
            pd.concat(preds).to_csv('modelos/e2_cv_predicciones.csv', index=False)
print('FIN')
