import pandas as pd, numpy as np, glob, unicodedata, re
def nz(s):
    s=str(s).replace('Ã‘','N').replace('Ã±','n')
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().upper().strip()
    return re.sub(r'\s+',' ',s)
f=glob.glob('/mnt/user-data/attachments/*/*Subnational_HDI_Data*')[0]
d=pd.read_csv(f)
iso={'AR':'ARG','BR':'BRA','CL':'CHL','CO':'COL','PE':'PER','UY':'URY'}
d=d[d.isocode3.isin(iso.values())]
nat=d[d.level=='National'][['isocode3','year','shdi']].rename(columns={'shdi':'shdi_nac'})
sub=d[d.level=='Subnat'].copy()
cols=['isocode3','year','region','shdi','incindex','edindex','healthindex','lgnic','msch','esch','lifexp','pop']
sub=sub[cols].merge(nat,on=['isocode3','year'],how='left')
sub['shdi_brecha']=sub.shdi-sub.shdi_nac
sub.rename(columns={'region':'shdi_region'}).to_csv('final/shdi_subnacional_6paises.csv',index=False)

# mapeos panel -> region SHDI
AR={'Gran Buenos Aires':['CABA','CAPITAL FEDERAL','CIUDAD AUTONOMA DE BUENOS AIRES'],
 'Pampeana':['BUENOS AIRES','BS AS','CORDOBA','ENTRE RIOS','LA PAMPA','SANTA FE'],
 'Cuyo':['MENDOZA','SAN JUAN','SAN LUIS'],
 'NOA':['JUJUY','SALTA','TUCUMAN','CATAMARCA','LA RIOJA','SANTIAGO DEL ESTERO','S. DEL ESTERO'],
 'NEA':['CHACO','CORRIENTES','FORMOSA','MISIONES'],
 'Patagonia':['CHUBUT','NEUQUEN','RIO NEGRO','SANTA CRUZ','TIERRA DEL FUEGO','TIERRA DEL FUEGO, ANTARTIDA E ISLAS DEL ATLANTICO SUR']}
