# Recorta bases SQLite de un binario descomprimido (tamaño = page_size * page_count del encabezado).
import sys, struct, re, os, sqlite3
src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
d = open(src, 'rb').read()
for k, m in enumerate(re.finditer(re.escape(b'SQLite format 3\x00'), d)):
    o = m.start()
    ps = struct.unpack('>H', d[o+16:o+18])[0]; ps = 65536 if ps == 1 else ps
    n = struct.unpack('>I', d[o+28:o+32])[0]
    out = os.path.join(outdir, f'db_{k}.sqlite')
    open(out, 'wb').write(d[o:o+ps*n])
    con = sqlite3.connect(f'file:{out}?mode=ro', uri=True)
    tabs = [r[0] for r in con.execute("select name from sqlite_master where type='table' order by name")]
    print(out, ps*n//1_000_000, 'MB', 'tablas:', len(tabs), tabs[:40])
    con.close()
