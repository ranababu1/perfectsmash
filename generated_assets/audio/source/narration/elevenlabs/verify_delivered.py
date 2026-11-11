import json,re,glob,os,sys
from faster_whisper import WhisperModel
D=json.load(open('direction.json'))
def norm(s):
    s=re.sub(r'\[[^\]]*\]','',s).lower(); s=s.replace('-',' ')
    return re.sub(r"[^a-z' ]",' ',s).split()
m=WhisperModel('medium.en',compute_type='int8')
out={}
for f in sorted(glob.glob('/workspace/tfj-narration/generated_assets/audio/voice/*/gam_vo_*.ogg')):
    b=os.path.basename(f)[7:-4]; seq,n=b.rsplit('_',1); ref=norm(D[seq][str(int(n))])
    res=[]
    for temp in (0.0,0.2):
        segs,_=m.transcribe(f,language='en',beam_size=5,temperature=temp,condition_on_previous_text=False)
        hyp=norm(' '.join(s.text for s in segs))
        import difflib
        sm=difflib.SequenceMatcher(None,ref,hyp); err=sum(max(i2-i1,j2-j1) for t,i1,i2,j1,j2 in sm.get_opcodes() if t!='equal')
        res.append(err)
    out[b]=res; print(b,res,flush=True)
json.dump(out,open('verify_delivered.json','w'))
