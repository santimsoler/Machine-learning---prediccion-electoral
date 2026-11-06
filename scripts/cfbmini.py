# Lector mínimo de archivos OLE/CFB (.msi): lista y extrae streams.
import struct, sys, os
def cfb_streams(path):
    d = open(path, 'rb').read()
    assert d[:8] == bytes.fromhex('d0cf11e0a1b11ae1')
    ss = 1 << struct.unpack_from('<H', d, 0x1E)[0]
    nfat, dirsec = struct.unpack_from('<II', d, 0x2C)
    fdifat, ndifat = struct.unpack_from('<II', d, 0x44)
    difat = list(struct.unpack_from('<109I', d, 0x4C))
    s = fdifat
    for _ in range(ndifat):
        off = (s + 1) * ss
        difat += list(struct.unpack_from('<%dI' % (ss//4 - 1), d, off))
        s = struct.unpack_from('<I', d, off + ss - 4)[0]
    fat = []
    for sec in difat[:nfat]:
        fat += list(struct.unpack_from('<%dI' % (ss//4), d, (sec + 1) * ss))
    def chain(start):
        out = []; s = start
        while s < 0xFFFFFFFA:
            out.append(s); s = fat[s]
        return out
    def read(start, size):
        return b''.join(d[(s+1)*ss:(s+2)*ss] for s in chain(start))[:size]
    dirdata = b''.join(d[(s+1)*ss:(s+2)*ss] for s in chain(dirsec))
    ents = []
    for i in range(len(dirdata)//128):
        e = dirdata[i*128:(i+1)*128]
        nl = struct.unpack_from('<H', e, 64)[0]
        name = e[:max(nl-2,0)].decode('utf-16le', 'replace')
        typ = e[66]
        start, size = struct.unpack_from('<IQ', e, 116)
        ents.append((name, typ, start, size))
    return ents, read, ss
if __name__ == '__main__':
    ents, read, ss = cfb_streams(sys.argv[1])
    big = sorted([e for e in ents if e[1] == 2], key=lambda e: -e[3])
    for e in big[:10]: print(e[3], repr(e[0]))
    if len(sys.argv) > 2:
        os.makedirs(sys.argv[2], exist_ok=True)
        for name, typ, start, size in big:
            if size >= 4096:
                data = read(start, size)
                if data[:4] == b'MSCF':
                    out = os.path.join(sys.argv[2], 'stream_%d.cab' % start)
                    open(out, 'wb').write(data); print('CAB extraído', out, len(data))
