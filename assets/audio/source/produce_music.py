"""Build every music cue. Usage: python3 produce_music.py [cue_id_substring ...] [--jobs=N]"""
import sys, os, json, time, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool

KEYS = {'helix': 'D minor', 'vita': 'E minor (Lydian colour on bVI)', 'nova': 'C minor (Phrygian bII)',
        'civitas': 'B minor', 'meridian': 'D minor (Neapolitan bII)'}
ORDER = ['helix', 'vita', 'nova', 'civitas', 'meridian']
LEVELS = {'helix': '1-20', 'vita': '21-40', 'nova': '41-60', 'civitas': '61-80', 'meridian': '81-100'}
IDX = {c: i + 1 for i, c in enumerate(ORDER)}


def registry():
    from tfjaudio.chapters import CH
    R = []
    R.append(dict(id='mus_main_theme', kind='theme', use='Title / main theme; trailer and store video bed', bpm=84, key='D minor', mood='mysterious, resolute, cinematic; the Temporal motif in full',
                  intro_outro='Piano intro (motif), builds to tutti statement, F-major hope bridge, climax, unresolved piano outro ending on the second degree', loop=False, build=('cues2', 'main_theme', ())))
    R.append(dict(id='mus_menu_loop', kind='loop', use='Main menu, chapter select, settings', bpm=76, key='D minor', mood='calm, suspended, quietly hopeful',
                  intro_outro='Seamless loop from sample 0; no intro or outro (cross-fade in/out with MusicDirector)', loop=True, build=('cues2', 'menu_loop', ())))
    for ch in ORDER:
        d = CH[ch]
        lv = LEVELS[ch]
        R.append(dict(id=f'mus_{ch}_theme', kind='theme', chapter=ch, levels=lv, use=f'{d["title"]} chapter theme: chapter intro screen, chapter select preview, story archive', bpm=d['bpm'], key=KEYS[ch], mood=d['mood'],
                      intro_outro='Ambient intro, motif statement, development, peak, soft outro with natural tail', loop=False, build=('cues2', 'chapter_theme', (ch,))))
        R.append(dict(id=f'mus_{ch}_prep_loop', kind='loop', chapter=ch, levels=lv, use='Tactical preparation: mission briefing, aiming before the first shot, pause menu', bpm=d['bpm'], key=KEYS[ch], mood='sparse, focused, ' + d['mood'].split(';')[0],
                      intro_outro='Seamless loop from sample 0; same tempo, key and length as the tension and combat loops so it can be cross-faded in sync', loop=True, build=('cues', 'mission_loop', (ch, 1))))
        R.append(dict(id=f'mus_{ch}_tension_loop', kind='loop', chapter=ch, levels=lv, use='Standard mission bed (default gameplay intensity)', bpm=d['bpm'], key=KEYS[ch], mood=d['mood'],
                      intro_outro='Seamless loop from sample 0; synchronised with prep, combat and critical layer', loop=True, build=('cues', 'mission_loop', (ch, 2))))
        R.append(dict(id=f'mus_{ch}_combat_loop', kind='loop', chapter=ch, levels=lv, use='High-intensity destruction / chain-reaction phase', bpm=d['bpm'], key=KEYS[ch], mood='driving, forceful, ' + d['mood'].split(';')[0],
                      intro_outro='Seamless loop from sample 0; synchronised with prep, tension and critical layer', loop=True, build=('cues', 'mission_loop', (ch, 3))))
        R.append(dict(id=f'mus_{ch}_critical_layer', kind='layer', chapter=ch, levels=lv, use='Critical-asset engagement layer: add on top of the tension or combat loop while a critical target is exposed or damaged', bpm=d['bpm'], key=KEYS[ch], mood='urgent, alarm-tinged',
                      intro_outro='Stem: seamless loop, same length as the mission loops; play in sync (AudioStreamSynchronized) and fade in/out', loop=True, build=('cues2', 'critical_layer', (ch,))))
        R.append(dict(id=f'mus_{ch}_climax', kind='climax', chapter=ch, levels=lv, use=f'Mission climax / boss track for the chapter finale (level {lv.split("-")[1]}) and other hero missions', bpm=d['bpm'], key=KEYS[ch], mood='monumental, relentless',
                      intro_outro='8-bar build intro played once, then the 64-bar body loops from loop_offset to the end of the file', loop=True, build=('cues2', 'climax', (ch,))))
        R.append(dict(id=f'mus_cin_{ch}_intro', kind='cinematic', chapter=ch, levels=lv.split('-')[0], use=f'Chapter {IDX[ch]} introduction cinematic score (narrated stills)', bpm=d['bpm'], key=KEYS[ch], mood='expectant, briefing; leaves space for the Control voice',
                      intro_outro='Starts directly; end-card hit 8 beats before the end (see end_card_s) with natural tail', loop=False, build=('cues2', 'cin_intro', (ch, IDX[ch]))))
        R.append(dict(id=f'mus_cin_{ch}_outro', kind='cinematic', chapter=ch, levels=lv.split('-')[1], use=f'Chapter {IDX[ch]} ending cinematic score', bpm=72, key=KEYS[ch] + ' (opens in the relative major)', mood='relief turning to unease',
                      intro_outro='Hopeful opening, minor turn at beat 24, timeline-shift hit (see timeline_shift_hit_s), natural tail', loop=False, build=('cues2', 'cin_outro', (ch, IDX[ch]))))
        R.append(dict(id=f'mus_stinger_chapter_{ch}', kind='stinger', chapter=ch, use=f'Chapter {IDX[ch]} transition stinger / chapter reveal', bpm=d['bpm'], key=KEYS[ch], mood='decisive',
                      intro_outro='Motif head and hit; one-shot with tail', loop=False, build=('cues2', 'stinger', (ch,))))
    R.append(dict(id='mus_cin_opening', kind='cinematic', use='Opening cinematic "The Last Transmission" (7 narrated slides)', bpm=60, key='D minor', mood='desolate, intimate, building to resolve',
                  intro_outro='Slide starts at 0/12/24/36/47/58/70 s; countdown taiko at 74/75/76 s; title hit at 78 s; tail to the end', loop=False, build=('cues2', 'cin_opening', ())))
    R.append(dict(id='mus_cin_finale', kind='cinematic', levels='100', use='Level 100 finale "The Wrong Future"', bpm=66, key='D major turning to D minor', mood='apparent victory, dread, revelation',
                  intro_outro='Hope (0 s), signal returns (see signal_returns_s), 2041 reveal hit (reveal_2041_s), unresolved ending, final hit (final_hit_s)', loop=False, build=('cues2', 'cin_finale', ())))
    R.append(dict(id='mus_cin_expansion_teaser', kind='cinematic', use='Expansion teaser after the credits (NEXT COORDINATE: 2041)', bpm=92, key='G minor', mood='ominous anticipation',
                  intro_outro='Pulse intro, motif in a new key, hard hit at 31.3 s, single piano note tail', loop=False, build=('cues2', 'cin_teaser', ())))
    R.append(dict(id='mus_stinger_timeline_shift', kind='stinger', use='Generic timeline shift / time insertion transition', bpm=90, key='D minor', mood='fractured',
                  intro_outro='One-shot with tail', loop=False, build=('cues2', 'stinger_timeline_shift', ())))
    R.append(dict(id='mus_result_mission_success', kind='result', use='Mission success results screen', bpm=96, key='D major', mood='clean triumph',
                  intro_outro='One-shot; hope motif head, major chord ring-out', loop=False, build=('cues2', 'result_success', ())))
    R.append(dict(id='mus_result_mission_fail', kind='result', use='Mission failed results screen', bpm=72, key='D minor', mood='sinking, restrained',
                  intro_outro='One-shot; descending line and sub drop', loop=False, build=('cues2', 'result_fail', ())))
    R.append(dict(id='mus_result_chapter_complete', kind='result', use='Chapter complete screen', bpm=96, key='D major', mood='earned, expansive',
                  intro_outro='One-shot; tom pickup, full hope phrase, ring-out', loop=False, build=('cues2', 'result_chapter_complete', ())))
    R.append(dict(id='mus_credits', kind='credits', use='Ending / credits music', bpm=72, key='D minor (journeys through every chapter key)', mood='reflective, bittersweet, unresolved',
                  intro_outro='Piano solo opening, chapter cameos in order, convergence tutti, unresolved piano ending and natural tail', loop=False, build=('cues2', 'credits', ())))
    for c in R:
        _contract(c)
    return R


