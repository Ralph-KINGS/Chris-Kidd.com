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
SHOTS=[(0,2.59,1,'c'),(2.59,5.17,1.2,'c'),(5.17,8.26,1,'c'),(8.26,9.93,1.2,'c'),(9.93,11.15,1,'c'),
(11.15,12.14,1.2,'c'),(12.14,15.77,1,'c'),(15.77,18.60,1.2,'c'),(18.60,19.66,1,'c'),(19.66,21.98,1.2,'c'),
(21.98,22.44,1,'c'),(22.44,24.95,1.28,'t'),(24.95,28.74,1,'c'),(28.74,32.66,1.2,'c'),(32.66,35.45,1,'c'),
(35.45,37.30,1.28,'t'),(37.30,42.36,1,'c'),(42.36,43.70,1.2,'c')]
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
