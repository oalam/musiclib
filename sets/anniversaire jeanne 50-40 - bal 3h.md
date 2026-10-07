# Anniversaire Jeanne (50) et sa soeur (40) — bal old school, 3h

Set 1 sur 2 : playlist bal de village (swing, soul, rock, tango, latino, folk,
disco, danses de mariage). Duree : 20+20+30+15+20+30+25+30+15 = 205 min (~3h25,
a degraisser pour tenir 3h).
Chaque bloc = un sous-dossier `library/audio/<style>/` (flag `--folder` de grab.py).

## 1. Swing / retro — 20 min — `--folder swing`

- Glenn Miller — In the Mood
- Benny Goodman — Sing, Sing, Sing
- Louis Prima — Just a Gigolo / I Ain't Got Nobody
- The Andrews Sisters — Boogie Woogie Bugle Boy
- Django Reinhardt — Minor Swing
- Ray Charles — Mess Around

## 2. Soul 60s — 20 min — `--folder soul`

- The Contours — Do You Love Me
- Wilson Pickett — Land of 1000 Dances
- Sam & Dave — Soul Man
- Aretha Franklin — Respect
- James Brown — I Got You (I Feel Good)
- Ike & Tina Turner — Proud Mary

## 3. Rock'n'roll / twist — 30 min — `--folder rock`

- Bill Haley — Rock Around the Clock
- Elvis Presley — Jailhouse Rock
- Chuck Berry — Johnny B. Goode
- Jerry Lee Lewis — Great Balls of Fire
- Little Richard — Tutti Frutti
- Chubby Checker — Let's Twist Again
- Les Chats Sauvages — Twist à Saint-Tropez
- Dion — Runaround Sue
- The Beatles — Twist and Shout
- Status Quo — Rockin' All Over the World

## 4. Tango — 15 min — `--folder tango`

- Juan D'Arienzo — La Cumparsita
- Carlos Gardel — Por una cabeza
- Astor Piazzolla — Libertango
- Alibert — Le Plus Beau Tango du monde
- Gotan Project — Santa María (del Buen Ayre)

## 5. Cha-cha / latino — 20 min — `--folder latino`

- Tito Puente — Oye Como Va (ou la version Santana)
- Dean Martin — Sway (Quién Será)
- Tommy Dorsey Orchestra — Tea for Two Cha Cha
- Pérez Prado — Mambo No. 5
- Miriam Makeba — Pata Pata
- Ritchie Valens — La Bamba
- Compay Segundo — Chan Chan (respiration)

## 6. Folk / bal trad — 30 min — `--folder folk`

Amorce chansons connues :
- Hugues Aufray — Santiano
- Tri Yann — La Jument de Michao (se danse en an dro)
- Alan Stivell — Tri Martolod
- Manau — La Tribu de Dana (meme melodie que Tri Martolod, enchainer)

Danses collectives guidees (le titre importe peu, prendre un enregistrement
de bal folk et valider a l'ecoute — Blowzabella, Ciac Boum, Duo Artense…) :
- Un cercle circassien
- Une chapelloise (Aleman's marsj)
- Une scottish (si le public suit)
- Un an dro fest-noz (Sonerien Du ou Startijenn)

Rappel pratique : montrer les pas du cercle circassien et de la chapelloise
au micro avant de lancer, sinon seule l'amorce fonctionne.

## 7. Disco — 25 min — `--folder disco`

Orientation deep cuts (Salsoul, boogie, disco francais) plutot que tubes :
- Cerrone — Supernature (ancrage reconnaissable)
- Sylvester — You Make Me Feel (Mighty Real)
- Cheryl Lynn — Got to Be Real
- Dan Hartman — Relight My Fire
- Voyage — From East to West (disco francais meconnu)
- MFSB — Love Is the Message (l'instrumental fondateur, Philadelphie)
- Double Exposure — Ten Percent (Salsoul)
- Instant Funk — I Got My Mind Made Up

En reserve :
- Karen Young — Hot Shot
- Loleatta Holloway — Love Sensation (LA voix samplee partout)
- Patrice Rushen — Forget Me Nots (boogie 82)
- Kano — I'm Ready (italo, pont possible vers le set 2 electronique)
- Patrick Hernandez — Born to Be Alive (filet de securite si la piste decroche)

## 8. Danses universelles de mariage — 30 min — `--folder mariage`

- Claude François — Alexandrie Alexandra (madison)
- Village People — YMCA
- Los del Río — Macarena
- La Bande à Basile — La Chenille
- Las Ketchup — Aserejé (The Ketchup Song)
- Rednex — Cotton Eye Joe
- Kool & the Gang — Celebration
- Earth, Wind & Fire — September
- Gloria Gaynor — I Will Survive
- Boney M — Rasputin
- Émile & Images — Les Démons de minuit
- Whigfield — Saturday Night

En reserve si la piste est pleine :
- ABBA — Dancing Queen
- Bee Gees — Stayin' Alive
- Ottawan — D.I.S.C.O.
- John Travolta & Olivia Newton-John — You're the One That I Want

## 9. Slows et cloture — 15 min — `--folder slow`

- Bill Medley & Jennifer Warnes — (I've Had) The Time of My Life (transition)
- The Righteous Brothers — Unchained Melody
- Elvis Presley — Can't Help Falling in Love
- The Platters — Only You
- Johnny Hallyday — Que je t'aime
- Michel Sardou — Les Lacs du Connemara (cloture du bal)

## Telechargement

Un bloc = une commande, exemple pour le swing :

```bash
cd scripts
python3 grab.py --folder swing "Glenn Miller In the Mood
Benny Goodman Sing Sing Sing
Louis Prima Just a Gigolo I Ain't Got Nobody
The Andrews Sisters Boogie Woogie Bugle Boy
Django Reinhardt Minor Swing
Ray Charles Mess Around"
```