CODE = {'helix': 'HLX', 'vita': 'VTA', 'nova': 'NVG', 'civitas': 'CVT', 'meridian': 'MRD'}
CHKEY = {'helix': 'helix', 'vita': 'vita', 'nova': 'nova_grid', 'civitas': 'civitas', 'meridian': 'meridian'}
GAME = {'mus_main_theme': ('GAM-MUS-MAIN_THEME-01', None), 'mus_menu_loop': ('GAM-MUS-MENU-01', 'menu'),
        'mus_cin_opening': ('GAM-MUS-OPENING-01', 'cinematic'), 'mus_cin_finale': ('GAM-MUS-FINALE-01', 'ending'),
        'mus_cin_expansion_teaser': ('GAM-MUS-TEASER-01', None), 'mus_stinger_timeline_shift': ('GAM-MUS-TRANSITION-TIMELINE_SHIFT', None),
        'mus_result_mission_success': ('GAM-MUS-VICTORY-MISSION', None), 'mus_result_mission_fail': ('GAM-MUS-DEFEAT-MISSION', None),
        'mus_result_chapter_complete': ('GAM-MUS-VICTORY-CHAPTER', None), 'mus_credits': ('GAM-MUS-ENDING-CREDITS', 'ending')}
PER = {'theme': ('THEME-01', None), 'prep_loop': ('GAMEPLAY-PREP', None), 'tension_loop': ('GAMEPLAY-TENSION', '{c}_gameplay'),
       'combat_loop': ('COMBAT-01', '{c}_combat'), 'critical_layer': ('CRITICAL_LAYER-01', None), 'climax': ('BOSS-01', '{c}_boss'),
       'intro': ('INTRO-01', '{c}_intro'), 'outro': ('OUTRO-01', '{c}_outro'), 'stinger': ('TRANSITION-STINGER', None)}


