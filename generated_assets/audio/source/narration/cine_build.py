#!/usr/bin/env python3
"""Narration package orchestration: naming, voiced timelines and mix plans for every cinematic.

  cine_build.py timeline SEQ   -> work/cine/SEQ/timeline.json + plan.json (needs mastered stems)
Names follow ASSET_CONTRACT: <prefix>_vo_<intro|outro>_NN for chapter cinematics, gam_vo_<seq>_NN for
opening/finale/teaser_2041; beds <prefix>_mus_cine_<name>_bed, mixes <prefix>_cine_<name>_mix_ref.
Word times come from faster-whisper word timestamps on the mastered stems (used for subtitle sync
points and for musical hits); slide gaps are chosen per dramatic beat (GAPS below).
"""
import json, os, re, sys

EL = os.environ.get('TFJ_EL', '/workspace/tfj-narration-el')
CIN = os.environ.get('TFJ_CIN', '/workspace/tfj-narration-main/data/cinematics.json')
SEQ = {  # seq: (prefix, folder, short name, bed kind, tfjaudio chapter)
    'opening': ('gam', 'opening', 'opening', 'opening', 'meridian'),
    'ch01_intro': ('hlx', 'helix', 'intro', 'intro', 'helix'), 'ch01_outro': ('hlx', 'helix', 'outro', 'outro', 'helix'),
    'ch02_intro': ('vta', 'vita', 'intro', 'intro', 'vita'), 'ch02_outro': ('vta', 'vita', 'outro', 'outro', 'vita'),
    'ch03_intro': ('nvg', 'nova_grid', 'intro', 'intro', 'nova'), 'ch03_outro': ('nvg', 'nova_grid', 'outro', 'outro', 'nova'),
    'ch04_intro': ('cvt', 'civitas', 'intro', 'intro', 'civitas'), 'ch04_outro': ('cvt', 'civitas', 'outro', 'outro', 'civitas'),
    'ch05_intro': ('mrd', 'meridian', 'intro', 'intro', 'meridian'),
    'finale': ('gam', 'finale', 'finale', 'finale', 'meridian'), 'teaser_2041': ('gam', 'teaser_2041', 'teaser_2041', 'teaser', 'meridian'),
}
PRE = {'intro': 3.5, 'outro': 3.0, 'finale': 3.0, 'teaser': 3.0}
# extra gap (s) BEFORE slide n (1-based) for dramatic beats; default 2.0, speaker change 2.5
GAPS = {'finale': {3: 3.0, 4: 2.5, 5: 3.2, 6: 2.5, 7: 2.5}, 'teaser_2041': {2: 2.2, 3: 2.8, 4: 2.5}}
SFX = {  # seq: [(sfx, anchor, offset_s, lufs, fade_in, fade_out)]; anchor = 'sN' slide start, 'eN' slide end, 0 = start
    'ch01_intro': [('arrival', 0, 0.0, -24, 0, 0.5), ('helix_city', 0, 1.0, -33, 2.0, 3.0)],
    'ch01_outro': [('helix_powerdown', 0, 0.0, -24, 0, 2.0)],
    'ch02_intro': [('arrival', 0, 0.0, -24, 0, 0.5), ('vita_lab', 's2', -1.0, -33, 2.0, 3.0)],
    'ch02_outro': [('vita_heartbeat', 0, 0.2, -30, 1.0, 3.0)],
    'ch03_intro': [('arrival', 0, 0.0, -24, 0, 0.5), ('nova_reactor', 's2', -1.5, -32, 2.0, 3.0)],
    'ch03_outro': [('nova_signal', 's2', 0.0, -31, 2.0, 3.0)],
    'ch04_intro': [('arrival', 0, 0.0, -24, 0, 0.5), ('civitas_crowd', 0, 0.8, -32, 1.5, 3.0)],
    'ch04_outro': [('civitas_data', 'e2', -2.5, -29, 1.0, 1.0)],
    'ch05_intro': [('arrival', 0, 0.0, -24, 0, 0.5), ('meridian_facility', 0, 1.0, -32, 2.0, 3.0)],
    'finale': [('finale_alert', 's3', -1.2, -27, 0.2, 2.0)],
    'teaser_2041': [('teaser_morning', 0, 0.0, -32, 1.5, 3.0), ('teaser_machine', 's2', 2.4, -28, 0.1, 1.5), ('arrival', 's3', -1.0, -26, 0, 0.5)],
}


def seqs():
    return {s['id']: s for s in json.load(open(CIN))['sequences']}


def vo_base(seq, n):
    p, f, name, k, ch = SEQ[seq]
    return f'{p}_vo_{name}_{n:02d}'


def vo_id(seq, n):
    return vo_base(seq, n).upper().replace('_VO_', '-VO-').replace('TEASER_2041', 'TEASER_2041').replace('_', '-', 0)


def asset_id(base):
    parts = base.split('_')
    # <prefix>_vo_<name...>_NN -> PREFIX-VO-NAME-NN
    return '-'.join([parts[0].upper(), parts[1].upper(), '_'.join(parts[2:-1]).upper(), parts[-1]])


