import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
e=pd.read_csv('final/panel_modelo_eleccion.csv'); r=pd.read_csv('final/panel_modelo_region.csv'); O='entrega2/'
def fmt(x): return ('+' if x>0 else '−')+('%.2f'%abs(x)).replace('.',',')
# fig 1
f,ax=plt.subplots(1,2,figsize=(11,3.9))
a=e[e.vuelta==1].y_share_nacional; b=e[e.vuelta==2].y_share_nacional; bins=np.arange(0,75,5)
ax[0].hist([a,b],bins=bins,stacked=True,color=['#4a78a8','#f58518'],label=[f'Primera vuelta (n={len(a)})',f'Segunda vuelta (n={len(b)})'])
ax[0].set_title('Variable a predecir (nacional)'); ax[0].set_xlabel('Voto nacional del oficialismo (%)'); ax[0].set_ylabel('Elecciones-vuelta'); ax[0].legend(frameon=False,fontsize=9)
y=r.y_share_oficialismo.dropna(); ax[1].hist(y,bins=np.arange(0,105,5),color='#76b5b0'); ax[1].set_title(f'Versión regional (n={len(y)})'); ax[1].set_xlabel('Voto del oficialismo en la región (%)'); ax[1].set_ylabel('Regiones-elección')
plt.tight_layout(); plt.savefig(O+'fig_dist.png',dpi=160); plt.close()
# fig 2
cols={'AR':'#4e79a7','BO':'#9c755f','BR':'#59a14f','CL':'#e15759','CO':'#f28e2b','CR':'#b07aa1','EC':'#bab0ac','MX':'#17becf','PA':'#d4a017','PE':'#a0509a','PY':'#edc948','UY':'#76b7b2'}
cols['PE']='#8c564b'; cols['MX']='#1b9e77'; cols['PA']='#7f7f7f'; cols['PE']='#e377c2'
f,ax=plt.subplots(1,2,figsize=(11,4.3))
for k,(x,xl) in enumerate([('aprobacion_oficial_completa','Aprobación del presidente antes de la elección (%)'),('d_pobnac_685_mandato','Cambio de la pobreza durante el mandato (p.p.)')]):
    d=e[[x,'y_share_nacional','pais']].dropna()
    for p,g in d.groupby('pais'): ax[k].scatter(g[x],g.y_share_nacional,s=18,color=cols[p],label=p,edgecolor='white',linewidth=.4)
    m,c0=np.polyfit(d[x],d.y_share_nacional,1); xs=np.array([d[x].min(),d[x].max()]); ax[k].plot(xs,m*xs+c0,color='k',lw=1.6)
    ax[k].set_title(f'r = {fmt(d[[x,"y_share_nacional"]].corr().iloc[0,1])}  (n={len(d)})'); ax[k].set_xlabel(xl); ax[k].set_ylabel('Voto nacional del oficialismo (%)')
ax[0].legend(ncol=4,frameon=False,fontsize=8,loc='lower right',handletextpad=.2,columnspacing=.8)
plt.tight_layout(); plt.savefig(O+'fig_attr.png',dpi=160); plt.close()
