"""Filas regionales (32 entidades) de México para 1994, 2000, 2006, 2018 y 2024 (tablas por estado de en.wikipedia, bajadas por el usuario; ver mx_parse_estados.py).
Voto válido = candidatos + no registrados (excluye nulos/en blanco), igual que y_share_nacional. Falta 2012 y la pobreza regional. Idempotente; correr al final del pipeline."""
import pandas as pd, numpy as np
F='final/'; D2='data_ampliacion2/'
v=pd.read_csv(D2+'mx_estado_votos.csv',keep_default_na=False); v=v[~v.candidato_col.isin(['Invalid','None'])]
OF={'MX-1994-PRES-1':'Zedillo','MX-2000-PRES-1':'Labastida','MX-2006-PRES-1':'Calderón','MX-2012-PRES-1':'Vázquez','MX-2018-PRES-1':'Meade','MX-2024-PRES-1':'Sheinbaum'}
SUB={'Cevallos':'Fernández de Cevallos','López':'López Obrador','Vázquez':'Vázquez Mota','Peña':'Peña Nieto'}
c=pd.read_csv(F+'candidatos_ampliacion.csv'); c=c[c.id_eleccion.str.startswith('MX-')]
def ec(eid,col):
    d=c[c.id_eleccion==eid[:7]]; m=d[d.candidato.str.contains(SUB.get(col,col),regex=False)]
    return m.e_cont.iloc[0] if len(m) else np.nan
v['e_cont']=[ec(a,b) for a,b in zip(v.id_eleccion,v.candidato_col)]
E=pd.read_csv(F+'panel_modelo_eleccion.csv'); R=pd.read_csv(F+'panel_modelo_region.csv'); R=R[R.pais!='MX']
out=[]
for eid,g in v.groupby('id_eleccion'):
    n=E[E.id_eleccion==eid].iloc[0]
    for reg,h in g.groupby('region'):
        tot=h.votos.sum(); of=h[h.candidato_col==OF[eid]].votos.sum(); otro=h[(h.candidato_col!=OF[eid])&(~h.candidato_col.str.startswith('Write'))].votos.max()
        con=h[h.e_cont.notna()]; cov=con.votos.sum()/tot
        r=dict(id_eleccion=eid,region=reg,votos_validos=tot,y_share_oficialismo=100*of/tot,y_gana_region=int(of>otro),y_desvio_regional=100*of/tot-n.y_share_nacional,
               cobertura_ideo=cov,y_share_izquierda=(100*h[h.e_cont<-0.5].votos.sum()/tot if cov>=.8 else np.nan),ideologia_voto_media=((con.e_cont*con.votos).sum()/con.votos.sum() if cov>=.8 else np.nan))
        for k in R.columns:
            if k not in r and k in E.columns: r[k]=n[k]
        out.append(r)
out=pd.DataFrame(out); out=out[[k for k in R.columns if k in out.columns]]
pd.concat([R,out],ignore_index=True).to_csv(F+'panel_modelo_region.csv',index=False)
print(out.groupby('id_eleccion').agg(of_pond=('y_share_oficialismo','mean'),ganadas=('y_gana_region','sum'),cob=('cobertura_ideo','mean'),izq=('y_share_izquierda','mean')).round(2)); print(len(R),'->',len(R)+len(out))
