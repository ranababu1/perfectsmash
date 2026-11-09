"""Build the manifest fragment, the cue sheet (Markdown + JSON) and the compact QC report from the
per-file QC records written by produce_music.py / produce_sfx.py. Lists only files that exist."""
import os, json, glob, datetime
REPO = '/workspace/tfj-audio'
A = f'{REPO}/generated_assets/audio'
TODAY = datetime.date(2026, 11, 10).isoformat()
SOURCE_MUS = ('Original algorithmic composition produced for the owner by the audio stream: composed and rendered as code with the '
              'tfjaudio Python synthesis engine (generated_assets/audio/source/, cue builder {b}), mixed and mastered on the box on {d}; '
              'no third-party samples, no AI music service')
SOURCE_SFX = ('Original sound design produced for the owner by the audio stream: synthesised as code with the tfjaudio engine '
              '(generated_assets/audio/source/, {g}), rendered on {d}; no recordings, no third-party samples, no AI audio service')
RIGHTS = 'original algorithmic composition produced for the owner; no third-party samples; owner holds all rights (pending owner review)'
RIGHTS_SFX = 'original synthesised sound design produced for the owner; no third-party samples or recordings; owner holds all rights (pending owner review)'
PROPOSED_CUE = {'GAMEPLAY-PREP': '{c}_prep', 'CRITICAL_LAYER-01': '{c}_critical', 'THEME-01': '{c}_theme', 'TRANSITION-STINGER': '{c}_transition'}
GAM_PROPOSED = {'GAM-MUS-MAIN_THEME-01': 'title', 'GAM-MUS-TEASER-01': 'teaser', 'GAM-MUS-TRANSITION-TIMELINE_SHIFT': 'timeline_shift',
                'GAM-MUS-VICTORY-MISSION': 'mission_success', 'GAM-MUS-DEFEAT-MISSION': 'mission_fail', 'GAM-MUS-VICTORY-CHAPTER': 'chapter_complete'}


def music_entries():
    E, C = [], []
    for f in sorted(glob.glob('/workspace/tfj-scratch/qc/*.json')):
        d = json.load(open(f))
        if not os.path.exists(f"{REPO}/{d['path']}"):
            continue
        notes = [f"BPM {d['bpm']}, key {d['key']}, mood: {d['mood']}.", f"Structure: {d['intro_outro']}."]
        if d.get('loop'):
            notes.append(f"Loop {d['loop_start_samples']}-{d['loop_end_samples']} samples at 44.1 kHz (loop_offset {d['loop_offset_seconds']} s); "
                         f"Seam: wrap error {d['seam']['wrap_error_db']} dB vs {d['seam'].get('tile_boundary_error_db')} dB codec error at an internal boundary of the same material, HF delta {d['seam']['wrap_hf_delta_db']} dB (no click).")
        notes.append(f"Integrated {d['lufs_i']} LUFS, true peak {d['true_peak_dbtp']} dBTP, measured on the delivered file. Master 48 kHz 24-bit FLAC (box only).")
        for k in ('end_card_s', 'timeline_shift_hit_s', 'signal_returns_s', 'reveal_2041_s', 'final_hit_s', 'title_hit_s'):
            if k in d:
                notes.append(f"{k} = {d[k]}")
        if 'CRITICAL_LAYER' in d['id']:
            notes.append('Play sample-aligned on top of the chapter GAMEPLAY-TENSION or COMBAT-01 loop (same length) and lower that bed by 3 dB while the layer is up: the pair then measures about -16 LUFS and at most -1.7 dBTP (qc_extra.py).')
        prop = None
        if not d.get('music_cue'):
            tail = d['id'].split('-MUS-')[1]
            if tail in PROPOSED_CUE and d.get('chapter'):
                prop = PROPOSED_CUE[tail].format(c=d['manifest_chapter'])
            elif d['id'] in GAM_PROPOSED:
                prop = GAM_PROPOSED[d['id']]
            if prop:
                notes.append(f"Proposed music_cue (not in contract v1.3 yet): {prop}.")
        used = f"MusicDirector cue {d['music_cue']}" if d.get('music_cue') else (f"MusicDirector (proposed cue {prop})" if prop else 'MusicDirector')
        e = dict(id=d['id'], path=d['path'], category='music', render_type='audio', format='ogg',
                 purpose=d['use'], source=SOURCE_MUS.format(b='.'.join(d.get('build_ref', [])) or d.get('legacy_working_id'), d=TODAY),
                 rights_status=RIGHTS, approval_status='pending_review', used_by=used,
                 chapter=d['manifest_chapter'], duration_seconds=d['seconds'], loop=bool(d.get('loop')), bus='Music',
                 sample_rate=d['sample_rate'], channels=d['channels'], loudness_lufs=d['lufs_i'],
                 master_path=d['master'].replace('.flac', '.flac'), notes=' '.join(notes))
        if d.get('loop') and d['loop_offset_seconds']:
            e['loop_offset_seconds'] = d['loop_offset_seconds']
        if d.get('music_cue'):
            e['music_cue'] = d['music_cue']
        if d.get('levels'):
            a, _, b = str(d['levels']).partition('-')
            e['levels'] = list(range(int(a), int(b or a) + 1))
        E.append(e)
        C.append(dict(id=d['id'], path=d['path'], kind=d['kind'], use=d['use'], chapter=d['manifest_chapter'], duration_seconds=d['seconds'],
                      bpm=d['bpm'], key=d['key'], mood=d['mood'], intro_outro=d['intro_outro'], loop=bool(d.get('loop')),
                      loop_start_samples=d.get('loop_start_samples'), loop_end_samples=d.get('loop_end_samples'), loop_offset_seconds=d.get('loop_offset_seconds'),
                      master_loop_start_samples=d.get('master_loop_start_samples'), master_loop_end_samples=d.get('master_loop_end_samples'),
                      format='Ogg Vorbis q6', sample_rate=d['sample_rate'], channels=d['channels'], lufs_integrated=d['lufs_i'], true_peak_dbtp=d['true_peak_dbtp'],
                      sample_peak_dbfs=d['sample_peak_dbfs'], clipped_samples=d['clipped_samples'], seam=d.get('seam'), music_cue=d.get('music_cue'),
                      proposed_music_cue=prop, bytes=d['bytes'], master_path=d['master'], master_format='FLAC 48 kHz 24-bit',
                      markers={k: d[k] for k in d if k.endswith('_s') and isinstance(d[k], (int, float))}, rights=RIGHTS))
    return E, C


