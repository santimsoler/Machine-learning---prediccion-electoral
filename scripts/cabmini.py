import struct, sys, os, zlib

def parse(path):
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] != b"MSCF":
        raise ValueError("no es CAB")
    flags = struct.unpack("<H", data[30:32])[0]
    nfolders, nfiles = struct.unpack("<HH", data[26:30])
    coffFiles = struct.unpack("<I", data[16:20])[0]
    pos = 36
    cbFolderReserve = 0
    if flags & 4:
        cbCFHeader, cbCFFolder, cbCFData = struct.unpack("<HBB", data[36:40])
        pos = 40 + cbCFHeader
        cbFolderReserve = cbCFFolder
    folders = []
    for _ in range(nfolders):
        coffCab, cCF, typeCompress = struct.unpack("<IHH", data[pos:pos + 8])
        folders.append((coffCab, cCF, typeCompress))
        pos += 8 + cbFolderReserve
    files = []
    pos = coffFiles
    for _ in range(nfiles):
        cbFile, uoffFolderStart, iFolder, date, time, attribs = struct.unpack("<IIHHHH", data[pos:pos + 16])
        end = data.index(b"\x00", pos + 16)
        name = data[pos + 16:end].decode("latin-1")
        files.append((name, cbFile, uoffFolderStart, iFolder))
        pos = end + 1
    return data, folders, files, flags

def folder_bytes(data, folders, fi):
    coffCab, cCF, comp = folders[fi]
    method = comp & 0x0F
    out = bytearray()
    p = coffCab
    if method == 0:
        for _ in range(cCF):
            cbData = struct.unpack("<H", data[p + 4:p + 6])[0]
            p += 8
            out += data[p:p + cbData]
            p += cbData
        return bytes(out), "none"
    if method == 1:  # MSZIP
        for _ in range(cCF):
            cbData = struct.unpack("<H", data[p + 4:p + 6])[0]
            p += 8
            blk = data[p:p + cbData]
            p += cbData
            if blk[:2] != b"CK":
                raise ValueError("bloque MSZIP sin firma CK")
            window = bytes(out[-32768:])
            d = zlib.decompressobj(-15, zdict=window) if window else zlib.decompressobj(-15)
            out += d.decompress(blk[2:]) + d.flush()
        return bytes(out), "mszip"
    raise ValueError(f"método de compresión no soportado: {method} (LZX/Quantum)")

if __name__ == "__main__":
    mode, cab = sys.argv[1], sys.argv[2]
    data, folders, files, flags = parse(cab)
    if mode == "list":
        print("carpetas:", [(hex(c[2]), c[1]) for c in folders])
        for n, sz, off, fi in files:
            print(f"{sz:>12}  {n}  (carpeta {fi})")
    elif mode == "extract":
        outdir = sys.argv[3]; os.makedirs(outdir, exist_ok=True)
        cache = {}
        for n, sz, off, fi in files:
            if fi not in cache:
                buf, meth = folder_bytes(data, folders, fi)
                cache[fi] = buf
            buf = cache[fi]
            safe = n.replace("\\", "_").replace("/", "_")
            with open(os.path.join(outdir, safe), "wb") as fh:
                fh.write(buf[off:off + sz])
        print("extraídos:", len(files), "en", outdir)
