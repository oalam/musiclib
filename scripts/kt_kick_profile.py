#!/usr/bin/env python3
"""Profil du kick moyen et du rumble d'un plateau (KT5, KT10 ; stems Demucs).

Prend les temps d'un plateau (mesures `bar_from`-`bar_to` de la bank Digitakt,
grille re-suivie sur le stem drums), recale chaque kick sur son attaque dans
le stem drums, moyenne les kicks (300 ms) et imprime :

- l'enveloppe RMS (temps a -6 / -12 / -24 dB apres le pic) ;
- la hauteur de la queue (f0 par autocorrelation, 30-200 Hz, a 5-130 ms) :
  le pitch envelope et la note (doctrine §11, note mesuree sur la queue) ;
- le spectre par bandes de l'attaque (0-15 ms) et du corps (15-120 ms) ;
- des indices de saturation : facteur de crete du corps (sinus 3 dB, carre
  0 dB), part des echantillons pres du pic, niveau des harmoniques 120-300 Hz
  sous le fondamental ;
- l'attaque : centroide spectral des 8 premieres ms, 3-8 kHz attaque / corps ;
- le rumble : sub 30-100 Hz entre les kicks (du quart de temps au kick
  suivant) par stem drums / bass / other, relatif au sub de l'attaque ; et le
  profil du sub du stem drums sur un temps en 8 tranches.

Demucs decide du stem qui recoit un rumble tonal (souvent `bass`) : lire les
trois colonnes ensemble.

    scripts/.venv/bin/python kt_kick_profile.py kodaman_-_beton 17 28
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings

import numpy as np
warnings.filterwarnings("ignore")
import librosa
from scipy.signal import butter, sosfilt

parser = argparse.ArgumentParser(description="Profil du kick moyen et du rumble d'un plateau (stems Demucs, grille de la bank).")
parser.add_argument("slug"); parser.add_argument("bar_from", type=int, help="premiere mesure du plateau (1 = premiere mesure de la bank)")
parser.add_argument("bar_to", type=int, help="derniere mesure du plateau")
args = parser.parse_args(); slug, b0, b1 = args.slug, args.bar_from, args.bar_to
bank = json.load(open(f"library/digitakt/{slug}.json"))
bars = np.array(bank["bar_times_s"]); bpm = bank["bpm"]
beat = 60 / bpm
stems = f"/Volumes/xtreme/Mix/stems/{slug}/"
sr = 44100
dr, _ = librosa.load(stems + "drums.wav", sr=sr, mono=True)
ba, _ = librosa.load(stems + "bass.wav", sr=sr, mono=True)
ot, _ = librosa.load(stems + "other.wav", sr=sr, mono=True)
def band(x, lo, hi):
    sos = butter(4, [lo, hi], btype="band", fs=sr, output="sos"); return sosfilt(sos, x)
def db(x): return 20 * np.log10(max(x, 1e-9))
# temps (beats) du plateau
beats = np.concatenate([np.linspace(a, b, 4, endpoint=False) for a, b in zip(bars[b0-1:b1], bars[b0:b1+1])])
# recaler chaque kick sur son attaque (max de la montee sub dans ±40 ms)
sub = band(dr, 30, 150)
hits = []
for t in beats:
    c = int(t * sr); w = sub[c - int(0.04*sr): c + int(0.04*sr)]
    if len(w) < 100: continue
    k = c - int(0.04*sr) + int(np.argmax(np.abs(w)))
    if np.max(np.abs(w)) < 0.05: continue
    hits.append(k)
print(f"{slug[:30]} : {len(hits)} kicks, mesures {b0}-{b1}, {bpm} BPM, temps = {beat*1000:.0f} ms")
L = int(0.30 * sr)
K = np.array([dr[h - int(0.005*sr): h - int(0.005*sr) + L] for h in hits if h + L < len(dr)])
k = K.mean(axis=0)              # kick moyen (aligne sur l'attaque)
peak = np.max(np.abs(k))
# enveloppe RMS 2 ms
fr = int(0.002 * sr)
env = np.array([np.sqrt(np.mean(k[i:i+fr]**2)) for i in range(0, L - fr, fr)])
t_env = np.arange(len(env)) * 2.0
e0 = env.max(); i0 = env.argmax()
def t_at(dbdown):
    idx = np.where(env[i0:] < e0 * 10 ** (-dbdown / 20))[0]
    return t_env[i0 + idx[0]] - t_env[i0] if len(idx) else None
print(f"enveloppe : -6 dB a {t_at(6)} ms, -12 dB a {t_at(12)} ms, -24 dB a {t_at(24)} ms apres le pic")
# hauteur : autocorrelation sur fenetres de 20 ms, 0-150 ms
print("hauteur (f0, sub 30-150 Hz) :", end=" ")
for start in (5, 20, 40, 60, 90, 130):
    a = int(start/1000*sr); w = band(k, 30, 200)[a:a+int(0.025*sr)]
    if np.max(np.abs(w)) < peak * 0.02: print(f"{start}ms:-", end="  "); continue
    ac = np.correlate(w, w, "full")[len(w)-1:]
    lo, hi = int(sr/200), int(sr/30)
    lag = lo + int(np.argmax(ac[lo:hi])); f0 = sr / lag
    print(f"{start}ms:{f0:.0f}Hz({librosa.hz_to_note(f0)})", end="  ")
print()
# spectre moyen des kicks : bandes, attaque (0-15 ms) vs corps (15-120 ms)
def bands(x):
    out = {}
    for name, lo, hi in [("sub 30-60", 30, 60), ("60-120", 60, 120), ("120-300", 120, 300), ("300-1k", 300, 1000), ("1-3k", 1000, 3000), ("3-8k", 3000, 8000), ("8-16k", 8000, 16000)]:
        out[name] = db(np.sqrt(np.mean(band(x, lo, hi)**2)))
    return out
att = bands(k[:int(0.015*sr)]); body = bands(k[int(0.015*sr):int(0.12*sr)])
ref = max(body.values())
print("spectre (dB rel. au max du corps) :")
print("  bande        attaque 0-15ms   corps 15-120ms")
for n in att: print(f"  {n:11}  {att[n]-ref:7.1f}          {body[n]-ref:7.1f}")
# saturation : facteur de crete du corps, platitude des cretes (fraction d'echantillons > 0.9 du pic local)
bodyk = k[int(0.01*sr):int(0.1*sr)]
crest = db(np.max(np.abs(bodyk))) - db(np.sqrt(np.mean(bodyk**2)))
flat = np.mean(np.abs(bodyk) > 0.85 * np.max(np.abs(bodyk)))
# harmoniques : rapport energie 120-1000 / 30-120 sur le corps
hr = body["120-300"] - max(body["sub 30-60"], body["60-120"])
print(f"saturation : facteur de crete du corps {crest:.1f} dB (sinus pur = 3 dB, carre = 0 dB), {flat*100:.0f} % des echantillons a plus de 85 % du pic ; harmoniques 120-300 Hz a {hr:+.1f} dB du fondamental")
# transitoire : centroid spectral des 8 premieres ms
a8 = k[:int(0.008*sr)]
spec = np.abs(np.fft.rfft(a8 * np.hanning(len(a8)))); f = np.fft.rfftfreq(len(a8), 1/sr)
print(f"attaque : centroide spectral des 8 premieres ms = {np.sum(f*spec)/np.sum(spec):.0f} Hz ; energie 3-8 kHz attaque vs corps : {att['3-8k']-body['3-8k']:+.1f} dB")
# rumble : sub entre les kicks, par stem, fenetre pas 2-4 (apres 1/4 de temps jusqu'au kick suivant)
def between(x):
    v = []
    for h in hits:
        a = h + int(beat/4*sr); b = h + int(beat*0.95*sr)
        if b < len(x): v.append(np.sqrt(np.mean(band(x, 30, 100)[a:b]**2)))
    return db(np.mean(v))
on = db(np.sqrt(np.mean(band(k, 30, 100)[:int(beat/4*sr)]**2)))
print(f"rumble (30-100 Hz entre les kicks, rel. au sub du kick) : drums {between(dr)-on:+.1f} dB, bass {between(ba)-on:+.1f} dB, other {between(ot)-on:+.1f} dB")
# decroissance du sub du drums stem sur le temps entier (profil en 8 tranches)
prof = []
for q in range(8):
    a = int(q*beat/8*sr); b = int((q+1)*beat/8*sr)
    seg = np.array([band(dr, 30, 100)[h+a:h+b] for h in hits if h+b < len(dr)])
    prof.append(db(np.sqrt(np.mean(seg**2))))
prof = np.array(prof) - prof[0]
print("profil sub drums sur un temps (8 tranches, dB rel. a l'attaque) :", " ".join(f"{v:+.0f}" for v in prof))
