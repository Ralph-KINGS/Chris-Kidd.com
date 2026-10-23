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
SHOTS=[(0,7.66,1,'c'),(7.66,9.55,1,'c'),(9.55,11.56,1.2,'c'),(11.56,13.85,1,'c'),(13.85,18.05,1,'c'),
(18.05,20.36,1.2,'c'),(20.36,24.41,1,'c'),(24.41,26.00,1.2,'c'),(26.00,30.25,1,'b'),(30.25,32.54,1,'c'),
(32.54,35.63,1.2,'c'),(35.63,37.25,1,'c'),(37.25,39.17,1.2,'c'),(39.17,42.58,1,'b'),(42.58,43.68,1,'c')]
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
