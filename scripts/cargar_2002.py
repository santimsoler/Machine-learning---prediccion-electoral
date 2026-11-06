# Carga elecciones 2002 (presidencia, Senado, Cámara) desde Estadistico2002.mdb (Jet 4).
# Códigos especiales en las tablas votos_*: 996 blanco, 997 nulos, 998 tarjetas no marcadas, 999 total reportado.
# En Senado, la circunscripción 3 (indígena) no tiene fila 999 propia: sus votos están
# incluidos en el total 999 de la circunscripción nacional (0) del mismo municipio.
import os
from collections import defaultdict
from mdbmini import Mdb

def estado(total, dif):
    if total in ('', None, 0):
        return 'sin_control'
    return 'cuadra' if dif == 0 else 'no_cuadra'

def filas_2002(path, COLS_add):
    """Devuelve lista de dicts con columnas del consolidado."""
    db = Mdb(path); cat = db.catalogo()
    out = []
    fuente = 'Estadistico2002.mdb (CD 2002 RNEC)'

    def base(**k):
        d = {c: '' for c in COLS_add}; d.update(pais='CO', anio=2002, fuente=fuente); d.update(k)
        return d

    # --- Presidencia 2002 (1ª y única vuelta). Fecha: no aparece en el CD.
    P = list(db.filas(cat['votos_presidente']))
    mp = defaultdict(lambda: {'cand': {}, 'esp': {}, 'nom': {}})
    for r in P:
        k = (r['cod_dpto'], r['cod_mpio'])
        m = mp[k]; m['nom'] = (r['nom_dpto'], r['nom_mpio'])
        c = r['cod_candidato']
        if c >= 900: m['esp'][c] = r['votos'] or 0
        else: m['cand'][c] = (r['votos'] or 0, r['Nom_candidato'], r['cod_partido'], r['movimiento'])
    for (dep, mun), m in mp.items():
        tot = m['esp'].get(999, 0)
        suma = sum(v for v, *_ in m['cand'].values()) + sum(m['esp'].get(c, 0) for c in (996, 997, 998))
        dif = suma - tot if tot else ''
        for c, (v, nom, pc, pn) in m['cand'].items():
            out.append(base(id_eleccion='2002-PRES-1', fecha='2002-05-26', oficio='presidencial',
                codigo_depto_rnec=int(dep), nombre_depto=m['nom'][0], codigo_muni_rnec=int(mun),
                nombre_muni=m['nom'][1], codigo_opcion=c, nombre_opcion=nom.strip(),
                partido_codigo=pc, partido_nombre=pn.strip(), votos=v,
                votos_blancos=m['esp'].get(996, 0), votos_nulos=m['esp'].get(997, 0),
                total_control=tot, diferencia_control=dif, estado_control=estado(tot, dif)))

    # --- Senado 2002. Circunscripción 0 = nacional, 3 = indígena.
    S = list(db.filas(cat['votos_senado']))
    gs = defaultdict(lambda: defaultdict(int)); nom = {}
    for r in S:
        k = (r['cod_dpto'], r['cod_mpio'], r['circunscripcion'])
        gs[k][r['cod_candidato']] += r['votos'] or 0
        nom[(r['cod_candidato'], r['circunscripcion'])] = r
    for r in S:
        pass  # (datos de nombre tomados abajo por fila)
    seen = set()
    for r in S:
        k = (r['cod_dpto'], r['cod_mpio'], r['circunscripcion'], r['cod_candidato'])
        if k in seen: continue
        seen.add(k)
        dep, mun, circ, c = k[0], k[1], k[2], k[3]
        d = gs[(dep, mun, circ)]
        if circ == 0 and 999 in d:
            c3 = sum(gs.get((dep, mun, 3), {}).values())
            suma = sum(v for x, v in d.items() if x < 900) + d.get(996, 0) + d.get(997, 0) + d.get(998, 0) + c3
            tot = d[999]; dif = suma - tot
            est = estado(tot, dif)
        else:
            tot, dif, est = '', '', 'sin_control'
        if c >= 900:
            continue  # filas especiales (996-999) no son opciones
        out.append(base(id_eleccion='2002-SEN', fecha='2002-03-10', oficio='senado',
            codigo_depto_rnec=int(dep), nombre_depto=r['nom_dpto'], codigo_muni_rnec=int(mun),
            nombre_muni=r['nom_mpio'], codigo_opcion=c, nombre_opcion=r['nom_candidato'].strip(),
            partido_codigo=r['cod_partido'], partido_nombre=r['movimiento'].strip(),
            votos=d.get(c, 0), votos_blancos=d.get(996, 0) if circ == 0 else '',
            votos_nulos=d.get(997, 0) if circ == 0 else '', total_control=tot,
            diferencia_control=dif, estado_control=est, circunscripcion=circ))
    # --- Cámara 2002 (circunscripción departamental). Filas especiales 996-999 por municipio.
    C = list(db.filas(cat['votos_camara']))
    mc = defaultdict(lambda: defaultdict(int)); nomc = {}
    for r in C:
        k = (r['cod_dpto'], r['cod_mpio'])
        mc[k][r['cod_candidato']] += r['votos'] or 0
        nomc[(k, r['cod_candidato'])] = r
    for (dep, mun), d in mc.items():
        tot = d.get(999, 0)
        suma = sum(v for x, v in d.items() if x < 900) + d.get(996, 0) + d.get(997, 0) + d.get(998, 0)
        dif = suma - tot if tot else ''
        for c in sorted(x for x in d if x < 900):
            r = nomc[((dep, mun), c)]
            out.append(base(id_eleccion='2002-CAM', fecha='2002-03-10', oficio='camara',
                codigo_depto_rnec=int(dep), nombre_depto=r['Nom_dpto'], codigo_muni_rnec=int(mun),
                nombre_muni=r['nom_mpio'], codigo_opcion=c, nombre_opcion=r['nom_candidato'].strip(),
                partido_codigo=r['cod_partido'], partido_nombre=r['movimiento'].strip(),
                votos=d[c], votos_blancos=d.get(996, 0), votos_nulos=d.get(997, 0),
                total_control=tot, diferencia_control=dif, estado_control=estado(tot, dif)))
    return out
