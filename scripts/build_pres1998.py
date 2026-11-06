import csv, hashlib, collections, sys, os
sys.path.insert(0, "/tmp/claude-0/-home-claude/fbc2a8cf-9f07-5c94-8ce1-557ba4094ca9/scratchpad/scripts")
from dbfmini import read_dbf

BASE = sys.argv[1]          # carpeta CD 1997-1998 extraída
OUT = sys.argv[2]           # carpeta de salida
FECHA_DESCARGA = "2026-10-27"
os.makedirs(OUT, exist_ok=True)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

F = {n: os.path.join(BASE, n) for n in ["resupres.dbf", "PRESIDEN.DBF", "MUNICIPI.DBF", "DEPARTAM.DBF", "PARTIDO.DBF"]}
pres = {int(r["CODICAND"]): r for r in read_dbf(F["PRESIDEN.DBF"])}
partido = {int(r["CODIPART"]): r["NOMBPART"] for r in read_dbf(F["PARTIDO.DBF"])}
depto = {int(r["CODIDEPA"]): r["NOMBDEPA"] for r in read_dbf(F["DEPARTAM.DBF"])}
muni = {(int(r["CODIDEPA"]), int(r["CODIMUNI"])): r["NOMBMUNI"] for r in read_dbf(F["MUNICIPI.DBF"])}
filas = list(read_dbf(F["resupres.dbf"]))

CAND = set(range(1, 14))          # 1..13: candidatos a presidencia
BLANCO, NULO, TNM, TOTAL = 96, 97, 98, 99
RONDAS = {
    "1998-PRES-1": ("VOTOPRIM", "DEPAPRIM", "MUNIPRIM", "TOTAPAI1"),
    "1998-PRES-2": ("VOTOSEGU", "DEPASEGU", "MUNISEGU", "TOTAPAI2"),
}
hash_src = sha256(F["resupres.dbf"])
fuente = f"resupres.dbf (sha256 {hash_src[:12]}) CD 1997-1998 RNEC"

# agrupar por municipio y ronda
por_mun = collections.defaultdict(dict)   # (depto,mun) -> {cod: row}
for r in filas:
    por_mun[(int(r["CODIDEPA"]), int(r["CODIMUNI"]))][int(r["CODICAND"])] = r

checks = {}
for ronda, (vcol, dcol, mcol, tcol) in RONDAS.items():
    rows_out = []
    err_mun = []
    dep_sum = collections.Counter()      # suma de municipios por depto
    dep_declared = {}
    nat_cand = collections.Counter()
    nat_tot99 = 0
    for (d, m), cods in por_mun.items():
        votos = {c: int(r[vcol] or 0) for c, r in cods.items()}
        any_row = next(iter(cods.values()))
        muni_decl = int(any_row[mcol] or 0)
        dep_decl = int(any_row[dcol] or 0)
        dep_declared[d] = dep_decl
        suma_mun = sum(v for c, v in votos.items() if c in CAND or c in (BLANCO, NULO, TNM))
        if suma_mun != muni_decl:
            err_mun.append((d, m, suma_mun, muni_decl))
        dep_sum[d] += muni_decl
        blancos = votos.get(BLANCO, 0)
        nulos = votos.get(NULO, 0)
        tnm = votos.get(TNM, 0)
        validos = sum(v for c, v in votos.items() if c in CAND) + blancos
        for c in sorted(CAND):
            if c in cods:
                v = votos[c]
                nat_cand[c] += v
                rows_out.append({
                    "id_eleccion": ronda,
                    "nivel_distrito": "municipio",
                    "codigo_depto_rnec": d,
                    "nombre_depto": depto.get(d, ""),
                    "codigo_distrito_rnec": m,
                    "nombre_distrito": muni.get((d, m), ""),
                    "id_candidato": c,
                    "nombre_candidato": pres[c]["NOMBPRES"] if c in pres else "",
                    "partido_codigo": pres[c]["CODIPART"] if c in pres else "",
                    "partido_nombre": partido.get(int(pres[c]["CODIPART"]), "") if c in pres else "",
                    "votos": v,
                    "votos_validos_distrito": validos,
                    "votos_blancos": blancos,
                    "votos_nulos": nulos,
                    "tarjetas_no_marcadas": tnm,
                    "total_reportado_99": votos.get(TOTAL, ""),
                    "fuente_archivo": fuente,
                    "fecha_descarga": FECHA_DESCARGA,
                })
        nat_tot99 += votos.get(TOTAL, 0)
    # controles
    dep_err = [(d, dep_sum[d], dep_declared[d]) for d in dep_sum if dep_sum[d] != dep_declared[d]]
    nat_decl = {c: int(pres[c][ "TOTACAN1" if ronda.endswith("1") else "TOTACAN2"] or 0) for c in pres if c in CAND}
    nat_diff = {c: nat_cand[c] - nat_decl[c] for c in sorted(CAND) if c in nat_decl}
    checks[ronda] = dict(filas=len(rows_out), err_mun=len(err_mun), dep_err=dep_err,
                         nat_diff=nat_diff, total99=nat_tot99,
                         total_dec=int(next(iter(pres.values()))[tcol] or 0))
    with open(os.path.join(OUT, f"resultados_presidente_{ronda}.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows_out[0].keys()))
        w.writeheader(); w.writerows(rows_out)

# candidatos
with open(os.path.join(OUT, "candidatos_presidente_1998.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["id_candidato", "id_eleccion", "nombre", "vicepresidente", "partido_codigo", "partido_nombre",
                "total_1ra_declarado", "total_2da_declarado", "fuente_archivo", "fecha_descarga"])
    for c, r in sorted(pres.items()):
        if c not in CAND: continue
        w.writerow([c, "1998-PRES-1;1998-PRES-2", r["NOMBPRES"], r["NOMBVICE"], r["CODIPART"],
                    partido.get(int(r["CODIPART"]), ""), r["TOTACAN1"], r["TOTACAN2"], "PRESIDEN.DBF", FECHA_DESCARGA])

for ronda, c in checks.items():
    print(f"\n== {ronda}")
    print(" filas candidato-municipio:", c["filas"])
    print(" municipios donde suma != total declarado:", c["err_mun"])
    print(" departamentos donde suma municipal != total depto:", c["dep_err"])
    print(" diferencia nacional (suma municipal - TOTACAN):", c["nat_diff"])
    print(" suma de 99 (total reportado):", c["total99"], " | TOTAPAI declarado:", c["total_dec"])
