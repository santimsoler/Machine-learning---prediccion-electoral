import csv, collections, os, struct, sys, glob

def read_dbf(path, enc="latin-1"):
    with open(path, "rb") as fh:
        head = fh.read(32); nrec = struct.unpack("<I", head[4:8])[0]
        hlen = struct.unpack("<H", head[8:10])[0]; rlen = struct.unpack("<H", head[10:12])[0]
        fields = []
        while True:
            fd = fh.read(32)
            if not fd or fd[0] == 0x0D: break
            fields.append((fd[:11].split(b"\x00")[0].decode(enc, "replace"), fd[16]))
        fh.seek(hlen)
        for _ in range(nrec):
            rec = fh.read(rlen)
            if len(rec) < rlen: break
            if rec[:1] == b"*": continue
            pos, row = 1, {}
            for name, flen in fields:
                row[name] = rec[pos:pos+flen].decode(enc, "replace").strip(); pos += flen
            yield row

BASE = glob.glob("/content/z1997/**/CD 1997-1998", recursive=True)[0] if os.path.exists("/content") else sys.argv[1]
OUT = "/content/salida_1997_1998" if os.path.exists("/content") else sys.argv[2]
os.makedirs(OUT, exist_ok=True)
def P(name):
    m = [x for x in os.listdir(BASE) if x.lower() == name.lower()]
    return os.path.join(BASE, m[0])

depto = {r["CODIDEPA"]: r["NOMBDEPA"] for r in read_dbf(P("DEPARTAM.DBF"))}
muni = {(r["CODIDEPA"], r["CODIMUNI"]): r["NOMBMUNI"] for r in read_dbf(P("MUNICIPI.DBF"))}
partido = {r["CODIPART"]: r["NOMBPART"] for r in read_dbf(P("PARTIDO.DBF"))}
FECHA = "2026-10-27"
F_SEN = "8/3/1998 (SENADO.rtf); Cámara también el 8/3/1998 (SENADO.rtf)"
F_TER = "26/10/1997 (instructivo DEIN11 y Municipios.rtf)"
COLS = ["id_eleccion", "codigo_depto_rnec", "nombre_depto", "codigo_muni_rnec", "nombre_muni",
        "codigo_lista_o_candidato", "nombre_lista_o_candidato", "partido_codigo", "partido_nombre",
        "votos", "votos_blancos", "votos_nulos", "grupo_control", "total_declarado", "diferencia_control",
        "fuente", "fecha_descarga"]
resumen = {}

