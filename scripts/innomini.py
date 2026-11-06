# Extrae el bloque de datos comprimido (LZMA) de un instalador Inno Setup 5.x con compresión sólida.
# Uso: python3 -I innomini.py <setup.exe> <salida.bin>
import sys, lzma, struct
exe, out = sys.argv[1], sys.argv[2]
d = open(exe, 'rb').read()
i = d.find(b'zlb\x1a')
assert i >= 0, 'sin bloque zlb'
props = d[i+4:i+9]
pb_lp_lc = props[0]; dict_size = struct.unpack('<I', props[1:5])[0]
lc = pb_lp_lc % 9; lp = (pb_lp_lc // 9) % 5; pb = pb_lp_lc // 45
print('offset', i, 'lc/lp/pb', lc, lp, pb, 'dict', dict_size)
dec = lzma.LZMADecompressor(format=lzma.FORMAT_RAW,
        filters=[{'id': lzma.FILTER_LZMA1, 'dict_size': dict_size, 'lc': lc, 'lp': lp, 'pb': pb}])
pos = i + 9; total = 0
with open(out, 'wb') as fh:
    try:
        while pos < len(d) and not dec.eof:
            chunk = d[pos:pos + (1 << 22)]; pos += len(chunk)
            o = dec.decompress(chunk); fh.write(o); total += len(o)
    except lzma.LZMAError as e:
        print('fin con error LZMA (normal si no hay marca de fin):', e)
print('descomprimido', total, 'bytes')
