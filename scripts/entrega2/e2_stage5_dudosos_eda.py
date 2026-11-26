"""Etapa 5: (a) modelo final sin los 8 oficialismos dudosos; (b) exploración SOLO con datos de entrenamiento (< 2022)."""
import sys; sys.path.insert(0,'scripts')
import pandas as pd, numpy as np, e2_core as c
df=c.cargar(); rng=np.random.default_rng(0); out=[]
cols=[x for x in c.BASE if x!='oficialismo_dudoso']      # sin la marca (constante cuando se excluyen los dudosos)
for nombre,f in [('todas',df.colapso>=0),('sin dudosos',df.oficialismo_dudoso==0),('sin colapsos',df.colapso==0),('sin dudosos ni colapsos',(df.oficialismo_dudoso==0)&(df.colapso==0))]:
    d=df[f].reset_index(drop=True); tr=np.where(d.fecha<c.CORTE_TEST)[0]; te=np.where(d.fecha>=c.CORTE_TEST)[0]; y=d.y_share_nacional.values[te]
    fila=dict(muestra=nombre,n_total=len(d),n_val=None,n_test=len(te))
    for mod in ['Benchmark','Ridge']:
        R,m,_=c.validacion_externa(d,mod,cols if mod=='Ridge' else c.BASE,tr)
        fila[f'val_MAE_{mod}']=m['MAE_pool']; fila['n_val']=m['n']; fila[f'val_foldSD_{mod}']=m['MAE_fold_desvio']
        p,_=c.ajustar_predecir(d,mod,cols if mod=='Ridge' else c.BASE,tr,te,d.fecha); fila[f'test_MAE_{mod}']=np.abs(y-p).mean()
    out.append(fila); print({k:(round(v,2) if isinstance(v,float) else v) for k,v in fila.items()},flush=True)
pd.DataFrame(out).to_csv('modelos/e2_dudosos.csv',index=False)
# exploración solo con entrenamiento
tr=df[df.fecha<c.CORTE_TEST]; V=['d_pobnac_685_mandato','d_pobnac_365_mandato','aprobacion_oficial_completa','bm_inflacion_ipc_tm1','us_current_account_tm1','fp_prev1','oficialismo_va_por_reeleccion','oficialismo_dudoso','vuelta']
E_=[]
for v in V:
    z=tr[[v,'y_share_nacional']].dropna(); z1=tr[tr.vuelta==1][[v,'y_share_nacional']].dropna()
    E_.append(dict(variable=v,n_todas=len(z),r_pearson=z.corr().iloc[0,1],r_spearman=z.corr(method='spearman').iloc[0,1],n_R1=len(z1),r_R1=z1.corr().iloc[0,1]))
E_=pd.DataFrame(E_); E_.to_csv('modelos/e2_eda_entrenamiento.csv',index=False); print(E_.round(2).to_string(index=False))
print(tr.groupby('vuelta').y_share_nacional.agg(['count','mean','std']).round(1))
