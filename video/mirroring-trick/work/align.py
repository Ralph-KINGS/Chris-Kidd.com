import numpy as np, json, re, onnxruntime as ort, glob
snap=glob.glob('/root/.cache/huggingface/hub/models--Xenova--wav2vec2-base-960h/snapshots/*/')[0]
vocab=json.load(open(snap+'vocab.json'))
a=np.fromfile('work/a.raw',dtype=np.int16).astype(np.float32)/32768
sess=ort.InferenceSession(snap+'onnx/model.onnx')
inp=sess.get_inputs()[0].name
# chunk 20s with 1s overlap context -> simple: process 10s chunks with 1s pad each side
sr=16000; C=10*sr; P=sr
logits=[]
for s in range(0,len(a),C):
    lo=max(0,s-P); hi=min(len(a),s+C+P)
    x=a[lo:hi]; x=(x-x.mean())/(x.std()+1e-7)
    out=sess.run(None,{inp:x[None]})[0][0]
    fr=out.shape[0]/(hi-lo)  # frames per sample
    a0=int(round((s-lo)*fr)); a1=a0+int(round(min(C,len(a)-s)*fr))
    logits.append(out[a0:a1])
L=np.concatenate(logits); L=L-np.log(np.exp(L-L.max(1,keepdims=True)).sum(1,keepdims=True))-L.max(1,keepdims=True)
fps=L.shape[0]/(len(a)/sr)
words=json.load(open('src/transcript.json')); words=words if isinstance(words,list) else words['words']
clean=[re.sub(r"[^A-Z']","",w['text'].upper()) for w in words]
blank=vocab['<pad>']; sep=vocab['|']
tok=[];wid=[]
for i,c in enumerate(clean):
    for ch in c: tok.append(vocab[ch]); wid.append(i)
    tok.append(sep); wid.append(-1)
# CTC viterbi with blanks
S=[blank]
for t in tok: S+= [t,blank]
T=L.shape[0]; N=len(S)
NEG=-1e9
dp=np.full((T,N),NEG,np.float32); bp=np.zeros((T,N),np.int32)
dp[0,0]=L[0,S[0]]; dp[0,1]=L[0,S[1]]
Sarr=np.array(S)
allow2=np.zeros(N,bool)
for j in range(2,N): allow2[j]= S[j]!=blank and S[j]!=S[j-2]
for t in range(1,T):
    p0=dp[t-1]; p1=np.r_[NEG,p0[:-1]]; p2=np.r_[NEG,NEG,p0[:-2]]; p2=np.where(allow2,p2,NEG)
    st=np.stack([p0,p1,p2]); k=st.argmax(0)
    dp[t]=st[k,np.arange(N)]+L[t,Sarr]; bp[t]=k
j=N-1 if dp[-1,N-1]>dp[-1,N-2] else N-2
path=[0]*T
for t in range(T-1,-1,-1):
    path[t]=j; j-=bp[t,j]
# map states to token idx
first={};last={}
for t,s in enumerate(path):
    if s%2==1:
        ti=(s-1)//2; w=wid[ti]
        if w>=0:
            first.setdefault(w,t); last[w]=t
res=[]
for i,w in enumerate(words):
    if i in first: res.append({'id':f'w{i}','text':w['text'],'start':round(first[i]/fps,3),'end':round((last[i]+1)/fps,3)})
    else: res.append({'id':f'w{i}','text':w['text'],'start':w['start'],'end':w['end'],'unaligned':True})
json.dump(res,open('work/aligned.json','w'),indent=0)
for i in range(0,len(res),6): print(' | '.join(f"{r['id']}:{r['start']:.2f}-{r['end']:.2f} {r['text']}" for r in res[i:i+6]))
