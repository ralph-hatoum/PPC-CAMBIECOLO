import random

nb_joueurs = 3

motifs = ["plane","car", "train", "bike", "shoes"]

cartes = []
cartes_joueurs = []

for i in range(nb_joueurs):
    cartes_joueurs.append([])
    for j in range(5):
        cartes.append(motifs[i])

#print(cartes)

for i in range(len(cartes_joueurs)):
    for j in range(5):
        k = random.randint(0,len(cartes)-1)
        print(k)
        print(i)
        print(j)
        cartes_joueurs[i][j] = cartes[k]
        cartes.pop(k)

print(cartes_joueurs)

