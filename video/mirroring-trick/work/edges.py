import sys
d=sys.stdin.buffer.read();n=64*36;fps=24000/1001
rows=[]
for i in range(len(d)//n):
  t=i/fps
  if not any(a<=t<=b for a,b in [(0,1),(19,21),(25,26.2),(33,34),(37.3,38.3)]): continue
  f=d[i*n:(i+1)*n]; rows.append(f'{t:.2f}:{sum(f)/n:.0f}')
for k in range(0,len(rows),10): print('  '.join(rows[k:k+10]))