def sfx_entries():
    E, C = [], []
    for f in sorted(glob.glob('/workspace/tfj-scratch/qc_sfx/*.json')):
        d = json.load(open(f))
        if not os.path.exists(f"{REPO}/{d['file']}"):
            continue
        amb = bool(d.get('ambience'))
        cat = 'audio'
        notes = [f"{d['description']}. Variation {d['variation']} of {d['variations']}" + (' (pick at random).' if d['variations'] > 1 else '.')]
        if amb:
            notes.append(f"Integrated {d['lufs_i']} LUFS (target -24), true peak {d['true_peak_dbtp']} dBTP.")
        else:
            notes.append(f"Momentary max {d['momentary_max_lufs']} LUFS-M (family {d['family']}), true peak {d['true_peak_dbtp']} dBTP, sample peak {d['sample_peak_dbfs']} dBFS.")
        if d.get('loop'):
            notes.append(f"Seamless loop 0-{d['loop_end_samples']} samples at 44.1 kHz; wrap error {d['seam']['wrap_error_db']} dB vs codec error {d['seam']['mid_error_db']} dB, HF delta {d['seam']['wrap_hf_delta_db']} dB.")
        notes.append('Master 48 kHz 24-bit WAV (box only).')
        used = (f"AudioService sound_id {d['sound_id']}" if d.get('sound_id') else
                f"ambience_cue {d['ambience_cue']}" if amb else 'AudioService (no contract sound_id yet; animation or layer event)')
        e = dict(id=d['id'], path=d['file'], category=cat, render_type='audio', format=d['ext'],
                 purpose=d['use'], source=SOURCE_SFX.format(g=d['generator'], d=TODAY), rights_status=RIGHTS_SFX,
                 approval_status='pending_review', used_by=used, chapter=d['manifest_chapter'], duration_seconds=d['seconds'],
                 loop=bool(d.get('loop')), bus=d['bus'], sample_rate=d['sample_rate'], channels=d['channels'],
                 loudness_lufs=(round(d['lufs_i'] - 3.01, 2) if d['channels'] == 1 else d['lufs_i']), master_path=d['master'], notes=' '.join(notes))
        if d['channels'] == 1:
            e['notes'] += f" loudness_lufs is the file measured as one channel (BS.1770, as ffmpeg ebur128 reports mono); played centred on two speakers it measures {d['lufs_i']} LUFS integrated, which is the value the family targets use."
        if d.get('sound_id'):
            e['sound_id'] = d['sound_id']
        if amb:
            e['ambience_cue'] = d['ambience_cue']
        E.append(e)
        C.append(dict(id=d['id'], path=d['file'], group=d['base'], variation=d['variation'], variations=d['variations'], use=d['use'],
                      description=d['description'], chapter=d['manifest_chapter'], duration_seconds=d['seconds'], loop=bool(d.get('loop')),
                      loop_end_samples=d.get('loop_end_samples'), format=d['format'], sample_rate=d['sample_rate'], channels=d['channels'],
                      bus=d['bus'], sound_id=d.get('sound_id'), ambience_cue=d.get('ambience_cue'), family=d['family'],
                      lufs_integrated=d['lufs_i'], momentary_max_lufs=d['momentary_max_lufs'], true_peak_dbtp=d['true_peak_dbtp'],
                      sample_peak_dbfs=d['sample_peak_dbfs'], clipped_samples=d['clipped_samples'], dc_offset=d['dc_offset'],
                      lead_silence_ms=d['lead_silence_ms'], tail_silence_ms=d['tail_silence_ms'], seam=d.get('seam'),
                      bytes=d['bytes'], master_path=d['master'], generator=d['generator'], rights=RIGHTS_SFX))
    return E, C


