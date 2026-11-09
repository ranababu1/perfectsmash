"""Build the SFX and ambience library. Usage: python3 produce_sfx.py [id_substring ...] [--jobs=N]"""
import sys, os, json, time, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool
import numpy as np

ROOT = '/workspace/tfj-audio'
CHFOLDER = {'HLX': 'helix', 'VTA': 'vita', 'NVG': 'nova_grid', 'CVT': 'civitas', 'MRD': 'meridian', 'OPR': 'shared', 'SHR': 'shared', 'GAM': 'shared'}
UI_WAV = {'UI_CLICK', 'UI_CONFIRM', 'UI_BACK', 'UI_ERROR'}


def registry():
    """One entry per file. Ids follow ASSET_CONTRACT section 6: <CH>-SFX-<NAME>-<VARIANT>."""
    R = []
    def add(ch, name, gen, args, nvar, chans, target, desc, use, sound_id=None, family='', bus='SFX', loop=False, tier=None):
        for v in range(1, nvar + 1):
            cid = f'{ch}-SFX-{name}-{v:02d}'
            fmt = 'wav' if name in UI_WAV else 'ogg'
            folder = f'sfx/{CHFOLDER[ch]}'
            R.append(dict(id=cid, base=f'{ch}-SFX-{name}', folder=folder, gen=gen, args=args, seed=1000 * (len(R) + 1) + v, variation=v,
                          variations=nvar, channels=chans, target=target, description=desc, use=use, loop=loop, tier=tier,
                          sound_id=sound_id, family=family, bus=bus, ext=fmt, manifest_chapter=CHFOLDER[ch],
                          file=f"assets/audio/{folder}/{cid.lower().replace('-', '_')}.{fmt}"))
    W = 'weapons and explosions (-14 to -10 LUFS-M)'
    WH = 'weapon handling (UI-like, -18 to -16 LUFS-M)'
    I = 'impacts and debris (-18 to -14 LUFS-M)'
    U = 'UI (-22 to -18 LUFS-M)'
    add('OPR', 'KINETIC_CHARGE', 'kinetic_charge', {}, 3, 1, -16, 'Electromagnetic capacitor charge-up with lock click at full charge (0.9 s)', 'Kinetic Accelerator aim/charge (aim_preview); play on charge start', None, WH)
    add('OPR', 'KINETIC_FIRE', 'kinetic_fire', {'tier': 0}, 5, 1, -12, 'Magnetic snap, falling rail thwip, body thump, short metallic ring', 'Kinetic Accelerator shot, base weapon (pick a variation at random)', 'kinetic_fire', W)
    for tr in (1, 2, 3):
        add('OPR', f'KINETIC_FIRE_T{tr}', 'kinetic_fire', {'tier': tr}, 3, 1, -12 + 0.5 * tr, f'Kinetic Accelerator shot, upgrade tier {tr}: heavier sub, longer zap' + (', crackle and ring' if tr >= 2 else '') + (', rail resonance' if tr >= 3 else ''), f'Kinetic Accelerator shot when the summed upgrade level reaches tier {tr}', 'kinetic_fire', W, tier=tr)
    add('OPR', 'KINETIC_TRAVEL_LOOP', 'kinetic_travel_loop', {}, 3, 1, -20, 'Projectile flight whine and air rush, 1 s seamless loop', 'Loop on the projectile while in flight (AudioStreamPlayer2D; pitch can follow speed)', None, 'loop (integrated -20 LUFS)', loop=True)
    add('OPR', 'KINETIC_IMPACT', 'kinetic_impact', {}, 5, 1, -14, 'Hard strike crack, metallic clank, thump and a short descending temporal ripple', 'Kinetic projectile hits any structure (layer with the material impact)', None, I)
    add('OPR', 'BREACH_PREP', 'breach_prep', {}, 3, 1, -17, 'Canister load clack, servo whirr, latch and two arming beeps', 'Breach Charge selected / loaded', None, WH)
    add('OPR', 'BREACH_LAUNCH', 'breach_launch', {}, 4, 1, -13, 'Pneumatic launcher thump, tube resonance and air burst', 'Breach Charge launch (lobbed canister)', 'breach_launch', W)
    add('OPR', 'BREACH_ARM', 'breach_activate', {}, 3, 1, -17, 'Rising triple beep and a short electrical build', 'Breach canister arms on landing / just before detonation', None, WH)
    add('OPR', 'BREACH_EXPLOSION', 'breach_explosion', {'tier': 0}, 5, 2, -10, 'Explosion: broadband crack, deep body, mid crunch for phone speakers, debris tail', 'Breach Charge detonation, base weapon', 'breach_detonate', W)
    for tr in (1, 2, 3):
        add('OPR', f'BREACH_EXPLOSION_T{tr}', 'breach_explosion', {'tier': tr}, 3, 2, -10, f'Breach Charge detonation, upgrade tier {tr}: longer body, more debris' + (', sub drop' if tr >= 2 else ''), f'Breach Charge detonation at upgrade tier {tr}', 'breach_detonate', W, tier=tr)
    add('OPR', 'BREACH_SHOCKWAVE', 'breach_shockwave', {}, 3, 2, -12, 'Low whoomp and a sweeping air-pressure rush', 'Layer on the blast impulse / large chain reactions', None, W)
    add('OPR', 'RELOAD_READY', 'cooldown', {}, 3, 1, -18, 'Vent hiss, cooling ticks and a two-note ready chime', 'Weapon cooldown complete / ready again', 'reload_ready', WH)
    add('OPR', 'WEAPON_SWITCH', 'weapon_switch', {}, 3, 1, -17, 'Slide, two latches, servo blip and a confirm blip', 'Switch between Kinetic Accelerator and Breach Charge', 'weapon_switch', WH)
    add('SHR', 'METAL_STRESS', 'metal_bend', {}, 4, 1, -17, 'Stick-slip creak through metal resonances, low groan', 'reinforced_steel / lightweight_alloy under stress (damage stage 1-2)', None, I)
    add('SHR', 'IMPACT_METAL', 'metal_break', {}, 5, 1, -14, 'Snap transient, two-stage metallic ring, small tinkles', 'reinforced_steel / lightweight_alloy hit or destroyed', 'impact_metal', I)
    add('SHR', 'IMPACT_GLASS', 'glass_break', {}, 5, 1, -14, 'Crack, 55-85 resonant shards, tinkle tail', 'glass_polymer hit or destroyed', 'impact_glass', I)
    add('SHR', 'IMPACT_CONCRETE', 'concrete_crack', {}, 5, 1, -14, 'Dense crackle, thump, crunch and dust', 'concrete hit or destroyed', 'impact_concrete', I)
    add('SHR', 'IMPACT_COMPOSITE', 'composite_crack', {}, 4, 1, -15, 'Fibrous crack with plastic resonances', 'composite hit or destroyed', 'impact_composite', I)
    add('SHR', 'ELECTRIC_SHORT', 'electrical_short', {}, 5, 1, -15, 'Gated arc buzz, crackle and pop', 'electronic_module hit or destroyed', 'impact_electronic', I)
    add('SHR', 'ENERGY_DISCHARGE', 'energy_discharge', {}, 4, 1, -14, 'FM zap falling into plasma whoosh with plate shimmer', 'energy_component destroyed', 'component_destroyed', I)
    add('SHR', 'MACHINE_FAILURE', 'machinery_failure', {}, 4, 1, -16, 'Motor wind-down, gear whine, grinding, final clunk', 'Machinery components (fans, pumps, servers, conveyors) destroyed', 'component_destroyed', I)
    add('SHR', 'SECONDARY_BLAST', 'secondary_blast', {}, 4, 2, -12, 'Chain-reaction blast: crack, mid-size boom, crunch, fire puff and debris (2.2 s)', 'A destroyed component detonates or a chain reaction propagates', 'secondary_blast', W)
    add('SHR', 'STRUCTURE_COLLAPSE', 'structural_collapse', {}, 4, 2, -12, 'Rumble, staggered heavy impacts, concrete and metal layers, debris (4.0 s)', 'Large structure or support collapse; mission-ending chain reaction', 'component_destroyed', W)
    add('SHR', 'DEBRIS_HEAVY', 'debris_heavy', {}, 5, 1, -15, 'Bouncing heavy chunks (modal low impacts with accelerating rhythm)', 'Heavy fragments landing / large component falls', None, I)
    add('SHR', 'DEBRIS_SMALL', 'debris_small', {}, 5, 1, -18, 'Scattered small fragment ticks', 'Small fragments, light components, aftermath detail', None, I)
    for ch, gen, desc in [('HLX', 'crit_helix', 'AI core power-down sweep, data stutter, blast, discharge and fan wind-down'),
                          ('VTA', 'crit_vita', 'Bioreactor vessel shatter, liquid gush and bubbling, pressure hiss, blast'),
                          ('NVG', 'crit_nova', 'Pressure build, reactor breach blast, arcs, metal groan, dying transformer hum'),
                          ('CVT', 'crit_civitas', 'Alarm cut, data cascade glitches, blast, glass and metal, screens shutting off'),
                          ('MRD', 'crit_meridian', 'Temporal implosion (reverse swell) into blast, falling shimmer cloud, sub drop, fractures')]:
        add(ch, 'CORE_DESTROYED', gen, {}, 3, 2, -10, desc + ' (4.0 s)', f'{CHFOLDER[ch]} critical asset destroyed (mission objective)', 'core_destroyed', W)
    add('SHR', 'ALARM_KLAXON', 'alarm', {'style': 1}, 1, 1, -16, 'Two-tone facility klaxon (740 / 587 Hz), 2.0 s seamless loop', 'Critical asset exposed / facility alert; loop while active', 'alarm', 'alarm (-16 LUFS-M)', loop=True)
    add('SHR', 'ALARM_SIREN', 'alarm', {'style': 2}, 1, 1, -16, 'Rising siren sweep, 1.6 s seamless loop', 'Escalation / countdown alert; loop while active', 'alarm', 'alarm (-16 LUFS-M)', loop=True)
    add('SHR', 'ALARM_PULSE', 'alarm', {'style': 3}, 1, 1, -17, 'Digital triple-pulse warning, 1.2 s seamless loop', 'System warning, low-time alert; loop while active', 'alarm', 'alarm (-16 LUFS-M)', loop=True)
    add('GAM', 'UI_CLICK', 'ui_select', {}, 4, 1, -21, 'Short precise FM blip with a fine tick', 'Button / list focus and select', 'ui_click', U, bus='UI')
    add('GAM', 'UI_CONFIRM', 'ui_confirm', {}, 3, 1, -19, 'Rising two-note blip (fifth)', 'Confirm / accept', 'ui_confirm', U, bus='UI')
    add('GAM', 'UI_BACK', 'ui_back', {}, 3, 1, -20, 'Falling two-note blip (fourth)', 'Back / cancel', 'ui_back', U, bus='UI')
    add('GAM', 'UI_ERROR', 'ui_error', {}, 3, 1, -19, 'Two soft square-wave pulses, detuned', 'Invalid action / insufficient Research Data', None, U, bus='UI')
    add('GAM', 'UI_UNLOCK', 'ui_unlock', {}, 1, 2, -18, 'Four-note rising chime with shimmer', 'Level, chapter or weapon unlocked', None, U, bus='UI')
    for tr in (1, 2, 3):
        add('GAM', f'UI_UPGRADE_T{tr}', 'ui_upgrade', {'tier': tr}, 1, 2, -18, f'Power-up sweep and {2 + tr}-note arpeggio (tier {tr})', f'Weapon upgrade purchased, level {tr}', None, U, bus='UI', tier=tr)
    add('GAM', 'UI_ACHIEVEMENT', 'ui_achievement', {}, 1, 2, -18, 'Bright bell chord with sparkle and plate', 'Achievement / best score', None, U, bus='UI')
    add('GAM', 'UI_OBJECTIVE_COMPLETE', 'objective_complete', {}, 2, 2, -18, 'Quick rising triad with a soft low thump and shimmer', 'Objective cleared during a mission', 'objective_complete', U, bus='UI')
    add('GAM', 'UI_VICTORY', 'ui_mission_complete', {}, 1, 2, -18, 'Three-note rising confirmation with soft thump', 'Mission success UI layer (the GAM-MUS-VICTORY-MISSION music cue plays separately)', 'mission_success', U, bus='UI')
    add('GAM', 'UI_DEFEAT', 'ui_mission_fail', {}, 1, 2, -18, 'Descending three-note figure and falling tone', 'Mission failed UI layer (the GAM-MUS-DEFEAT-MISSION music cue plays separately)', 'mission_fail', U, bus='UI')
    add('OPR', 'SUIT_MOVE', 'suit_move', {}, 5, 1, -24, 'Tactical suit fabric movement', 'Operative idle shifts, aim adjust, animation events', None, 'foley (-24 LUFS-M)')
    add('OPR', 'EQUIPMENT_RATTLE', 'equipment', {}, 4, 1, -24, 'Small equipment rattles and strap creak', 'Operative movement, landing, recoil settle', None, 'foley (-24 LUFS-M)')
    add('OPR', 'WEAPON_HANDLE', 'weapon_handle', {}, 4, 1, -22, 'Grip rustle, metal click, soft thump, latch tick', 'Raise / lower / reload handling animation events', None, 'foley (-22 LUFS-M)')
    add('OPR', 'SUIT_SERVO', 'servo', {}, 5, 1, -22, 'Small suit or weapon servo whirr (odd = rising, even = falling)', 'Weapon aim motor, suit augmentation, rig animation', None, 'foley (-22 LUFS-M)')
    from tfjaudio.ambience import BANDS
    code = {'helix': 'HLX', 'vita': 'VTA', 'nova_grid': 'NVG', 'civitas': 'CVT', 'meridian': 'MRD'}
    for chk, bands in BANDS.items():
        for band, fn, sec, desc in bands:
            cid = f'{code[chk]}-AMB-{band}-01'
            R.append(dict(id=cid, base=cid, folder=f'ambience/{chk}', gen='amb:' + fn.__name__, args={'sec': sec}, seed=7000 + len(R), variation=1, variations=1,
                          channels=2, target=-24, description=desc, use=f'{chk} mission bed for the {band.lower()} band', loop=True, tier=None, ambience=True,
                          ambience_cue=f'{chk}_{band.lower()}', bus='Ambience', ext='ogg', family='ambience (-24 LUFS integrated)', manifest_chapter=chk, sound_id=None,
                          file=f"assets/audio/ambience/{chk}/{cid.lower().replace('-', '_')}.ogg"))
    return R


