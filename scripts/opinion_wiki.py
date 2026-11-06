import csv
H=['id_eleccion','pais','candidato','variable','encuestadora','fecha_campo_inicio','fecha_campo_fin','valor','n_muestra','fuente','notas']
rows=list(csv.reader(open('final/opinion_candidatos.csv',encoding='utf-8')))[1:]
rows=[r for r in rows if r[0].startswith('BR-') and not r[0].startswith('BR-2026')]  # idempotente: conservar Brasil previo
def wiki(p,y): return f'Wikipedia: Opinion polling for the {y} {p} (consultada 2026-11-02)'
def blk(eid,pais,fuente,var,names,data,notas=''):
    for pol,ini,fin,n,vals in data:
        for nm,v in zip(names,vals):
            if v is None: continue
            rows.append([eid,pais,nm,var,pol,ini,fin,v,n if n else '',fuente,notas])
# Chile 2025 (última de cada encuestadora en la ventana de 30 días)
c25=['Jeannette Jara','José Antonio Kast','Evelyn Matthei','Johannes Kaiser','Franco Parisi','Harold Mayne-Nicholls','Eduardo Artés','Marco Enríquez-Ominami']
blk('CL-2025-PRES-1','CL',wiki('Chilean presidential election','2025'),'intencion_voto_total_pct',c25,[
('Panel Ciudadano','2025-10-30','2025-10-31',None,[26,21,14,14,10,3,1,1]),
('Activa','2025-10-28','2025-10-31',None,[24.9,16.9,11.2,12.2,14.0,3.4,0.6,1.9]),
('AtlasIntel','2025-10-25','2025-10-30',None,[33.2,16.8,13.9,16.8,14.2,1.9,0.1,1.0]),
('Black & White','2025-10-28','2025-10-29',None,[30,23,17,20,7,3,1,1]),
('Criteria','2025-10-27','2025-10-29',None,[27,23,14,15,9,3,1,2]),
('Data Influye','2025-10-23','2025-10-29',None,[27,20,11,13,9,3,1,2]),
('LCN','2025-10-17','2025-10-28',None,[33.5,17.7,19.3,19.3,4.5,4.3,0,0.7]),
('Cadem','2025-10-22','2025-10-24',None,[27,20,13,14,11,4,1,1]),
('ICSO-UDP','2025-10-17','2025-10-21',None,[26,24,14,10,9,2,0,1])],'sin tamaño muestral en la fuente; la base (total o válidos) varía por encuestadora y no está indicada en Wikipedia')
c21=['Gabriel Boric','José Antonio Kast','Yasna Provoste','Sebastián Sichel','Franco Parisi','Eduardo Artés','Marco Enríquez-Ominami']
blk('CL-2021-PRES-1','CL',wiki('Chilean presidential election','2021'),'intencion_voto_total_pct',c21,[
('Cadem (base 100)','2021-11-20','2021-11-20',None,[27,29,11,14,13,2,5]),
('AtlasIntel','2021-11-05','2021-11-06',None,[21.9,27.2,9.2,11.7,11.4,2.8,6.2]),
('Activa (general)','2021-11-02','2021-11-05',None,[17.7,21.7,10.9,8.2,7.3,1.9,3.9]),
('UDD','2021-11-02','2021-11-03',None,[22,25,10,9,10,2,5]),
('Criteria (general)','2021-10-29','2021-11-02',None,[24,23,9,8,8,2,6]),
('Feedback (votante probable)','2021-10-29','2021-11-02',None,[30,36,9,11,4,1,2]),
('Studio Público','2021-10-26','2021-10-31',None,[27.6,37.9,11.4,10.5,5.9,1.9,4.7]),
('Tú Influyes','2021-10-29','2021-10-29',None,[32,27,13,9,8,2,4]),
('La Cosa Nostra','2021-10-20','2021-10-26',None,[36,30,14,11,5,2,4])],'tipo de muestra según Wikipedia (general / votante probable / base 100); tamaño muestral no consignado')
p26=['Keiko Fujimori','Rafael López Aliaga','Carlos Álvarez','Roberto Sánchez','Alfonso López Chau','Mario Vizcarra']
pn=['Keiko Fujimori','Rafael López Aliaga','Nieto','Roberto Sánchez','Álvarez','Belmont']
blk('PE-2026-PRES-1','PE',wiki('Peruvian general election','2026'),'intencion_voto_validos_pct',pn,[
('Ipsos Perú/Perú 21','2026-04-01','2026-04-02',1192,[18.6,10.9,5.6,9.0,12.1,4.3]),
('Datum Internacional/El Comercio','2026-04-01','2026-04-04',1422,[18.1,10.3,7.2,7.2,10.8,6.5]),
('CPI/RPP','2026-04-03','2026-04-04',1722,[16.2,13.0,6.4,5.2,11.8,5.9])],'excluye blancos (filas "Excl. blank" de Wikipedia); los apellidos Nieto, Álvarez y Belmont figuran así en la tabla; normalizar a nombre completo contra candidatos.csv')
blk('PE-2026-PRES-2','PE',wiki('Peruvian general election','2026'),'intencion_voto_total_pct',['Keiko Fujimori','Roberto Sánchez'],[
('Ipsos','2026-06-06','2026-06-06',4032,[44.1,43.7]),
('Datum Internacional','2026-06-06','2026-06-06',2622,[44.9,43.9]),
('Ipsos','2026-06-03','2026-06-03',1231,[43.2,43.8]),
('IEP/La República','2026-05-22','2026-05-26',1204,[36.0,30.0])],'incluye blanco/nulo e indecisos fuera de la columna')
p21=['Pedro Castillo','Keiko Fujimori','Rafael López Aliaga','Hernando de Soto','Yonhy Lescano','Julio Guzmán','Verónika Mendoza']
blk('PE-2021-PRES-1','PE',wiki('Peruvian general election','2021'),'intencion_voto_total_pct',p21,[
('IEP/La República','2021-04-01','2021-04-02',1212,[6.6,9.8,8.4,9.8,8.2,2.3,7.3]),
('Ipsos Perú/El Comercio','2021-03-31','2021-03-31',1505,[6,8,6,9,10,2,9]),
('CPI/Exitosa','2021-03-19','2021-03-23',1600,[4.3,7.1,5.2,4.5,11,2,5.4]),
('Datum/Perú 21/Gestión','2021-03-18','2021-03-21',1201,[3,8,9,5,14,2,6])],'incluye blanco/nulo e indecisos fuera de la columna; la tabla fuente termina el 2-abr-2021 (restricción de difusión de encuestas)')
co=['Gustavo Petro','Federico Gutiérrez','Rodolfo Hernández','Sergio Fajardo']
blk('CO-2022-PRES-1','CO',wiki('Colombian presidential election','2022'),'intencion_voto_pct',co,[
('AtlasIntel','2022-05-17','2022-05-20',2781,[40.0,26.7,21.4,8.8]),
('CELAG','2022-05-16','2022-05-20',2174,[45.1,20.1,20.4,4.9]),
('Guarumo','2022-05-16','2022-05-19',2258,[37.9,30.8,20.3,4.3]),
('CNC','2022-05-13','2022-05-19',3860,[41.0,23.9,21.9,4.5]),
('Invamer','2022-05-13','2022-05-18',1312,[40.6,27.1,20.9,5.1]),
('Mosqueteros','2022-05-15','2022-05-18',6000,[44.7,22.4,15.8,6.9])],'base (válidos o total) no especificada por Wikipedia')
ar=['Sergio Massa','Javier Milei','Patricia Bullrich','Juan Schiaretti','Myriam Bregman']
blk('AR-2023-PRES-1','AR',wiki('Argentine general election','2023'),'intencion_voto_pct',ar,[
('AtlasIntel','2023-10-10','2023-10-13',5702,[30.9,26.5,24.4,10.0,3.2]),
('Consultora Tendencias','2023-10-09','2023-10-12',17702,[29.8,30.2,23.1,4.6,3.9]),
('Clivajes Consultores','2023-10-09','2023-10-11',1240,[31.4,33.1,26.8,3.6,2.1]),
('Circuitos Consultora','2023-10-09','2023-10-11',2131,[32.3,34.1,24.4,2.1,2.3]),
('CB Consultora','2023-10-09','2023-10-11',4069,[29.1,29.9,21.8,3.4,6.0]),
('Opinaia','2023-10-02','2023-10-11',2000,[29,32,22,3,7]),
('DC Consultores','2023-10-07','2023-10-10',2700,[26.2,35.6,28.9,3.4,2.7]),
('Proyección Consultores','2023-10-03','2023-10-09',2966,[30.9,35.5,23.2,2.7,3.4]),
('CIGP','2023-10-05','2023-10-08',1500,[28.1,27.2,20.9,1.3,5.8]),
('Giacobbe & Asociados','2023-09-30','2023-10-07',2500,[28.5,32.9,27.3,3.3,4.2]),
('Fixer','2023-10-02','2023-10-05',2506,[26.1,34.3,25.4,3.1,5.5]),
('Zuban Córdoba & Asociados','2023-10-03','2023-10-04',1400,[32.7,34.7,25.0,1.6,2.7]),
('Reale Dalla Torre','2023-09-28','2023-10-03',2615,[24.7,36.2,21.8,3.8,5.0]),
('Aresco','2023-09-21','2023-09-29',1200,[32.1,35.0,25.9,2.3,4.7]),
('UdeSA','2023-09-14','2023-09-25',1000,[29.8,34.7,26.4,3.0,6.0])],'los porcentajes dejan fuera a indecisos (columna aparte en la fuente), por lo que no suman 100')

