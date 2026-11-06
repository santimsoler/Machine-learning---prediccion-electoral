"""Filas regionales (7 provincias) de Costa Rica para las rondas con datos oficiales del TSE (cuadros por provincia): 1990, 1994, 1998, 2002 (R1 y R2), 2006, 2010, 2014 R1, 2018 R1.
Sin voto en el extranjero. Corre al final del pipeline (después de panel_modelo_completo.py). Idempotente. Faltan: 2014 R2, 2018 R2, 2022, 2026 (sin tabla oficial accesible)."""
import pandas as pd, numpy as np
F='final/'; D2='data_ampliacion2/'
P=['San José','Alajuela','Cartago','Heredia','Guanacaste','Puntarenas','Limón']
rows=[]
for l in open(D2+'cr_prov_votos_raw.txt'):
    if l.startswith('#') or not l.strip(): continue
    e,p,v=l.strip().split(';')
    for r,x in zip(P,v.split(',')): rows.append((e,r,p,float(x)))
v=pd.DataFrame(rows,columns=['id_eleccion','region','partido','votos'])
OF={'CR-1990-PRES-1':'PLN','CR-1994-PRES-1':'PUSC','CR-1998-PRES-1':'PLN','CR-2002-PRES-1':'PUSC','CR-2002-PRES-2':'PUSC','CR-2006-PRES-1':'PUSC','CR-2010-PRES-1':'PLN','CR-2014-PRES-1':'PLN','CR-2018-PRES-1':'PAC'}
PAT={'PLN':'(PLN)','PUSC':'(PUSC)','PAC':'(PAC)','ML':'(ML)','FA':'(FA)','PRN':'(PRN)','PIN':'(PIN)','FD':'FD'}
c=pd.read_csv(F+'candidatos_ampliacion.csv'); c=c[c.id_eleccion.str.startswith('CR-')]
def ec(eid,party):
    d=c[c.id_eleccion==eid[:7]]; m=d[d.candidato.str.contains(PAT.get(party,'@@@'),regex=False)]
    return m.e_cont.iloc[0] if len(m) else np.nan
v['e_cont']=[ec(a,b) for a,b in zip(v.id_eleccion,v.partido)]
E=pd.read_csv(F+'panel_modelo_eleccion.csv'); R=pd.read_csv(F+'panel_modelo_region.csv'); R=R[R.pais!='CR']
out=[]
for eid,g in v.groupby('id_eleccion'):
    n=E[E.id_eleccion==eid].iloc[0]
    for reg,h in g.groupby('region'):
        tot=h.votos.sum(); of=h[h.partido==OF[eid]].votos.sum(); otros=h[(h.partido!=OF[eid])&(h.partido!='Otros')].votos.max()
        con=h[h.e_cont.notna()]; cov=con.votos.sum()/tot
        r=dict(id_eleccion=eid,region=reg,votos_validos=tot,y_share_oficialismo=100*of/tot,y_gana_region=int(of>otros),y_desvio_regional=100*of/tot-n.y_share_nacional,
               cobertura_ideo=cov,y_share_izquierda=(100*h[h.e_cont<-0.5].votos.sum()/tot if cov>=.8 else np.nan),ideologia_voto_media=((con.e_cont*con.votos).sum()/con.votos.sum() if cov>=.8 else np.nan))
        for k in R.columns:
            if k not in r and k in E.columns: r[k]=n[k]
        out.append(r)
out=pd.DataFrame(out)[[c for c in R.columns if c in set(pd.DataFrame(out).columns)]]

# --- CR 2014 segunda vuelta: solo porcentajes por provincia (en.wikipedia, bajado por el usuario); votos_validos queda vacío ---
R2={'San José':(77.6,22.3),'Alajuela':(78.9,21.1),'Cartago':(80.3,19.6),'Heredia':(80.8,19.1),'Puntarenas':(73.1,26.8),'Limón':(77.5,22.4),'Guanacaste':(69.7,30.2)}  # (PAC, PLN)
n=E[E.id_eleccion=='CR-2014-PRES-2'].iloc[0]; eP=ec('CR-2014-PRES-2','PAC'); eL=ec('CR-2014-PRES-2','PLN'); rr=[]
for reg,(pac,pln) in R2.items():
    r=dict(id_eleccion='CR-2014-PRES-2',region=reg,votos_validos=np.nan,y_share_oficialismo=pln,y_gana_region=int(pln>pac),y_desvio_regional=pln-n.y_share_nacional,cobertura_ideo=1.0,
           y_share_izquierda=(pac if eP<-0.5 else 0.0)+(pln if eL<-0.5 else 0.0),ideologia_voto_media=(eP*pac+eL*pln)/(pac+pln))
    for k in R.columns:
        if k not in r and k in E.columns: r[k]=n[k]
    rr.append(r)
out=pd.concat([out,pd.DataFrame(rr)[[k for k in R.columns if k in pd.DataFrame(rr).columns]]],ignore_index=True)
pd.concat([R,out],ignore_index=True).to_csv(F+'panel_modelo_region.csv',index=False)
# control: promedio ponderado regional vs nacional
chk=out.groupby('id_eleccion').apply(lambda d:pd.Series({'of_regional_ponderado':100*(d.votos_validos*d.y_share_oficialismo/100).sum()/d.votos_validos.sum(),'nacional':d.y_share_oficialismo.mean()*0+E.set_index('id_eleccion').loc[d.name,'y_share_nacional'],'n_prov':len(d),'ganadas':d.y_gana_region.sum(),'cobertura':d.cobertura_ideo.mean()}),include_groups=False)
print(chk.round(2).to_string()); print(len(R),'->',len(R)+len(out))
