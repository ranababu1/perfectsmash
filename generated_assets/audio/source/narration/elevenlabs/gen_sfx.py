import sys,json,os,subprocess; sys.path.insert(0,'.'); from el import post, log_usage
S={
"arrival":("Temporal arrival: a soft reverse whoosh resolving into a shimmering high tone and a gentle low thump, sci-fi, no music",4),
"helix_city":("Futuristic city at dawn from a high window, distant automated traffic hum, soft electronic chimes, gentle wind, no voices, no music",12),
"helix_powerdown":("Huge server hall powering down: electrical hum winding down into silence, relays clicking off one by one, no music",7),
"vita_lab":("Sterile biotech laboratory ambience, soft refrigeration hum, quiet medical monitor beeps, faint liquid bubbling, no voices, no music",12),
"vita_heartbeat":("Slow steady heartbeat monitor beeping in a quiet empty laboratory, then slowly fading out, no music",8),
"nova_reactor":("Enormous energy reactor deep resonant hum with a faint repeating electronic signal pulse buried in static interference, no music",12),
"nova_signal":("Eerie distorted radio signal emerging from static noise, a repeating pulsed pattern, sci-fi, no voices, no music",8),
"civitas_crowd":("Muffled city crowd murmur slowly fading away into a quiet cold electronic data hum, no music",12),
"civitas_data":("Ominous digital data stream, rapid computer processing chatter and clicks building up, then an abrupt stop, no music",6),
"meridian_facility":("Vast hidden underground facility, deep low drone, distant metal resonances, cold ventilation air, no voices, no music",12),
"finale_alert":("Sci-fi alert: a soft repeating warning tone with glitching corrupted digital signal interference, tense, no music",6),
"teaser_morning":("Quiet early morning outside a university building, birdsong, distant city traffic, calm and ordinary, no music, no voices",10),
"teaser_machine":("Small laboratory machine switching on for the first time: a click, a soft electrical hum rising, faint whirring, no music",5),
}
meta=json.load(open('sfx/meta.json'))
for k,(p,d) in S.items():
    if os.path.exists(f'sfx/{k}.wav'): continue
    r=post('/v1/sound-generation',{"text":p,"duration_seconds":d,"prompt_influence":0.5},params={"output_format":"pcm_48000"},raw=True)
    cost=r.headers.get('character-cost'); log_usage('sfx',float(cost or 0),{"key":k,"chars":0})
    open(f'sfx/{k}.pcm','wb').write(r.content)
    subprocess.run(['ffmpeg','-v','error','-y','-f','s16le','-ar','48000','-ac','2','-i',f'sfx/{k}.pcm',f'sfx/{k}.wav'],check=True)
    meta[k]={"prompt":p,"duration_seconds":float(d),"prompt_influence":0.5,"output_format":"pcm_48000","character_cost":cost}
    json.dump(meta,open('sfx/meta.json','w'),indent=1); print(k,cost,flush=True)
