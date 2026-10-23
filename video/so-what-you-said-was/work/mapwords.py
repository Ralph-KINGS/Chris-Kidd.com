import json
W=json.load(open('work/aligned.json')); E=json.load(open('work/edl.json'))
out=[]
for s in E['segments']:
    for w in W:
        if s['src']-1e-3<=w['start'] and w['end']<=s['end']+1e-3:
            out.append({'id':w['id'],'text':w['text'],'start':round(s['out']+w['start']-s['src'],3),'end':round(s['out']+w['end']-s['src'],3)})
out.sort(key=lambda w:w['start'])
json.dump(out,open('work/words_out.json','w'))
print(len(out)); print(' '.join(w['text'] for w in out))