def _contract(c):
    old = c['id']
    c['legacy_working_id'] = old
    if old in GAME:
        cid, mc = GAME[old]
        folder, chap = 'shared', 'shared'
    else:
        ch = c['chapter']
        if old.startswith('mus_cin_'):
            kind = old.rsplit('_', 1)[1]
        elif old.startswith('mus_stinger_chapter_'):
            kind = 'stinger'
        else:
            kind = old[len(f'mus_{ch}_'):]
        suf, mc = PER[kind]
        cid = f'{CODE[ch]}-MUS-{suf}'
        folder = chap = CHKEY[ch]
        mc = mc.format(c=CHKEY[ch]) if mc else None
    c['id'] = cid
    c['manifest_chapter'] = chap
    c['music_cue'] = mc
    c['bus'] = 'Music'
    c['path'] = f'generated_assets/audio/music/{folder}/{cid.lower().replace("-", "_")}.ogg'


def run(cue):
    import importlib
    from tfjaudio.build import produce_music
    mod, fn, args = cue['build']
    m = importlib.import_module('tfjaudio.' + mod)
    t0 = time.time()
    try:
        res = getattr(m, fn)(*args)
        intro = None
        if isinstance(res, tuple):
            intro, song = res
        else:
            song = res
        meta = {k: v for k, v in cue.items() if k != 'build'}
        meta.update({k: v for k, v in song.meta.items()})
        rec = produce_music(meta, song, intro=intro)
        print(f"OK {cue['id']} {rec['seconds']}s {rec['lufs_i']}LUFS {rec['true_peak_dbtp']}dBTP {round(time.time()-t0)}s", flush=True)
        return rec
    except Exception:
        print('FAIL', cue['id'], traceback.format_exc(), flush=True)
        return None


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    jobs = 3
    for a in sys.argv[1:]:
        if a.startswith('--jobs='):
            jobs = int(a.split('=')[1])
    cues = registry()
    if args:
        if '--exact' in sys.argv:
            cues = [c for c in cues if c['id'] in args]
        else:
            cues = [c for c in cues if any(a in c['id'] for a in args)]
    print('cues', len(cues), flush=True)
    if '--resume' in sys.argv:
        cues = [c for c in cues if not os.path.exists(f"/workspace/tfj-scratch/qc/{c['id']}.json")]
        print('to render', len(cues), flush=True)
    if jobs == 1 or '--isolated' in sys.argv:
        # one subprocess per cue: an out-of-memory kill only loses that cue, never hangs the run
        import subprocess
        from concurrent.futures import ThreadPoolExecutor
        def one(c):
            r = subprocess.run([sys.executable, os.path.abspath(__file__), c['id'], '--exact', '--jobs=1', '--inline'], capture_output=True, text=True)
            print((r.stdout.strip().splitlines() or ['?'])[-1] if r.returncode == 0 else f"FAIL {c['id']} rc={r.returncode} {r.stderr[-400:]}", flush=True)
        if '--inline' in sys.argv:
            for c in cues:
                run(c)
        else:
            with ThreadPoolExecutor(jobs) as ex:
                list(ex.map(one, cues))
    else:
        with Pool(jobs) as p:
            p.map(run, cues, chunksize=1)
