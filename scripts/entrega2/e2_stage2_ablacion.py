"""Etapa 2 (solo entrenamiento): aporte de cada variable = mismo modelo con y sin ella, mismas particiones; concentración del error."""
import sys; sys.path.insert(0,'scripts')
import pandas as pd, numpy as np, e2_core as c
df=c.cargar(); out=[]; P={}
rng=np.random.default_rng(0)
for muestra,f in [('todas',df.colapso>=0),('sin_colapsos',df.colapso==0)]:
    d=df[f].reset_index(drop=True); tr=np.where(d.fecha<c.CORTE_TEST)[0]
    R0,m0,_=c.validacion_externa(d,'Ridge',c.BASE,tr); P[(muestra,'completo')]=R0
    out.append(dict(muestra=muestra,variable='(modelo completo)',MAE=m0['MAE_pool'],dMAE=0,lo=0,hi=0))
    for v in c.BASE:
        cols=[x for x in c.BASE if x!=v]
        R,m,_=c.validacion_externa(d,'Ridge',cols,tr)
        dif=(R.set_index('id_eleccion').err-R0.set_index('id_eleccion').err).values   # >0: sin la variable empeora
        bs=[rng.choice(dif,len(dif)).mean() for _ in range(3000)]
        out.append(dict(muestra=muestra,variable=v,MAE=m['MAE_pool'],dMAE=dif.mean(),lo=np.percentile(bs,2.5),hi=np.percentile(bs,97.5)))
        print(muestra,v,round(m['MAE_pool'],2),round(dif.mean(),2),flush=True)
pd.DataFrame(out).to_csv('modelos/e2_ablacion.csv',index=False)
# concentración del error
for k,R in P.items():
    R=R.sort_values('err',ascending=False); tot=R.err.sum()
    print('\n',k,'MAE',round(R.err.mean(),2),'| top5 aportan',round(R.err.head(5).sum()/tot*100),'% del error absoluto | top10',round(R.err.head(10).sum()/tot*100),'%')
    print(R.head(8).round(1)[['id_eleccion','y','pred','err']].to_string(index=False))
    R.to_csv(f'modelos/e2_errores_{k[0]}.csv',index=False)
# horizonte 90 dias: share de aprobaciones medidas a <=90 dias de la eleccion
e=pd.read_csv('final/panel_modelo_eleccion.csv'); g=e[e.vuelta==1].aprob_ead_gap_dias
print('\nAprobación EAD con gap<=90d:',(g<=90).sum(),'de',g.notna().sum(), '| otras fuentes:', e[e.vuelta==1].aprobacion_fuente_completa.ne('EAD').sum())
