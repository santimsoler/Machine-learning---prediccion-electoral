"""Parsea data_ampliacion2/mx_wikipedia_estados_raw.txt (salida de Colab con las tablas por estado de en.wikipedia) -> data_ampliacion2/mx_estado_votos.csv (largo)."""
import pandas as pd, re
D2='data_ampliacion2/'; rows=[]; eid=None; cols=None; anio=None
REN={'Distrito Federal':'Ciudad de México','Mexico City':'Ciudad de México','México':'Estado de México'}
for l in open(D2+'mx_wikipedia_estados_raw.txt',encoding='utf-8'):
    l=l.rstrip('\n')
    m=re.match(r'### (\d{4})_Mexican',l)
    if m: anio=int(m.group(1)); eid=f'MX-{anio}-PRES-1'; continue
    if l.startswith('COLS:'):
        cols=[c.strip() for c in l[5:].split(';')]
        if anio>=2018: names=[c.split('/')[0].split(' ')[0] for c in cols if c.endswith('/Votes') and not c.startswith('Total')]
        else: names=[c.split('/')[0].split(' ')[0] for c in cols][1:]
        continue
    if not eid or '|' not in l or l.startswith('---'): continue
    p=l.split('|'); reg=p[0]
    if reg in ('Total','Voto en el exterior'): continue
    v=p[1:]
    if anio>=2018: v=v[0::2][:len(names)]            # votos, %, votos, %...
    for n_,x in zip(names,v):
        if x not in ('','nan'): rows.append((eid,REN.get(reg,reg),n_.replace('[b]',''),float(x)))
d=pd.DataFrame(rows,columns=['id_eleccion','region','candidato_col','votos']); d.to_csv(D2+'mx_estado_votos.csv',index=False)
print(d.groupby('id_eleccion').region.nunique().to_dict())
OFC={'MX-2012-PRES-1':'Vázquez','MX-1994-PRES-1':'Zedillo','MX-2000-PRES-1':'Labastida','MX-2006-PRES-1':'Calderón','MX-2018-PRES-1':'Meade','MX-2024-PRES-1':'Sheinbaum'}
for e,g in d.groupby('id_eleccion'):
    val=g[~g.candidato_col.isin(['Invalid/blank','None','Invalid'])]
    print(e,sorted(g.candidato_col.unique()), round(100*val[val.candidato_col==OFC[e]].votos.sum()/val.votos.sum(),2))
