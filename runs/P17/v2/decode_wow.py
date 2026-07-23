import re, zlib, sys
data = open(sys.argv[1],'rb').read()
objs={}
for m in re.finditer(rb'(\d+) 0 obj(.*?)endobj', data, re.S):
    objs[int(m.group(1))]=m.group(2)

def b36(s):
    v=0
    for c in s:
        v=v*36+(ord(c)-55 if c.isalpha() else ord(c)-48)
    return v
def g2c(g):
    try:
        v=b36(g)-360
        if 32<=v<127: return chr(v)
    except Exception: pass
    return '\ufffd'

def parse_diffs(raw):
    m=re.search(rb'/Differences\s*\[(.*?)\]', raw, re.S)
    if not m: return None
    enc={}; code=0
    for tok in re.finditer(rb'(\d+)|/([A-Za-z0-9.]+)', m.group(1)):
        if tok.group(1): code=int(tok.group(1))
        else: enc[code]=tok.group(2).decode(); code+=1
    return enc

def enc_of_font(raw):
    d=parse_diffs(raw)
    if d: return d
    m=re.search(rb'/Encoding\s+(\d+) 0 R', raw)
    if m: return parse_diffs(objs.get(int(m.group(1)),b''))
    return None

def get_stream(objraw):
    m=re.search(rb'stream\r?\n(.*?)\r?\nendstream', objraw, re.S)
    if not m: return b''
    s=m.group(1)
    if b'FlateDecode' in objraw:
        try: s=zlib.decompress(s)
        except Exception:
            try: s=zlib.decompress(s+b'\x00')
            except Exception: pass
    return s

pages=[(n,r) for n,r in objs.items() if re.search(rb'/Type\s*/Page\b', r) and b'/Contents' in r]
pages.sort()
out=[]
for num,raw in pages:
    # resources
    m=re.search(rb'/Resources\s+(\d+) 0 R', raw)
    res=objs[int(m.group(1))] if m else raw
    fonts={}
    fm=re.search(rb'/Font\s*<<(.*?)>>', res, re.S)
    if fm:
        for f in re.finditer(rb'/([A-Za-z0-9]+)\s+(\d+) 0 R', fm.group(1)):
            fonts[f.group(1).decode()]=int(f.group(2))
    else:
        m2=re.search(rb'/Font\s+(\d+) 0 R', res)
        if m2:
            for f in re.finditer(rb'/([A-Za-z0-9]+)\s+(\d+) 0 R', objs[int(m2.group(1))]):
                fonts[f.group(1).decode()]=int(f.group(2))
    # contents: array or single
    carr=re.search(rb'/Contents\s*\[(.*?)\]', raw, re.S)
    if carr:
        cids=[int(x) for x in re.findall(rb'(\d+) 0 R', carr.group(1))]
    else:
        m3=re.search(rb'/Contents\s+(\d+) 0 R', raw)
        cids=[int(m3.group(1))] if m3 else []
    stream=b''.join(get_stream(objs[c]) for c in cids if c in objs)
    cur=None; text=[]
    for tok in re.finditer(rb'/([A-Za-z0-9]+)\s+[\d.]+\s+Tf|\(((?:\\.|[^\\()])*)\)\s*Tj|\[((?:\((?:\\.|[^\\()])*\)|[^\]])*)\]\s*TJ|T\*|TD|Td|ET', stream):
        t=tok.group(0)
        if t.endswith(b'Tf'):
            cur=fonts.get(tok.group(1).decode())
        elif t in (b'T*',b'Td',b'TD',b'ET'):
            if text and text[-1]!='\n': text.append('\n')
        else:
            enc=enc_of_font(objs.get(cur,b'')) or {}
            body=t
            for sm in re.finditer(rb'\(((?:\\.|[^\\()])*)\)', body):
                s=sm.group(1); j=0
                while j<len(s):
                    c=s[j]
                    if c==0x5c:
                        j+=1
                        if j<len(s) and 48<=s[j]<=55:
                            k=j
                            while k<len(s) and k<j+3 and 48<=s[k]<=55: k+=1
                            c=int(s[j:k],8); j=k
                        else:
                            c=s[j]; j+=1
                    else: j+=1
                    g=enc.get(c)
                    text.append(g2c(g) if g else ' ')
            text.append(' ')
    out.append(''.join(text))
open('/tmp/wow_decoded.txt','w').write('\n<<<PAGE>>>\n'.join(out))
print("pages:",len(pages))
