"""Take selection for the full package: ASR exact match (errs_min of two decodes = 0), no clipping,
pace 95-175 wpm over the speech span, longest pause <= 1.5 s, then highest UTMOS."""
import json, collections, sys
ev = json.load(open('eval_full.json')); asr = json.load(open('asr2_full.json')); en = json.load(open('energy_full.json'))
prefix = sys.argv[1].split(',') if len(sys.argv) > 1 else None
by = collections.defaultdict(list)
for k in asr:
    line = k.split('/')[1].rsplit('_s', 1)[0]
    if prefix and not any(line.startswith(p) for p in prefix): continue
    by[line].append(k)
picks = json.load(open('picks_full.json')) if len(sys.argv) > 2 else {}
sel = {}
for line in sorted(by):
    rows = [(k, ev[k]['mos'], asr[k]['errs_min'], ev[k]['clip'], en[k]['wpm_e'], en[k]['max_pause_s']) for k in sorted(by[line])]
    ok = [r for r in rows if r[2] == 0 and r[3] == 0 and 95 <= r[4] <= 175 and r[5] <= 1.5]
    if ok:
        b = max(ok, key=lambda r: r[1]); sel[line] = 's' + b[0].rsplit('_s', 1)[1][:-4]
        print(line, sel[line], 'mos', b[1], 'wpm', b[4], 'pause', b[5], '| passing', len(ok), '/', len(rows))
    else:
        print('NONE', line, [(r[0][-6:-4], r[1], r[2], r[4], r[5]) for r in rows])
json.dump(sel, open('picks_sel_tmp.json', 'w'), indent=1)
