import pandas as pd
R=[
("AR-2019","AR",2019,"Mauricio Macri","UdeSA (según iProfesional; a verificar institución)","","2019-01-12",35,62,"2019-10-27","https://www.iprofesional.com/politica/284742-El-62-desaprueba-a-Macri-pero-64-nunca-votaria-a-Cristina","Aprobación del desempeño del gobierno. Horizonte largo (~9 meses): reemplazar por medición de julio-2019 si se encuentra."),
("AR-2023","AR",2023,"Alberto Fernández","UdeSA (Satisfacción Política y Opinión Pública)","2023-03-22/2023-03-30","2023-04-09",17,81,"2023-10-22","https://www.bloomberglinea.com/latinoamerica/argentina/a-cuatro-meses-de-las-paso-una-encuesta-marca-desaprobacion-record-del-gobierno/","Medición más cercana encontrada (~205 días antes). Alternativa: Poliarquía, desaprobación 71% e imagen positiva 18% (La Nación 2023-04-20)."),
("BR-2022","BR",2022,"Jair Bolsonaro","Datafolha","2022-06-22/2022-06-23","2022-06-24",26,47,"2022-10-02","https://www.correiobraziliense.com.br/politica/2022/06/5017652-datafolha-governo-bolsonaro-e-rejeitado-por-47-aprovacao-e-de-26.html","Aprobación = 'ótimo' 26% (la nota no separa 'bom'); desaprobación = ruim/péssimo. Escala distinta a approve/disapprove."),
("BR-2026","BR",2026,"Luiz Inácio Lula da Silva","Datafolha","","",32,38,"2026-10-04","https://tribunadejundiai.com.br/politica/eleicoes-2026/datafolha-avaliacao-governo-lula-julho-2026/","Ótimo/bom 32, ruim/péssimo 38, regular 28. Aprobación del trabajo de Lula: 49% aprueba / 48% desaprueba. Fecha de campo no informada (julio 2026)."),
("CL-2021","CL",2021,"Sebastián Piñera","Cadem Plaza Pública","2021-08-11/2021-08-13","",27,64,"2021-11-21","https://cadem.cl/wp-content/uploads/2021/08/Plaza-Publica-396-Agosto-S2.pdf","n=704."),
("CL-2025","CL",2025,"Gabriel Boric","Cadem Plaza Pública","2025-07 (2ª semana)","2025-07-13",38,55,"2025-11-16","https://www.biobiochile.cl/noticias/nacional/chile/2025/07/13/aprobacion-al-alza-presidente-boric-consigue-su-mejor-desempeno-en-cadem-en-mas-de-dos-anos.shtml",""),
("CO-2022","CO",2022,"Iván Duque","Invamer","2022-02-04/2022-02-13","2022-02-16",20,73,"2022-05-29","https://www.bluradio.com/nacion/desaprobacion-de-ivan-duque-sube-a-73-segun-encuesta-invamer",""),
("CO-2026","CO",2026,"Gustavo Petro","Invamer","","2026-02-26",49.1,46.1,"2026-05-31","https://www.rtvcnoticias.com/politica/gobierno/aprobacion-presidente-petro-aumento-invamer","n=3800. Fecha de campo no informada."),
("PE-2021","PE",2021,"Francisco Sagasti","Ipsos Perú","2021-01-13/2021-01-15","",34,47,"2021-04-11","https://www.ipsos.com/sites/default/files/ct/news/documents/2021-01/opinion_data_-_enero_2021.pdf","Cifras leídas de gráfico; columnas suman 100."),
("PE-2026","PE",2026,"José Jerí","Ipsos Perú / Perú21","2026-01-07/2026-01-08","",43,43,"2026-04-12","https://www.ipsos.com/sites/default/files/ct/news/documents/2026-01/Encuesta%20-%20Per%C3%BA%2021%20-%20%20Aprobaci%C3%B3n%20Autoridades%2C%20Petroper%C3%BA%2C%20Venezuela%20Final.pdf","Jerí no era presidente en la elección (interino posterior: Balcázar). Revisar qué medición usar."),
("UY-2024","UY",2024,"Luis Lacalle Pou","Equipos Consultores","datos hasta 2024-04","2024-05-29",49,32,"2024-10-27","https://www.ambito.com/uruguay/el-49-los-os-aprueba-la-gestion-lacalle-pou-n6006920","18% ni aprueba ni desaprueba."),
]
c=["id_eleccion","pais","anio","presidente","encuestadora","fecha_campo","fecha_publicacion","aprobacion_pct","desaprobacion_pct","fecha_primera_vuelta","fuente_url","notas"]
d=pd.DataFrame(R,columns=c)
ref=pd.to_datetime(d.fecha_publicacion.replace("",pd.NA).fillna(d.fecha_campo.str[:10].where(d.fecha_campo.str.match(r"\d{4}-\d{2}-\d{2}"))),errors="coerce")
d["dias_a_primera_vuelta"]=(pd.to_datetime(d.fecha_primera_vuelta)-ref).dt.days
d.to_csv("final/aprobacion_presidencial_post2019.csv",index=False)
print(d[["id_eleccion","aprobacion_pct","desaprobacion_pct","dias_a_primera_vuelta"]])