def escribir(nombre, filas):
    with open(os.path.join(OUT, nombre), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(filas)

# ---------- CAMARA 1998 ----------
cat = {}
for r in read_dbf(P("LISTACAM.DBF")):
    k = (r["CODIDEPA"], r["CODILIST"])
    cat.setdefault(k, {"total": int(r["TOTALIST"] or 0), "partido": r["CODIPART"], "nombres": []})["nombres"].append(r["NOMBCAMA"])
filas, suma = [], collections.Counter(); blancos_inc = 0
mun_bn = collections.defaultdict(set)
res = list(read_dbf(P("rcama.dbf")))
for r in res:
    suma[(r["CODIDEPA"], r["CODILIST"])] += int(r["VOTOCAMA"] or 0)
    mun_bn[(r["CODIDEPA"], r["CODIMUNI"])].add((r["VOTOBLAN"], r["VOTONULO"]))
blancos_inc = sum(1 for v in mun_bn.values() if len(v) > 1)
for r in res:
    k = (r["CODIDEPA"], r["CODILIST"]); c = cat.get(k)
    dif = suma[k] - c["total"] if c else ""
    bn = next(iter(mun_bn[(r["CODIDEPA"], r["CODIMUNI"])]))
    filas.append({"id_eleccion": "1998-CAM", "codigo_depto_rnec": r["CODIDEPA"], "nombre_depto": depto.get(r["CODIDEPA"], ""),
        "codigo_muni_rnec": r["CODIMUNI"], "nombre_muni": muni.get((r["CODIDEPA"], r["CODIMUNI"]), ""),
        "codigo_lista_o_candidato": r["CODILIST"], "nombre_lista_o_candidato": "; ".join(c["nombres"]) if c else "",
        "partido_codigo": c["partido"] if c else "", "partido_nombre": partido.get(c["partido"], "") if c else "",
        "votos": r["VOTOCAMA"], "votos_blancos": bn[0], "votos_nulos": bn[1],
        "grupo_control": f"depto {r['CODIDEPA']} lista {r['CODILIST']}", "total_declarado": c["total"] if c else "",
        "diferencia_control": dif, "fuente": "rcama.dbf; LISTACAM.DBF", "fecha_descarga": FECHA})
escribir("camara_1998.csv", filas)
resumen["camara"] = {"filas": len(filas), "listas_controladas": sum(1 for k in suma if k in cat),
    "listas_que_no_cuadran": sum(1 for k in suma if k in cat and suma[k] != cat[k]["total"]),
    "municipios_con_blanco_nulo_inconsistente": blancos_inc}

# ---------- SENADO 1998 ----------
cat = {}
for r in read_dbf(P("LISTASEN.DBF")):
    cat.setdefault(r["CODILIST"], {"total": int(r["TOTALIST"] or 0), "partido": r["CODIPART"], "nombres": []})["nombres"].append(r["NOMBSENA"])
res = list(read_dbf(P("resusena.dbf")))
seen, unicos, conflictos = {}, [], []
for r in res:
    k = (r["CODIDEPA"], r["CODIMUNI"], r["CODILIST"])
    if k not in seen:
        seen[k] = r; unicos.append(r)
    elif seen[k] != r:
        conflictos.append(k)
suma = collections.Counter()
for r in unicos: suma[r["CODILIST"]] += int(r["VOTOSENA"] or 0)
filas = []
for r in unicos:
    c = cat.get(r["CODILIST"])
    dif = suma[r["CODILIST"]] - c["total"] if c else ""
    k = (r["CODIDEPA"], r["CODIMUNI"], r["CODILIST"])
    filas.append({"id_eleccion": "1998-SEN", "codigo_depto_rnec": r["CODIDEPA"], "nombre_depto": depto.get(r["CODIDEPA"], ""),
        "codigo_muni_rnec": r["CODIMUNI"], "nombre_muni": muni.get((r["CODIDEPA"], r["CODIMUNI"]), ""),
        "codigo_lista_o_candidato": r["CODILIST"], "nombre_lista_o_candidato": "; ".join(c["nombres"]) if c else "",
        "partido_codigo": c["partido"] if c else "", "partido_nombre": partido.get(c["partido"], "") if c else "",
        "votos": r["VOTOSENA"], "votos_blancos": r["VOTOBLAN"], "votos_nulos": r["VOTONULO"],
        "grupo_control": f"lista nacional {r['CODILIST']}", "total_declarado": c["total"] if c else "",
        "diferencia_control": dif,
        "fuente": "resusena.dbf; LISTASEN.DBF (NO CONCILIADO si diferencia_control != 0; conflicto de duplicado: " + ("sí" if k in conflictos else "no") + ")",
        "fecha_descarga": FECHA})
escribir("senado_1998.csv", filas)
resumen["senado"] = {"filas": len(filas), "duplicados_identicos_descartados": len(res) - len(unicos) - len(conflictos),
    "claves_con_valores_distintos": len(set(conflictos)),
    "listas_controladas": sum(1 for l in suma if l in cat),
    "listas_que_no_cuadran": sum(1 for l in suma if l in cat and suma[l] != cat[l]["total"])}

# ---------- TERRITORIALES 1997 ----------
def controlar_terr(nombre, res_file, vcol, cat_file, catkeys, catval, resgroup, eleccion, nombre_cat_field, codigo_field, total_name=None):
    res = list(read_dbf(P(res_file)))
    cat = {}
    for r in read_dbf(P(cat_file)):
        key = tuple(r[k] for k in catkeys)
        if key not in cat:
            cat[key] = {"total": int(r[catval] or 0), "nombre": r.get(nombre_cat_field, ""), "partido": r.get("CODIPART", "")}
    suma = collections.Counter()
    for r in res: suma[tuple(r[k] for k in resgroup)] += int(r[vcol] or 0)
    filas = []
    for r in res:
        key = tuple(r[k] for k in resgroup)
        c = cat.get(key)
        dif = suma[key] - c["total"] if c else ""
        filas.append({"id_eleccion": eleccion, "codigo_depto_rnec": r["CODIDEPA"], "nombre_depto": depto.get(r["CODIDEPA"], ""),
            "codigo_muni_rnec": r.get("CODIMUNI", ""), "nombre_muni": muni.get((r["CODIDEPA"], r.get("CODIMUNI", "")), ""),
            "codigo_lista_o_candidato": r[codigo_field], "nombre_lista_o_candidato": c["nombre"] if c else "",
            "partido_codigo": c["partido"] if c else "", "partido_nombre": partido.get(c["partido"], "") if c and c["partido"] else "",
            "votos": r[vcol], "votos_blancos": r.get("VOTOBLAN", r.get("MVOTOBLA", "")), "votos_nulos": r.get("VOTONULO", r.get("MVOTONUL", "")),
            "grupo_control": "|".join(f"{k}={r[k]}" for k in resgroup), "total_declarado": c["total"] if c else "",
            "diferencia_control": dif, "fuente": f"{res_file}; {cat_file}", "fecha_descarga": FECHA})
    escribir(nombre, filas)
    con = [k for k in suma if k in cat]
    return {"filas": len(filas), "grupos_controlados": len(con),
            "grupos_que_no_cuadran": sum(1 for k in con if suma[k] != cat[k]["total"]),
            "grupos_sin_catalogo": sum(1 for k in suma if k not in cat)}

resumen["alcaldes"] = controlar_terr("alcaldes_1997.csv", "RESUALCA.DBF", "VOTOALCA", "Alcalde.dbf",
    ["CODIDEPA", "CODIMUNI", "CODICAND"], "TOTAALCA", ["CODIDEPA", "CODIMUNI", "CODICAND"], "1997-ALC", "NOMBALCA", "CODICAND")
resumen["gobernadores"] = controlar_terr("gobernadores_1997.csv", "resugobe.dbf", "VOTOGOBE", "gobernad.dbf",
    ["CODIDEPA", "CODICAND"], "TOTAGOBE", ["CODIDEPA", "CODICAND"], "1997-GOB", "NOMBGOBE", "CODICAND")

# gobernadores: el total de cada candidato es por departamento; la suma se hace por (depto, candidato)
resumen["concejos"] = controlar_terr("concejos_1997.csv", "Resuconc.dbf", "VOTOCONC", "listacon.dbf",
    ["CODIDEPA", "CODIMUNI", "CODILIST"], "TOTACONC", ["CODIDEPA", "CODIMUNI", "CODILIST"], "1997-CON", "NOMBCONC", "CODILIST")
resumen["asambleas"] = controlar_terr("asambleas_1997.csv", "RESUASAM.DBF", "VOTOASAM", "LISTAASA.DBF",
    ["CODIDEPA", "CODILIST"], "TOTALIST", ["CODIDEPA", "CODILIST"], "1997-ASA", "NOMBASAM", "CODILIST")

for k, v in resumen.items():
    print(k, v)
