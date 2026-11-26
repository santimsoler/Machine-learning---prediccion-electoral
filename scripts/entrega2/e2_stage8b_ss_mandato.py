"""Etapa 8b (solo entrenamiento): sudden stop en la SEGUNDA MITAD DEL MANDATO del oficialismo (no 'dos años antes').
Ventana = [t-ceil(m/2), t-1], con t = año electoral y m = duración del mandato (anios_mandato). Datos anuales del año t no se usan (ex ante).
Indicadores: (1) proxy WB (dCA>=3pp PIB y crecimiento<=0 o caída>=3pp), (2) depreciación máxima, (3) caída de reservas>=15% anual (base_final, 7 países)."""
import sys, math; sys.path.insert(0,'scripts')
import pandas as pd, numpy as np, e2_core as c
df=c.cargar(); rng=np.random.default_rng(0)
m=pd.read_csv('final/panel_modelo_eleccion.csv').set_index('id_eleccion').anios_mandato
df['m']=df.id_eleccion.map(m).fillna(4).astype(int)
w=pd.read_csv('final/macro_panel_ss.csv').set_index(['pais','anio'])
b=pd.read_csv('final/base_final.csv')
iso={'ARG':'AR','BRA':'BR','CHL':'CL','COL':'CO','PRY':'PY','PER':'PE','URY':'UY'}
b=b[b.iso3c.isin(iso)].assign(pais=lambda x:x.iso3c.map(iso)).set_index(['pais','year'])
b['perd_res']=(b.d_ln_res<=math.log(0.85)).astype(float).where(b.d_ln_res.notna())
def vent(r,tab,col,f=max):
    ys=range(r.anio-math.ceil(r.m/2),r.anio); v=[tab[col].get((r.pais,y),np.nan) for y in ys]; v=[x for x in v if pd.notna(x)]
    return f(v) if v else np.nan
df['ss_m']=[vent(r,w,'ss') for r in df.itertuples()]
df['dep_m']=[np.log1p(max(vent(r,w,'depre'),0)/100) if pd.notna(vent(r,w,'depre')) else np.nan for r in df.itertuples()]
df['res_m']=[vent(r,b,'perd_res') for r in df.itertuples()]
df['n_ss_m']=[sum(w['ss'].get((r.pais,y),0) or 0 for y in range(r.anio-math.ceil(r.m/2),r.anio)) for r in df.itertuples()]
df[['id_eleccion','pais','anio','m','ss_m','dep_m','res_m','n_ss_m']].to_csv('modelos/e2_ss_mandato_vars.csv',index=False)
tr=df[df.fecha<c.CORTE_TEST]
print('Elecciones con sudden stop (proxy) en 2ª mitad del mandato: total',int((df.ss_m==1).sum()),'/',int(df.ss_m.notna().sum()),'| entrenamiento',int((tr.ss_m==1).sum()))
print('Con caída de reservas >=15%: total',int((df.res_m==1).sum()),'/',int(df.res_m.notna().sum()),'| entrenamiento',int((tr.res_m==1).sum()))
print(df[df.ss_m==1][['id_eleccion','m','y_share_nacional']].to_string(index=False))
t1=tr[tr.vuelta==1]; print('\nVoto medio oficialismo (1ª vuelta, entrenamiento) según proxy en 2ª mitad del mandato:'); print(t1.groupby('ss_m').y_share_nacional.agg(['count','mean','median']).round(1))
print('según caída de reservas:'); print(t1.groupby('res_m').y_share_nacional.agg(['count','mean','median']).round(1))
B=c.BASE
S={'Base':B,'Base + sudden stop 2ª mitad del mandato':B+['ss_m'],'Base + depreciación máx. 2ª mitad':B+['dep_m'],'Base + caída de reservas 2ª mitad (7 países)':B+['res_m'],'Base + las tres':B+['ss_m','dep_m','res_m']}
out=[]
for muestra,f in [('todas',df.colapso>=0),('sin_colapsos',df.colapso==0)]:
    d=df[f].reset_index(drop=True); trn=np.where(d.fecha<c.CORTE_TEST)[0]; R0=None
    for n,cols in S.items():
        R,mm,_=c.validacion_externa(d,'Ridge',cols,trn)
        if R0 is None: R0=R
        dif=(R.set_index('id_eleccion').err-R0.set_index('id_eleccion').err).values; bs=[rng.choice(dif,len(dif)).mean() for _ in range(2000)]
        out.append(dict(muestra=muestra,modelo=n,MAE=mm['MAE_pool'],R2=mm['R2'],d_vs_base=dif.mean(),lo=np.percentile(bs,2.5),hi=np.percentile(bs,97.5)))
        print(f'{muestra:13s} {n:48s} MAE {mm["MAE_pool"]:.2f} Δ {dif.mean():+.2f} [{np.percentile(bs,2.5):+.2f},{np.percentile(bs,97.5):+.2f}]',flush=True)
pd.DataFrame(out).to_csv('modelos/e2_ss_mandato.csv',index=False)
