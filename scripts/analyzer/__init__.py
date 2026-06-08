"""Analyzer audiophile — Phase 1 : qualite audio.

Modules :
- audio_loader : decode l'audio en numpy float32
- metadata     : codec / bitrate / sample rate / bit depth via ffprobe
- signal       : sample peak / true peak / clipping
- loudness     : LUFS integre + loudness range (pyloudnorm)
- dynamic      : crest factor + categorie dynamique
- spectral     : bandwidth detection + fake-lossless probability
- scoring      : score audiophile pondere
- report       : rendu terminal + JSON sidecar
"""
from __future__ import annotations
