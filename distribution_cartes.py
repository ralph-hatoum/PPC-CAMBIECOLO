import random


def distrib_cartes():
    nb_joueurs = 5

    motifs = ["plane", "car", "train", "bike", "shoes"]

    motifs = motifs[0:nb_joueurs]

    tas_de_cartes = []

    for i in motifs:
        for j in range(5):
            tas_de_cartes.append(i)

    cartes = [[] for i in range(nb_joueurs)]

    for i in range(nb_joueurs):
        for j in range(5):
            cartes[i].append(motifs[random.randint(0, len(motifs) - 1)])
