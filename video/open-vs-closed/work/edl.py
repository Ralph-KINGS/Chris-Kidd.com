import json, numpy as np
db=np.load('work/db.npy'); W=json.load(open('work/aligned.json'))
# sections: (first word idx, last word idx, optional skip word ranges)
SECTIONS=[("hook",15,20),("resp",21,32),("closed",0,8),("recraft",33,48),("elab",49,60),("open",77,81),
 ("typical",82,93),("example",129,143),("now",144,164),("great",165,171)]
PAD_IN,PAD_OUT=0.06,0.10
def silent(a,b): 
    seg=db[int(a*100):int(b*100)]; return len(seg)>0 and seg.max()<-42
segs=[]
for name,i0,i1 in SECTIONS:
    s=W[i0]['start']-PAD_IN; 
    # extend end to the first silence after last word (natural decay), cap 0.18
    e=W[i1]['end']+PAD_OUT
    cur=s
    for k in range(i0,i1):
        g0=W[k]['end']; g1=W[k+1]['start']
        if g1-g0>0.22:
            # tighten: keep 0.07 after word end, 0.05 before next start
            segs.append([name,round(cur,3),round(g0+0.07,3)])
            cur=g1-0.05
            note='silent' if silent(g0+0.07,g1-0.05) else 'VOICED(um?)'
            print(f'  {name}: cut {g0+0.07:.2f}-{g1-0.05:.2f} ({g1-g0-0.12:.2f}s) {note} [{W[k]["text"]} | {W[k+1]["text"]}]')
    segs.append([name,round(cur,3),round(e,3)])
segs=[[n,a,min(b,26.34) if n=='elab' else b] for n,a,b in segs]
json.dump(segs,open('work/segs.json','w'))
tot=sum(b-a for _,a,b in segs); print('segments',len(segs),'total %.2f s'%tot)
