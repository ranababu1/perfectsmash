import os, json, base64, requests, sys, time
K=os.environ["ELEVENLABS_API_KEY"]; H={"xi-api-key":K}
B="https://api.elevenlabs.io"
def mask(s): return str(s).replace(K,"***")
def post(path, body, params=None, raw=False):
    for i in range(4):
        r=requests.post(B+path,headers={**H,"Content-Type":"application/json"},json=body,params=params,timeout=300)
        if r.status_code==429 or r.status_code>=500: time.sleep(5*(i+1)); continue
        break
    if r.status_code!=200: raise RuntimeError(f"{path} {r.status_code} {mask(r.text[:400])}")
    return r if raw else r.json()
def get(path, params=None):
    r=requests.get(B+path,headers=H,params=params,timeout=60)
    if r.status_code!=200: raise RuntimeError(f"{path} {r.status_code} {mask(r.text[:300])}")
    return r.json()
USAGE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"usage.jsonl")
def log_usage(kind, cost, extra):
    open(USAGE,"a").write(json.dumps({"t":time.strftime("%Y-%m-%dT%H:%M:%S"),"kind":kind,"cost":cost,**extra})+"\n")
def tts(voice_id, text, model="eleven_v4", fmt="pcm_48000", settings=None, seed=None, prev=None, nxt=None, out=None):
    body={"text":text,"model_id":model}
    if settings: body["voice_settings"]=settings
    if seed is not None: body["seed"]=seed
    if prev: body["previous_text"]=prev
    if nxt: body["next_text"]=nxt
    r=post(f"/v1/text-to-speech/{voice_id}",body,params={"output_format":fmt},raw=True)
    cost=int(r.headers.get("character-cost","0") or 0)
    log_usage("tts",cost,{"voice":voice_id,"model":model,"chars":len(text),"out":out})
    if out: open(out,"wb").write(r.content)
    return r, cost
