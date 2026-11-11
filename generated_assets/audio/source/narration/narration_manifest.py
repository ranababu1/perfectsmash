#!/usr/bin/env python3
"""Add/refresh manifest_parts/narration.json entries (voice stems, beds, mix references) for built cinematics.
usage: narration_manifest.py SEQ [SEQ ...]"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import cine_build as CB
from package_build import meas, picks, REPO, EL, MASTERS
TOS = 'https://elevenlabs.io/terms-of-use'
RIGHTS_VO = ("ElevenLabs output generated under Imran's paid ElevenLabs plan (Creator tier, inferred from the API: 44.1 kHz MP3 192 kbps allowed, 44.1 kHz PCM refused); "
             "commercially usable per provider terms (" + TOS + ", paid plans include a commercial licence and the user owns the output; Prohibited Use Policy https://elevenlabs.io/use-policy forbids using output to train models); "
             "voice designed with ElevenLabs Voice Design for this project (no cloning, no library voice, no real person's voice). Not legally cleared.")
RIGHTS_MUS = ("Music: original algorithmic composition rendered with our tfjaudio engine (no third-party samples, no AI music service). "
              "Sound effects layered in: ElevenLabs Sound Effects output under the same paid plan, commercially usable per provider terms (" + TOS + "). Not legally cleared.")
VOICES = {'narrator': ('TFJ Narrator (Temporal First Jump)', 'ekSI8bXMs4l0ajdl4bMT'), 'control': ('TFJ Control (Temporal First Jump)', 'RyGrFtWwuk4TeI35VwiE')}
SET = {'narrator': {'stability': 0.4, 'similarity_boost': 0.8}, 'control': {'stability': 0.5, 'similarity_boost': 0.8}}
CHAP = {'helix': 'helix', 'vita': 'vita', 'nova_grid': 'nova_grid', 'civitas': 'civitas', 'meridian': 'meridian'}


def entries(seq):
    S = CB.seqs()[seq]; P = picks(); p, folder, name, kind, ch = CB.SEQ[seq]
    chapter = CHAP.get(folder, 'shared'); out = []
    ev = {**json.load(open(os.path.join(EL, 'eval_full.json'))), **json.load(open(os.path.join(EL, 'eval_takes.json')))}
    en = json.load(open(os.path.join(EL, 'energy_full.json'))) if os.path.exists(os.path.join(EL, 'energy_full.json')) else {}
    sfx = json.load(open(os.path.join(EL, 'sfx', 'meta.json')))
    tl = json.load(open(os.path.join(EL, 'cine', seq, 'timeline.json')))
    plan = json.load(open(os.path.join(EL, 'cine', seq, 'plan.json')))
    for i, sl in enumerate(S['slides'], 1):
        base = CB.vo_base(seq, i); key = f'{seq}_{i:02d}'; take = P[key]; role = sl['speaker']
        path = f'generated_assets/audio/voice/{folder}/{base}.ogg'; m = meas(os.path.join(REPO, path))
        e = ev.get(f'takes/{key}_{take}.wav', {}); g = en.get(f'takes/{key}_{take}.wav', {})
        it = tl['items'][i - 1]
        out.append({'id': CB.asset_id(base), 'path': path, 'category': 'audio', 'render_type': 'audio', 'format': 'ogg',
                    'purpose': f'Narration: {seq} ("{S["title"]}") slide {i} ({role}), verbatim subtitle text from data/cinematics.json.',
                    'source': (f"ElevenLabs text-to-speech, model eleven_v4 with audio tags, voice '{VOICES[role][0]}' voice_id {VOICES[role][1]} (Voice Design), "
                               f"voice_settings {json.dumps(SET[role])}, seed {take[1:]} (take {take} of 5), previous_text/next_text = neighbouring slides, output pcm_48000; generated 2026-11-12 IST. "
                               "Tagged input in generated_assets/audio/source/narration/elevenlabs/direction.json (spoken words verbatim; years and AURA/VITA written as words for the model only). "
                               "Mastered by generated_assets/audio/source/narration/master_vo.py (soxr 44.1 kHz, role EQ/compression, two-pass loudnorm -18 LUFS), Vorbis."),
                    'rights_status': RIGHTS_VO, 'approval_status': 'pending_review',
                    'used_by': f'Not wired yet. Intended for CinematicCatalog slide voice: {seq} slide index {i - 1} (see docs/narration/CODING_AGENT_NARRATION_GUIDE.md).',
                    'chapter': chapter, 'duration_seconds': m['seconds'], 'sample_rate': m['sr'], 'channels': m['ch'], 'loudness_lufs': m['lufs'], 'bus': 'Voice',
                    'master_path': f'{MASTERS}/voice/{folder}/{base}.flac',
                    'provider': 'ElevenLabs', 'model_id': 'eleven_v4', 'voice_id': VOICES[role][1], 'voice_settings': SET[role], 'seed': int(take[1:]), 'terms_url': TOS,
                    'notes': (f"Selected automatically from 5 takes (alternates kept as FLAC in {MASTERS}/voice/takes/{seq}/): ASR exact match (two decodes), no clipping, "
                              f"UTMOS {e.get('mos')}, pace {g.get('wpm_e', e.get('wpm'))} wpm, longest pause {g.get('max_pause_s', e.get('maxgap'))} s. "
                              f"Measured on the delivered file: {m['lufs']} LUFS, true peak {m['tp']} dBTP, LRA {m['lra']} LU, {m['kbps']} kbps mono. "
                              f"Default timeline: voice starts at {it['start_s']} s of the mix reference. Not a listening test.")})
    cd = 'generated_assets/audio/music/cinematic/'
    used = ', '.join(f"{x['name']} ({sfx[x['name']]['prompt'][:60]}...)" for x in plan['sfx'])
    for base, fmt, isbed in ((CB.bed_base(seq), 'ogg', True), (CB.mix_base(seq), 'ogg', False), (CB.mix_base(seq), 'mp3', False)):
        path = cd + base + '.' + fmt; m = meas(os.path.join(REPO, path))
        aid = CB.asset_id(base) if not isbed else '-'.join([p.upper(), 'MUS', f'CINE_{name.upper()}', 'BED'])
        if not isbed: aid = '-'.join([p.upper(), 'CINE', name.upper(), 'MIX_REF']) + ('-MP3' if fmt == 'mp3' else '')
        out.append({'id': aid, 'path': path, 'category': 'music', 'render_type': 'audio', 'format': fmt,
                    'purpose': (f'Music bed for the voiced {seq} cinematic, un-ducked (duck under voice with {base}.duck_env.json or about -9 dB).' if isbed
                                else f'Full mixed reference of the voiced {seq} cinematic (voice + ducked bed + SFX). Review reference only.' + (' MP3 listening copy.' if fmt == 'mp3' else '')),
                    'source': (f'Re-arrangement of our own original cinematic cue for {seq} (tfjaudio cues2 cin_{kind}, chapter {ch}) re-timed to the voiced timeline by '
                               f'generated_assets/audio/source/narration/cine_beds.py; ElevenLabs Sound Effects layered by mix_cine.py: {used or "none"}.' if isbed else
                               'mix_cine.py plan: voice stems at the default timeline, bed ducked 9 dB by a voice-activity envelope (look-ahead 0.15 s, attack 0.12 s, hold 0.25 s, release 0.6 s), normalised to -16 LUFS.'),
                    'rights_status': RIGHTS_MUS if isbed else RIGHTS_VO + ' ' + RIGHTS_MUS, 'approval_status': 'pending_review',
                    'used_by': 'Not wired yet (cinematic music bed).' if isbed else 'Not used by the game (review reference).',
                    'chapter': chapter, 'duration_seconds': m['seconds'], 'sample_rate': m['sr'], 'channels': m['ch'], 'loudness_lufs': m['lufs'],
                    'bus': 'Music' if isbed else 'Master', 'loop': False, 'master_path': f'{MASTERS}/music/cinematic/{base}.flac', 'terms_url': TOS,
                    'notes': f"Measured on the delivered file: {m['lufs']} LUFS, true peak {m['tp']} dBTP, LRA {m['lra']} LU, {m['kbps']} kbps. Timeline: slide starts {tl['slide_starts_s']} s, end card {tl['end_card_s']} s."})
    return out


if __name__ == '__main__':
    frag = os.path.join(REPO, 'generated_assets/manifest_parts/narration.json'); d = json.load(open(frag))
    new = [e for seq in sys.argv[1:] for e in entries(seq)]; ids = {e['id'] for e in new}
    d['entries'] = [e for e in d['entries'] if e['id'] not in ids] + new; d['updated'] = '2026-11-12'
    json.dump(d, open(frag, 'w'), indent=1, ensure_ascii=False); open(frag, 'a').write('\n')
    for e in new: print(e['id'], e['duration_seconds'], e['loudness_lufs'])