# --- Brasil 2026 (Datafolha final, publicada 2026-10-01; notas de prensa) ---
T1='Tribuna de Jundiaí 2026-10-01 (Datafolha, registro BR-08039/2026)'
for c,v in [('Lula',42),('Flávio Bolsonaro',38),('Augusto Cury',4),('Ronaldo Caiado',3),('Renan Santos',3),('Romeu Zema',1),('Samara Martins',1),('Wilson Grassi',1)]:
    rows.append(['BR-2026-PRES-1','BR',c,'intencion_voto_total_pct','Datafolha','','',v,2506,T1,'fechas de campo no indicadas en la nota; publicada 2026-10-01; blanco/nulo 5%, indecisos 2%'])
for c,v in [('Lula',45),('Flávio Bolsonaro',40)]:
    rows.append(['BR-2026-PRES-1','BR',c,'intencion_voto_validos_pct','Datafolha','','',v,2506,T1,'según la nota'])
for c,v in [('Lula',45),('Flávio Bolsonaro',45),('Renan Santos',16),('Romeu Zema',15),('Ronaldo Caiado',14),('Augusto Cury',11)]:
    rows.append(['BR-2026-PRES-1','BR',c,'rechazo_pct','Datafolha','','',v,2506,T1,'publicada 2026-10-01'])
