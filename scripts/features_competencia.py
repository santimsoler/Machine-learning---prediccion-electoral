import pandas as pd,numpy as np,re,unicodedata
F='final/'
c=pd.read_csv(F+'candidatos_unificado.csv'); c=c[c.vuelta==1].copy()
def norm(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().upper()
    return re.sub(r'\s+',' ',re.sub(r'[^A-Z0-9 ]',' ',s)).strip()
c['cand']=c.candidato_o_formula.where(c.candidato_o_formula.notna(),c.partido_o_coalicion).map(norm)
c['cand']=c.cand.str.split(' ').str[:2].str.join(' ')  # apellido(s) principales para colapsar listas provinciales
c['nom']=(c.candidato_o_formula.fillna('').astype(str)+' | '+c.partido_o_coalicion.fillna('').astype(str)).map(norm)
# ---------- familia partidaria (mapeo explícito por país; criterio de identidad: nombre del candidato/coalición) ----------
FAM={
'AR':[('PJ',r'JUSTICIALISTA|FRENTE PARA LA VICTORIA|FRENTE DE TODOS|UNION POR LA PATRIA|LEALTAD|MENEM|LUDER|KIRCHNER|SCIOLI|FERNANDEZ|MASSA|DUHALDE'),('UCR',r'UNION CIVICA RADICAL|ALFONSIN|ANGELOZ|MASSACCESI|DE LA RUA|ALIANZA PARA EL TRABAJO'),('PRO_UCR',r'CAMBIEMOS|JUNTOS POR EL CAMBIO|MACRI|BULLRICH'),('LLA',r'LIBERTAD AVANZA|MILEI'),('FREPASO',r'PAIS SOLIDARIO|BORDON')],
'BR':[('PT',r'\bPT\b|LULA|DILMA|HADDAD'),('PSDB',r'PSDB|SERRA|ALCKMIN|AECIO'),('BOLSONARISMO',r'\bPSL\b|\bPL\b|BOLSONARO'),('MDB',r'MEIRELLES|\bMDB\b|TEBET')],
'CL':[('CENTROIZQ',r'AYLWIN|FREI|LAGOS|BACHELET|GUILLIER|JARA|BORIC|ENRIQUEZ'),('DERECHA',r'BUCHI|ALESSANDRI|LAVIN|PINERA|MATTHEI|SICHEL|KAST|ERRAZURIZ')],
'CO':[('LIBERAL',r'SERPA|LIBERAL|GAVIRIA'),('CONSERVADOR',r'PASTRANA|CONSERVADOR|RAMIREZ'),('URIBISMO',r'URIBE VELEZ|ZULUAGA|DUQUE|CENTRO DEMOCRATICO|PRIMERO COLOMBIA|DE LA ESPRIELLA|SANTOS'),('IZQUIERDA',r'PETRO|CEPEDA|POLO|PACTO|CLARA LOPEZ')],
'PE':[('APRA',r'GARCIA PEREZ|APRISTA'),('FUJIMORISMO',r'FUJIMORI|FUERZA'),('OTROS',r'.')],
'UY':[('FA',r'FRENTE AMPLIO|VAZQUEZ|MARTINEZ|ORSI'),('PN',r'PARTIDO NACIONAL|LACALLE|DELGADO'),('PC',r'PARTIDO COLORADO|BORDABERRY|TALVI|OJEDA')],
}
def fam(pais,nom):
    for k,rx in FAM.get(pais,[]):
        if re.search(rx,nom): return k
    return 'OTROS'
# la familia se define sobre el nombre del candidato primero, luego la coalición
def fam2(r):
    n=norm(r.candidato_o_formula) if pd.notna(r.candidato_o_formula) else ''
    f=fam(r.pais,n) if n else 'OTROS'
    return f if f!='OTROS' else fam(r.pais,r.nom)
c['familia']=c.apply(fam2,axis=1)
# colapsar por candidato (sumar listas provinciales)
g=c.groupby(['id_eleccion','pais','anio','cand']).agg(share=('share_nacional_pct','sum'),of=('es_oficialismo','max'),familia=('familia',lambda s:s.value_counts().index[0]),ideo=('e_cont','mean')).reset_index()
g.loc[g.share>100,'share']=np.nan
# ---------- por elección ----------
rows=[]
for eid,d in g.groupby('id_eleccion'):
    d=d[d.share.notna()]; s=d.share/ d.share.sum()  # re-normalizar a 1
    enc=1/(s**2).sum(); n1=(d.share>=1).sum(); n5=(d.share>=5).sum()
    of=d[d.of==1]
    ideo_of=of.ideo.mean() if len(of) else np.nan
    oth=d[(d.of!=1)&(d.share>=5)]
    cerc=oth[(oth.ideo.sub(ideo_of).abs()<=1.0)] if pd.notna(ideo_of) else oth.iloc[0:0]
    top2=d.sort_values('share',ascending=False).head(2).familia.tolist()
    rows.append(dict(id_eleccion=eid,enc=enc,n_cand_1pct=n1,n_cand_5pct=n5,hhi_top1=d.share.max()/d.share.sum()*100,
      n_fuertes_cercanos=len(cerc) if pd.notna(ideo_of) else np.nan,
      share_fuertes_cercanos=cerc.share.sum() if pd.notna(ideo_of) else np.nan,
      cobertura_ideologia=oth.ideo.notna().mean() if len(oth) else np.nan,
      familia_of=of.familia.iloc[0] if len(of) else None, top2_familias='|'.join(top2)))
E=pd.DataFrame(rows)
E=E.merge(g[['id_eleccion','pais','anio']].drop_duplicates(),on='id_eleccion')
# ---------- partido principal ----------
E=E.sort_values(['pais','anio'])
prev=[];cnt=[]
for p,d in E.groupby('pais'):
    hist=[]
    for i,r in d.iterrows():
        n=sum(1 for h in hist if r.familia_of in h) if isinstance(r.familia_of,str) and r.familia_of!='OTROS' else np.nan
        prev.append((i,(int(r.familia_of in hist[-1]) if hist and isinstance(r.familia_of,str) else np.nan)))
        cnt.append((i,n if hist else np.nan)); hist.append(r.top2_familias.split('|'))
E['of_top2_eleccion_previa']=pd.Series(dict(prev)); E['of_n_top2_previas']=pd.Series(dict(cnt))
TRAD={'AR':['PJ','UCR'],'CO':['LIBERAL','CONSERVADOR'],'UY':['PN','PC'],'CL':['CENTROIZQ','DERECHA'],'BR':['PT','PSDB','MDB']}
E['of_tradicional']=E.apply(lambda r:(int(r.familia_of in TRAD.get(r.pais,[])) if isinstance(r.familia_of,str) else np.nan),axis=1)
pd.DataFrame([(p,f) for p,l in TRAD.items() for f in l],columns=['pais','familia_tradicional']).to_csv(F+'partidos_tradicionales.csv',index=False)
E['pre2000']=(E.anio<2000).astype(int)
E['of_tradicional_x_pre2000']=E.of_tradicional*E.pre2000
E['anio_c']=(E.anio-2000)/10
print(E[['id_eleccion','familia_of','of_tradicional','of_n_top2_previas','of_top2_eleccion_previa','enc','n_cand_5pct','n_fuertes_cercanos','share_fuertes_cercanos','cobertura_ideologia']].round(1).to_string())
E.to_csv(F+'competencia_por_eleccion.csv',index=False)
E5=E
E.to_pickle('/tmp/E.pkl')
