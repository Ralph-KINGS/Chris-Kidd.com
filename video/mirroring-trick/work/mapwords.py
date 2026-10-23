import json
W=json.load(open('work/aligned.json')); E=json.load(open('work/edl.json'))
def m(t):
    for s in E['segments']:
        if s['src']-1e-3<=t<=s['end']+1e-3: return round(s['out']+t-s['src'],3)
out=[]
for w in W:
    a,b=m(w['start']),m(w['end'])
    if a is None or b is None: continue
    out.append({'id':w['id'],'text':w['text'],'start':a,'end':b})
json.dump(out,open('work/words_out.json','w'))
print(len(out))
print(' '.join(f"{w['text']}@{w['start']:.2f}" for w in out))
