"""Contact sheets of SFX spectrograms per folder."""
import sys, os, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, soundfile as sf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import stft
ROOT = '/workspace/tfj-audio/assets/audio'
def sheet(folder, out, pattern='*'):
    files = sorted(glob.glob(f'{ROOT}/{folder}/{pattern}.wav') + glob.glob(f'{ROOT}/{folder}/{pattern}.ogg'))
    if not files:
        return
    cols = 5
    rows = (len(files) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3.0, rows * 1.9), dpi=70, squeeze=False)
    for ax in axes.flat:
        ax.axis('off')
    for i, f in enumerate(files):
        x, sr = sf.read(f, always_2d=True)
        m = x.mean(1)
        ax = axes.flat[i]
        n = 512 if len(m) > 4096 else 256
        fr, t, Z = stft(m, sr, nperseg=n, noverlap=n * 3 // 4)
        S = 20 * np.log10(np.abs(Z) + 1e-9)
        ax.pcolormesh(t, fr, S, vmin=S.max() - 80, vmax=S.max(), shading='auto', cmap='magma')
        ax.set_yscale('symlog', linthresh=300)
        ax.set_ylim(40, 20000)
        ax.set_title(os.path.basename(f).rsplit('.', 1)[0].replace('sfx_', ''), fontsize=7, color='w')
        ax.axis('off')
    fig.patch.set_facecolor('#111418')
    plt.tight_layout()
    fig.savefig(out, facecolor='#111418')
    plt.close(fig)
    from PIL import Image
    Image.open(out).convert('RGB').quantize(colors=96).save(out, optimize=True)

def _sheet(files, out):
    cols = 5
    rows = (len(files) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3.0, rows * 1.9), dpi=70, squeeze=False)
    for ax in axes.flat:
        ax.axis('off')
    for i, f in enumerate(files):
        x, sr = sf.read(f, always_2d=True)
        m = x.mean(1)
        ax = axes.flat[i]
        n = 512 if len(m) > 4096 else 256
        fr, t, Z = stft(m, sr, nperseg=n, noverlap=n * 3 // 4)
        S = 20 * np.log10(np.abs(Z) + 1e-9)
        ax.pcolormesh(t, fr, S, vmin=S.max() - 80, vmax=S.max(), shading='auto', cmap='magma')
        ax.set_yscale('symlog', linthresh=300)
        ax.set_ylim(40, 20000)
        ax.set_title(os.path.basename(f).rsplit('.', 1)[0], fontsize=7, color='w')
        ax.axis('off')
    fig.patch.set_facecolor('#111418')
    plt.tight_layout()
    tmp = out + '.png'
    fig.savefig(tmp, facecolor='#111418')
    plt.close(fig)
    from PIL import Image
    Image.open(tmp).convert('RGB').save(out, 'WEBP', quality=80, method=6)
    os.remove(tmp)


if __name__ == '__main__':
    P = f'{ROOT}/previews/sfx'
    os.makedirs(P, exist_ok=True)
    g = lambda *pats: sorted(sum([glob.glob(f'{ROOT}/{p}') for p in pats], []))
    groups = {
        'weapons_kinetic': g('sfx/shared/opr_sfx_kinetic_*'),
        'weapons_breach_and_handling': g('sfx/shared/opr_sfx_breach_*', 'sfx/shared/opr_sfx_reload_*', 'sfx/shared/opr_sfx_weapon_switch_*'),
        'destruction': g('sfx/shared/shr_sfx_*'),
        'critical_assets': g('sfx/helix/*', 'sfx/vita/*', 'sfx/nova_grid/*', 'sfx/civitas/*', 'sfx/meridian/*'),
        'ui': g('sfx/shared/gam_sfx_ui_*'),
        'character_foley': g('sfx/shared/opr_sfx_suit_*', 'sfx/shared/opr_sfx_equipment_*', 'sfx/shared/opr_sfx_weapon_handle_*'),
        'ambience': g('ambience/*/*.ogg'),
    }
    for name, files in groups.items():
        if files:
            _sheet(files, f'{P}/{name}_sheet.webp')
            print(name, len(files))
