# Lector mínimo de SPSS .sav (sin librerías). Devuelve (variables, etiquetas_var, etiquetas_valor, filas)
import struct
def vars_by_slot(vars, slots, i):
    s = slots[i] if i < len(slots) else None
    return [vars[s][0]] if s is not None else []
def leer(path):
    b = open(path, 'rb').read(); assert b[:4] == b'$FL2', b[:4]
    e = '<' if struct.unpack('<i', b[64:68])[0] in (2, 3) else '>'
    comp = struct.unpack(e + 'i', b[72:76])[0]; ncase = struct.unpack(e + 'i', b[80:84])[0]; bias = struct.unpack(e + 'd', b[76 + 8 - 8 + 0:76 + 8][:8])[0] if False else 100.0
    bias = struct.unpack(e + 'd', b[84:92])[0]
    p = 176; vars = []; lab = {}; vl = {}; slots = []
    while True:
        t = struct.unpack(e + 'i', b[p:p + 4])[0]; p += 4
        if t == 2:
            typ, hl, nm, pr, wr = struct.unpack(e + 'iiiii', b[p:p + 20]); name = b[p + 20:p + 28].decode('latin-1').strip(); p += 28
            if hl:
                n = struct.unpack(e + 'i', b[p:p + 4])[0]; l = b[p + 4:p + 4 + n].decode('latin-1').strip(); p += 4 + (n + 3) // 4 * 4
            else: l = ''
            p += 8 * abs(nm)
            if typ == -1: slots.append(None); continue          # continuación de cadena larga
            vars.append([name, typ, l]); slots.append(len(vars) - 1)
        elif t == 3:
            n = struct.unpack(e + 'i', b[p:p + 4])[0]; p += 4; d = []
            for _ in range(n):
                v = b[p:p + 8]; ln = b[p + 8]; sl = b[p + 9:p + 9 + ln].decode('latin-1').strip()
                p += 8 + ((1 + ln + 7) // 8) * 8; d.append((struct.unpack(e + 'd', v)[0], sl))
            p += 4; k = struct.unpack(e + 'i', b[p:p + 4])[0]; p += 4
            idx = struct.unpack(e + 'i' * k, b[p:p + 4 * k]); p += 4 * k
            for i in idx:
                nm_ = [x for x in vars_by_slot(vars, slots, i - 1)]
                for nme in nm_: vl.setdefault(nme, {}).update(dict(d))
        elif t == 6:
            n = struct.unpack(e + 'i', b[p:p + 4])[0]; p += 4 + 80 * n
        elif t == 7:
            st, sz, cnt = struct.unpack(e + 'iii', b[p:p + 12]); p += 12 + sz * cnt
        elif t == 999:
            p += 4; break
        else: raise ValueError('record %d' % t)
    # datos
    nslots = len(slots); vals = []
    if comp == 1:
        out = []; 
        while len(out) < ncase * nslots and p < len(b):
            codes = b[p:p + 8]; p += 8
            for c in codes:
                if c == 0: continue
                if c == 252: break
                if 1 <= c <= 251: out.append(('n', c - bias))
                elif c == 253: out.append(('r', b[p:p + 8])); p += 8
                elif c == 254: out.append(('r', b'        '))
                elif c == 255: out.append(('n', None))
                if len(out) >= ncase * nslots: break
        raw = out
    else:
        raw = []
        for i in range(ncase * nslots): raw.append(('r', b[p:p + 8])); p += 8
    rows = []; it = iter(raw)
    # asignar por casos: cada caso consume nslots celdas de 8 bytes
    cells = list(raw); si = [s for s in slots]
    for c in range(ncase):
        row = [None] * len(vars)
        for j, s in enumerate(si):
            k, v = cells[c * nslots + j]
            if s is None: continue
            if vars[s][1] == 0:
                row[s] = v if k == 'n' else struct.unpack(e + 'd', v)[0]
            else:
                row[s] = (row[s] or b'') + v if False else v.decode('latin-1').rstrip()
        rows.append(row)
    return vars, vl, rows
