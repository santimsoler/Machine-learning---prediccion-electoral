"""Completa variables de mandato de la primera elección de cada país en la muestra, con la elección previa conocida (fuera de muestra).
 - anios_mandato: años desde la elección previa (BR 1998->2002, CO 1994->1998, UY 2009->2014, BO 1989->1993, PY 1989->1993).
 - d_pobnac_*_mandato: pobreza (año previo a la elección) menos pobreza del año previo a la elección anterior, WDI con interpolación (BR, CO, UY; BO/PY/MX/CR/PA no tienen serie WDI antes de 1990).
 - of_top2_eleccion_previa: el oficialismo estuvo entre los dos primeros en la elección previa (BR-2002 PSDB sí; CO-1998 Liberal sí; UY-2014 FA sí; BO-1993 MIR no (3º); PY-1993 Colorado sí; MX-1994 PRI sí; CR-1990 PLN sí).
 - of_n_top2_previas = 0 en las primeras elecciones de la muestra (cuenta solo elecciones dentro de la muestra).
 CL-1989 y PA-1994 (elección previa anulada/dictadura) quedan imputados. Corre después de ampliacion_mx_cr_pa.py y antes de panel_modelo_completo.py. Idempotente."""
import pandas as pd, numpy as np
F='final/'
w=pd.read_csv('wb/wdi_pobreza_gini.csv')
def val(iso,ind,y):
    s=w[(w.pais==iso)&(w.indicador==ind)].set_index('anio').valor.sort_index()
    if y in s.index: return s[y]
    if len(s)==0 or y<s.index.min() or y>s.index.max(): return np.nan
    a=s[s.index<y]; b=s[s.index>y]; ya,yb=a.index.max(),b.index.min(); return a[ya]+(b[yb]-a[ya])*(y-ya)/(yb-ya)
PREV={'BR-2002':('BRA',1998),'CO-1998':('COL',1994),'UY-2014':('URY',2009)}
AM={'BR-2002':4,'CO-1998':4,'UY-2014':5,'BO-1993':4,'PY-1993':4}
T2={'BR-2002':1,'CO-1998':1,'UY-2014':1,'BO-1993':0,'PY-1993':1,'MX-1994':1,'CR-1990':1}
N0=['BR-2002','CO-1998','UY-2014','BO-1993','PY-1993','MX-1994','CR-1990','PA-1994','CL-1989','PE-2021']
for nm in ['panel_modelo_eleccion','panel_modelo_region']:
    P=pd.read_csv(F+nm+'.csv'); k=P.id_eleccion.str[:7]
    for e,v in AM.items():
        if 'anios_mandato' in P: P.loc[k==e,'anios_mandato']=v
    for e,v in T2.items():
        if 'of_top2_eleccion_previa' in P: P.loc[k==e,'of_top2_eleccion_previa']=v
    for e in N0:
        if 'of_n_top2_previas' in P: P.loc[k==e,'of_n_top2_previas']=0
    for e,(iso,yp) in PREV.items():
        for nn,ind in [('685','pob_6.85usd'),('365','pob_3.65usd')]:
            ini=val(iso,ind,yp-1); m=(k==e)
            if f'pobnac_{nn}_tm1' in P and pd.notna(ini):
                P.loc[m,f'd_pobnac_{nn}_mandato']=P.loc[m,f'pobnac_{nn}_tm1']-ini
                if nn=='685': P.loc[m,'pobnac_685_eleccion_prev']=ini
    P.to_csv(F+nm+'.csv',index=False)
