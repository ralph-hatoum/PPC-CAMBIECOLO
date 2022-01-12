import random
import threading
import os
import time
from multiprocessing import Process

import sysv_ipc

key = 129
keyConnexions = 150
os.system("ipcrm -Q 150")
connexions = sysv_ipc.MessageQueue(keyConnexions, sysv_ipc.IPC_CREAT)

connexion_time = True

mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

offers = {}

offers_locks = {}

point_list = [0, 0, 0, 0, 0]

offer_lock = threading.Lock()

playing = True

playing_lock = threading.Lock()

players = {}


# con
def connexion_receiver():
    global players
    id_player = -1
    while True:
        message, _ = connexions.receive(type=2)
        message = message.decode()
        print(message)
        if connexion_time:
            if message == "request_player":
                id_player += 1
                if id_player > 4:
                    mes = "no"
                    mes = mes.encode()
                    connexions.send(mes, type=1)
                    print("NO")
                else:
                    mes = str(id_player)
                    print(mes, "= mes")
                    mes = mes.encode()
                    print(mes, "= mesDECODE")
                    print(id_player)
                    connexions.send(mes, type=1)
                    pl = threading.Thread(target=player, args=(id_player,))
                    players[id_player] = pl
        else:
            mes = "The game is running"
            mes = mes.encode()
            connexions.send(mes, type=1)
            print("tentative")


def player(id):
    # Cartes du joueur
    cards = ["plane", "plane", "plane", "car", "car"]

    # Intéraction avec le joueur

    while playing:
        print("Playing")

        interaction, _ = mq.receive(type=(id + 7))
        interaction = interaction.decode()
<<<<<<< HEAD
        print(interaction, "INTe")
=======
>>>>>>> a3f73dcfa1c540efb759eaed70da7649714b357f

        if interaction == "sleep":
            time.sleep(10)

        if interaction == "ring_bell":
            ring_bell(cards, id, playing)

        if interaction == "display_cards":
            display_cards(id, cards)

        if interaction == "make_offer":
            make_offer(id, cards)

        if interaction == "accept_offer":
            number_id = input("Entrez l'identifiant de l'offre id :" + str(id))
            accept_offer(int(number_id), cards, id)

        if interaction == "display_offers":
            display_offers()

        if interaction == "display_locks":
            display_locks()


def ring_bell(card_list, player, playing):
    # Pour sonner la cloche et signaler qu'on (pense) avoir gagné

    playing_lock.acquire()
    test = True
    # On regarde si toutes les cartes sont identiques
    for i in card_list:
        if i != card_list[0]:
            test = False
    # Si c'est le cas, on arrête le jeu
    if test:
        playing = False
    # Sinon, on signale que le joueur n'a pas 5 cartes identiques, le jeu reprend
    else:
        print("Vous n'avez pas 5 cartes identiques", "id :", id)
    playing_lock.release()


def display_cards(id, card_list):
    l = card_list
    mes = ",".join([_ for _ in l])
    mes = mes.encode()
    mq.send(mes, type=(id + 2))


def display_offers():
    print(offers)


def display_locks():
    print(offers_locks)


def make_offer(id, cards):
    mes = "Quelle offre voulez-vous faire [Nbr Motif]"
    mes = mes.encode()
    mq.send(mes, type=id+2)

    res, _ = mq.receive(type=id+7)
    res = res.decode()
    offer = res.split(" ")
    number_of_cards = offer[0]
    pattern = offer[1]

    # On vérifie d'abord que l'offre ne contient pas plus de 3 cartes (contrainte donnée dans le sujet)
    if number_of_cards > 3:
        mes = "You can't do that, 3 cards maximum"
        mes = mes.encode()
        mq.send(mes, type=id+2)
        return None

    # Ensuite, on vérifie que le joueur a bien les cartes qu'il veut échanger
    k = 0

    # On compte les cartes du motif donné dans le jeu du joueur
    for i in cards:
        if i == pattern:
            k += 1

    # On teste si le nombre de cartes offertes est inféreur ou égal au nombre de cartes du même motif présentes dans le jeu du joueur
    test = number_of_cards <= k
    # Si c'est le cas, alors on peut échanger les cartes
    if test:
        mes = "Offer accepted, you cannot touch the cards implied anymore"
        mes = mes.encode()
        mq.send(mes, type=id + 2)

        offer_lock.acquire()
        # On code l'offre, sous la forme "motif, nombre_de_cartes"
        offer = pattern + "," + str(number_of_cards) + "," + str(id_player) + ", OFFER"

        # On crée un identifiant d'offre
        id = len(offers) + 1

        # On ajoute l'offre dans le dictionnaire global des offres
        offers[id] = offer

        # On crée un lock pour cette offre
        offers_locks[id] = threading.Lock()

        # On imprime la liste des offres pour bien montrer au joueur que son offre est ajoutée
        print(offers)
    else:
        # Si les condition n'étaient pas vérifiées, on ne peut pas faire l'échange
        mes = "You can't do that, You don't have the cards"
        mes = mes.encode()
        mq.send(mes, type=(id + 2))


def accept_offer(offer_id, card_list, id_player):

    # On commence par récupérer l'offre
    offers_locks[offer_id].acquire()
    offer = offers[offer_id]

    # On transforme la chaine de caractère qui représente l'offre en liste de la forme [motif, nb_cartes]
    offer = offer.split(",")

    # On vérifie que le joueur n'accepte pas sa propre offre
    if id_player == offer[2]:
        print("Vous ne pouvez pas accepter votre propre offre", "id :", id_player)
        return None

    # On récupère le nombre de cartes
    nb_cards = int(offer[1])

    # On demande au joueur d'entrer les cartes à échanger (séparées par des espaces)
    pattern_to_exchange = input("Entrez le motif à echanger id :" + str(id_player))

    # On compte le nombre de carte du motif que le joueur veut echanger
    cards_counter = 0
    for i in card_list:
        if i == pattern_to_exchange:
            cards_counter += 1

    # On check si le deal peut etre respecte
    test = cards_counter >= nb_cards

    # test
    if test:
        for i in range(nb_cards):
            if card_list[i] == pattern_to_exchange:
                card_list.pop(i)
        print(card_list)
        for i in range(nb_cards):
            card_list.append(offer[0])
        print(card_list)
        mq.send("Accepted," + offer[0] + "," + pattern_to_exchange + "," + nb_cards)

    return "Offer accepted"


def distrib_cartes(nb_joueurs):

    motifs = ["plane", "car", "train", "bike", "shoes"]

    motifs = motifs[0:nb_joueurs]

    tas_de_cartes = []

    for i in motifs:
        for j in range(5):
            tas_de_cartes.append(i)

    cartes = {i: [] for i in range(nb_joueurs)}

    for i in range(nb_joueurs):
        for j in range(5):
            cartes[i].append(motifs[random.randint(0, len(motifs) - 1)])
    return cartes


if __name__ == "__main__":

    conThread = threading.Thread(target=connexion_receiver)
    conThread.start()
    time.sleep(3)
    connexion_time = False
    print("FIN DES INSCRIPTIONS")
    print(players)
    all_players_cards = distrib_cartes(len(players))
    mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

    for i in range(len(players)):
        players[i].start()
