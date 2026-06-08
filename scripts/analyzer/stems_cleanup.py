"""Post-processing techno-aware des stems Demucs.

Demucs separe correctement la pop/rock mais a quelques fuites typiques
sur techno/tribe/hardtek :
- Sub-kick (20-60 Hz) parfois replique dans `bass.wav`
- Leads acides occasionnellement leakes dans `bass.wav` (au-dessus 500 Hz)
- `vocals.wav` souvent quasi-silencieux sur tracks instrumentaux mais
  contient des leaks de leads/sirenes

Ce module applique 3 regles domain-aware :

1. **Sub-kick clamp** : highpass `bass.wav` a 60 Hz. Le sub 20-60 Hz
   appartient au kick (drums), pas a la bass. Le sub residuel dans
   `bass.wav` est presque toujours une fuite.
2. **Bass top-cut** : lowpass `bass.wav` a 500 Hz. Une bassline techno
   ne monte (presque) jamais plus haut → tout ce qui depasse est une
   fuite de lead/synth.
3. **Vocals merge** : si RMS(vocals) tres faible (< -40 dBFS), on merge
   dans `other.wav` (track instrumental, ce qui est dans vocals est
   du bruit ou du leak).

Note : ces regles sont **techno-aware**. Pour de la pop/rock, elles
empirent le resultat (bass guitar peut monter a 1 kHz, vocals contient
de la vraie voix). A activer selon le genre.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

_STEMS = ("drums", "bass", "other", "vocals")

# Seuils par defaut
_BASS_HIGHPASS_HZ = 60.0
_BASS_LOWPASS_HZ = 500.0
_VOCALS_MERGE_RMS_DBFS = -40.0  # en dessous on considere vocals vide


def _butterworth(data: np.ndarray, sr: int, cutoff: float, mode: str, order: int = 4) -> np.ndarray:
    """Filtre Butterworth zero-phase via filtfilt."""
    from scipy.signal import butter, filtfilt
    nyq = sr * 0.5
    b, a = butter(order, cutoff / nyq, btype=mode)
    if data.ndim == 1:
        return filtfilt(b, a, data).astype(np.float32)
    # Multichannel : applique sur chaque colonne
    return np.column_stack([filtfilt(b, a, data[:, c]) for c in range(data.shape[1])]).astype(np.float32)


def _rms_dbfs(data: np.ndarray) -> float:
    if data.size == 0:
        return -120.0
    rms = float(np.sqrt(np.mean(data.astype(np.float64) ** 2)))
    if rms <= 0:
        return -120.0
    return float(20.0 * np.log10(rms))


def cleanup_techno(
    stems_dir: Path,
    bass_highpass_hz: float = _BASS_HIGHPASS_HZ,
    bass_lowpass_hz: float = _BASS_LOWPASS_HZ,
    vocals_merge_threshold_dbfs: float = _VOCALS_MERGE_RMS_DBFS,
) -> dict[str, str]:
    """Applique les regles techno aux 4 stems. Overwrite les fichiers.

    Retourne un dict {stem: action_appliquee} pour reporting."""
    import soundfile as sf

    actions: dict[str, str] = {}
    files = {s: stems_dir / f"{s}.wav" for s in _STEMS}
    for s, p in files.items():
        if not p.exists():
            actions[s] = "missing"
            return actions

    # Lecture
    audios: dict[str, tuple[np.ndarray, int]] = {}
    for s, p in files.items():
        data, sr = sf.read(str(p), always_2d=True, dtype="float32")
        audios[s] = (data, int(sr))

    sr = audios["bass"][1]

    # 1. Bass : highpass 60 Hz pour retirer sub-kick residuel
    bass_data = audios["bass"][0]
    bass_clean = _butterworth(bass_data, sr, bass_highpass_hz, "highpass")
    actions["bass"] = f"highpass {int(bass_highpass_hz)}Hz"

    # 2. Bass : lowpass 500 Hz pour retirer fuites de leads
    bass_clean = _butterworth(bass_clean, sr, bass_lowpass_hz, "lowpass")
    actions["bass"] = (
        f"highpass {int(bass_highpass_hz)}Hz + lowpass {int(bass_lowpass_hz)}Hz"
    )

    # 3. Vocals merge si quasi-silence
    vocals_data, _ = audios["vocals"]
    other_data, _ = audios["other"]
    vocals_rms = _rms_dbfs(vocals_data.mean(axis=1) if vocals_data.ndim == 2 else vocals_data)
    if vocals_rms < vocals_merge_threshold_dbfs:
        # Merger vocals dans other (avec gain neutre, somme sample-par-sample)
        if vocals_data.shape == other_data.shape:
            other_clean = (other_data + vocals_data).astype(np.float32)
            # Vocals devient silence (on garde le fichier pour coherence)
            vocals_clean = np.zeros_like(vocals_data)
            actions["other"] = f"merged vocals (rms={vocals_rms:.1f} dBFS < {vocals_merge_threshold_dbfs})"
            actions["vocals"] = "zeroed (merged into other)"
        else:
            other_clean = other_data
            vocals_clean = vocals_data
            actions["other"] = "unchanged (shape mismatch)"
            actions["vocals"] = "unchanged"
    else:
        other_clean = other_data
        vocals_clean = vocals_data
        actions["other"] = "unchanged"
        actions["vocals"] = f"unchanged (rms={vocals_rms:.1f} dBFS)"

    actions.setdefault("drums", "unchanged")

    # Ecriture (overwrite)
    sf.write(str(files["bass"]), bass_clean, sr, subtype="FLOAT")
    sf.write(str(files["other"]), other_clean, sr, subtype="FLOAT")
    sf.write(str(files["vocals"]), vocals_clean, sr, subtype="FLOAT")
    # drums non modifie

    return actions
