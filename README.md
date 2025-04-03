# BTC PUZZLE SOLVER

## Description
Un outil en Python pour tenter de résoudre les "Bitcoin Puzzles" en recherchant des clés privées correspondant à des adresses Bitcoin spécifiques. Le programme utilise une approche multi-processus et génère des clés privées aléatoirement dans une plage définie.

## Fonctionnalités
- Recherche de clés privées par génération aléatoire
- Traitement multi-cœur pour optimiser les performances
- Support pour 37 puzzles Bitcoin différents (puzzles #21 à #160)
- Affichage en temps réel des performances (clés/seconde)
- Notification sonore quand une clé est trouvée

## Prérequis
- Python 3.x
- Bibliothèques requises:
  - bit==0.8.0
  - pandas==2.2.0

## Installation
1. Clonez ce dépôt
2. Installez les dépendances:
   ```
   pip install -r requirements.txt
   ```

## Utilisation
Exécutez le script principal:
```
python main_enhanced.py
```

Le programme vous demandera:
1. Le numéro du puzzle à résoudre (1-160)
2. Le nombre de cœurs CPU à utiliser

## Structure des données
Les données des puzzles sont stockées dans `data/puzzles_data.csv` avec les informations suivantes:
- `puzzle_number`: Numéro du puzzle
- `hex`: Adresse Bitcoin cible
- `start_key`: Début de la plage de recherche (en hexadécimal)
- `stop_key`: Fin de la plage de recherche (en hexadécimal)

## Note importante
La probabilité de trouver une clé privée valide est extrêmement faible. Ce projet est principalement éducatif pour comprendre le fonctionnement des clés Bitcoin et les probabilités associées.
