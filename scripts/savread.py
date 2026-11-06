import struct, numpy as np
def read_dict(path):
    f=open(path,'rb'); h=f.read(176)
    cs,comp,wi,nc=struct.unpack('<iiii',h[68:84]); bias=struct.unpack('<d',h[84:92])[0]
    vars_=[];slot=0;vl={};longn={}
    while True:
        t=struct.unpack('<i',f.read(4))[0]
        if t==2:
            typ,hl,nm,_,_=struct.unpack('<iiiii',f.read(20)); name=f.read(8).decode('latin1').strip()
            lab=''
            if hl:
                n=struct.unpack('<i',f.read(4))[0]; lab=f.read((n+3)//4*4)[:n].decode('utf8','replace')
            if nm: f.read(8*abs(nm))
            if typ!=-1: vars_.append(dict(name=name,typ=typ,label=lab,slot=slot)); 
            slot+=1
        elif t==3:
            n=struct.unpack('<i',f.read(4))[0]; pairs=[]
            for _ in range(n):
                v=f.read(8); l=f.read(1)[0]; s=f.read((l+1+7)//8*8-1)[:l].decode('utf8','replace'); pairs.append((v,s))
            assert struct.unpack('<i',f.read(4))[0]==4
            k=struct.unpack('<i',f.read(4))[0]; idx=struct.unpack('<%di'%k,f.read(4*k))
            for i in idx: vl[i-1]=pairs  # index in slots (1-based)
        elif t==6:
            n=struct.unpack('<i',f.read(4))[0]; f.read(80*n)
        elif t==7:
            st,sz,cnt=struct.unpack('<iii',f.read(12)); d=f.read(sz*cnt)
            if st==13:
                for kv in d.decode('utf8','replace').split('\t'):
                    if '=' in kv: a,b=kv.split('=',1); longn[a.strip()]=b.strip()
        elif t==999:
            f.read(4); break
        else: raise Exception('rec %d'%t)
    for v in vars_: v['name']=longn.get(v['name'],v['name'])
    return dict(vars=vars_,cs=cs,comp=comp,nc=nc,bias=bias,data_off=f.tell(),vl=vl)
def read_cols(path,D,names):
    want={v['slot']:v['name'] for v in D['vars'] if v['name'] in names and v['typ']==0}
    cs,nc,bias=D['cs'],D['nc'],D['bias']; out={n:np.full(nc,np.nan) for n in want.values()}
    f=open(path,'rb'); f.seek(D['data_off'])
    SYS=-1.797693134862316e308
    buf=f.read(); pos=0; case=0; col=0; L=len(buf)
    while case<nc and pos<L:
        ctrl=buf[pos:pos+8]; pos+=8
        for c in ctrl:
            if c==0: continue
            if c==252: case=nc; break
            if c==253: val=struct.unpack_from('<d',buf,pos)[0]; pos+=8
            elif c==254: val=None; 
            elif c==255: val=np.nan
            else: val=c-bias
            if col in want and val is not None: out[want[col]][case]=val
            if c==254: pass
            col+=1
            if col==cs: col=0; case+=1
            if case>=nc: break
    return out
