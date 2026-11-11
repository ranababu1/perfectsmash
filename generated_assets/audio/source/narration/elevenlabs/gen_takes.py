import sys,json,os; sys.path.insert(0,'.'); from el import *
from concurrent.futures import ThreadPoolExecutor
c={s['id']:s for s in json.load(open('/workspace/tfj-narration-main/data/cinematics.json'))['sequences']}
D=json.load(open('direction.json')); V=json.load(open('voices_created.json'))
SEEDS=[int(x) for x in sys.argv[1].split(',')]; only=sys.argv[2] if len(sys.argv)>2 else None
ST={"narrator":{"stability":0.4,"similarity_boost":0.8},"control":{"stability":0.5,"similarity_boost":0.8}}
jobs=[]
for seq,lines in D.items():
    sl=c[seq]['slides']
    for n,text in lines.items():
        i=int(n)-1; spk=sl[i]['speaker']
        if only and f"{seq}_{int(n):02d}" not in only.split(','): continue
        vid=V['nar_uk' if spk=='narrator' else 'ctl_f']['voice_id']
        prev=sl[i-1]['subtitle'] if i>0 else None; nxt=sl[i+1]['subtitle'] if i+1<len(sl) else None
        for s in SEEDS:
            out=f"takes/{seq}_{int(n):02d}_s{s}.pcm"
            if os.path.exists(out): continue
            jobs.append((vid,text,ST[spk],s,prev,nxt,out))
def run(j):
    vid,text,st,s,prev,nxt,out=j
    r,cost=tts(vid,text,settings=st,seed=s,prev=prev,nxt=nxt,out=out); return out,cost
with ThreadPoolExecutor(3) as ex:
    tot=0
    for out,cost in ex.map(run,jobs): tot+=cost; print(out,cost,flush=True)
print("total cost",tot)