D1='DGABC 2026-09-24 (Datafolha, registro BR-00304/2026)'
for c,v in [('Lula',45),('Flávio Bolsonaro',45),('Renan Santos',15),('Romeu Zema',14),('Ronaldo Caiado',13),('Augusto Cury',8),('Samara Martins',9),('Wilson Grassi',5)]:
    rows.append(['BR-2026-PRES-1','BR',c,'rechazo_pct','Datafolha','2026-09-22','2026-09-23',v,2002,D1,'publicada 2026-09-24'])
# --- Colombia 2026 ---
W26='Wikipedia: 2026 Colombian presidential election (consultada 2026-11-02)'
blk('CO-2026-PRES-1','CO',W26,'intencion_voto_pct',['Iván Cepeda','Abelardo de la Espriella','Paloma Valencia','Sergio Fajardo'],[
('Invamer','2026-05-13','2026-05-20',2224,[44.6,31.6,14.0,2.2]),
('AtlasIntel/SEMANA','2026-05-09','2026-05-14',5039,[36.0,31.5,16.0,4.7])],'la fila de Fundación Génesis Crea no se cargó: la tabla fuente es inconsistente')
blk('CO-2026-PRES-2','CO',W26,'intencion_voto_pct',['Iván Cepeda','Abelardo de la Espriella'],[
('Génesis Crea','2026-05-04','2026-05-11',4352,[46.5,41.4]),
('AtlasIntel/SEMANA','2026-05-11','2026-05-14',5039,[40.4,44.0]),
('Invamer','2026-05-13','2026-05-20',2224,[52.4,45.3]),
('AtlasIntel/SEMANA','2026-05-18','2026-05-21',None,[41.3,50.0]),
('CNC','2026-05-15','2026-05-22',None,[40.9,43.6]),
('AtlasIntel/SEMANA','2026-06-01','2026-06-02',None,[42.6,50.3]),
('AtlasIntel/SEMANA','2026-06-05','2026-06-10',None,[44.5,52.2]),
('Guarumo/EcoAnalítica','2026-06-08','2026-06-11',None,[45.0,52.6]),
('AtlasIntel/SEMANA','2026-06-09','2026-06-11',None,[44.4,52.4]),
('CNC','2026-06-06','2026-06-13',None,[44.7,48.6])],'segunda vuelta del 21-jun-2026; tamaño muestral omitido donde la fuente no es clara')
# --- Argentina 2019 ---
blk('AR-2019-PRES-1','AR',wiki('Argentine general election','2019'),'intencion_voto_pct',['Alberto Fernández','Mauricio Macri','Roberto Lavagna','Nicolás del Caño','José Luis Espert','Juan José Gómez Centurión'],[
('Opinaia','2019-09-30','2019-09-30',3000,[48,30,7,2,3,2])],'única encuesta en la tabla de Wikipedia para el período final; resultado PASO 2019-08-11 (47,7/32,1/8,2/2,9/2,2/2,6) no es encuesta')

