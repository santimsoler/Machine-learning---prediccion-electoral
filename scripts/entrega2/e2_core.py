"""Segunda entrega - núcleo de validación.
Panel crudo (con NaN) -> imputación DENTRO del pipeline; ventana expansiva por año; hiperparámetros con validación interna temporal.
"""
import numpy as np, pandas as pd, warnings
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV
warnings.filterwarnings('ignore')

CORTE_TEST = pd.Timestamp('2022-01-01')   # elecciones desde esta fecha = conjunto de prueba (se toca una sola vez)
PRIMER_ANIO_VAL = 2010                     # primer año de la validación en ventana expansiva

BASE = ['oficialismo_dudoso','oficialismo_va_por_reeleccion','aprobacion_oficial_completa',
        'bm_inflacion_ipc_tm1','us_current_account_tm1','vuelta','fp_prev1','fp_nunca_top2']
TEXTO = ['malestar','cont_cambio','fragm_txt','izq_der']
AMPLIO = BASE + ['ideologia_of','percep_econ_lb','bm_crecimiento_pib_tm1','bm_desempleo_oit_tm1','us_fiscal_primario_tm1',
        'us_ner_var_tm1','us_cuenta_corriente_wb_tm1','of_tradicional','anio_c','pobnac_685_tm1','pobnac_365_tm1',
        'd_pobnac_685_mandato','d_pobnac_365_mandato','anios_mandato','of_top2_eleccion_previa','of_n_top2_previas']

def slog(x): return np.sign(x)*np.log1p(np.abs(x))

def cargar():
    e = pd.read_csv('final/panel_modelo_eleccion.csv'); fp = pd.read_csv('final/fuerza_partido_previa.csv')
    key = e.id_eleccion.str[:-1]+'1'                      # la 2a vuelta hereda la fuerza previa de su 1a vuelta
    for c in ['fp_prev1','fp_nunca_top2']: e[c] = key.map(dict(zip(fp.id_eleccion, fp[c]))).fillna(0).values
    e['fecha'] = pd.to_datetime(e.fecha)
    for c in ['bm_inflacion_ipc_tm1','us_ner_var_tm1']: e[c] = slog(e[c])
    # resultado de la 1a vuelta (conocido antes de la 2a): NaN en las primeras vueltas, se imputa dentro del pipeline
    r1 = e[e.vuelta==1].set_index('id_eleccion').y_share_nacional
    e['r1_share'] = np.where(e.vuelta==2, key.map(r1), np.nan)
    t = pd.read_csv('final/texto_conteos.csv'); ok = t.n_prev >= 150; k = 1000/t.n_prev.where(ok)
    t['malestar'] = (t.crisis+t.corrup+t.protesta+t.insegur)*k; t['cont_cambio'] = (t.continu-t.cambio)*k
    t['fragm_txt'] = t.fragm*k; t['izq_der'] = (t.izq-t.der)*k; t['leak_txt'] = t.FUGA*k
    for c in ['malestar','cont_cambio','fragm_txt','izq_der','leak_txt']: e[c] = key.map(dict(zip(t.id_eleccion, t[c])))   # la 2a vuelta hereda el texto de su 1a
    e = e.sort_values(['fecha','id_eleccion']).reset_index(drop=True)
    e['colapso'] = (e.y_share_nacional < 10).astype(int)
    return e

def bloques(fechas, idx, desde_anio):
    """Bloques de validación = un año calendario; entrena solo con elecciones estrictamente anteriores al bloque."""
    f = fechas.iloc[idx]; out = []
    for a in sorted(f.dt.year.unique()):
        if a < desde_anio: continue
        va = idx[(f.dt.year == a).values]; ini = fechas.iloc[va].min()
        tr = idx[(f < ini).values]
        if len(tr) >= 15: out.append((tr, va, a))
    return out

def cv_interno(fechas, tr, k=5):
    """Validación interna dentro de la partición: ventana expansiva sobre los últimos k años del entrenamiento."""
    res = bloques(fechas, tr, int(fechas.iloc[tr].dt.year.min()))
    res = res[-k:]
    return [(np.where(np.isin(tr, a))[0], np.where(np.isin(tr, b))[0]) for a, b, _ in res]

def pipe(modelo, cols):
    imp = SimpleImputer(strategy='median')
    if modelo in ('Ridge','ElasticNet'):
        est = Ridge() if modelo=='Ridge' else ElasticNet(max_iter=20000)
        return Pipeline([('imp',imp),('sc',StandardScaler()),('m',est)])
    est = (RandomForestRegressor(n_estimators=300, random_state=0, n_jobs=1) if modelo=='RandomForest'
           else GradientBoostingRegressor(subsample=0.7, random_state=0))
    return Pipeline([('imp',imp),('m',est)])

GRIDS = {
 'Ridge': {'m__alpha': list(np.logspace(-2,3,12))},
 'ElasticNet': {'m__alpha': [0.01,0.05,0.2,0.5,1,3], 'm__l1_ratio':[0.3,0.7]},
 'RandomForest': {'m__max_depth':[2,3,5], 'm__min_samples_leaf':[3,6], 'm__max_features':[0.5,1.0]},
 'GradBoost': {'m__learning_rate':[0.02,0.05], 'm__max_depth':[1,2,3], 'm__n_estimators':[100,300]},
}

def ajustar_predecir(df, modelo, cols, tr, te, fechas):
    """Ajusta con hiperparámetros elegidos por validación interna (solo con tr) y predice te."""
    X = df[cols]; y = df.y_share_nacional.values
    if modelo == 'Benchmark':   # promedio histórico por vuelta, solo con entrenamiento
        m = {v: y[tr][df.vuelta.values[tr]==v].mean() for v in (1,2)}
        return np.array([m[v] for v in df.vuelta.values[te]]), {}
    gs = GridSearchCV(pipe(modelo, cols), GRIDS[modelo], cv=cv_interno(fechas, tr), scoring='neg_mean_absolute_error', n_jobs=2)
    gs.fit(X.iloc[tr], y[tr])
    return gs.predict(X.iloc[te]), gs.best_params_

def validacion_externa(df, modelo, cols, idx_train):
    """Ventana expansiva sobre el entrenamiento. Devuelve predicciones por elección y MAE por bloque."""
    fechas = df.fecha; filas = []; hp = []
    for tr, va, a in bloques(fechas, idx_train, PRIMER_ANIO_VAL):
        p, b = ajustar_predecir(df, modelo, cols, tr, va, fechas); hp.append(b)
        for i, pi in zip(va, p): filas.append((df.id_eleccion[i], a, df.y_share_nacional[i], pi))
    R = pd.DataFrame(filas, columns=['id_eleccion','bloque','y','pred']); R['err'] = (R.y-R.pred).abs()
    mae_b = R.groupby('bloque').err.mean()
    return R, dict(MAE_pool=R.err.mean(), RMSE=np.sqrt(((R.y-R.pred)**2).mean()),
                   R2=1-((R.y-R.pred)**2).sum()/((R.y-R.y.mean())**2).sum(),
                   MAE_fold_media=mae_b.mean(), MAE_fold_desvio=mae_b.std(), n=len(R), folds=len(mae_b)), hp
