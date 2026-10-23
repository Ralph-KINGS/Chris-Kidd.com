import json, statistics as st
E=json.load(open('work/edl.json'))['segments']; F=json.load(open('work/faces.json'))
S0=1500/1080; TOP0=420
def src_of(t):
    for s in E:
        d=s['end']-s['src']
        if s['out']-1e-3<=t<s['out']+d:
            x=s['src']+t-s['out']
            vs=s.get('videoSwap')
            if vs and x>=vs['at']: x+=vs['offset']
            return x
    s=E[-1]; return s['end']
# (start, end, zoom, mode)  mode: c=face-centred, t=top-anchored (hides burned-in boxes)
SHOTS=[(0,1.63,1.2,'c'),(1.63,3.59,1,'c'),(3.59,5.26,1.2,'c'),(5.26,7.55,1,'c'),(7.55,8.97,1.28,'t'),
(8.97,12.10,1,'c'),(12.10,14.47,1.2,'c'),(14.47,18.23,1,'c'),(18.23,19.73,1.2,'c'),(19.73,21.77,1,'c'),
(21.77,23.94,1.28,'t'),(23.94,27.03,1,'c'),(27.03,29.07,1.28,'t'),(29.07,30.95,1,'c'),(30.95,33.78,1.2,'c'),
(33.78,34.16,1,'c'),(34.16,35.62,1.28,'t')]
out=[]
for a,b,z,m in SHOTS:
    xs=[src_of(a+(b-a)*k/10) for k in range(11)]
    pts=[] if m=='b' else [f for f in F if any(abs(f[0]-x)<0.3 for x in xs) and f[1]<900]
    fx=st.median(p[1] for p in pts) if pts else (960 if m=='b' else 530)
    fy=st.median(p[2] for p in pts) if pts else (540 if m=='b' else 300)
    S=S0*z
    left=540-fx*S; left=min(0,max(1080-1920*S,left))
    if m=='t': top=TOP0
    elif m=='b': top=TOP0
    else:
        top=TOP0+fy*S0-fy*S; top=min(TOP0,max(1920-1080*S,top))
    out.append({'t':a,'end':b,'zoom':z,'x':round(left,1),'y':round(top-TOP0,1),'s':round(S,4),'fx':fx,'fy':fy,'n':len(pts)})
json.dump(out,open('work/shots.json','w'),indent=0)
for o in out: print(o)
