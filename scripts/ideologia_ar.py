import csv,unicodedata
nz=lambda s:''.join(c for c in unicodedata.normalize('NFD',s.upper()) if unicodedata.category(c)!='Mn')
D='https://www.diariodecuyo.com.ar/noticias/las-dos-caras-de-las-propuestas-624663.html'
C19='https://chequeado.com/el-explicador/que-proponen-los-6-candidatos-presidenciales-en-caso-de-ganar/'
C23='https://chequeado.com/el-explicador/debate-presidencial-2023-que-proponen-milei-bullrich-y-massa-sobre-seguridad-y-trabajo/'
V23='https://www.vozdeamerica.com/a/quienes-son-los-cinco-candidatos-a-la-presidencia-de-argentina-/7319330.html'
# (elecciones, clave candidato, eje, valor, fuente, url, fecha, evidencia)
S=[
(['AR-2015'],'SCIOLI','e',-1,'Diario de Cuyo','21-nov-2015',D,'sin ajuste ni quita de subsidios; mantiene Precios Cuidados, Fútbol para Todos, AUH; baja retenciones'),
(['AR-2015'],'MACRI','e',1,'Diario de Cuyo','21-nov-2015',D,'menos intervención estatal; elimina cepo y Precios Cuidados; baja retenciones y Ganancias; mantiene planes sociales'),
(['AR-2019'],'ALBERTO FERNANDEZ','e',-1,'Chequeado','4-oct-2019',C19,'créditos baratos a familias, sin IVA a canasta básica, regular lobby empresarial'),
(['AR-2019'],'LAVAGNA','e',0,'Chequeado','4-oct-2019',C19,'equilibrio macro y déficit cero con acuerdos empresa-sindicato; mixto'),
(['AR-2019'],'DEL CANO','e',-2,'Chequeado','4-oct-2019',C19,'romper con el FMI, no pagar deuda, expropiar Barrick y Chevron'),
(['AR-2019'],'DEL CANO','s',-2,'Chequeado','4-oct-2019',C19,'legalizar el aborto'),
(['AR-2003'],'MENEM','s',1,'conocimiento general del analista (sin fuente citada)','',"",'conservador católico'),
(['AR-2003'],'KIRCHNER','s',-1,'conocimiento general del analista (sin fuente citada)','',"",'derechos humanos: anulación de punto final y obediencia debida'),
(['AR-2003'],'LOPEZ MURPHY','s',1,'conocimiento general del analista (sin fuente citada)','',"",'liberal-conservador, orden'),
(['AR-2003'],'RODRIGUEZ SAA','s',1,'conocimiento general del analista (sin fuente citada)','',"",'peronismo federal conservador'),
(['AR-2003'],'CARRIO','s',0,'conocimiento general del analista (sin fuente citada)','',"",'centro, agenda institucional'),
(['AR-1989'],'ANGELOZ','s',0,'conocimiento general del analista (sin fuente citada)','',"",'UCR de centro'),
(['AR-1989'],'ALSOGARAY','s',1,'conocimiento general del analista (sin fuente citada)','',"",'liberalismo conservador'),
(['AR-1995'],'MASSACCESI','s',0,'conocimiento general del analista (sin fuente citada)','',"",'UCR de centro'),
(['AR-1999'],'CAVALLO','s',1,'conocimiento general del analista (sin fuente citada)','',"",'liberal-conservador'),
(['AR-2007'],'RODRIGUEZ SAA','s',1,'conocimiento general del analista (sin fuente citada)','',"",'peronismo federal conservador'),
(['AR-2011'],'FERNANDEZ DE KIRCHNER','s',-1,'conocimiento general del analista (sin fuente citada)','',"",'matrimonio igualitario 2010 y ley de identidad de género'),
(['AR-2015'],'SCIOLI','s',0,'conocimiento general del analista (sin fuente citada)','',"",'peronismo oficialista, centro'),
(['AR-2015'],'MACRI','s',0,'conocimiento general del analista (sin fuente citada)','',"",'centro'),
(['AR-2019'],'LAVAGNA','s',0,'conocimiento general del analista (sin fuente citada)','',"",'centro'),
(['AR-2019'],'GOMEZ CENTURION','s',2,'Chequeado','4-oct-2019',C19,'contra el aborto desde la concepción; revaloriza fuerzas armadas y de seguridad'),
(['AR-2019'],'ESPERT','e',2,'Chequeado','4-oct-2019',C19,'baja gasto 40%, reduce aranceles, tratados de libre comercio, elimina regímenes de promoción'),
(['AR-2023'],'MILEI','e',2,'Voz de América (AP)','20-oct-2023',V23,'recorte drástico del gasto, cierre del BCRA, dolarización, privatizaciones, eliminar impuestos'),
(['AR-2023'],'MILEI','s',2,'Voz de América (AP) y Chequeado','20-oct-2023',V23,'contra el aborto; cuestiona educación sexual; desregular armas (Chequeado 27-sep-2023)'),
(['AR-2023'],'BULLRICH','e',1,'Voz de América (AP)','20-oct-2023',V23,'reforma del Estado, déficit cero, BCRA independiente, sin retenciones a granos, fin del cepo'),
(['AR-2023'],'BULLRICH','s',1,'Chequeado','27-sep-2023',C23,'baja imputabilidad a 14 años, amplía legítima defensa; sin postura sobre aborto en la fuente'),
(['AR-2023'],'MASSA','e',-1,'Chequeado y Voz de América','27-sep-2023',C23,'paritarias libres, piso salarial, Puente al Empleo; equilibrio fiscal y tipo de cambio competitivo'),
(['AR-2023'],'SCHIARETTI','e',0,'Voz de América (AP)','20-oct-2023',V23,'equilibrio fiscal, prudencia en emisión, política de ingresos'),
(['AR-2023'],'BREGMAN','e',-2,'Voz de América (AP)','20-oct-2023',V23,'romper con el FMI, no pagar deuda, expropiar mineras y energéticas sin indemnización'),
(['AR-2023'],'BREGMAN','s',-2,'Tiempo Argentino y Chequeado','8-oct-2023','https://www.tiempoar.com.ar/ta_article/elecciones-en-argentina-que-proponen-les-candidates-en-materia-de-genero-y-diversidad/amp/','aplicar la ley IVE y anticoncepción gratuita; ESI obligatoria, laica y científica; separar Iglesia y Estado (Chequeado 3-ago-2023)'),
(['AR-2023'],'MASSA','s',-1,'Tiempo Argentino','8-oct-2023','https://www.tiempoar.com.ar/ta_article/elecciones-en-argentina-que-proponen-les-candidates-en-materia-de-genero-y-diversidad/amp/','igual remuneración, cuidados; vice Rossi apoyó ley de identidad de género; sin postura reportada sobre aborto (confianza baja)'),
(['AR-2023'],'SCHIARETTI','s',0,'Tiempo Argentino y Chequeado','8-oct-2023','https://www.tiempoar.com.ar/ta_article/elecciones-en-argentina-que-proponen-les-candidates-en-materia-de-genero-y-diversidad/amp/','sistema de cuidados con perspectiva de género; sin postura reportada sobre aborto (confianza baja)'),
(['AR-2019'],'ALBERTO FERNANDEZ','s',-1,'Ámbito','13-oct-2019','https://www.ambito.com/el-aborto-otro-los-puntos-fuertes-del-debate-presidencial-n5059762','a favor de legalizar el aborto en el debate presidencial'),
(['AR-2019'],'ESPERT','s',1,'Ámbito','13-oct-2019','https://www.ambito.com/el-aborto-otro-los-puntos-fuertes-del-debate-presidencial-n5059762','rechaza que la ESI degenere en ideología de género; sin postura reportada sobre aborto (confianza baja)'),
(['AR-2011'],'FERNANDEZ DE KIRCHNER','e',-1,'Agrofy News','7-ago-2011','https://news.agrofy.com.ar/noticia/107850/null','profundizar las líneas de la gestión; controles de Moreno institucionalizados; recuperar superávit gemelos'),
(['AR-2007'],'LOPEZ MURPHY','e',1,'Consejo (Argentina y sus candidatos)','24-oct-2007','https://archivo.consejo.org.ar/noticias07/candidatospres_2410.htm','bajar impuestos a niveles sensatos, reglas fiscales claras, inversión en infraestructura energética'),
(['AR-2007'],'RODRIGUEZ SA','e',1,'Consejo (Argentina y sus candidatos)','24-oct-2007','https://archivo.consejo.org.ar/noticias07/candidatospres_2410.htm','el gobierno debe retirarse de la economía y el campo; sistema impositivo simple y presupuesto equilibrado'),
(['AR-2003'],'KIRCHNER','e',-1,'Real Instituto Elcano','14-abr-2003','https://www.realinstitutoelcano.org/analisis/informe-elecciones-presidenciales-argentinas-2003/','neokeynesiano; revisar privatizaciones y recuperar renta petrolera (sin estatizar); reprogramar deuda con quita'),
(['AR-2003'],'MENEM','e',2,'Real Instituto Elcano','14-abr-2003','https://www.realinstitutoelcano.org/analisis/informe-elecciones-presidenciales-argentinas-2003/','privatización inmediata de todo lo privatizable, superávit fiscal, Estado sólo rector y fiscalizador'),
(['AR-2003'],'RODRIGUEZ SA','e',-1,'Real Instituto Elcano','14-abr-2003','https://www.realinstitutoelcano.org/analisis/informe-elecciones-presidenciales-argentinas-2003/','revisar contratos de privatizadas, recuperar petróleo y ferrocarriles, redistribuir ingreso; austeridad estatal'),
(['AR-2003'],'LOPEZ MURPHY','e',2,'Real Instituto Elcano','14-abr-2003','https://www.realinstitutoelcano.org/analisis/informe-elecciones-presidenciales-argentinas-2003/','disciplina fiscal, apertura, línea privatizadora, bajar impuestos al trabajo y eliminar derechos de exportación'),
(['AR-2003'],'CARRIO','e',-1,'Real Instituto Elcano','14-abr-2003','https://www.realinstitutoelcano.org/analisis/informe-elecciones-presidenciales-argentinas-2003/','más presencia estatal en regulación, control de oligopolios, revisar concesiones, ingreso ciudadano'),
(['AR-1989'],'ALSOGARAY','e',2,'Wikipedia (en) 1989 Argentine general election','consultada nov-2026','https://en.wikipedia.org/wiki/1989_Argentine_general_election','libre mercado, privatizaciones masivas y fuertes recortes del gasto social'),
(['AR-1989'],'ANGELOZ','e',1,'Wikipedia (en) 1989 Argentine general election','consultada nov-2026','https://en.wikipedia.org/wiki/1989_Argentine_general_election','recortes del gasto social en la plataforma radical (confianza baja)'),
(['AR-2015'],'MASSA','e',1,'La Izquierda Diario (fuente crítica)','22-sep-2015','https://www.laizquierdadiario.com/Massa-2015-Presentismo-docente-y-terminar-con-la-extorsion-piquetera','déficit cero, fin del cepo en 100 días, eliminar Ganancias y bajar impuestos 30%'),
(['AR-2015'],'MASSA','s',1,'La Izquierda Diario (fuente crítica)','22-sep-2015','https://www.laizquierdadiario.com/Massa-2015-Presentismo-docente-y-terminar-con-la-extorsion-piquetera','Ejército junto a la policía contra el narcotráfico, 240 cárceles, reglamentar la protesta'),
(['AR-1983'],'ALFONSIN','e',-1,'Discurso de campaña Ferrocarril Oeste (alfonsin.org)','30-sep-1983','https://www.alfonsin.org/wp-content/uploads/2019/02/Discurso_de_campana-en_el_estadio_del_ClubFerrocarrilOeste.pdf','reactivar vía salario real, bajar tasas, reforma tributaria sobre consumos suntuarios, rechazo a recetas del FMI, con disciplina monetaria y fiscal'),
(['AR-1983'],'ALFONSIN','s',-1,'Discurso de campaña Ferrocarril Oeste (alfonsin.org)','30-sep-1983','https://www.alfonsin.org/wp-content/uploads/2019/02/Discurso_de_campana-en_el_estadio_del_ClubFerrocarrilOeste.pdf','rechaza la autoamnistía, equipara pena del torturador al homicida, pluralismo, sindicalismo independiente'),
(['AR-2007'],'FERNANDEZ DE KIRCHNER','e',-1,'Infobae (EFE) y Libertad y Desarrollo','30-oct-2007','https://www.infobae.com/2007/10/30/346227-cristina-kirchner-anticipo-sus-prioridades-y-dijo-que-tiene-alemania-como-modelo/','continuidad del modelo; prioridad pobreza, desempleo y educación; modelo exportador (LyD 23-ago-2007: equipo algo más ortodoxo; confianza baja)'),
(['AR-2007'],'CARRIO','e',-1,'Libertad y Desarrollo (la describe de centroizquierda)','23-ago-2007','https://lyd.org/storage/other/files_mf/EII-395-Argentina Elecciones presidenciales en Octubre mayor gasto y aumento de la inflacion-23-0.pdf','ARI descripta como centroizquierda; sin propuestas económicas detalladas (confianza baja)'),
(['AR-1983'],'LUDER','e',-1,'conocimiento general del analista (sin fuente citada)','',"",'peronismo tradicional'),
(['AR-1983'],'LUDER','s',1,'conocimiento general del analista (sin fuente citada)','',"",'campaña evocando a Perón; no condenó la amnistía militar'),
(['AR-1995'],'MENEM','e',2,'conocimiento general del analista (sin fuente citada)','',"",'continuidad de convertibilidad y privatizaciones'),
(['AR-1995'],'MENEM','s',1,'conocimiento general del analista (sin fuente citada)','',"",'conservador en valores'),
(['AR-1995'],'BORDON','e',-1,'conocimiento general del analista (sin fuente citada)','',"",'socialdemócrata FREPASO'),
(['AR-1995'],'BORDON','s',-1,'conocimiento general del analista (sin fuente citada)','',"",'socialdemócrata FREPASO'),
(['AR-1995'],'MASSACCESI','e',0,'conocimiento general del analista (sin fuente citada)','',"",'socioliberal UCR'),
(['AR-1999'],'DE LA RUA','e',0,'conocimiento general del analista (sin fuente citada)','',"",'Alianza: continuidad de la convertibilidad con ajuste moderado'),
(['AR-1999'],'DE LA RUA','s',0,'conocimiento general del analista (sin fuente citada)','',"",'centro'),
(['AR-1999'],'DUHALDE','e',-1,'conocimiento general del analista (sin fuente citada)','',"",'peronismo bonaerense, reactivación'),
(['AR-1999'],'DUHALDE','s',1,'conocimiento general del analista (sin fuente citada)','',"",'seguridad dura'),
(['AR-1999'],'CAVALLO','e',2,'conocimiento general del analista (sin fuente citada)','',"",'liberal-conservador, arquitecto de la convertibilidad'),
(['AR-2007'],'FERNANDEZ DE KIRCHNER','s',0,'conocimiento general del analista (sin fuente citada)','',"",'sin posición declarada sobre aborto'),
(['AR-2007'],'CARRIO','s',1,'conocimiento general del analista (sin fuente citada)','',"",'conservadora en aborto'),
(['AR-2011'],'BINNER','e',-1,'conocimiento general del analista (sin fuente citada)','',"",'socialista'),
(['AR-2011'],'BINNER','s',-1,'conocimiento general del analista (sin fuente citada)','',"",'socialista; apoyó el matrimonio igualitario'),
(['AR-2011'],'ALFONSIN','e',-1,'conocimiento general del analista (sin fuente citada)','',"",'UCR socialdemócrata'),
(['AR-2011'],'ALFONSIN','s',0,'conocimiento general del analista (sin fuente citada)','',"",'centro'),
(['AR-2011'],'DUHALDE','e',-1,'conocimiento general del analista (sin fuente citada)','',"",'peronismo tradicional'),
(['AR-2011'],'DUHALDE','s',1,'conocimiento general del analista (sin fuente citada)','',"",'orden y seguridad'),
(['AR-2019'],'MACRI','e',1,'conocimiento general del analista (sin fuente citada)','',"",'continuidad de su programa 2015: menos intervención, reforma fiscal y laboral'),
(['AR-2019'],'MACRI','s',0,'conocimiento general del analista (sin fuente citada)','',"",'centro'),
(['AR-1989'],'MENEM','e',-1,'conocimiento general del analista (sin fuente citada)','',"",'campaña "salariazo" y "revolución productiva"; programa populista, antes del giro de 1989-90'),
(['AR-1989'],'MENEM','s',1,'conocimiento general del analista (sin fuente citada)','',"",'peronismo tradicional, catolicismo; contrario al aborto'),
(['AR-2007'],'LAVAGNA','e',0,'conocimiento general del analista (sin fuente citada)','',"",'ex ministro de Economía; heterodoxia con equilibrio fiscal'),
(['AR-2007'],'LAVAGNA','s',0,'conocimiento general del analista (sin fuente citada)','',"",'centro'),
(['AR-2007'],'SOLANAS','e',-2,'conocimiento general del analista (sin fuente citada)','',"",'Proyecto Sur, nacionalismo económico de izquierda'),
(['AR-2007'],'SOLANAS','s',-1,'conocimiento general del analista (sin fuente citada)','',"",'izquierda nacional progresista'),
(['AR-2011'],'RODRIGUEZ SAA','e',-1,'conocimiento general del analista (sin fuente citada)','',"",'peronismo federal'),
(['AR-2011'],'RODRIGUEZ SAA','s',1,'conocimiento general del analista (sin fuente citada)','',"",'peronismo federal, conservador en lo social'),
(['AR-2015'],'DEL CANO','e',-2,'conocimiento general del analista (sin fuente citada)','',"",'Frente de Izquierda, trotskismo'),
(['AR-2015'],'DEL CANO','s',-2,'conocimiento general del analista (sin fuente citada)','',"",'Frente de Izquierda, agenda progresista'),
]
rows=list(csv.DictReader(open('final/candidatos.csv')))
for r in rows:
    if r['version_codebook']=='v1':
        r['eje_economico']='pendiente';r['eje_sociocultural']='pendiente';r['fuente_ideologia']='';r['version_codebook']=''
