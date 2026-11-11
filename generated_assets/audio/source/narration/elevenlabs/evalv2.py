import sys, re, json, warnings; warnings.filterwarnings("ignore")
import torch, librosa, numpy as np, soundfile as sf
from faster_whisper import WhisperModel
mos=torch.hub.load("tarepan/SpeechMOS:v1.2.0","utmos22_strong",trust_repo=True,verbose=False)
asr=WhisperModel(sys.argv[3] if len(sys.argv)>3 else "medium.en",device="cpu",compute_type="int8")
NUM={"2089":"twenty eighty nine","2149":"twenty one forty nine","2041":"twenty forty one"}
def norm(s):
    s=s.lower()
    for k,v in NUM.items(): s=s.replace(k,v)
    s=re.sub(r"\[[^\]]*\]"," ",s).replace("-"," ")
    s=s.replace("synchronized","synchronised")
    return re.sub(r"[^a-z0-9' ]"," ",s).split()
def wer(r,h):
    d=[[0]*(len(h)+1) for _ in range(len(r)+1)]
    for i in range(len(r)+1): d[i][0]=i
    for j in range(len(h)+1): d[0][j]=j
    for i in range(1,len(r)+1):
        for j in range(1,len(h)+1):
            d[i][j]=min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+(r[i-1]!=h[j-1]))
    return d[-1][-1]
refs=json.load(open(sys.argv[1])); out={}
for f,ref in refs.items():
    y,sr=librosa.load(f,sr=16000)
    yf,srf=librosa.load(f,sr=None)
    clip=int(np.sum(np.abs(yf)>=0.999))
    m=float(mos(torch.from_numpy(y).unsqueeze(0),16000))
    segs,_=asr.transcribe(f,beam_size=5,word_timestamps=True); segs=list(segs)
    hyp=" ".join(s.text for s in segs)
    words=[w for s in segs for w in s.words]
    speech=sum(w.end-w.start for w in words) if words else 0
    span=(words[-1].end-words[0].start) if words else 0
    gaps=[round(b.start-a.end,2) for a,b in zip(words,words[1:]) if b.start-a.end>0.25]
    f0,vf,_=librosa.pyin(y,fmin=50,fmax=400,sr=16000); f0=f0[~np.isnan(f0)]
    rn,hn=norm(ref),norm(hyp)
    out[f]=dict(mos=round(m,2),errs=wer(rn,hn),nref=len(rn),f0=round(float(np.median(f0)),1) if len(f0) else 0,f0sd=round(float(np.std(12*np.log2(f0/np.median(f0)))),2) if len(f0) else 0,
                wpm=round(len(rn)/span*60) if span else 0,dur=round(len(y)/16000,2),lead=round(words[0].start,2) if words else 0,tail=round(len(y)/16000-words[-1].end,2) if words else 0,
                maxgap=max(gaps) if gaps else 0,clip=clip,peak=round(float(20*np.log10(np.abs(yf).max()+1e-9)),2),hyp=hyp.strip())
    print(f,{k:v for k,v in out[f].items() if k!='hyp'},flush=True)
json.dump(out,open(sys.argv[2],"w"),indent=1)