def bed_base(seq):
    p, f, name, k, ch = SEQ[seq]; return f'{p}_mus_cine_{name}_bed'


def mix_base(seq):
    p, f, name, k, ch = SEQ[seq]; return f'{p}_cine_{name}_mix_ref'


_asr = None
def words(wav):
    global _asr
    cache = wav + '.words.json'
    if os.path.exists(cache): return json.load(open(cache))
    if _asr is None:
        from faster_whisper import WhisperModel
        _asr = WhisperModel('medium.en', device='cpu', compute_type='int8')
    segs, _ = _asr.transcribe(wav, beam_size=5, word_timestamps=True, condition_on_previous_text=False)
    w = [{'w': x.word.strip(), 's': round(x.start, 3), 'e': round(x.end, 3)} for s in segs for x in s.words]
    json.dump(w, open(cache, 'w')); return w


def dur(wav):
    import soundfile as sf
    i = sf.info(wav); return i.frames / i.samplerate


def sentences(sub, w, d):
    """subtitle sentence sync points from word times (relative to stem start)."""
    sents = [x.strip() for x in re.split(r'(?<=[.!?:])\s+', sub) if x.strip()]
    out, wi = [], 0
    def n(s): return len(re.findall(r"[A-Za-z0-9']+", s.replace('-', ' ')))
    YR = re.compile(r'\b(20\d\d|21\d\d)\b')
    for st in sents:
        k = n(YR.sub(lambda m: 'x x x', st))
        if not w: break
        a = min(wi, len(w) - 1); b = min(len(w) - 1, wi + max(1, k) - 1)
        out.append({'text': st, 'start_s': w[a]['s'], 'end_s': w[b]['e']}); wi = b + 1
    if out:
        out[0]['start_s'] = min(out[0]['start_s'], 0.06); out[-1]['end_s'] = round(max(out[-1]['end_s'], d - 0.18), 3)
    return out


def timeline(seq):
    S = seqs()[seq]; p, f, name, kind, ch = SEQ[seq]
    sl = S['slides']; t = PRE.get(kind, 3.0); starts, ends, gaps, items = [], [], [], []
    for i, x in enumerate(sl, 1):
        if i > 1:
            g = GAPS.get(seq, {}).get(i, 2.5 if x['speaker'] != sl[i - 2]['speaker'] else 2.0)
            gaps.append([round(t, 3), round(t + g, 3)]); t += g
        wav = os.path.join(EL, 'stems', vo_base(seq, i) + '.master.wav')
        d = dur(wav); w = words(wav)
        starts.append(round(t, 3)); ends.append(round(t + d, 3))
        items.append({'slide': i, 'speaker': x['speaker'], 'wav': wav, 'start_s': round(t, 3), 'duration_s': round(d, 3), 'words': w,
                      'sentences': sentences(x['subtitle'], w, d)})
        t += d
    tl = {'seq': seq, 'kind': kind, 'chapter': ch, 'pre_roll_s': PRE.get(kind, 3.0), 'slide_starts_s': starts, 'slide_ends_s': ends, 'gaps': gaps}
    last = ends[-1]
    tl['end_card_s'] = round(last + (1.4 if kind == 'intro' else 1.2 if kind == 'outro' else 2.0), 3)
    if kind == 'outro':
        tl['turn_s'] = starts[1]; tl['shift_s'] = starts[-1]
    if kind == 'teaser':
        w4 = items[3]['words']; k = next(i for i, x in enumerate(w4) if x['w'].lower().startswith('season'))
        tl['hit_s'] = round(starts[3] + w4[k]['s'] - 0.12, 3); tl['end_card_s'] = tl['hit_s']
    tl['end_s'] = round(max(last, tl['end_card_s']) + 1.0, 3)
    tl['items'] = items
    return tl


def anchor(tl, a):
    if a == 0: return 0.0
    n = int(a[1:]) - 1
    return tl['slide_starts_s'][n] if a[0] == 's' else tl['slide_ends_s'][n]


if __name__ == '__main__':
    cmd, seq = sys.argv[1:3]
    out = os.path.join(EL, 'cine', seq); os.makedirs(out, exist_ok=True)
    tl = timeline(seq)
    json.dump(tl, open(os.path.join(out, 'timeline.json'), 'w'), indent=1)
    plan = {'bed': os.path.join(out, 'bed48.wav'), 'base': seq,
            'voices': [[it['wav'], it['start_s']] for it in tl['items']],
            'sfx': [{'name': n, 'path': os.path.join(EL, 'sfx', n + '.wav'), 'start_s': round(max(0.0, anchor(tl, a) + o), 3), 'lufs': l, 'fade_in': fi, 'fade_out': fo}
                    for n, a, o, l, fi, fo in SFX.get(seq, [])]}
    json.dump(plan, open(os.path.join(out, 'plan.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in tl.items() if k != 'items'}))
