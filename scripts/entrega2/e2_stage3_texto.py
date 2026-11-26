"""Etapa 3 (solo entrenamiento): ¿aporta la fuente de texto? Mismo modelo con/sin, mismas particiones."""
import sys; sys.path.insert(0,'scripts')
import pandas as pd, numpy as np, e2_core as c
df=c.cargar(); rng=np.random.default_rng(0); out=[]
V={'Base':c.BASE,'Base+Texto(4 índices)':c.BASE+c.TEXTO,'Base+cont_cambio':c.BASE+['cont_cambio'],'Base+malestar':c.BASE+['malestar'],'Base+fragm_txt':c.BASE+['fragm_txt'],'Base+izq_der':c.BASE+['izq_der']}
for muestra,f in [('todas',df.colapso>=0),('sin_colapsos',df.colapso==0)]:
    d=df[f].reset_index(drop=True); tr=np.where(d.fecha<c.CORTE_TEST)[0]
    for mod in ['Ridge','ElasticNet']:
        R0=None
        for nom,cols in V.items():
            R,m,_=c.validacion_externa(d,mod,cols,tr)
            if nom=='Base': R0=R
            dif=(R.set_index('id_eleccion').err-R0.set_index('id_eleccion').err).values  # <0: mejora con texto
            bs=[rng.choice(dif,len(dif)).mean() for _ in range(3000)]
            out.append(dict(muestra=muestra,modelo=mod,set=nom,MAE=m['MAE_pool'],MAE_fold=m['MAE_fold_media'],SD_fold=m['MAE_fold_desvio'],R2=m['R2'],d_vs_base=dif.mean(),lo=np.percentile(bs,2.5),hi=np.percentile(bs,97.5)))
            print(muestra,mod,nom,round(m['MAE_pool'],2),round(dif.mean(),2),flush=True)
pd.DataFrame(out).to_csv('modelos/e2_texto.csv',index=False)