BRUF={'AC':'Acre','AL':'Alagoas','AP':'Amapa','AM':'Amazonas','BA':'Bahia','CE':'Ceara','DF':'Distrito Federal','ES':'Espirito Santo','GO':'Goias','MA':'Maranhao','MT':'Mato Grosso','MS':'Mato Grosso do Sul','MG':'Minas Gerais','PA':'Para','PB':'Paraiba','PR':'Parana','PE':'Pernambuco','PI':'Piaui','RJ':'Rio de Janeiro','RN':'Rio Grande do Norte','RS':'Rio Grande do Sul','RO':'Rondonia','RR':'Roraima','SC':'Santa Catarina','SP':'Sao Paulo','SE':'Sergipe','TO':'Tocantins'}
CL=[('ARICA','Tarapaca (incl Arica and Parinacota)'),('TARAPACA','Tarapaca (incl Arica and Parinacota)'),('ANTOFAGASTA','Antofagasta'),('ATACAMA','Atacama'),('COQUIMBO','Coquimbo'),('VALPARAISO','Valparaiso (former Aconcagua)'),('HIGGINS','OHiggins'),('MAULE','Maule'),('NUBLE','Bio Bio'),('BIOBIO','Bio Bio'),('ARAUCANIA','Arbucania'),('LOS RIOS','Los Lagos (incl Los Rios)'),('LOS LAGOS','Los Lagos (incl Los Rios)'),('AISEN','Aisen'),('AYSEN','Aisen'),('MAGALLANES','Magallanes and La Antartica Chilena'),('METROPOLITANA','Region Metropolitana')]
COX={'ANTIOQUIA':'Antioquia (incl Medellin)','ATLANTICO':'Atlantico (incl Barranquilla)','BOGOTA':'Bogota D.C.','BOLIVAR':'Bolivar (Sur and Norte)','VALLE':'Valle (incl Cali)','GUAINIA':'Guainja','VAUPES':'Vaupis','GUAJIRA':'Guajira','LA GUAJIRA':'Guajira','NARINO':'Narino','NORTE DE SAN':'Norte de Santander','STAFE DE BOGOTA D.C.':'Bogota D.C.'}
PE={'Central (Huancavelica, Huanuco, Junin, Pasco)':['HUANCAVELICA','HUANUCO','JUNIN','PASCO'],'East (Madre de Dios, Cusco, Puno, Apurimac)':['MADRE DE DIOS','CUSCO','PUNO','APURIMAC'],'North (Tumbes, Piura, Lambayeque, Cajamarca, La Libertad)':['TUMBES','PIURA','LAMBAYEQUE','CAJAMARCA','LA LIBERTAD'],'North East (Amazonas, Loreto, San Martin, Ucayali)':['AMAZONAS','LORETO','SAN MARTIN','UCAYALI'],'South (Tacna, Moquegua, Arequipa, Ica, Ayacucho)':['TACNA','MOQUEGUA','AREQUIPA','ICA','AYACUCHO'],'West (Ancash, Lima, Callao)':['ANCASH','LIMA','CALLAO']}
UY={'Centro (Durazno and Tacuarembo)':['DURAZNO','TACUAREMBO'],'Centro Sur (Flores, Florida and Lavalleja)':['FLORES','FLORIDA','LAVALLEJA'],'Costa Este (Canelones, Maldonado and Rocha)':['CANELONES','MALDONADO','ROCHA'],'Litoral Norte (Paysandu, Salto and Rio Negro)':['PAYSANDU','SALTO','RIO NEGRO'],'Litoral Sur (Soriano, Colonia and San Jose)':['SORIANO','COLONIA','SAN JOSE'],'Montevideo and Metropolitan area':['MONTEVIDEO'],'Norte (Artigas, Rivera, Cerro Largo and Trienta y Tres)':['ARTIGAS','RIVERA','CERRO LARGO','TREINTA Y TRES']}
def inv(m): return {nz(v):k for k,vs in m.items() for v in vs}
IAR,IPE,IUY=inv(AR),inv(PE),inv(UY)
def mapea(p,r):
    n=nz(r)
    if p=='AR': return IAR.get(n)
    if p=='BR': return BRUF.get(str(r).strip())
    if p=='PE': return IPE.get(n)
    if p=='UY': return IUY.get(n)
    if p=='CL':
        for k,v in CL:
            if k in n: return v
        return None
    if p=='CO':
        if n in [nz(k) for k in COX]: return {nz(k):v for k,v in COX.items()}[n]
        for g in sub[sub.isocode3=='COL'].shdi_region.unique() if 'shdi_region' in sub else sub[sub.isocode3=='COL'].region.unique():
            if nz(g)==n: return g
        return None
r=pd.read_csv('final/panel_modelo_region.csv')
r['shdi_region']=[mapea(p,x) for p,x in zip(r.pais,r.region)]
print(r[r.shdi_region.isna()].groupby(['pais','region']).size())
S=sub.rename(columns={'region':'shdi_region'})
ind=['shdi','incindex','edindex','healthindex','lgnic','msch','esch','lifexp','shdi_brecha']
out=[]
for i,row in r.iterrows():
    if pd.isna(row.shdi_region): out.append([np.nan]*(len(ind)+1)); continue
    y=int(row.anio)-1; c=iso[row.pais]
    g=S[(S.isocode3==c)&(S.shdi_region==row.shdi_region)].set_index('year')
    yy=min(max(y,g.index.min()),g.index.max())
    out.append([g.loc[yy,k] for k in ind]+[y-yy])
o=pd.DataFrame(out,columns=['shdi_'+k if not k.startswith('shdi') else k for k in ind]+['shdi_rezago_extra'],index=r.index)
o=o.rename(columns={'shdi_incindex':'shdi_ingreso','shdi_edindex':'shdi_educ','shdi_healthindex':'shdi_salud','shdi_lgnic':'shdi_lgnic','shdi_msch':'shdi_msch','shdi_esch':'shdi_esch','shdi_lifexp':'shdi_lifexp'})
r=r.drop(columns=[c for c in r.columns if c in o.columns])
r=pd.concat([r,o],axis=1)
r.to_csv('final/panel_modelo_region.csv',index=False)
print(r.groupby('pais')[['shdi','shdi_rezago_extra']].agg(['count','mean']).round(2))
print(r.shape, o.columns.tolist())