ev=[];n=0
for el,key,eje,val,fu,fe,url,txt in S:
    hit=[r for r in rows if any(r['id_eleccion'].startswith(e) for e in el) and key in nz(r['candidato_o_formula'])]
    assert hit,key
    for r in hit:
        col='eje_economico' if eje=='e' else 'eje_sociocultural'
        r[col]=str(val); r['version_codebook']='v1'
        r['fuente_ideologia']=(r['fuente_ideologia']+' | ' if r['fuente_ideologia'] else '')+f"{col[5:8]}: {fu} {fe}"
        n+=1
    for r in hit[:1]: ev.append([r['id_eleccion'][:7],r['candidato_o_formula'],'economico' if eje=='e' else 'sociocultural',val,fu,fe,url,txt,'claude_v1','una_sola_codificacion','conocimiento_general_verificar' if fu.startswith('conocimiento') else 'fuente_citada'])
w=csv.DictWriter(open('final/candidatos.csv','w',newline='',encoding='utf-8'),fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
w=csv.writer(open('final/ideologia_evidencia.csv','w',newline='',encoding='utf-8'))
w.writerow(['elecciones','candidato','eje','valor','fuente','fecha_fuente','url','evidencia_resumida','codificador','control','nivel_evidencia'])
w.writerows(ev)
print(n,len(ev))
