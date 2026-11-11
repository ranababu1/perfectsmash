"""Verify delivered stems: ASR (word-timestamp decode of the master, cached by cine_build) must match the subtitle;
falls back to a chunked decode of the delivered ogg when the whole-file decode drops words."""
import sys, json, re
sys.path.insert(0, '/workspace/tfj-narration/generated_assets/audio/source/narration')
import cine_build as CB
src = open('asr2.py').read()
ns = {}; exec('import re\n' + open('evalv2.py').read()[open('evalv2.py').read().index('NUM='):open('evalv2.py').read().index('refs=json.load')], ns)
FIX = [(r'\bnov[aoi] ?grid\b', 'nova grid')]
def norm(s):
    s = s.lower()
    for a, b in FIX: s = re.sub(a, b, s)
    return ns['norm'](s)
S = CB.seqs(); out = {}
for seq in sys.argv[1:]:
    for i, sl in enumerate(S[seq]['slides'], 1):
        base = CB.vo_base(seq, i); wav = f'stems/{base}.master.wav'
        w = CB.words(wav); hyp = ' '.join(x['w'] for x in w)
        e = ns['wer'](norm(sl['subtitle']), norm(hyp))
        r = {'errs_word_timing_decode': e, 'hyp': hyp}
        if e:
            CB.words(wav)
            ogg = f'/workspace/tfj-narration/generated_assets/audio/voice/{CB.SEQ[seq][1]}/{base}.ogg'
            segs, _ = CB._asr.transcribe(ogg, beam_size=5, condition_on_previous_text=False) if CB._asr else (None, None)
            if CB._asr is None:
                from faster_whisper import WhisperModel; CB._asr = WhisperModel('medium.en', device='cpu', compute_type='int8')
                segs, _ = CB._asr.transcribe(ogg, beam_size=5, condition_on_previous_text=False)
            h2 = ' '.join(x.text for x in segs).strip(); e2 = ns['wer'](norm(sl['subtitle']), norm(h2))
            r.update({'errs_ogg_decode': e2, 'hyp_ogg': h2}); hyp = hyp + ' || ogg: ' + h2 + f' ({e2})'
        out[base] = r
        print(base, e, '' if e == 0 else hyp)
json.dump(out, open('verify_' + '_'.join(sys.argv[1:2]) + '.json', 'w'), indent=1)