def run(e):
    from tfjaudio import sfx as S
    from tfjaudio.dsp import SR, tp_limit, undb, true_peak_db
    from tfjaudio.analyze import qc, decode, seam_metrics, momentary_max
    from tfjaudio.song import lufs
    from tfjaudio.export import write_master, write_ogg, write_wav16
    try:
        t0 = time.time()
        if e['gen'].startswith('amb:'):
            from tfjaudio import ambience as A
            fn = getattr(A, e['gen'][4:])
        else:
            fn = getattr(S, e['gen'])
        args = dict(e['args'])
        x = fn(e['seed'], **args)
        if x.ndim == 1:
            x = x[:, None]
        if e['channels'] == 1 and x.shape[1] == 2:
            x = x.mean(1, keepdims=True)
        if e['channels'] == 2 and x.shape[1] == 1:
            x = np.repeat(x, 2, 1)
        x = x - x.mean(0, keepdims=True) * (1 if e.get('loop') else 0)
        # loudness normalisation
        # loudness is measured as played: mono files are counted on both speakers
        x2 = np.repeat(x, 2, 1) if x.shape[1] == 1 else x
        if e.get('ambience') or e['id'].startswith('OPR-SFX-KINETIC_TRAVEL_LOOP'):
            cur = lufs(x2)
        else:
            cur = momentary_max(x2)
        if not e.get('loop'):
            # remove DC and sub-audible drift (2nd-order high-pass at 18 Hz, causal)
            from scipy.signal import butter, sosfilt
            x = sosfilt(butter(2, 18, 'hp', fs=SR, output='sos'), x, axis=0)
        measure = (lambda z: lufs(z)) if (e.get('ambience') or e['id'].startswith('OPR-SFX-KINETIC_TRAVEL_LOOP')) else momentary_max
        st2 = lambda z: np.repeat(z, 2, 1) if z.shape[1] == 1 else z
        comp_db = 0.0
        CEIL = -1.3
        saturable = not (e.get('loop') or e['bus'] == 'UI')
        g = e['target'] - measure(st2(x))

        def limit(z):
            if e.get('loop'):
                # periodic limiting: limit a 3x tile and take the middle
                t3 = tp_limit(np.concatenate([z, z, z], 0), CEIL)
                return t3[z.shape[0]: 2 * z.shape[0]]
            return tp_limit(np.concatenate([z, np.zeros((int(0.01 * SR), z.shape[1]))], 0), CEIL)[: z.shape[0]]

        for it in range(8):
            over_db = true_peak_db(st2(x) * undb(g)) - CEIL
            if over_db > 3.5 and saturable and comp_db < 9.0:
                # spiky one-shots (crackle, small debris, fibre snaps) need more than about 3 dB of peak
                # reduction to reach the family loudness: soft-saturate only the spikes (4x oversampled
                # tanh knee, at most 9 dB in total) and leave the last 3 dB to the true-peak limiter
                from scipy.signal import resample_poly
                amt = min(over_db - 3.0, 9.0 - comp_db)
                z = resample_poly(x * undb(g), 4, 1, axis=0)
                c = undb(CEIL + 3.0 - amt)
                knee = 0.5 * c
                mag = np.abs(z)
                hit = mag > knee
                z[hit] = np.sign(z[hit]) * (knee + (c - knee) * np.tanh((mag[hit] - knee) / (c - knee)))
                x = resample_poly(z, 1, 4, axis=0)[: x.shape[0]] / undb(g)
                comp_db += amt
                continue
            if over_db > 4.0:
                # never ask the limiter for more than 4 dB (keeps transients intact)
                g -= over_db - 4.0
                y = limit(x * undb(g))
                break
            y = limit(x * undb(g))
            miss = e['target'] - measure(st2(y))
            if abs(miss) < 0.25:
                break
            g += miss
        else:
            y = limit(x * undb(g))
        if not e.get('loop'):
            # trim silence padding: start 1 ms before -60 dBFS, end 15 ms after the last sample above -66 dBFS
            a = np.abs(y).max(1)
            nz = np.where(a > 10 ** (-60 / 20))[0]
            nt = np.where(a > 10 ** (-66 / 20))[0]
            i0 = max(0, nz[0] - int(0.001 * SR))
            i1 = min(y.shape[0], nt[-1] + int(0.015 * SR))
            y = y[i0:i1].copy()
            f = int(0.012 * SR)
            y[-f:] *= np.linspace(1, 0, f)[:, None] ** 2
            if i0 > 0:
                f0 = int(0.0005 * SR)
                y[:f0] *= np.linspace(0, 1, f0)[:, None]
        from tfjaudio.export import to_game_rate, GAME_SR
        import soundfile as sf
        import subprocess
        rel = e['file']
        full = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        for attempt in range(4):
            gbuf = to_game_rate(y, loop=bool(e.get('loop')))
            if e['ext'] == 'wav':
                rr = np.random.default_rng(e['seed'])
                d = (rr.random(gbuf.shape) - rr.random(gbuf.shape)) / 32768.0
                sf.write(full, np.clip(gbuf + d, -1, 1), GAME_SR, subtype='PCM_16')
                fmt = 'wav_pcm16_44100'
            else:
                tmp = full + '.tmp.wav'
                sf.write(tmp, np.clip(gbuf, -1, 1), GAME_SR, subtype='FLOAT')
                subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-c:a', 'libvorbis', '-q:a', '6', '-ar', str(GAME_SR),
                                '-map_metadata', '-1', '-fflags', '+bitexact', '-flags:a', '+bitexact', full], check=True)
                os.remove(tmp)
                fmt = 'ogg_vorbis_q6_44100'
            from scipy.signal import resample_poly as _rp
            _d, _ = sf.read(full, always_2d=True)
            _tp = true_peak_db(_rp(_d, 160, 147, axis=0))
            if _tp <= -1.05:
                break
            # the codec added overshoot: pull the whole file down just enough and encode again
            y = y * undb(-(_tp + 1.15))
        master = write_master(y, f"{e['folder']}/{os.path.basename(rel).rsplit('.', 1)[0]}.wav", fmt='WAV')
        dec44, sr = sf.read(full, always_2d=True)
        from scipy.signal import resample_poly
        dec = resample_poly(dec44, 160, 147, axis=0)
        dd = dec if dec.shape[1] == 2 else np.repeat(dec, 2, 1)
        info = qc(dd, loop=False, kind='sfx')
        info['channels'] = int(dec44.shape[1])
        info['sample_rate'] = int(sr)
        info['samples'] = int(dec44.shape[0])
        info['seconds'] = round(dec44.shape[0] / sr, 4)
        info['momentary_max_lufs'] = round(momentary_max(dd), 2)
        if e.get('loop'):
            k = int(0.15 * GAME_SR)
            gg = gbuf if gbuf.shape[1] == 2 else np.repeat(gbuf, 2, 1)
            d2 = dec44 if dec44.shape[1] == 2 else np.repeat(dec44, 2, 1)
            k = min(k, gg.shape[0] // 4)
            ref = np.concatenate([gg[-k:], gg[:k]], 0)
            mid = gg.shape[0] // 2 - k
            info['seam'] = seam_metrics(d2, ref, (mid, gg[mid: mid + 2 * k]), sr=GAME_SR)
            # stricter reference for short loops: encode three cycles back to back and measure the codec
            # error at the internal cycle boundary (identical material, no file wrap)
            if gg.shape[0] < 20 * GAME_SR:
                tile = np.concatenate([gbuf, gbuf, gbuf], 0)
                tp3 = full + '.tile.wav'
                to3 = full + '.tile.ogg'
                sf.write(tp3, np.clip(tile, -1, 1), GAME_SR, subtype='FLOAT')
                subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tp3, '-c:a', 'libvorbis', '-q:a', '6', to3], check=True)
                dt, _ = sf.read(to3, always_2d=True)
                os.remove(tp3); os.remove(to3)
                dt = dt if dt.shape[1] == 2 else np.repeat(dt, 2, 1)
                nb = gg.shape[0]
                seg_t = dt[nb - k: nb + k]
                err_t = 20 * np.log10(np.sqrt(np.mean((seg_t - ref) ** 2)) / (np.sqrt(np.mean(ref ** 2)) + 1e-12) + 1e-12)
                info['seam']['tile_boundary_error_db'] = round(float(err_t), 1)
                info['seam']['seamless'] = bool(info['seam']['wrap_hf_delta_db'] < 1.5 and info['seam']['wrap_error_db'] <= max(info['seam']['mid_error_db'], err_t) + 3)
            info['seam']['intrinsic_click_db'] = intrinsic_click(yy if False else (y if y.shape[1] == 2 else np.repeat(y, 2, 1)))
            info['loop_start_samples'] = 0
            info['loop_end_samples'] = int(dec44.shape[0])
        info['samples_match_master'] = bool(dec44.shape[0] == gbuf.shape[0])
        rec = {k: v for k, v in e.items() if k not in ('gen', 'args', 'seed')}
        rec.update(info)
        rec['generator'] = f"tfjaudio.sfx.{e['gen']}({', '.join(f'{k}={v}' for k, v in e['args'].items())}) seed={e['seed']}"
        rec['format'] = fmt
        rec['master'] = master
        rec['bytes'] = os.path.getsize(os.path.join(ROOT, rel))
        rec['gain_applied_db'] = round(float(g), 2)
        rec['transient_compression_db'] = round(comp_db, 1)
        os.makedirs('/workspace/tfj-scratch/qc_sfx', exist_ok=True)
        rec['master_sample_rate'] = SR
        rec['lufs_integrated'] = info.get('lufs_i')
        json.dump(rec, open(f"/workspace/tfj-scratch/qc_sfx/{e['id']}.json", 'w'), indent=1)
        print('OK', e['id'], rec['seconds'], rec.get('momentary_max_lufs'), rec['true_peak_dbtp'], round(time.time() - t0, 1), flush=True)
        return rec
    except Exception:
        print('FAIL', e['id'], traceback.format_exc(), flush=True)


def intrinsic_click(x):
    """HF energy at the wrap compared with the 99th percentile of the same measure across the file."""
    from tfjaudio.dsp import hp, SR
    k = int(0.2 * SR)
    j = np.concatenate([x[-k:], x[:k]], 0).mean(1)
    h = hp(j, 6000)
    w = int(0.004 * SR)
    e = np.convolve(h ** 2, np.ones(w) / w, mode='same')
    at = e[k - w: k + w].max()
    full = hp(x.mean(1), 6000)
    ef = np.convolve(full ** 2, np.ones(w) / w, mode='same')
    p99 = np.percentile(ef, 99)
    return round(float(10 * np.log10(at / (p99 + 1e-14) + 1e-14)), 2)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    jobs = 3
    for a in sys.argv[1:]:
        if a.startswith('--jobs='):
            jobs = int(a.split('=')[1])
    R = registry()
    if args:
        R = [e for e in R if any(a in e['id'] for a in args)]
    print('sfx', len(R), flush=True)
    with Pool(jobs) as p:
        p.map(run, R, chunksize=1)
