#!/usr/bin/env python3
"""Kick mesure par mesure, en croches : rebond, deplacement, roulements (KT10).

La passe `rhythm_signature` replie le morceau sur 16 pas et moyenne les
mesures : un kick ajoute une mesure sur trois y devient un coup faible sans
periode. Ce script lit la grille de beats du sidecar (`beats.beat_times_s`),
prend le stem `drums.wav` de `<MEDIA>/Mix/stems/<slug>/` s'il existe (sinon
le mix, ou la basse en contretemps compte comme un kick), detecte l'attaque
du kick par la montee rapide de l'enveloppe 35-130 Hz (le rumble tenu ne
monte pas) et imprime une ligne de 8 croches par mesure (`X` >= 0,6, `x` >=
0,35 du 80e centile des temps), puis la periode des coups sur chaque « et »
et la sequence des mesures (T sur les temps, E decale d'une croche, R
roulement, m mixte, _ vide). La phase (decalage de 0 a 3 temps) est celle qui
met le plus d'energie sur les temps.

    scripts/.venv/bin/python kt_kick_bars.py kodaman_mosmoz_adharaa_-_kodaman_x_mosmoz_x_adharaa_smash_fs02_free_dl

Exemple (Kodaman x Mosmoz x Adharaa, *Smash*, 152 BPM, 115 mesures) : 21
mesures sur les temps, 21 decalees d'une croche, 20 de roulement ; les
roulements de 1-2 mesures a longueur impaire font basculer le four-on-floor
sur le « et » pour 3 a 5 mesures, puis le ramenent : le « martial » de KT10.
"""
from __future__ import annotations

import argparse, json, sys, warnings
import numpy as np
warnings.filterwarnings("ignore")
import librosa
from scipy.signal import butter, sosfilt

parser = argparse.ArgumentParser(description="Kick mesure par mesure, en croches (rebond, deplacement, roulements).")
parser.add_argument("slug", help="slug du morceau (sidecar library/quality/<slug>.json)")
slug = parser.parse_args().slug
d = json.load(open(f"library/quality/{slug}.json"))
import glob, os
stem = glob.glob(f"/Volumes/xtreme/Mix/stems/{slug}/*drums*")
path = stem[0] if stem else "/Volumes/xtreme/Mix/" + d["file_path"]
print("source :", os.path.basename(path))
beats = np.array(d["beats"]["beat_times_s"])
y, sr = librosa.load(path, sr=22050, mono=True)
sos = butter(4, [35, 130], btype="band", fs=sr, output="sos")
low = sosfilt(sos, y)
# attaque du kick = montee rapide de l'enveloppe (le rumble tenu ne monte pas)
from scipy.ndimage import maximum_filter1d
env_abs = maximum_filter1d(np.abs(low), int(0.005 * sr))
rise = np.clip(np.diff(env_abs, prepend=env_abs[0]), 0, None)
env = maximum_filter1d(rise, int(0.02 * sr))
# energie par croche : entre deux beats, 2 cases
rows = []
for i in range(len(beats) - 1):
    t0, t1 = beats[i], beats[i + 1]
    half = (t1 - t0) / 2
    vals = []
    for k in range(2):
        a = int((t0 + k * half) * sr); b = int((t0 + (k + 1) * half) * sr)
        seg = env[a:b]
        # attaque : max des 40 premieres ms
        vals.append(float(np.max(seg[: int(0.06 * sr)])) if len(seg) > 10 else 0.0)
    rows.append(vals)
steps = np.array(rows).reshape(-1)  # croches
nb = len(steps) // 8
bars = steps[: nb * 8].reshape(nb, 8)
ref = np.percentile(bars[:, [0, 2, 4, 6]], 80) or 1.0
def g(v):
    r = v / ref
    return "X" if r >= 0.6 else ("x" if r >= 0.35 else ".")
pat = ["".join(g(v) for v in bar) for bar in bars]
# phase : choisir le decalage de beat (0-3) qui maximise les coups sur les temps
best = None
for sh in range(4):
    sh_steps = steps[2 * sh:]
    nb2 = len(sh_steps) // 8
    b2 = sh_steps[: nb2 * 8].reshape(nb2, 8)
    score = b2[:, [0, 2, 4, 6]].mean() - b2[:, [1, 3, 5, 7]].mean()
    if best is None or score > best[0]:
        best = (score, sh, b2)
score, sh, bars = best
pat = ["".join(g(v) for v in bar) for bar in bars]
print(f"{slug} : {len(bars)} mesures, decalage de beat {sh}, bpm {d['beats']['tempo_bpm']}")
for i in range(0, len(pat), 8):
    print(f"{i+1:3d}  " + "  ".join(pat[i:i + 8]))
# periodicite des coups hors temps (croches 1,3,5,7 = les « et »)
off = (bars[:, [1, 3, 5, 7]] / ref >= 0.35)
idx = {k: np.where(off[:, k])[0] for k in range(4)}
names = {0: "et du temps 1", 1: "et du temps 2", 2: "et du temps 3", 3: "et du temps 4 (avant le 1)"}
for k in range(4):
    ii = idx[k]
    gaps = np.diff(ii)
    print(f"{names[k]:28} : {len(ii)} mesures sur {len(bars)}" + (f", ecarts {np.bincount(gaps)[1:6].tolist()} (1..5 mesures)" if len(gaps) else ""))

# classification par mesure : sur le temps / sur le « et » / roulement / autre
on = (bars[:, [0, 2, 4, 6]] / ref >= 0.35); offb = (bars[:, [1, 3, 5, 7]] / ref >= 0.35)
labels = []
for o, f in zip(on, offb):
    n_on, n_off = int(o.sum()), int(f.sum())
    if n_on + n_off >= 7: labels.append("R")      # roulement de croches
    elif n_on >= 3 and n_off <= 1: labels.append("T")   # kick sur les temps
    elif n_off >= 3 and n_on <= 1: labels.append("E")   # kick sur les « et » (decale d'une croche)
    elif n_on + n_off == 0: labels.append("_")          # pas de kick
    else: labels.append("m")                            # mixte / rebond
runs = []
for l in labels:
    if runs and runs[-1][0] == l: runs[-1][1] += 1
    else: runs.append([l, 1])
print("sequence (T temps, E decale d'une croche, R roulement, m mixte, _ vide) :")
print("  " + " ".join(f"{l}{n}" for l, n in runs))
print("  mesures : T", labels.count("T"), " E", labels.count("E"), " R", labels.count("R"), " m", labels.count("m"), " _", labels.count("_"))
