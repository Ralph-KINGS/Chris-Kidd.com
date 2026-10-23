import json, numpy as np
db=np.load('work/db.npy'); W=json.load(open('work/aligned.json'))
# sections: (first word idx, last word idx, optional skip word ranges)
SECTIONS=[
 ("hook",154,167),
 ("most",1,15),("hearing",16,30),("beginner",31,44),("advanced",45,63),("onus",64,75),
 ("near",76,103),("said",104,119),("concern",140,153),("beauty",154,176),("good",177,186)]
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
json.dump(segs,open('work/segs.json','w'))
tot=sum(b-a for _,a,b in segs); print('segments',len(segs),'total %.2f s'%tot)
