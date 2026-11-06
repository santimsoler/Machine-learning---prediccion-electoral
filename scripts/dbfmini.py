import struct, sys, os, glob, csv

def read_dbf(path, enc="latin-1"):
    with open(path, "rb") as fh:
        head = fh.read(32)
        nrec = struct.unpack("<I", head[4:8])[0]
        hlen = struct.unpack("<H", head[8:10])[0]
        rlen = struct.unpack("<H", head[10:12])[0]
        fields = []
        fh.seek(32)
        while True:
            fd = fh.read(32)
            if not fd or fd[0] == 0x0D:
                break
            name = fd[:11].split(b"\x00")[0].decode(enc, "replace")
            ftype = chr(fd[11])
            flen = fd[16]
            fdec = fd[17]
            fields.append((name, ftype, flen, fdec))
        fh.seek(hlen)
        for _ in range(nrec):
            rec = fh.read(rlen)
            if len(rec) < rlen:
                break
            if rec[:1] == b"*":
                continue  # registro borrado
            pos = 1
            row = {}
            for name, ftype, flen, fdec in fields:
                raw = rec[pos:pos + flen]
                pos += flen
                row[name] = raw.decode(enc, "replace").strip()
            yield row

def info(path):
    with open(path, "rb") as fh:
        head = fh.read(32)
    nrec = struct.unpack("<I", head[4:8])[0]
    return nrec

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "info":
        for f in sys.argv[2:]:
            with open(f, "rb") as fh:
                head = fh.read(32)
                fh.seek(32)
                fields = []
                while True:
                    fd = fh.read(32)
                    if not fd or fd[0] == 0x0D: break
                    fields.append((fd[:11].split(b"\x00")[0].decode("latin-1"), chr(fd[11]), fd[16], fd[17]))
            print(f"\n## {os.path.basename(f)}  registros={struct.unpack('<I', head[4:8])[0]}")
            print("  ", [(n, t, l) for n, t, l, _ in fields])
    elif mode == "sample":
        f = sys.argv[2]; k = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        for i, r in enumerate(read_dbf(f)):
            print(r)
            if i + 1 >= k: break
    elif mode == "csv":
        f, out = sys.argv[2], sys.argv[3]
        rows = list(read_dbf(f))
        if rows:
            with open(out, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
                w.writeheader(); w.writerows(rows)
        print(os.path.basename(f), "->", len(rows), "filas")