# --- Brasil 2010 ---
blk('BR-2010-PRES-1','BR',wiki('Brazilian presidential election','2010'),'intencion_voto_total_pct',['Dilma Rousseff','José Serra','Marina Silva'],[
('Datafolha','2010-10-01','2010-10-02',None,[47,29,16]),
('Ibope','2010-10-01','2010-10-02',None,[47,29,16]),
('Datafolha','2010-09-28','2010-09-29',None,[47,28,14]),
('CNT/Sensus','2010-09-26','2010-09-28',None,[47.5,25.6,11.6]),
('Vox Populi','2010-10-02','2010-10-02',None,[47,26,14])],'tamaño muestral no consignado en la fuente')
# --- Chile 2025 segunda vuelta ---
rows.append(['CL-2025-PRES-2','CL','José Antonio Kast','intencion_voto_validos_pct','Cadem','','',58,'','BioBioChile 2025-11-30 (Cadem)','publicada 2025-11-29/30; fechas de campo y muestra no indicadas; suma 100 (base válidos)'])
rows.append(['CL-2025-PRES-2','CL','Jeannette Jara','intencion_voto_validos_pct','Cadem','','',42,'','BioBioChile 2025-11-30 (Cadem)','publicada 2025-11-29/30'])
# --- Colombia 2018 ---
CC='Valora Analitik 2018-05-10/11 (Cifras & Conceptos, Polimétrica Caracol Radio)'
for c,v in [('Iván Duque',34.0),('Gustavo Petro',22.5),('Sergio Fajardo',13.8),('Germán Vargas Lleras',13.2),('Humberto de la Calle',3.0)]:
    rows.append(['CO-2018-PRES-1','CO',c,'intencion_voto_pct','Cifras & Conceptos','2018-05-03','2018-05-07',v,2977,CC,'voto en blanco 6,8%'])
IV='Valora Analitik 2018-03-22 (Invamer)'
for c,v in [('Iván Duque',45.9),('Gustavo Petro',26.7),('Sergio Fajardo',10.7)]:
    rows.append(['CO-2018-PRES-1','CO',c,'intencion_voto_pct','Invamer','','',v,'',IV,'encuesta de marzo de 2018 (fuera de la ventana de 60 días); fechas y muestra no indicadas'])
# --- Uruguay 2024: estimaciones por partido mapeadas al candidato presidencial ---
UY=[('Frente Amplio','Yamandú Orsi'),('Partido Nacional','Álvaro Delgado'),('Partido Colorado','Andrés Ojeda'),('Cabildo Abierto','Guido Manini Ríos'),('Partido Independiente','Pablo Mieres'),('Identidad Soberana','Gustavo Salle')]
UYD=[('Opción',[45,24,16,4,1,4],'incluye indecisos en blanco/anulado/indefinido'),('Factum',[45.5,25.1,15.0,4.1,2.5,2.9],''),('Cifra',[46,25,16,3,2,2],''),('Equipos',[45.8,24.8,17.7,2.1,2.2,1.9],'')]
for pol,vals,nt in UYD:
    for (par,cand),v in zip(UY,vals):
        rows.append(['UY-2024-PRES-1','UY',cand,'intencion_voto_partido_pct',pol,'','',v,'','El Observador 2024-10-26 (últimas encuestas antes del 27-oct)','estimación por PARTIDO mapeada al candidato presidencial; fechas y muestra no indicadas; '+nt])

