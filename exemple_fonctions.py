def sonner_cloche(i):
    test = True
    for j in cartes_joueurs[i]:
        test += (j == cartes_joueurs[i][0])
    if test:
        game_on = False
        liste_points[i] += 1

def afficher_cartes(i):
    
