#!/usr/bin/env python3
"""Build the narration package for one or more cinematics, end to end (box paths via env).

  package_build.py SEQ [SEQ ...]
steps per SEQ: master picked takes (master_vo.py, Vorbis q6, true-peak retry) -> voiced timeline + plan
(cine_build.py) -> music bed (cine_beds.py, tfjaudio venv) -> SFX + ducking + mix (mix_cine.py plan) ->
encode bed (Vorbis q5) and mix reference (Vorbis q5 + MP3 192k) -> place in the repo -> FLAC masters,
alternate takes as FLAC -> measurements to work/cine/SEQ/report.json.
"""
import json, os, re, subprocess, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cine_build as CB
EL = CB.EL
REPO = os.environ.get('TFJ_REPO', '/workspace/tfj-narration')
MASTERS = os.environ.get('TFJ_MASTERS', '/workspace/tfj-masters/audio')
PY_TFJ = os.environ.get('TFJ_PY_TFJ', '/workspace/tfj-ui-vfx-venv/bin/python')
PY_CV = os.environ.get('TFJ_PY_CV', '/workspace/tfj-narration-tts/cvenv/bin/python')


def run(*a, **k):
    return subprocess.run(list(a), check=True, capture_output=True, text=True, **k).stdout


def meas(p):
    o = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    f = json.loads(run('ffprobe', '-v', 'error', '-show_entries', 'format=duration,bit_rate,size:stream=sample_rate,channels', '-of', 'json', p))
    return {'lufs': float(re.findall(r'I:\s+(-?[\d.]+) LUFS', o)[-1]), 'tp': float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', o)[-1]),
            'lra': float(re.findall(r'LRA:\s+(-?[\d.]+) LU', o)[-1]), 'seconds': round(float(f['format']['duration']), 3),
            'kbps': int(f['format']['bit_rate']) // 1000, 'bytes': int(f['format']['size']),
            'sr': int(f['streams'][0]['sample_rate']), 'ch': f['streams'][0]['channels']}


def picks():
    p = json.load(open(os.path.join(EL, 'picks.json'))); p.update(json.load(open(os.path.join(EL, 'picks_full.json')))); return p


def master_lines(seq):
    S = CB.seqs()[seq]; P = picks(); p, folder, name, kind, ch = CB.SEQ[seq]; rep = []
    for i, sl in enumerate(S['slides'], 1):
        key = f'{seq}_{i:02d}'; take = P[key]; base = CB.vo_base(seq, i)
        stem = os.path.join(EL, 'stems', base); src = os.path.join(EL, 'takes', f'{key}_{take}.wav')
        if not os.path.exists(stem + '.master.wav') or json.load(open(os.path.join(EL, 'stems', 'master_log.json'))).get(base, {}).get('take') != take:
            for tp in ('-2.0', '-2.6', '-3.2'):
                info = json.loads(run(PY_CV, os.path.join(HERE, 'master_vo.py'), sl['speaker'], src, stem, '--q', '6', '--tp', tp))
                if meas(stem + '.ogg')['tp'] <= -1.6: break
            log = json.load(open(os.path.join(EL, 'stems', 'master_log.json')))
            log[base] = {'take': take, 'role': sl['speaker'], **info}; json.dump(log, open(os.path.join(EL, 'stems', 'master_log.json'), 'w'), indent=1)
        dst = os.path.join(REPO, 'generated_assets/audio/voice', folder); os.makedirs(dst, exist_ok=True)
        for q in ('6', '5.5', '5', '6.5', '7'):   # keep the 80-96 kbps contract band
            run('ffmpeg', '-v', 'error', '-y', '-i', stem + '.master.wav', '-c:a', 'libvorbis', '-q:a', q, '-map_metadata', '-1', stem + '.ogg')
            k = meas(stem + '.ogg')
            if 80 <= k['kbps'] <= 96 and k['tp'] <= -1.5: break
        shutil.copy(stem + '.ogg', os.path.join(dst, base + '.ogg'))
        md = os.path.join(MASTERS, 'voice', folder); os.makedirs(md, exist_ok=True)
        run('ffmpeg', '-v', 'error', '-y', '-i', stem + '.master.wav', '-c:a', 'flac', os.path.join(md, base + '.flac'))
        td = os.path.join(MASTERS, 'voice', 'takes', seq); os.makedirs(td, exist_ok=True)
        for s in range(1, 9):
            t = os.path.join(EL, 'takes', f'{key}_s{s}.wav')
            if os.path.exists(t) and not os.path.exists(os.path.join(td, f'{base}_take_s{s}.flac')):
                run('ffmpeg', '-v', 'error', '-y', '-i', t, '-c:a', 'flac', os.path.join(td, f'{base}_take_s{s}.flac'))
        rep.append({'base': base, 'take': take, **meas(os.path.join(dst, base + '.ogg'))})
    return rep