# --- Brasil 2014 (Datafolha 1-2 oct, Congresso em Foco) ---
F='Congresso em Foco 2014-10-02 (Datafolha, protocolo BR-00933/2014)'
for c,t,v in [('Dilma Rousseff',40,45),('Marina Silva',24,27),('Aécio Neves',21,24),('Pastor Everaldo',1,None),('Luciana Genro',1,None),('Eduardo Jorge',1,None)]:
    rows.append(['BR-2014-PRES-1','BR',c,'intencion_voto_total_pct','Datafolha','2014-10-01','2014-10-02',t,12022,F,'blanco/nulo 5%, indecisos 5%'])
    if v: rows.append(['BR-2014-PRES-1','BR',c,'intencion_voto_validos_pct','Datafolha','2014-10-01','2014-10-02',v,12022,F,''])
rows.append(['BR-2014-PRES-1','BR','Dilma Rousseff','rechazo_pct','Datafolha','2014-10-01','2014-10-02',32,12022,F,'solo se informa para Dilma'])

# --- Uruguay 2019 / 2024 balotaje ---
FA='Factum, Encuesta Nacional, estimación de voto octubre 2019 (portal.factum.uy)'
for c,v in [('Daniel Martínez',38),('Luis Lacalle Pou',27),('Ernesto Talvi',16),('Guido Manini Ríos',10),('Edgardo Novick',2),('Pablo Mieres',2)]:
    rows.append(['UY-2019-PRES-1','UY',c,'intencion_voto_partido_pct','Factum','2019-10-02','2019-10-08',v,1004,FA,'estimación por partido mapeada al candidato; indicador de 21 variables, no proyección; "no sabe" 4%'])
RA='Montevideo Portal 2019-09-17 (Radar, VTV Noticias)'
for c,v in [('Daniel Martínez',40.2),('Luis Lacalle Pou',22),('Ernesto Talvi',17),('Guido Manini Ríos',10.3),('Pablo Mieres',1.3),('Edgardo Novick',0.7)]:
    rows.append(['UY-2019-PRES-1','UY',c,'intencion_voto_total_pct','Radar','2019-09-11','2019-09-16','%s'%v,'',RA,'blanco/anulado 2,3%, no sabe 2,7%; encuesta de septiembre (fuera de la ventana de 30 días)'])
OP='El Observador 2019-11-11 (Opción Consultores, Telenoche)'
for c,v in [('Luis Lacalle Pou',47),('Daniel Martínez',42)]:
    rows.append(['UY-2019-PRES-2','UY',c,'intencion_voto_total_pct','Opción','2019-11-04','2019-11-08',v,1000,OP,'blanco/anulado 5%, indecisos 6%'])
EQ='Equipos, Intención de voto Balotaje 2024-11-12 (equipos.com.uy)'
for c,v in [('Yamandú Orsi',45),('Álvaro Delgado',41)]:
    rows.append(['UY-2024-PRES-2','UY',c,'intencion_voto_total_pct','Equipos','2024-11-02','2024-11-11',v,1000,EQ,'blanco/nulo 6%, indecisos 8%'])
MZ='MDZ Online 2024-11-22 (resumen de encuestas del balotaje)'
for pol,ini,fin,o,d in [('Factum','2024-11-15','2024-11-19',47.1,46.6),('Cifra','2024-11-14','2024-11-20',47.0,46.4),('Equipos','','',48.0,46.2)]:
    for c,v in [('Yamandú Orsi',o),('Álvaro Delgado',d)]:
        rows.append(['UY-2024-PRES-2','UY',c,'intencion_voto_total_pct',pol,ini,fin,v,'',MZ,'indecisos/blanco aparte; Equipos sin fechas en la nota'])

# --- Perú 2026: Ipsos (potencial de voto y rechazo) ---
IP='Ipsos Perú/Perú 21, "Potencial de voto candidatos", abril 2026 (ipsos.com/es-pe, nodo 1073791)'
for c,v in [('Keiko Fujimori',10),('Carlos Álvarez',7),('Rafael López Aliaga',6),('César Acuña',2)]:
    rows.append(['PE-2026-PRES-1','PE',c,'voto_definitivo_pct','Ipsos','2026-04-01','2026-04-02','%s'%v,'',IP,'"definitivamente votaría"; n no indicada en la página'])
rows.append(['PE-2026-PRES-1','PE','Keiko Fujimori','rechazo_pct','Ipsos','2026-04-01','2026-04-02',59,'',IP,'"definitivamente no votaría"; solo informado para Fujimori'])

w=csv.writer(open('final/opinion_candidatos.csv','w',newline='',encoding='utf-8'));w.writerow(H);w.writerows(rows);print(len(rows))
