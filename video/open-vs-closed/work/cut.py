import json, subprocess
FPS=24000/1001
snap=lambda t: round(round(t*FPS)/FPS,5)
segs=json.load(open('work/segs.json'))
LEAD=0.0
V=[];A=[];edl=[];o=LEAD
SWAP_AT=19.70; SWAP_OFF=round(11.80*FPS)/FPS
for name,s,e in segs:
    s,e=snap(s),snap(e)
    A.append((s,e))
    if name=='called':
        m=snap(SWAP_AT); V.append((s,m)); V.append((m+SWAP_OFF,e+SWAP_OFF))
        edl.append({'name':name,'src':s,'end':e,'out':round(o,4),'videoSwap':{'at':m,'offset':SWAP_OFF}})
    else:
        V.append((s,e)); edl.append({'name':name,'src':s,'end':e,'out':round(o,4)})
    o+=e-s
json.dump({'segments':edl,'duration':round(o,4),'lead':LEAD},open('work/edl.json','w'),indent=1)
f=[]
for i,(s,e) in enumerate(V): f.append(f'[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}]')
for i,(s,e) in enumerate(A): f.append(f'[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,afade=t=in:d=0.006,afade=t=out:st={e-s-0.008:.4f}:d=0.008[a{i}]')
f.append(''.join(f'[v{i}]' for i in range(len(V)))+f'concat=n={len(V)}:v=1:a=0,fps=30,tpad=stop_mode=clone:stop_duration=0.5[v]')
f.append(''.join(f'[a{i}]' for i in range(len(A)))+f'concat=n={len(A)}:v=0:a=1,apad=pad_dur=0.5,loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000[a]')
open('work/cut.filter','w').write(';\n'.join(f))
subprocess.run(['ffmpeg','-v','error','-y','-i','src/source.mp4','-filter_complex_script','work/cut.filter','-map','[v]','-map','[a]',
 '-c:v','libx264','-preset','medium','-crf','14','-g','15','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-ar','48000','assets/talk.mp4'],check=True)
print('duration',round(o,3))
