import csv
from collections import defaultdict
O='out4/'
SRC=[('CO','base_presidencial_colombia_1998_2026.csv','nombre_opcion','partido_nombre','votos'),
('BR','br_presidencial_municipios_2002_2026.csv','nm_candidato','sg_partido','votos'),
('CL','cl_presidencial_comunas_1989_2025.csv','candidato','partido','votos'),
('AR','ar_presidencial_provincias_1983_2023.csv','formula','agrupacion_nombre','votos'),
('PE','pe_presidencial_distritos_2006_2021.csv','candidato','partido','votos'),
('UY','/tmp/work/out/uy_presidencial_departamentos_2014_2024.csv','candidato','lema_o_candidato','votos')]
ofi={}
for r in csv.DictReader(open('final/resultados_region.csv')):
    if r['es_oficialismo']=='1': ofi[(r['id_eleccion'],r['opcion'])]=1
INC={r['id_eleccion']:r for r in csv.DictReader(open('final/elecciones.csv'))}
agg=defaultdict(int)
for pais,f,cn,pn,v in SRC:
    for r in csv.DictReader(open(f if f.startswith('/') else O+f,encoding='utf-8')):
        eid=r['id_eleccion']
        if pais=='CO': eid='CO-'+eid
        agg[(pais,eid,r[cn].strip(),r[pn].strip())]+=int(float(r[v] or 0))
tot=defaultdict(int)
for (p,e,c,pt),v in agg.items(): tot[e]+=v
rows=[]
for (p,e,c,pt),v in sorted(agg.items()):
    i=INC[e]; kw=[k for k in i['palabras_clave_opcion_oficialista'].split(';') if k]
    import unicodedata
    nz=lambda s:''.join(ch for ch in unicodedata.normalize('NFD',s.upper()) if unicodedata.category(ch)!='Mn')
    es=int(any(k in nz(c+' '+pt) for k in kw)) if kw else (0 if i['estado_codificacion'].startswith('sin_') else '')
    rows.append([e,p,i['anio'],i['vuelta'],c,pt,v,round(v/tot[e]*100,3) if tot[e] else '',es,i['oficialismo_va_por_reeleccion'] if es==1 else '', 'pendiente','pendiente','','',''])
w=csv.writer(open('final/candidatos.csv','w',newline='',encoding='utf-8'))
w.writerow(['id_eleccion','pais','anio','vuelta','candidato_o_formula','partido_o_coalicion','votos_nacionales','share_nacional_pct','es_oficialismo','va_por_reeleccion','eje_economico','eje_sociocultural','fuente_ideologia','version_codebook','notas'])
w.writerows(rows)
print(len(rows))
import collections
print(collections.Counter(r[1] for r in rows))
print(sum(1 for r in rows if r[4]==''),'sin nombre de candidato')