def fmt_t(s):
    m, x = divmod(s, 60)
    return f'{int(m)}:{x:05.2f}'


def main():
    import sys
    me, mc = ([], []) if '--sfx-only' in sys.argv else music_entries()
    pre = [a.split('=', 1)[1].split(',') for a in sys.argv if a.startswith('--music-prefix=')]
    if pre:
        keep = lambda i: any(i.startswith(p + '-') for p in pre[0])
        me = [e for e in me if keep(e['id'])]
        mc = [c for c in mc if keep(c['id'])]
    se, sc = sfx_entries()
    os.makedirs(f'{REPO}/generated_assets/manifest_parts', exist_ok=True)
    json.dump({'stream': 'audio', 'updated': TODAY, 'entries': me + se}, open(f'{REPO}/generated_assets/manifest_parts/audio.json', 'w'), indent=1, ensure_ascii=False)
    extra = json.load(open('/workspace/tfj-scratch/qc_extra.json')) if os.path.exists('/workspace/tfj-scratch/qc_extra.json') and mc else {}
    json.dump({'updated': TODAY, 'rights': RIGHTS, 'stem_sums': extra.get('stems', {}), 'music': mc, 'sfx_and_ambience': sc}, open(f'{A}/cue_sheet.json', 'w'), indent=1, ensure_ascii=False)
    L = ['# Temporal: First Jump - audio cue sheet', '',
         f'Updated {TODAY}. Generated by `generated_assets/audio/source/build_docs.py` from the QC records of the delivered files. '
         'All loudness and peak values are measured on the delivered 44.1 kHz files (Ogg decoded). Loop points are in samples at 44.1 kHz; '
         'the 48 kHz master loop points are in `cue_sheet.json`.', '',
         f'Rights: {RIGHTS}.', '', '## Music', '',
         '| id | use | duration | BPM | key | mood | loop start-end (samples) | intro / outro | format | rate / ch | LUFS | dBTP |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for c in mc:
        lp = f"{c['loop_start_samples']}-{c['loop_end_samples']}" if c['loop'] else 'one-shot'
        L.append(f"| `{c['id']}` | {c['use']} | {fmt_t(c['duration_seconds'])} | {c['bpm']} | {c['key']} | {c['mood']} | {lp} | {c['intro_outro']} | Ogg Vorbis q6 | {c['sample_rate']} / {c['channels']} | {c['lufs_integrated']} | {c['true_peak_dbtp']} |")
    L += ['', '## Sound effects and ambience', '',
          'One row per sound group; variations share the group name with a `-01`, `-02` ... suffix and are picked at random.', '',
          '| group | files | use | duration (s) | format | ch | bus | sound_id / ambience_cue | LUFS-M max (range) | LUFS-I | dBTP max |', '|---|---|---|---|---|---|---|---|---|---|---|']
    groups = {}
    for c in sc:
        groups.setdefault(c['group'], []).append(c)
    for g, cs in groups.items():
        c0 = cs[0]
        durs = [c['duration_seconds'] for c in cs]
        mm = [c['momentary_max_lufs'] for c in cs]
        li = [c['lufs_integrated'] for c in cs]
        hook = c0['sound_id'] or c0['ambience_cue'] or '-'
        L.append(f"| `{g}` | {len(cs)} | {c0['use']} | {min(durs):.2f}-{max(durs):.2f} | {c0['format'].split('_')[0].upper()} | {c0['channels']} | {c0['bus']} | {hook} | "
                 f"{max(mm):.1f} ({min(mm):.1f} to {max(mm):.1f}) | {sum(li) / len(li):.1f} | {max(c['true_peak_dbtp'] for c in cs):.2f} |")
    open(f'{A}/CUE_SHEET.md', 'w').write('\n'.join(L) + '\n')
    print('music', len(me), 'sfx+amb', len(se))


if __name__ == '__main__':
    main()
