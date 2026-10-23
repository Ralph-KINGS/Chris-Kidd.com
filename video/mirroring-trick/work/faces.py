import cv2, json
cap=cv2.VideoCapture('src/source.mp4'); fps=cap.get(5)
cc=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
out=[]; i=0
while True:
    ok,f=cap.read()
    if not ok: break
    if i%6==0:
        g=cv2.cvtColor(cv2.resize(f,(960,540)),cv2.COLOR_BGR2GRAY)
        fs=cc.detectMultiScale(g,1.1,6,minSize=(60,60))
        if len(fs):
            x,y,w,h=max(fs,key=lambda r:r[2]*r[3])
            out.append([round(i/fps,2),int((x+w/2)*2),int((y+h/2)*2),int(w*2)])
    i+=1
json.dump(out,open('work/faces.json','w'))
import statistics as s
print(len(out),'cx',min(o[1] for o in out),s.median(o[1] for o in out),max(o[1] for o in out),'cy',min(o[2] for o in out),s.median(o[2] for o in out),max(o[2] for o in out),'w',s.median(o[3] for o in out))