def build(seq):
    p, folder, name, kind, ch = CB.SEQ[seq]
    rep = {'seq': seq, 'voice': master_lines(seq)}
    if seq == 'opening':
        return rep
    out = os.path.join(EL, 'cine', seq)
    print(run(PY_CV, os.path.join(HERE, 'cine_build.py'), 'timeline', seq).strip()[:300], flush=True)
    print(run(PY_TFJ, os.path.join(HERE, 'cine_beds.py'), kind, ch, os.path.join(out, 'timeline.json'), os.path.join(out, 'bed48.wav')).strip(), flush=True)
    mixr = json.loads(run(PY_CV, os.path.join(HERE, 'mix_cine.py'), 'plan', '--plan', os.path.join(out, 'plan.json'), '--out', out))
    cd = os.path.join(REPO, 'generated_assets/audio/music/cinematic'); md = os.path.join(MASTERS, 'music', 'cinematic')
    os.makedirs(cd, exist_ok=True); os.makedirs(md, exist_ok=True)
    bb, mb = CB.bed_base(seq), CB.mix_base(seq)
    for src, base in ((os.path.join(out, seq + '_bed.wav'), bb), (os.path.join(out, seq + '_mix.wav'), mb)):
        run('ffmpeg', '-v', 'error', '-y', '-i', src, '-c:a', 'libvorbis', '-q:a', '5', '-map_metadata', '-1', os.path.join(cd, base + '.ogg'))
        run('ffmpeg', '-v', 'error', '-y', '-i', src, '-c:a', 'flac', '-sample_fmt', 's32', os.path.join(md, base + '.flac'))
    run('ffmpeg', '-v', 'error', '-y', '-i', os.path.join(md, mb + '.flac'), '-c:a', 'libmp3lame', '-b:a', '192k', os.path.join(cd, mb + '.mp3'))
    os.makedirs(os.path.join(EL, 'refs'), exist_ok=True); shutil.copy(os.path.join(cd, mb + '.mp3'), os.path.join(EL, 'refs', mb + '.mp3'))
    shutil.copy(os.path.join(out, seq + '_duck_env.json'), os.path.join(cd, bb + '.duck_env.json'))
    rep.update({'mix': mixr, 'bed_file': meas(os.path.join(cd, bb + '.ogg')), 'mix_ogg': meas(os.path.join(cd, mb + '.ogg')), 'mix_mp3': meas(os.path.join(cd, mb + '.mp3'))})
    json.dump(rep, open(os.path.join(out, 'report.json'), 'w'), indent=1)
    return rep


if __name__ == '__main__':
    for seq in sys.argv[1:]:
        r = build(seq)
        print(seq, json.dumps({k: v for k, v in r.items() if k != 'voice'})[:600], flush=True)
        for v in r['voice']: print('  ', v['base'], v['take'], v['seconds'], v['lufs'], v['tp'], v['kbps'], flush=True)
