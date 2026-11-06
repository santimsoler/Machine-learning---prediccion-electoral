import sys, glob, os
from dbfread import DBF
d = sys.argv[1]
for f in sorted(glob.glob(os.path.join(d, "*.DBF")) + glob.glob(os.path.join(d, "*.dbf"))):
    pass
seen = set()
for f in sorted(glob.glob(os.path.join(d, "*")), key=str.lower):
    if f.lower().endswith(".dbf") and f.lower() not in seen:
        seen.add(f.lower())
        try:
            t = DBF(f, encoding="latin-1", char_decode_errors="replace")
            recs = []
            for i, r in enumerate(t):
                recs.append(r)
                if i >= 1: break
            n = len(DBF(f, encoding="latin-1", char_decode_errors="replace", load=False))
            print(f"\n## {os.path.basename(f)}  filas={len(t) if False else 'ver abajo'}")
            print("campos:", [(x.name, x.type, x.length) for x in t.fields])
            print("muestra:", recs[0] if recs else None)
        except Exception as e:
            print("ERR", f, e)
