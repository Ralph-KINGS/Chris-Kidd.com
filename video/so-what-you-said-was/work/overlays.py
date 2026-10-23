import sys
d=sys.stdin.buffer.read();n=64*36;fps=24000/1001
state=None;start=0;prev=None
def cls(f):
    m=sum(f)/n
    if m>200: return 'CARD'
    wb=sum(1 for r in range(27,35) for c in range(0,64) if f[r*64+c]>235)
    return 'BOX' if wb>20 else None
spans=[]
for i in range(len(d)//n):
    c=cls(d[i*n:(i+1)*n])
    if c!=state:
        if state: spans.append((state,start,i/fps))
        state=c;start=i/fps
if state: spans.append((state,start,len(d)//n/fps))
for s in spans: print(f'{s[0]} {s[1]:.2f}-{s[2]:.2f}')
