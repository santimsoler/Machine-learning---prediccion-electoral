import csv
W='Wikipedia (en) 2006/2011/2016/2021 Peruvian general election; UY: Wikipedia (en) 2014/2019/2024 Uruguayan general election'
M={}
def add(e,d,src):
    for k,v in d.items(): M[(e,k)]=(v,src)
pe='Wikipedia (en) Peruvian general election'
add('PE-2006-PRES-1',{'UNIDAD NACIONAL':'Lourdes Flores','ALIANZA POR EL FUTURO':'Martha Chávez','FRENTE DE CENTRO':'Valentín Paniagua','RESTAURACION NACIONAL':'Humberto Lay','CONCERTACION DESCENTRALISTA':'Susana Villarán','PARTIDO JUSTICIA NACIONAL':'Jaime Salinas','PARTIDO SOCIALISTA':'Javier Diez Canseco','ALIANZA PARA EL PROGRESO':'Natale Amprimo','CON FUERZA PERU':'Pedro Koechlin von Stein','MOVIMIENTO NUEVA IZQUIERDA':'Alberto Moreno','FUERZA DEMOCRATICA':'Alberto Borea','AVANZA PAIS - PARTIDO DE INTEGRACION SOCIAL':'Ulises Humala','PARTIDO RENACIMIENTO ANDINO':'Ciro Gálvez','PROGRESEMOS PERU':'Javier Espinoza','PARTIDO RECONSTRUCCION DEMOCRATICA':'José Cardó Guarderas','RESURGIMIENTO PERUANO':'Ántero Asto','Y SE LLAMA PERU':'Ricardo Wong','PERU AHORA':'Luis Guerrero'},pe+' 2006 (Cardó y Gálvez se retiraron antes de la elección)')
add('PE-2011-PRES-1',{'ALIANZA POR EL GRAN CAMBIO':'Pedro Pablo Kuczynski','PERU POSIBLE':'Alejandro Toledo','ALIANZA SOLIDARIDAD NACIONAL':'Luis Castañeda Lossio','FONAVISTAS DEL PERU':'José Ñique de la Puente','DESPERTAR NACIONAL':'Ricardo Noriega','ADELANTE':'Rafael Belaúnde Aubry','FUERZA NACIONAL':'Juliana Reymer','JUSTICIA, TECNOLOGIA, ECOLOGIA':'Humberto Pinazo','PARTIDO DESCENTRALISTA FUERZA SOCIAL':'Manuel Rodríguez Cuadros'},pe+' 2011')
add('PE-2016-PRES-1',{'EL FRENTE AMPLIO POR JUSTICIA, VIDA Y LIBERTAD':'Verónika Mendoza','ACCION POPULAR':'Alfredo Barnechea','ALIANZA POPULAR':'Alan García','DEMOCRACIA DIRECTA':'Gregorio Santos','FRENTE ESPERANZA':'Fernando Olivera','PERU POSIBLE':'Alejandro Toledo','PROGRESANDO PERU':'Miguel Hilario','PARTIDO POLITICO ORDEN':'Antero Flores Aráoz'},pe+' 2016')
add('PE-2021-PRES-1',{'RENOVACION POPULAR':'Rafael López Aliaga','AVANZA PAIS - PARTIDO DE INTEGRACION SOCIAL':'Hernando de Soto','ACCION POPULAR':'Yonhy Lescano','JUNTOS POR EL PERU':'Verónika Mendoza','ALIANZA PARA EL PROGRESO':'César Acuña','VICTORIA NACIONAL':'George Forsyth','PODEMOS PERU':'Daniel Urresti','PARTIDO MORADO':'Julio Guzmán','PARTIDO POPULAR CRISTIANO - PPC':'Alberto Beingolea','PARTIDO DEMOCRATICO SOMOS PERU':'Daniel Salaverry','PARTIDO NACIONALISTA PERUANO':'Ollanta Humala','RENACIMIENTO UNIDO NACIONAL':'Ciro Gálvez','EL FRENTE AMPLIO POR JUSTICIA, VIDA Y LIBERTAD':'Marco Arana','PERU PATRIA SEGURA':'Rafael Santos','DEMOCRACIA DIRECTA':'Andrés Alcántara'},pe+' 2021')
uy='Wikipedia (en) Uruguayan general election'
add('UY-2014-PRES-1',{'Frente Amplio':'Tabaré Vázquez','Partido Nacional':'Luis Lacalle Pou','Partido Colorado':'Pedro Bordaberry','Partido Independiente':'Pablo Mieres','Partido Asamblea Popular':'Gonzalo Abella','Partido Ecologista Radical Intransigente':'César Vega','Partido de los Trabajadores':'Rafael Fernández'},uy+' 2014')
add('UY-2019-PRES-1',{'Partido Frente Amplio':'Daniel Martínez','Partido Nacional':'Luis Lacalle Pou','Partido Colorado':'Ernesto Talvi','Partido Cabildo Abierto':'Guido Manini Ríos','Partido Ecologista Radical Intransigente':'César Vega','Partido de la Gente':'Edgardo Novick','Partido Independiente':'Pablo Mieres','Partido Asamblea Popular':'Gonzalo Abella','Partido Verde Animalista':'Gustavo Salle','Partido Digital':'Daniel Goldman','Partido de los Trabajadores':'Rafael Fernández Rodríguez'},uy+' 2019')
add('UY-2024-PRES-1',{'Partido Frente Amplio':'Yamandú Orsi','Partido Nacional':'Álvaro Delgado','Partido Colorado':'Andrés Ojeda','Partido Identidad Soberana':'Gustavo Salle','Partido Cabildo Abierto':'Guido Manini Ríos','Partido Independiente':'Pablo Mieres','Partido Constitucional Ambientalista':'Eduardo Lust','Partido Asamblea Popular':'Gonzalo Martínez','Partido Ecologista Radical Intransigente':'César Vega','Partido Por Los Cambios Necesarios (PCN)':'Guillermo Franchi','Partido Avanzar Republicano':'Martín Pérez Banchero'},uy+' 2024')
a19='AS/COA, explainer fórmulas 2019 (9-jul-2019)'
add('AR-2019-PRES-1',{'FRENTE DE TODOS':'Alberto Fernández - Cristina Fernández de Kirchner','JUNTOS POR EL CAMBIO':'Mauricio Macri - Miguel Ángel Pichetto','CONSENSO FEDERAL':'Roberto Lavagna - Juan Manuel Urtubey','FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD':'Nicolás del Caño - Romina del Plá','FRENTE NOS':'Juan José Gómez Centurión - Cynthia Hotton','UNITE POR LA LIBERTAD Y LA DIGNIDAD':'José Luis Espert - Luis Rosales'},a19)
c23='canal26, escrutinio definitivo 2023 (solo presidente; falta vice)'
for e in('AR-2023-PRES-1','AR-2023-PRES-2'):
    add(e,{'UNION POR LA PATRIA':'Sergio Massa','LA LIBERTAD AVANZA':'Javier Milei','JUNTOS POR EL CAMBIO':'Patricia Bullrich','HACEMOS POR NUESTRO PAIS':'Juan Schiaretti','FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD':'Myriam Bregman'},c23)
rows=list(csv.DictReader(open('final/candidatos.csv')))
n=0
for r in rows:
    k=(r['id_eleccion'],r['partido_o_coalicion'])
    if r['candidato_o_formula']=='' and k in M:
        r['candidato_o_formula'],src=M[k]; r['notas']=(r['notas']+'; ' if r['notas'] else '')+'nombre: '+src; n+=1
w=csv.DictWriter(open('final/candidatos.csv','w',newline='',encoding='utf-8'),fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(n,'completados;',sum(1 for r in rows if r['candidato_o_formula']==''),'quedan')
import collections;print(collections.Counter(r['id_eleccion'] for r in rows if r['candidato_o_formula']==''))
