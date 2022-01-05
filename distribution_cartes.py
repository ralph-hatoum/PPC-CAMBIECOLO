import random

nb_joueurs = 3

motifs = ["plane", "car", "train", "bike", "shoes"]

motifs = motifs[0:nb_joueurs]

tas_de_cartes = []

for i in motifs:
    for j in range(5):
        tas_de_cartes.append(i)

cartes = [[] for i in range(nb_joueurs)]
