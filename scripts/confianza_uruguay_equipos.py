import pandas as pd
F='final/'
# ultimo valor publicado antes de cada eleccion (UCU/Equipos); var12m solo donde la nota la publica
V={2019:(48.3,None,'2019-08'),2024:(55.8,4.4,'2024-08')}
n=pd.DataFrame([('UY',p,'icc_ucu_equipos',v,'indice','UCU/Equipos (notas El Observador 19/9/2019; Equipos ICC_Agosto_2024.pdf)','valor puntual, no promedio de 3 meses') for y,(v,_,p) in V.items()],
  columns=['pais','periodo','variable','valor','unidad','fuente','notas'])
c=pd.read_csv(F+'confianza_consumidor_mensual.csv'); c=c[~((c.pais=='UY')&(c.variable=='icc_ucu_equipos'))]
pd.concat([c,n]).to_csv(F+'confianza_consumidor_mensual.csv',index=False)
for f in ['panel_modelo_region.csv','panel_modelo_eleccion.csv']:
    p=pd.read_csv(F+f)
    if 'cc_aproximacion' in p: p['cc_aproximacion']=p['cc_aproximacion'].astype(object)
    for y,(v,d,_) in V.items():
        m=(p.pais=='UY')&(p.anio==y)
        p.loc[m,'cc_3m']=v
        if d is not None: p.loc[m,'cc_var12m']=d
        p.loc[m,'cc_aproximacion']='ultimo_ICC_UCU_Equipos_previo_a_eleccion'
    p.to_csv(F+f,index=False)
