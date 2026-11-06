import csv,unicodedata,sys
from collections import defaultdict
O='out4/'
def nz(s): return ''.join(c for c in unicodedata.normalize('NFD',s.upper()) if unicodedata.category(c)!='Mn')
# (pais,anio): presidente en ejercicio, partido oficialismo, palabras clave opcion oficialista, reeleccion, estado
INC={
('AR',1983):('Bignone (régimen militar)','—',[],0,'sin_gobierno_previo'),
('AR',1989):('Alfonsín','UCR',['ANGELOZ'],0,'analista_pendiente'),
('AR',1995):('Menem','PJ',['MENEM'],1,'analista_pendiente'),
('AR',1999):('Menem','PJ',['DUHALDE','JUSTICIALISTA'],0,'analista_pendiente'),
('AR',2003):('Duhalde (interino)','PJ',['KIRCHNER'],0,'verificado_apoyo_explicito_Duhalde_Pagina12_2003-01-15'),
('AR',2007):('N. Kirchner','PJ-FPV',['FERNANDEZ DE KIRCHNER','VICTORIA'],0,'analista_pendiente'),
('AR',2011):('C. Fernández de Kirchner','FPV',['VICTORIA'],1,'analista_pendiente'),
('AR',2015):('C. Fernández de Kirchner','FPV',['VICTORIA'],0,'analista_pendiente'),
('AR',2019):('Macri','Cambiemos/JxC',['JUNTOS POR EL CAMBIO'],1,'analista_pendiente'),
('AR',2023):('A. Fernández','Frente de Todos/UxP',['UNION POR LA PATRIA'],0,'analista_pendiente'),
('CO',1998):('Samper','Liberal',['SERPA'],0,'analista_pendiente'),
('CO',2002):('Pastrana','Conservador',['ALVARO URIBE'],0,'verificado_apoyo_oficial_Partido_Conservador_Uribe_independiente_Wikipedia'),
('CO',2006):('Uribe','Primero Colombia',['ALVARO URIBE'],1,'analista_pendiente'),
('CO',2010):('Uribe','Partido de la U',['SANTOS'],0,'analista_pendiente'),
('CO',2014):('Santos','Unidad Nacional/U',['SANTOS'],1,'analista_pendiente'),
('CO',2018):('Santos','Unidad Nacional',[],0,'sin_apoyo_explicito_Santos_no_endoso_formalmente_Semana_2018-04-07'),
('CO',2022):('Duque','Centro Democrático',[],0,'sin_apoyo_explicito_CD_sin_candidato_ni_endoso_Semana_2022-04-08'),
('CO',2026):('Petro','Pacto Histórico',['CEPEDA'],0,'analista_pendiente'),
('BR',2002):('Cardoso','PSDB',['SERRA'],0,'analista_pendiente'),
('BR',2006):('Lula','PT',['LULA'],1,'analista_pendiente'),
('BR',2010):('Lula','PT',['DILMA'],0,'analista_pendiente'),
('BR',2014):('Rousseff','PT',['DILMA'],1,'analista_pendiente'),
('BR',2018):('Temer','MDB',['MEIRELLES'],0,'analista_pendiente'),
('BR',2022):('Bolsonaro','PL',['BOLSONARO'],1,'analista_pendiente'),
('BR',2026):('Lula','PT',['LULA'],1,'analista_pendiente'),
('CL',1989):('Pinochet (régimen)','Régimen',['BUCHI'],0,'dudoso_regimen_militar'),
('CL',1993):('Aylwin','Concertación',['FREI'],0,'analista_pendiente'),
('CL',1999):('Frei Ruiz-Tagle','Concertación',['LAGOS'],0,'analista_pendiente'),
('CL',2005):('Lagos','Concertación',['BACHELET'],0,'analista_pendiente'),
('CL',2009):('Bachelet','Concertación',['FREI'],0,'analista_pendiente'),
('CL',2013):('Piñera','Alianza',['MATTHEI'],0,'analista_pendiente'),
('CL',2017):('Bachelet','Nueva Mayoría',['GUILLIER'],0,'analista_pendiente'),
('CL',2021):('Piñera','Chile Vamos',['SICHEL'],0,'analista_pendiente'),
('CL',2025):('Boric','Unidad por Chile',['JARA'],0,'analista_pendiente'),
('PE',2006):('Toledo','Perú Posible',[],0,'sin_candidato_oficialista_Belaunde_retirado_2006-01-31'),
('PE',2011):('García','APRA',[],0,'sin_candidato_oficialista_APRA_retiro_Araoz'),
('PE',2016):('Humala','Partido Nacionalista',[],0,'sin_candidato_oficialista_lista_nacionalista_ausente_en_datos_a_verificar_von_Hesse'),
('PE',2021):('Sagasti (interino)','Partido Morado',['PARTIDO MORADO'],0,'dudoso_Guzman_se_desmarca_del_gobierno'),
('UY',2014):('Mujica','Frente Amplio',['FRENTE AMPLIO','VAZQUEZ'],0,'analista_pendiente'),
('UY',2019):('Vázquez','Frente Amplio',['FRENTE AMPLIO','MARTINEZ'],0,'analista_pendiente'),
('UY',2024):('Lacalle Pou','Partido Nacional',['PARTIDO NACIONAL','DELGADO'],0,'analista_pendiente'),
}
BRD={2002:('2002-10-06','2002-10-27'),2006:('2006-10-01','2006-10-29'),2010:('2010-10-03','2010-10-31'),2014:('2014-10-05','2014-10-26'),2018:('2018-10-07','2018-10-28'),2022:('2022-10-02','2022-10-30'),2026:('2026-10-04','2026-10-25')}
SRC=[('CO','base_presidencial_colombia_1998_2026.csv','nombre_depto','nombre_opcion','votos','votos_validos_muni','votos_blancos','votos_nulos'),
('BR','br_presidencial_municipios_2002_2026.csv','uf','nm_candidato','votos','votos_validos_muni','votos_brancos','votos_nulos'),
('CL','cl_presidencial_comunas_1989_2025.csv','region','candidato','votos','votos_validos_comuna','votos_blancos','votos_nulos'),
('AR','ar_presidencial_provincias_1983_2023.csv','distrito_nombre','agrupacion_nombre','votos','votos_positivos_distrito','votos_blancos','votos_nulos'),
('PE','pe_presidencial_distritos_2006_2021.csv','departamento','candidato','votos','votos_validos_distrito','votos_blancos','votos_nulos'),
('UY','/tmp/work/out/uy_presidencial_departamentos_2014_2024.csv','departamento','candidato','votos','votos_validos_depto','votos_blancos','votos_anulados')]
res=[];el={}
for pais,f,reg,cand,v,vv,bl,nu in SRC:
    path=f if f.startswith('/') else O+f
    # unidades: distrito-nivel -> sumar por region; validos/blancos/nulos una vez por unidad base
    agg=defaultdict(int); tot=defaultdict(lambda:[0,0,0]); seen=set(); fam={}
    for r in csv.DictReader(open(path,encoding='utf-8')):
        eid=r['id_eleccion']
        if pais=='CO' and not eid.startswith('CO'): eid='CO-'+eid
        if pais=='BR': pass
        anio=int(r['anio']); vu=r['vuelta'] if r.get('vuelta') else eid[-1]
        c=r[cand]
        if pais=='AR': c=r['agrupacion_nombre']+' | '+r['formula']
        if pais=='UY': c=r['lema_o_candidato']+' | '+r['candidato']
        if pais=='PE': c=r['candidato']+' | '+r['partido']
        agg[(eid,r[reg],c)]+=int(float(r[v] or 0))
        unit=(eid,r.get('codigo_divipol') or r.get('cd_municipio_tse') or r.get('ubigeo') or r.get('comuna') or r.get('distrito_id') or r.get('departamento') or '', r[reg])
        if unit not in seen:
            seen.add(unit); t=tot[(eid,r[reg])]
            t[0]+=int(float(r[vv] or 0)); t[1]+=int(float(r[bl] or 0)); t[2]+=int(float(r[nu] or 0))
        fam[eid]=(anio,vu,r.get('fecha',''))
    for eid,(anio,vu,fe) in fam.items():
        if pais=='BR': fe=BRD[anio][int(vu)-1]
        el[eid]=(pais,anio,vu,fe)
    for (eid,rg,c),vt in agg.items():
        anio=fam[eid][0]; kw=INC[(pais,anio)][2]
        ofi=int(any(k in nz(c) for k in kw)) if kw else (0 if INC[(pais,anio)][4].startswith('sin_') else '')
        t=tot[(eid,rg)]
        res.append([eid,pais,anio,rg,c,vt,t[0],t[1],t[2],ofi])
with open('final/resultados_region.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['id_eleccion','pais','anio','region_nivel1','opcion','votos','votos_validos_region','votos_blancos_region','votos_nulos_region','es_oficialismo'])
    w.writerows(sorted(res))
with open('final/elecciones.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['id_eleccion','pais','anio','vuelta','fecha','presidente_en_ejercicio','partido_oficialismo','palabras_clave_opcion_oficialista','oficialismo_va_por_reeleccion','estado_codificacion'])
    for eid,(p,a,vu,fe) in sorted(el.items()):
        i=INC[(p,a)]; w.writerow([eid,p,a,vu,fe,i[0],i[1],';'.join(i[2]),i[3],i[4]])
print(len(res),len(el))
