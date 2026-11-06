import pandas as pd, math, re, unicodedata
A='/mnt/user-data/attachments/fbc2a8cf-9f07-5c94-8ce1-557ba4094ca9/'
ch=pd.read_csv(A+'f1c2292b-ches_la_2020_aggregate_level_v01.csv',encoding='latin-1').set_index(['country_abb','party_abb'])
def cont(x): return None if pd.isna(x) else round((x-5)/2.5,2)
def rd(v): return None if v is None else int(math.copysign(math.floor(abs(v)+0.5),v))
def nrm(t): return re.sub(r'[^a-z ]','',unicodedata.normalize('NFKD',str(t)).encode('ascii','ignore').decode().lower())
cand=pd.read_csv('final/candidatos.csv'); cand['share']=pd.to_numeric(cand.share_nacional_pct,errors='coerce')
CC='conocimiento_general_verificar'; FC='fuente_citada'; CP='ches_la_partido'
# (eleccion, clave_apellido, pais, party_ches|None, e, s, nivel, fuente, fecha, url, nota)
U_CG='https://www.congressoemfoco.com.br/artigo/119689/propostas-economicas-e-fiscais-dos-principais-candidatos-de-2026'
U_GP='https://gazetadopovo.com.br/eleicoes/2026/como-lula-e-flavio-bolsonaro-se-posicionam-em-6-temas-centrais-da-corrida-presidencial'
U_BBC='https://www.elobservador.com.uy/bbc-news-mundo/como-se-comparan-las-propuestas-mas-emblematicas-jara-y-kast-cara-las-elecciones-presidenciales-chile-este-domingo-n6027664'
U_TS='https://www.tiempodesanjuan.com/el-mundo/elecciones-chile-quienes-son-los-candidatos-que-proponen-y-como-llegan-las-urnas-n416799/amp'
U_BL='https://www.bloomberglinea.com/latinoamerica/colombia/lista-de-propuestas-y-planes-de-gobierno-de-ivan-cepeda-y-abelardo-de-la-espriella/'
U_PV='https://www.bloomberglinea.com/latinoamerica/colombia/quien-es-y-cuales-son-las-propuestas-de-paloma-valencia-candidata-a-la-presidencia-2026/'
U_SM='https://www.semana.com/politica/articulo/las-propuestas-de-abelardo-de-la-espriella-en-13-puntos-clave/202654/'
U_PM='https://www.publimetro.co/noticias/2026/08/27/ciclo-del-milagro-filtran-plan-del-gobierno-que-busca-porte-legal-de-armas-prohibir-aborto-y-acabar-con-la-jep/'
U_IN='https://www.infobae.com/peru/2026/04/06/planes-de-gobierno-sobre-economia-2026-2031-propuestas-de-los-candidatos-presidenciales-en-las-elecciones-2026/'
U_BP='https://www.bloomberglinea.com/latinoamerica/peru/lista-completa-de-candidatos-a-elecciones-2026-en-peru-y-principales-propuestas/'
U_GE='https://gestion.pe/peru/nuevo-plan-de-roberto-sanchez-que-cambio-respecto-al-programa-original-de-juntos-por-el-peru-noticia/'
U_BB='https://www.biobiochile.cl/noticias/internacional/america-latina/2026/06/05/roberto-sanchez-defendio-postura-a-favor-de-legalizar-de-aborto-en-caso-de-violacion-en-peru.shtml'
U_CH='CHES-LA 2020 (ches_la_2020_aggregate_level_v01.csv), ola 1 (jul-oct 2020); Peru ola 1.2 (may 2021)'
R=[
('BR-2026','flavio','BR','JB',1,2,FC,'Congresso em Foco; Gazeta do Povo + CHES-LA (Jair Bolsonaro, proxy sociocultural)','2026-06-16 / 2026-07-29',U_CG+' | '+U_GP,'e: retomar reforma laboral 2017, bajar impuestos a combustibles, reforma previsional, Estado menor; no recorta Bolsa Familia. s: reducir mayoría de edad penal, penas más duras. CHES (Jair) como proxy.'),
('BR-2026','lula','BR','PT',-1,-1,FC,'Congresso em Foco; Gazeta do Povo; CHES-LA PT','2026-06-16 / 2026-07-29',U_CG+' | '+U_GP,'e: exención IR hasta R$5.000, impuestos a los más ricos, estímulo al consumo. s: énfasis violencia de género; programas sociales eje.'),
('BR-2026','caiado','BR','PSD',1,1,FC,'Congresso em Foco; Tribuna de Jundiaí (40 presídios federais); CHES-LA PSD','2026-06-16',U_CG,'e: Custo Brasil, critica deuda, critica asistencialismo. s: mano dura. s por CHES PSD (+0,8).'),
('BR-2026','renan',None,None,2,1,CC,'Congresso em Foco (e); s sin fuente','2026-06-16',U_CG,'e: recorte grande de impuestos ("tesouraço"), previsión por capitalización, fin de indexación al salario mínimo. s: MBL/libertario, a verificar.'),
('BR-2026','cury',None,None,1,0,FC,'BPMoney; InvestNews; Folha vía BPMoney (autodefinición); Tribuna de Jundiaí','2026-08-26 / 2026-08-27 / 2026-09-02 / 2026-04-06','https://bpmoney.com.br/noticias/quem-e-augusto-cury-candidato-a-presidente-pelo-avante/ | https://bpmoney.com.br/brasil/augusto-cury-e-de-esquerda-ou-direita-entenda-posicao-politica-do-candidato/ | https://investnews.com.br/economia/quem-e-augusto-cury/amp/','e: "mente de direita y corazón social" (Valor) / "mente capitalista" (BBC, Folha); Estado más chico, déficit cercano a cero, clubes de emprendedurismo, elogió a Paulo Guedes. s: sin posición hallada sobre aborto, armas ni drogas; programa Mulheres Vivas, cupo mínimo de mujeres en el STF, rehabilitación carcelaria, criticó "bandido bom é bandido morto"; evitó posición sobre condenados del 8-ene. Se codifica 0 con baja confianza.'),
('CL-2025','jara',  'CL','PC',-1,-1,FC,'BBC Mundo (El Observador); Tiempo de San Juan; CHES-LA PC (contraste)','2025-12-12 / 2025-11-16',U_BBC+' | '+U_TS,'e: ingreso vital ~US$800, subsidios, 40 horas, aumento salario mínimo, reforma de pensiones. s: regularización acotada, control de armas. Se aparta del PC (CHES: e -1,52 / s -0,28) por perfil moderado: discrepancia marcada.'),
('CL-2025','kast',None,None,2,2,FC,'BBC Mundo (El Observador); Tiempo de San Juan','2025-12-12 / 2025-11-16',U_BBC+' | '+U_TS,'e: recorte gasto US$6.000M en 18 meses, impuesto corporativo 27%->23%. s: deportaciones masivas, migración irregular como delito; valores conservadores (evitó aborto/matrimonio en esta campaña).'),
('CL-2025','kaiser',None,None,2,2,FC,'Tiempo de San Juan','2025-11-16',U_TS,'e: reducir drásticamente el Estado, estilo Milei, armas. s: contra aborto e "ideología de género", defiende a Pinochet.'),
('CL-2025','matthei','CL','UDI',1,1,FC,'Tiempo de San Juan; CHES-LA UDI (contraste)','2025-11-16',U_TS,'e: estabilidad económica, incentivos al empleo. s: seguridad, orden, migración. CHES UDI: e +1,56 / s +1,64; se la considera más moderada que su partido: discrepancia marcada.'),
('CL-2025','parisi',None,None,0,None,CC,'Tiempo de San Juan (e)','2025-11-16',U_TS,'e: apoyos monetarios directos y reformas tributarias para la clase media, heterodoxo. s: sin evidencia (NA).'),
('PE-2021','castillo','PE','PL',None,None,CP,U_CH,'2020-2021','','Perú Libre'),
('PE-2021','fujimori','PE','FP',None,None,CP,U_CH,'2020-2021','','Fuerza Popular'),
('PE-2021','lopez aliaga','PE','RP',None,None,CP,U_CH,'2020-2021','','Renovación Popular'),
('PE-2021','soto','PE','AvP',None,None,CP,U_CH,'2020-2021','','Avanza País'),
('PE-2021','lescano','PE','AP',None,None,CP,U_CH,'2020-2021','','Acción Popular'),
('PE-2021','mendoza','PE','JP',None,None,CP,U_CH,'2020-2021','','Juntos por el Perú'),
('PE-2021','acuna','PE','APP',None,None,CP,U_CH,'2020-2021','','Alianza para el Progreso'),
('PE-2021','urresti','PE','PP',None,None,CP,U_CH,'2020-2021','','Podemos Perú (proxy partido)'),
('PE-2021','guzman','PE','PURP',None,None,CP,U_CH,'2020-2021','','Partido Morado'),
('PE-2026','fujimori','PE','FP',1,2,FC,'Infobae (e); CHES-LA FP 2021 (s, proxy)','2026-04-06',U_IN+' | '+U_BP,'e: déficit 1% PBI, regla fiscal, inversión privada/APP. s: proxy CHES FP (+1,6).'),
('PE-2026','sanchez',None,None,-2,-1,FC,'Infobae; Gestión; BioBioChile','2026-04-06 / 2026-06-03 / 2026-06-05',U_IN+' | '+U_GE+' | '+U_BB,'e: plan de 1ª vuelta (nacionalización parcial de recursos, fin del extractivismo, control de precios, presión tributaria 25% PBI). En 2ª vuelta moderó (autonomía BCR, reglas fiscales): se codifica el plan de 1ª vuelta. s: aborto por violación y terapéutico, unión civil, equidad de género, católico "provida".'),
('PE-2026','lopez aliaga','PE','RP',2,2,FC,'Infobae; Bloomberg Línea; CHES-LA RP 2021','2026-04-06 / 2026-04-08',U_IN+' | '+U_BP,'e: Estado más chico, baja IGV, quita exenciones, megaproyectos. s: expulsar migrantes venezolanos, "ultraconservador".'),
('PE-2026','nieto',None,None,-1,-1,CC,'Infobae (e); s sin fuente','2026-04-06',U_IN,'e: fondo soberano, presión tributaria 18% PBI, impuestos verdes. s por conocimiento general.'),
('PE-2026','belmont',None,None,0,None,FC,'Infobae (e)','2026-04-06',U_IN,'e: economía social de mercado, industrialización, participación estatal en sectores estratégicos. s: NA.'),
('PE-2026','alvarez',None,None,1,1,CC,'Infobae; Bloomberg Línea (e); s sin fuente','2026-04-06 / 2026-04-08',U_IN+' | '+U_BP,'e: déficit 1%, deuda <30% PBI, reforma sin subir tasas, quita exenciones. s: outsider de seguridad.'),
('PE-2026','lopez chau',None,None,-1,None,FC,'Infobae (e)','2026-04-06',U_IN,'e: política fiscal progresiva, fondo soberano, déficit <1%; ubicado a la izquierda (Caretas). s: NA.'),
('PE-2026','perez tello',None,None,0,None,FC,'Infobae (e)','2026-04-06',U_IN,'e: inversión privada, reforma tributaria progresiva, Estado digital. s: NA.'),
('CO-2022','petro','CO','DEC',-1,-1,CC,'CHES-LA Lista de la Decencia (contraste) y conocimiento general','2020',U_CH,'e: no nuevas exploraciones petroleras, reforma agraria y pensional, pero discurso de "capitalismo democrático". Se alinea con CHES DEC (e -0,76 / s -1,08) y con Petro 2018. Cepeda 2026 queda en -2 por la fuente citada (profundizar el rol del Estado).'),
('CO-2022','hernandez',None,None,1,None,CC,'conocimiento general','','','empresario outsider anticorrupción; s: NA.'),
('CO-2022','gutierrez','CO','RCP',1,1,CP,U_CH,'2020','','Equipo por Colombia; proxy Cambio Radical (CHES e +1,04 / s +1,0), coalición de centroderecha.'),
('CO-2022','fajardo',None,None,0,-1,CC,'conocimiento general; Manifesto 2018 (CC) como contraste','','','centro; Manifesto 2018: rile -20,8, markeco 0,6, planeco 0,6.'),
('CO-2026','espriella',None,None,2,2,FC,'Bloomberg Línea; Semana; Publimetro (plan filtrado)','2026-06-19 / 2026-06-21 / 2026-08-27',U_BL+' | '+U_SM+' | '+U_PM,'e: Estado más chico, menos impuestos, fracking y petróleo, ajuste fiscal 70 billones. s: porte de armas, revertir aborto, fin de la JEP, no adopción homoparental, contra "ideología de género" (esto último según plan filtrado, no oficial).'),
('CO-2026','cepeda',None,None,-2,-1,FC,'Bloomberg Línea (e); s por conocimiento general','2026-06-19',U_BL,'e: más intervención del Estado, profundizar reformas de Petro, más participación estatal en sectores estratégicos, impuestos progresivos, contra el fracking. s sin fuente citada.'),
('CO-2026','valencia','CO','CD',2,2,FC,'Bloomberg Línea; CHES-LA CD','2026-05-26',U_PV,'e: reducir Estado, fusionar ministerios, bajar impuestos a empresas, fracking. s: más Fuerzas Armadas, fumigación aérea, mano dura contra grupos armados, crítica a la JEP.'),
('CO-2026','fajardo',None,None,0,-1,CC,'conocimiento general','','','centro; mismo perfil que 2018 (Alianza Verde, V-Party s -1,8).'),
('UY-2019','martinez','UY','FA',None,None,CP,U_CH,'2020','','Frente Amplio'),
('UY-2019','lacalle','UY','LL',None,None,CP,U_CH+' (fila presidente en ejercicio: Lacalle Pou)','2020','','CHES lo incluye como presidente en 2020'),
('UY-2019','talvi','UY','PC',None,None,CP,U_CH,'2020','','Partido Colorado'),
('UY-2019','manini','UY','CA',None,None,CP,U_CH,'2020','','Cabildo Abierto'),
('UY-2024','orsi','UY','FA',None,None,CP,U_CH,'2020','','Frente Amplio'),
('UY-2024','delgado','UY','PN',None,None,CP,U_CH,'2020','','Partido Nacional'),
('UY-2024','ojeda','UY','PC',None,None,CP,U_CH,'2020','','Partido Colorado; Ojeda tiene perfil de mano dura, sociocultural probablemente > partido: a verificar'),
('UY-2024','manini','UY','CA',None,None,CP,U_CH,'2020','','Cabildo Abierto'),
]
rows=[]
for el,k,pais,pa,e,s,niv,fu,fe,url,nota in R:
    pais_=el[:2]
    g=cand[cand.id_eleccion.str.startswith(el)&(cand.vuelta==1)]
    hit=g[g.candidato_o_formula.map(lambda x:k in nrm(x))]
    sh=hit.share.sum() if len(hit) else None
    nm=hit.candidato_o_formula.iloc[0] if len(hit) else k
    ec=sc=None
    if pa is not None and (pais_,pa) in ch.index:
        r=ch.loc[(pais_,pa)]; ec=cont(r.lrecon); sc=cont(r.galtan)
    if niv==CP:
        e=rd(ec); s=rd(sc)
    rows.append(dict(id_eleccion=el+'-PRES-1',pais=pais_,anio=int(el[3:]),candidato=nm,share_pct=None if sh is None else round(sh,2),
        eje_economico=e,eje_sociocultural=s,ches_econ_cont=ec,ches_socio_cont=sc,nivel_evidencia=niv,fuente=fu,fecha_fuente=fe,url=url,notas=nota,codificador='claude_v1'))
d=pd.DataFrame(rows); d.to_csv('final/ideologia_recientes.csv',index=False)
pd.set_option('display.width',220)
print(d[['id_eleccion','candidato','share_pct','eje_economico','eje_sociocultural','ches_econ_cont','ches_socio_cont','nivel_evidencia']].to_string(index=False))
for e,g in d.groupby('id_eleccion'): print(e,'econ%',round(g.share_pct[g.eje_economico.notna()].sum(),1),'socio%',round(g.share_pct[g.eje_sociocultural.notna()].sum(),1))
