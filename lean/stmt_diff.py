import re,sys
def decls(p):
    s=open(p).read()
    out={}
    for m in re.finditer(r'^(theorem|def|abbrev) (\S+)(.*?)(:= by|:=\n|:= )',s,re.S|re.M):
        out[m.group(2)]=' '.join((m.group(1)+' '+m.group(2)+m.group(3)).split())
    return out
ok=True
for f in ['BridgeLemma','FiniteSample','Bases']:
    a=decls(f'/home/claude/lean_build/statements_before/{f}.lean'); b=decls(f'/home/claude/lean_build/bridge/MUB6Bridge/{f}.lean')
    for k in sorted(set(a)|set(b)):
        same=a.get(k)==b.get(k); ok&=same
        print(f,k,'UNCHANGED' if same else 'DIFFERENT')
print('ALL STATEMENTS UNCHANGED' if ok else 'MISMATCH')
