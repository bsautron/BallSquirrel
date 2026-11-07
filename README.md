# BallSquirrel

Un écureuil saute vers la souris pour attraper des glands en plein vol.

- Les glands arrivent aléatoirement depuis les côtés et rebondissent sur le sol et les bords.
- Clic gauche : l'écureuil (s'il est au sol) saute vers le curseur. Plus le clic est loin, plus le saut est puissant. Les pointillés montrent la trajectoire.
- Toucher un gland en plein vol le fait disparaître et rapporte 3 points. Un gland qui touche le sol est raté : il devient transparent, et l'attraper ensuite fait perdre un point (-1).

Touches : `R` rejouer, `P`/`Espace` pause, `Échap` quitter.

## Lancer

```sh
./play
```

Le premier lancement crée un environnement Python (`.venv`) et installe `pygame-ce`. Il faut Python 3.10 ou plus.

## Organisation

- `ballsquirrel/physics.py` : gravité, rebonds sol/bords, collisions (sans pygame).
- `ballsquirrel/game.py` : règles (écureuil, apparition des glands, score). Simulation à pas fixe et graine aléatoire, utilisable sans fenêtre.
- `ballsquirrel/app.py` : fenêtre, rendu, souris.

Tests : `.venv/bin/python -m unittest discover -s tests -t .`
