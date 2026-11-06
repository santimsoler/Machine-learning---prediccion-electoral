# Lector mínimo de Access/Jet 4 (.mdb, Access 2000-2002). Sin dependencias.
# Uso: python3 -I mdbmini.py listar <archivo.mdb>
#      python3 -I mdbmini.py volcar <archivo.mdb> <tabla> <salida.csv>
import sys, struct, csv, mmap

P = 4096

def u16(b, o): return struct.unpack_from('<H', b, o)[0]
def u32(b, o): return struct.unpack_from('<I', b, o)[0]

def texto_jet4(raw):
    """Texto Jet 4: UTF-16LE, o 'Unicode comprimido' si empieza con FF FE
    (1 byte por carácter; un byte 0x00 alterna entre modo comprimido y UTF-16)."""
    raw = bytes(raw)
    if raw[:2] != b'\xff\xfe':
        return raw.decode('utf-16le', 'replace')
    out = []; i = 2; comp = True
    while i < len(raw):
        if raw[i] == 0:
            comp = not comp; i += 1; continue
        if comp:
            out.append(chr(raw[i])); i += 1
        else:
            out.append(raw[i:i+2].decode('utf-16le', 'replace')); i += 2
    return ''.join(out)

class Mdb:
    def __init__(self, path):
        self.f = open(path, 'rb')
        self.m = mmap.mmap(self.f.fileno(), 0, access=mmap.ACCESS_READ)
        self.npages = len(self.m) // P
        assert self.m[4:16] == b'Standard Jet', 'no es un .mdb Jet'
        assert self.m[0x14] == 1, 'solo Jet 4 (Access 2000/2002)'
        self._cat = None

    def page(self, n):
        return self.m[n*P:(n+1)*P]

    def columns(self, tdef_pg):
        """Devuelve lista de dicts con nombre, tipo, longitud, var_idx, fijo y offset."""
        p = self.page(tdef_pg)
        nxt = u32(p, 4)                 # la definición puede seguir en otras páginas
        while nxt:
            q = self.page(nxt); p = p + q[8:]; nxt = u32(q, 4)
        ncols = u16(p, 45)
        nidx = u32(p, 51)
        base = 63 + nidx * 12          # inicio de las definiciones de columna (25 bytes c/u)
        recs = []
        for i in range(ncols):
            r = p[base + 25*i: base + 25*i + 25]
            recs.append({
                'tipo': r[0],
                'num': u16(r, 5),
                'var_idx': u16(r, 7),
                'flags': r[15],
                'fixed_off': u16(r, 21),
                'largo': u16(r, 23),   # tamaño de la columna (texto/numérico)
            })
        pos = base + 25*ncols
        # nombres: después de los registros de columna (se busca el desplazamiento válido)
        pos = base + 25*ncols
        names = []
        for extra in range(0, 1200, 2):
            q = pos + extra; out = []; ok = True
            for _ in range(ncols):
                ln = u16(p, q); q += 2
                if ln == 0 or ln > 255: ok = False; break
                s = p[q:q+ln].decode('utf-16le', 'replace'); q += ln
                if not s.isprintable(): ok = False; break
                out.append(s)
            if ok and len(out) == ncols:
                names = out; break
        assert names, 'no se encontraron nombres de columna'
        for r, n in zip(recs, names): r['nombre'] = n
        return recs

    def catalogo(self):
        """Tablas de usuario: Id de página de definición y nombre (desde MSysObjects, página 2)."""
        if self._cat is None:
            tabs = {}
            for row in self.filas(2):
                nombre, tipo, id_ = row.get('Name'), row.get('Type'), row.get('Id')
                if tipo == 1 and nombre and not nombre.startswith('MSys'):
                    tabs[nombre] = id_
            self._cat = tabs
        return self._cat

    def filas(self, tdef_pg):
        cols = self.columns(tdef_pg)
        for n in range(self.npages):
            p = self.page(n)
            if p[0] != 1 or u32(p, 4) != tdef_pg: continue
            nrows = u16(p, 12)
            offs = [u16(p, 14 + 2*i) for i in range(nrows)]
            starts = sorted({o & 0x0FFF for o in offs} | {P})
            for i in range(nrows):
                if offs[i] & 0x8000:            # fila borrada
                    continue
                s = offs[i] & 0x0FFF
                e = starts[starts.index(s) + 1]  # la fila termina donde empieza la siguiente
                row = p[s:e]
                if len(row) < 8: continue
                yield self._fila(row, cols)

    def _fila(self, row, cols):
        ncols = u16(row, 0)
        nmask = (ncols + 7) // 8
        mask = row[len(row)-nmask:]
        nvar_pos = len(row) - nmask - 2
        nvar = u16(row, nvar_pos)
        # desplazamientos de columnas de longitud variable (2 bytes c/u, en orden inverso)
        varoff = [u16(row, nvar_pos - 2*(k+1)) for k in range(nvar+1)]
        out = {}
        for c in cols:
            idx = c['num']
            present = (mask[idx//8] >> (idx % 8)) & 1 if idx//8 < len(mask) else 0
            if not present:
                out[c['nombre']] = None
                continue
            t = c['tipo']
            if c['flags'] & 0x01 == 0 and t in (0x0a, 0x0c, 0x0b, 0x09):   # longitud variable
                k = c['var_idx']
                s, e = varoff[k], varoff[k+1]
                raw = row[s:e]
                out[c['nombre']] = texto_jet4(raw) if t in (0x0a, 0x0c) else raw
            else:
                out[c['nombre']] = self._fijo(row, c, t)
        return out

    def _fijo(self, row, c, t):
        o = c['fixed_off'] + 2
        if t == 0x04: return struct.unpack_from('<i', row, o)[0]
        if t == 0x03: return struct.unpack_from('<h', row, o)[0]
        if t == 0x02: return row[o]
        if t == 0x01: return bool(row[o])
        if t == 0x05: return struct.unpack_from('<q', row, o)[0] / 10000
        if t == 0x06: return struct.unpack_from('<f', row, o)[0]
        if t == 0x07: return struct.unpack_from('<d', row, o)[0]
        if t == 0x08: return struct.unpack_from('<d', row, o)[0]   # fecha/hora (double)
        return None

if __name__ == '__main__':
    cmd, path = sys.argv[1], sys.argv[2]
    db = Mdb(path)
    if cmd == 'listar':
        for k, v in sorted(db.catalogo().items()): print(v, k)
