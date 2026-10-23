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
SHOTS=[(0,0.80,1,'c'),(0.80,2.00,1.2,'c'),(2.00,3.84,1,'c'),(3.84,5.84,1.2,'c'),(5.84,7.88,1,'c'),
(7.88,11.80,1.28,'t'),(11.80,14.18,1,'c'),(14.18,15.97,1.2,'c'),(15.97,19.06,1,'c'),(19.06,22.44,1.28,'t'),
(22.44,24.65,1,'c'),(24.65,26.57,1.2,'c'),(26.57,29.36,1,'c'),(29.36,32.12,1.2,'c'),(32.12,32.85,1,'c'),
(32.85,34.41,1.2,'c'),(34.41,37.45,1,'c'),(37.45,41.54,1.2,'c'),(41.54,45.38,1,'c'),(45.38,49.01,1.28,'t'),
(49.01,50.80,1,'c')]
out=[]
for a,b,z,m in SHOTS:
    xs=[src_of(a+(b-a)*k/10) for k in range(11)]
    pts=[f for f in F if any(abs(f[0]-x)<0.3 for x in xs)]
    fx=st.median(p[1] for p in pts) if pts else 537
    fy=st.median(p[2] for p in pts) if pts else 291
    S=S0*z
    left=540-fx*S; left=min(0,max(1080-1920*S,left))
    if m=='t': top=TOP0
    else:
        top=TOP0+fy*S0-fy*S; top=min(TOP0,max(1920-1080*S,top))
    out.append({'t':a,'end':b,'zoom':z,'x':round(left,1),'y':round(top-TOP0,1),'s':round(S,4),'fx':fx,'fy':fy,'n':len(pts)})
json.dump(out,open('work/shots.json','w'),indent=0)
for o in out: print(o)
