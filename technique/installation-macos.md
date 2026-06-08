---
tags: [technique, install, macos]
---

# Installation TidalCycles sur macOS

Tidal a quatre couches : SuperCollider (moteur audio), SuperDirt (banque de sons + interface OSC), Haskell + Tidal (langage de patterns), un éditeur (VS Code, Pulsar, Vim, Emacs).

## 1. SuperCollider + SuperDirt

```bash
brew install --cask supercollider
```

Lancer SuperCollider une fois (l'app), puis dans la fenêtre de code :

```supercollider
Quarks.checkForUpdates({ Quarks.install("SuperDirt", "v1.7.3"); thisProcess.recompile() })
```

Recompiler la classe (Language → Recompile Class Library), puis pour démarrer le serveur audio :

```supercollider
SuperDirt.start
```

Garder ces deux lignes dans un `start-superdirt.scd` à lancer avant chaque session.

## 2. Haskell + Tidal

Via [ghcup](https://www.haskell.org/ghcup/) :

```bash
curl --proto '=https' --tlsv1.2 -sSf https://get-ghcup.haskell.org | sh
ghcup install ghc recommended
ghcup install cabal recommended
ghcup set ghc recommended
cabal update
cabal install tidal --lib
```

## 3. Éditeur

VS Code + extension `tidalcycles` (Charlie Roberts). Ouvrir un fichier `.tidal`, lancer `Tidal: Boot Tidal` (Cmd+Shift+P), taper du code, `Shift+Enter` pour évaluer un bloc.

Alternative : [Pulsar](https://pulsar-edit.dev/) avec le package `tidalcycles` (fork d'Atom maintenu).

## 4. Vérif

Avec SuperDirt qui tourne, dans un fichier `.tidal` :

```haskell
d1 $ s "bd cp sn cp"
```

Si ça boume, c'est bon. Sinon : checker que SuperDirt a bien démarré et que le port OSC 57120 est libre.

## Pièges connus

- **macOS Sonoma+** : pas de son → vérifier les permissions audio pour SuperCollider dans Réglages Système → Confidentialité.
- **JACK** : pas nécessaire sur macOS, CoreAudio suffit.
- **Latence** : régler `s.options.hardwareBufferSize = 256` avant `SuperDirt.start`.
- **CPU qui chauffe en set long** : alléger les chaînes d'effets, éviter `room` sur 8 canaux à la fois.

#install #macos
