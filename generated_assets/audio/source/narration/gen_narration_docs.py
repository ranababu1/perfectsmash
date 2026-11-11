#!/usr/bin/env python3
"""Write generated_assets/docs/narration/NARRATION_MANIFEST.json and FINAL_SCRIPT.md from the built package.
usage: gen_narration_docs.py   (reads work/cine/*/timeline.json, the opening timeline, picks, direction, measurements)"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import cine_build as CB
from package_build import meas, picks, REPO, EL
DOCS = os.path.join(REPO, 'generated_assets/docs/narration')
VOICES = {'narrator': ('TFJ Narrator (Temporal First Jump)', 'ekSI8bXMs4l0ajdl4bMT'), 'control': ('TFJ Control (Temporal First Jump)', 'RyGrFtWwuk4TeI35VwiE')}
SET = {'narrator': {'stability': 0.4, 'similarity_boost': 0.8}, 'control': {'stability': 0.5, 'similarity_boost': 0.8}}


def opening_tl():
    t = json.load(open(os.path.join(EL, 'timeline.json'))); items = []
    for i, st in enumerate(t['slide_starts_s'], 1):
        wav = os.path.join(EL, 'stems', CB.vo_base('opening', i) + '.master.wav')
        d = CB.dur(wav); w = CB.words(wav)
        sub = CB.seqs()['opening']['slides'][i - 1]['subtitle']
        items.append({'slide': i, 'start_s': st, 'duration_s': round(d, 3), 'sentences': CB.sentences(sub, w, d)})
    t['items'] = items; t['end_card_s'] = t['title_hit_s']; t['slide_ends_s'] = [round(a + b, 3) for a, b in zip(t['slide_starts_s'], t['slide_durations_s'])]
    return t


def main():
    S = CB.seqs(); P = picks(); D = json.load(open(os.path.join(EL, 'direction.json')))
    man = {'schema': 'tfj-narration-manifest/1', 'generated': '2026-11-12', 'source_text': 'data/cinematics.json (main c104c06), verbatim',
           'times': 'seconds; slide-relative times are from the start of the voice file; timeline times are from the start of the mix reference',
           'voice_bus': 'Voice (to add)', 'voice_loudness_lufs': -18.0, 'cinematics': []}
    md = ['# Final narration script — Temporal: First Jump', '',
          'Every line below is the verbatim subtitle from `data/cinematics.json` (main c104c06). The bracketed **direction** is the eleven_v4 audio-tag input; '
          'it is never shown on screen. Years and AURA/VITA were written as words for the model only. Durations are the delivered voice files.', '']
    total = 0.0
    for seq, s in S.items():
        p, folder, name, kind, ch = CB.SEQ[seq]
        tl = opening_tl() if seq == 'opening' else json.load(open(os.path.join(EL, 'cine', seq, 'timeline.json')))
        bed = 'gam_mus_cine_opening_bed' if seq == 'opening' else CB.bed_base(seq)
        mix = 'gam_cine_opening_mix_ref' if seq == 'opening' else CB.mix_base(seq)
        cd = 'generated_assets/audio/music/cinematic/'
        mixm = meas(os.path.join(REPO, cd + mix + '.ogg'))
        entry = {'cinematic_id': seq, 'title': s['title'], 'music_bed': cd + bed + '.ogg', 'duck_envelope': cd + bed + '.duck_env.json',
                 'mix_reference': [cd + mix + '.ogg', cd + mix + '.mp3'], 'mix_seconds': mixm['seconds'],
                 'timeline': {'pre_roll_s': tl.get('pre_roll_s'), 'end_card_s': tl.get('end_card_s'), 'gaps_s': tl.get('gaps') or tl.get('gaps_after_s')},
                 'slides': []}
        md += [f'## {seq} — {s["title"]}', '', f'Mix reference: `{cd}{mix}.mp3` ({mixm["seconds"]:.1f} s). Bed: `{cd}{bed}.ogg`.', '',
               '| # | Speaker | Text (verbatim) | Direction (tags) | Voice file | Duration |', '|---|---|---|---|---|---|']
        for i, sl in enumerate(s['slides'], 1):
            base = CB.vo_base(seq, i); path = f'generated_assets/audio/voice/{folder}/{base}.ogg'
            m = meas(os.path.join(REPO, path)); total += m['seconds']
            it = tl['items'][i - 1]; take = P[f'{seq}_{i:02d}']
            entry['slides'].append({'slide_index': i - 1, 'slide_number': i, 'speaker': sl['speaker'], 'text': sl['subtitle'], 'caption': sl.get('caption'),
                                    'file': path, 'asset_id': CB.asset_id(base), 'duration_s': m['seconds'], 'loudness_lufs': m['lufs'], 'true_peak_dbtp': m['tp'],
                                    'voice': {'name': VOICES[sl['speaker']][0], 'voice_id': VOICES[sl['speaker']][1], 'model_id': 'eleven_v4', 'settings': SET[sl['speaker']], 'seed': int(take[1:]), 'take': take},
                                    'direction': D[seq][str(i)],
                                    'subtitle_sync': {'start_s': it['sentences'][0]['start_s'] if it.get('sentences') else 0.06, 'end_s': it['sentences'][-1]['end_s'] if it.get('sentences') else round(m['seconds'] - 0.18, 3),
                                                      'sentences': it.get('sentences', [])},
                                    'timeline': {'voice_start_s': it['start_s'], 'voice_end_s': round(it['start_s'] + m['seconds'], 3)},
                                    'recommended_slide_seconds': round(m['seconds'] + 1.2, 2)})
            md.append(f'| {i} | {sl["speaker"]} | {sl["subtitle"]} | {re.sub(chr(10), " ", D[seq][str(i)])} | `{base}.ogg` | {m["seconds"]:.2f} s |')
        md.append('')
        man['cinematics'].append(entry)
    man['total_voice_seconds'] = round(total, 2)
    json.dump(man, open(os.path.join(DOCS, 'NARRATION_MANIFEST.json'), 'w'), indent=1, ensure_ascii=False)
    md.insert(4, f'Total voiced runtime: {total / 60:.1f} min across {sum(len(s["slides"]) for s in S.values())} lines in {len(S)} cinematics.\n')
    open(os.path.join(DOCS, 'FINAL_SCRIPT.md'), 'w').write('\n'.join(md) + '\n')
    print('voice seconds', round(total, 2))


if __name__ == '__main__':
    main()
