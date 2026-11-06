import gzip,struct,bz2,lzma,io
class RS:
    def __init__(s,b,ascii=False): s.b=b;s.p=0;s.refs=[];s.A=ascii
    def line(s):
        e=s.b.index(b'\n',s.p);v=s.b[s.p:e];s.p=e+1;return v
    def i(s):
        if s.A:
            t=s.line().strip();return -2147483648 if t==b'NA' else int(t)
        v=struct.unpack('>i',s.b[s.p:s.p+4])[0];s.p+=4;return v
    def d(s,n):
        if s.A:
            out=[]
            for _ in range(n):
                t=s.line().strip()
                out.append(float('nan') if t==b'NA' else float('inf') if t==b'Inf' else float('-inf') if t==b'-Inf' else float(t))
            return out
        v=struct.unpack('>%dd'%n,s.b[s.p:s.p+8*n]);s.p+=8*n;return list(v)
    def ints(s,n):
        if s.A: return [s.i() for _ in range(n)]
        v=struct.unpack('>%di'%n,s.b[s.p:s.p+4*n]);s.p+=4*n;return list(v)
    def length(s):
        n=s.i()
        if n==-1: a=s.i();b=s.i();n=(a<<32)+b
        return n
    def header(s):
        f=s.b[s.p:s.p+2]; assert f in(b'X\n',b'A\n'),s.b[:10]; s.p+=2
        v=s.i();s.i();s.i()
        if v==3:
            n=s.i()
            if s.A: s.line()
            else: s.p+=n
    def item(s):
        f=s.i();t=f&0xFF;attr=bool(f&0x200);tag=bool(f&0x400)
        if t==254 or t==0: return None
        if t in(253,242,241,251,250,252): return ('special',t)
        if t==255:
            k=f>>8
            if k==0:k=s.i()
            return s.refs[k-1]
        if t==1:
            c=s.item();s.refs.append(c);return c
        if t==9:
            n=s.i()
            if n==-1: return None
            if s.A:
                v=s.line()
                import re
                def esc(m):
                    c=m.group(1)
                    if c[:1] in b'01234567'.decode(): return chr(int(c,8))
                    return {'n':'\n','t':'\t','\\\\':'\\','\\\'':"'",'"':'"','r':'\r'}.get(c,c)
                v=re.sub(rb'\\([0-7]{1,3}|.)',lambda m:bytes([int(m.group(1),8)]) if m.group(1)[:1].isdigit() else {b'n':b'\n',b't':b'\t',b'r':b'\r'}.get(m.group(1),m.group(1)),v)
            else:
                v=s.b[s.p:s.p+n];s.p+=n
            try:return v.decode('utf-8')
            except:return v.decode('latin1')
        if t in(249,248,247):
            s.i();n=s.i();v=[s.item() for _ in range(n)];s.refs.append(v);return v
        if t==4:
            s.i();idx=len(s.refs);s.refs.append(None)
            for _ in range(4): s.item()
            return ('env',)
        if t in(2,6,3,5,17):
            at=s.item() if attr else None
            tg=s.item() if tag else None
            car=s.item();cdr=s.item()
            out=[(tg,car)]
            if isinstance(cdr,list) and cdr and isinstance(cdr[0],tuple) and len(cdr[0])==2 and not isinstance(cdr[0][0],str) is False: pass
            if isinstance(cdr,list): out+=cdr
            if at is not None and t==2: pass
            return out
        if t==238:
            info=s.item();state=s.item();at=s.item()
            cls=info[0][1] if isinstance(info,list) else None
            cls=cls if isinstance(cls,str) else str(cls)
            if cls=='compact_intseq': n,st,step=state; return [int(st+k*step) for k in range(int(n))]
            if cls=='compact_realseq': n,st,step=state; return [st+k*step for k in range(int(n))]
            if cls.startswith('wrap_'): return state[0][1] if isinstance(state,list) and isinstance(state[0],tuple) else state[0]
            if cls=='deferred_string':
                a=state[0][1] if isinstance(state,list) and isinstance(state[0],tuple) else state[0]
                return [None if (x!=x) else str(int(x)) if float(x).is_integer() else str(x) for x in a]
            raise Exception('altrep '+cls)
        if t==10 or t==13:
            n=s.length();v=s.ints(n)
            if t==10: v=[None if x==-2147483648 else x for x in v]
            else: v=[None if x==-2147483648 else x for x in v]
            val=v
        elif t==14:
            n=s.length();val=s.d(n);val=[None if x!=x else x for x in val]
        elif t==16:
            n=s.length();val=[s.item() for _ in range(n)]
        elif t in(19,20):
            n=s.length();val=[s.item() for _ in range(n)]
        elif t==24:
            n=s.length();val=s.b[s.p:s.p+n];s.p+=n
        elif t==15:
            n=s.length();val=s.d(2*n)
        else: raise Exception('type %d at %d'%(t,s.p))
        if attr:
            a=s.item() or []
            return RObj(val,dict((k,v) for k,v in a if isinstance(k,str)))
        return RObj(val,{})
class RObj:
    def __init__(s,v,a): s.v=v;s.a=a
def unwrap(x): return x.v if isinstance(x,RObj) else x
def load(path):
    raw=open(path,'rb').read()
    for op in(gzip.decompress,bz2.decompress,lzma.decompress,lambda x:x):
        try: raw=op(raw);break
        except Exception: pass
    A=False
    if raw[:5] in(b'RDX3\n',b'RDX2\n'): raw=raw[5:]
    elif raw[:5] in(b'RDA3\n',b'RDA2\n'): raw=raw[5:];A=True
    s=RS(raw,A);s.header();return s.item()
def to_df(o):
    import pandas as pd
    cols=unwrap(o);names=unwrap(o.a['names'])
    data={}
    meta={}
    for n,c in zip(names,cols):
        v=unwrap(c)
        if isinstance(c,RObj):
            a=c.a
            lv=unwrap(a['levels']) if 'levels' in a else None
            labs=a.get('labels')
            if lv is not None: v=[None if x is None else lv[x-1] for x in v]
            elif labs is not None and isinstance(labs,RObj):
                mp={}
                for val,nm in zip(unwrap(labs),unwrap(labs.a['names'])): mp[val]=nm
                meta[n]=mp
            if 'label' in a: meta[n+'__label']=unwrap(a['label'])
        data[n]=v
    return pd.DataFrame(data),meta

def load_multi(path):
    raw=open(path,'rb').read()
    for op in(gzip.decompress,bz2.decompress,lzma.decompress,lambda x:x):
        try: raw=op(raw);break
        except Exception: pass
    A=False
    if raw[:5] in(b'RDX3\n',b'RDX2\n'): raw=raw[5:]
    elif raw[:5] in(b'RDA3\n',b'RDA2\n'): raw=raw[5:];A=True
    s=RS(raw,A);s.header();out={}
    while True:
        try:
            f=s.i();t=f&0xFF
            if t==254: break
            tag=s.item() if f&0x400 else None
            val=s.item(); out[tag]=val
        except Exception as e:
            out['__error__']=str(e);break
    return out
