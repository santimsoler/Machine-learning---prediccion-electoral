# Carga resultados de presidencia 1998 (1a y 2a vuelta) desde el CD 1997-1998 de la RNEC.
# Uso:  python3 cargar_presidencia_1998.py "<carpeta CD 1997-1998>" "<carpeta salida>"
import csv, hashlib, collections, os, struct, sys

def read_dbf(path, enc="latin-1"):
    """Lector DBF mínimo (sin dependencias). Omite registros borrados."""
    with open(path, "rb") as fh:
        head = fh.read(32)
        nrec = struct.unpack("<I", head[4:8])[0]
        hlen = struct.unpack("<H", head[8:10])[0]
        rlen = struct.unpack("<H", head[10:12])[0]
        fields = []
        while True:
            fd = fh.read(32)
            if not fd or fd[0] == 0x0D:
                break
            fields.append((fd[:11].split(b"\x00")[0].decode(enc, "replace"), fd[16]))
        fh.seek(hlen)
        for _ in range(nrec):
            rec = fh.read(rlen)
            if len(rec) < rlen:
                break
            if rec[:1] == b"*":
                continue
            pos, row = 1, {}
            for name, flen in fields:
                row[name] = rec[pos:pos + flen].decode(enc, "replace").strip()
                pos += flen
            yield row

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

BASE, OUT = sys.argv[1], sys.argv[2]
FECHA = "2026-10-27"
os.makedirs(OUT, exist_ok=True)
P = lambda n: os.path.join(BASE, n)

pres = {int(r["CODICAND"]): r for r in read_dbf(P("PRESIDEN.DBF"))}
partido = {int(r["CODIPART"]): r["NOMBPART"] for r in read_dbf(P("PARTIDO.DBF"))}
depto = {int(r["CODIDEPA"]): r["NOMBDEPA"] for r in read_dbf(P("DEPARTAM.DBF"))}
muni = {(int(r["CODIDEPA"]), int(r["CODIMUNI"])): r["NOMBMUNI"] for r in read_dbf(P("MUNICIPI.DBF"))}
filas = list(read_dbf(P("resupres.dbf")))
fuente = f"resupres.dbf sha256={sha256(P('resupres.dbf'))[:12]} CD 1997-1998 RNEC"

CAND = set(range(1, 14))          # candidatos (códigos 1 a 13)
BLANCO, NULO, TNM, TOTAL = 96, 97, 98, 99
RONDAS = {"1998-PRES-1": ("VOTOPRIM", "DEPAPRIM", "MUNIPRIM", "TOTACAN1"),
          "1998-PRES-2": ("VOTOSEGU", "DEPASEGU", "MUNISEGU", "TOTACAN2")}

por_mun = collections.defaultdict(dict)
for r in filas:
    por_mun[(int(r["CODIDEPA"]), int(r["CODIMUNI"]))][int(r["CODICAND"])] = r

resumen = {}
for ronda, (vcol, dcol, mcol, tcol) in RONDAS.items():
    salida, err_mun, dep_sum, dep_decl = [], [], collections.Counter(), {}
    nat = collections.Counter()
    for (d, m), cods in por_mun.items():
        votos = {c: int(r[vcol] or 0) for c, r in cods.items()}
        ref = next(iter(cods.values()))
        if sum(v for c, v in votos.items() if c in CAND or c in (BLANCO, NULO, TNM)) != int(ref[mcol] or 0):
            err_mun.append((d, m))
        dep_sum[d] += int(ref[mcol] or 0)
        dep_decl[d] = int(ref[dcol] or 0)
        blancos, nulos, tnm = votos.get(BLANCO, 0), votos.get(NULO, 0), votos.get(TNM, 0)
        # votos válidos = votos a candidatos + votos en blanco (criterio electoral estándar)
        validos = sum(v for c, v in votos.items() if c in CAND) + blancos
        for c in sorted(CAND & set(cods)):
            nat[c] += votos[c]
            salida.append({
                "id_eleccion": ronda, "nivel_distrito": "municipio",
                "codigo_depto_rnec": d, "nombre_depto": depto.get(d, ""),
                "codigo_distrito_rnec": m, "nombre_distrito": muni.get((d, m), ""),
                "id_candidato": c,
                "nombre_candidato": pres[c]["NOMBPRES"],
                "partido_codigo": pres[c]["CODIPART"],
                "partido_nombre": partido.get(int(pres[c]["CODIPART"]), ""),
                "votos": votos[c], "votos_validos_distrito": validos,
                "votos_blancos": blancos, "votos_nulos": nulos,
                "tarjetas_no_marcadas": tnm, "total_reportado_99": votos.get(TOTAL, ""),
                "fuente_archivo": fuente, "fecha_descarga": FECHA,
            })
    nombre = os.path.join(OUT, f"resultados_presidente_{ronda}.csv")
    with open(nombre, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(salida[0].keys()))
        w.writeheader(); w.writerows(salida)
    decl = {c: int(pres[c][tcol] or 0) for c in CAND if c in pres}
    resumen[ronda] = {
        "filas": len(salida),
        "municipios_con_suma_distinta": len(err_mun),
        "deptos_con_suma_distinta": [d for d in dep_sum if dep_sum[d] != dep_decl[d]],
        "diferencia_nacional_por_candidato": {c: nat[c] - decl[c] for c in sorted(decl)},
    }

with open(os.path.join(OUT, "candidatos_presidente_1998.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["id_candidato", "nombre", "vicepresidente", "partido_codigo", "partido_nombre",
                "total_1ra_declarado", "total_2da_declarado", "fuente_archivo", "fecha_descarga"])
    for c in sorted(CAND & set(pres)):
        r = pres[c]
        w.writerow([c, r["NOMBPRES"], r["NOMBVICE"], r["CODIPART"],
                    partido.get(int(r["CODIPART"]), ""), r["TOTACAN1"], r["TOTACAN2"],
                    "PRESIDEN.DBF", FECHA])

for ronda, r in resumen.items():
    print(f"\n== {ronda}")
    for k, v in r.items():
        print(f"  {k}: {v}")
