"""Paraguay 2023: voto presidencial por departamento (ABC Color/TSJE). Corre después de ampliacion_competencia.py."""
import pandas as pd, numpy as np, csv, re
F='final/'
def num(t):
    t=t.strip().replace(' ','')
    if re.fullmatch(r'\d{1,3}\.\d{3}',t): t=t.replace('.','')
    return float(t)
rows=[]
for p in csv.reader(open('data_ampliacion/paraguay_2023_regional.txt',encoding='utf-8')):
    if len(p)<17 or p[0].startswith('Fuente'): continue
    v=[num(p[i]) for i in (1,3,5,7,9,11)]; bl,nu,em,el=[num(p[i]) for i in (13,14,15,16)]
    rows.append(dict(otro_max=max(v[1:]),region=p[0].replace('P. Hayes','Presidente Hayes'),pena=v[0],cand_sum=sum(v),chequeo=sum(v)+bl+nu-em,electores=el,emitidos=em))
d=pd.DataFrame(rows); print(d.shape,'Peña total',d.pena.sum(),'cand total',d.cand_sum.sum()); print(d[d.chequeo.abs()>5])
d['y_share_oficialismo']=100*d.pena/d.cand_sum
R=pd.read_csv(F+'panel_modelo_region.csv'); R=R[~((R.id_eleccion=='PY-2023-PRES-1'))]
N=pd.read_csv(F+'panel_modelo_eleccion.csv'); base=N[N.id_eleccion=='PY-2023-PRES-1'].iloc[0]
new=pd.DataFrame([base.to_dict()]*len(d)); new['region']=d.region.values; new['votos_validos']=d.cand_sum.values
new['y_share_oficialismo']=d.y_share_oficialismo.values
top=d.assign(o=d.cand_sum-d.pena)
new['y_gana_region']=(d.pena>d.otro_max).astype(int).values
new['y_desvio_regional']=new.y_share_oficialismo-new.y_share_nacional
new['ampliacion']=1
for c in R.columns:
    if c not in new.columns: new[c]=np.nan
pd.concat([R,new[R.columns]],ignore_index=True).to_csv(F+'panel_modelo_region.csv',index=False)
print(new[['region','votos_validos','y_share_oficialismo','y_desvio_regional']].round(1).to_string())
