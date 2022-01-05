import random
import threading
import time

import sysv_ipc

key = 129
keyConnexions = 150

connexions = sysv_ipc.MessageQueue(keyConnexions, sysv_ipc.IPC_CREAT)
mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

offers = {}

offers_locks = {}

point_list = [0, 0, 0, 0, 0]

offer_lock = threading.Lock()

playing = True

playing_lock = threading.Lock()


def player(id):

    def finish_deal(message, card_list):
        mes = message.split(",")
        for i in range(mes[3]):
            if card_list[i] == mes[1]:
                card_list.remove(i)
        print(card_list, "id :", id)
        for i in range(mes[3]):
            card_list.append(mes[2])
        print(card_list, "id :", id)

    def message_receiver(id, card_list):
        while True:
            message, _ = mq.receive()
            message = message.decode()
            print(message, "id :", id)
            if message.startswith("Accepted"):
                finisher = threading.Thread(target=finish_deal, args=(message, card_list))
                finisher.start()

    # Cartes du joueur
    cards = ["plane", "car", "car", "train", "plane"]

    message_receiver = threading.Thread(target=message_receiver, args=(id, cards))
    message_receiver.start()

    # Intéraction avec le joueur

    while playing:
        interaction = input("Que voulez vous faire ? id :" + str(id))

        if interaction == "sleep":
            time.sleep(1)

        if interaction == "ring_bell":
            ring_bell(cards, id, playing)

        if interaction == "display_cards":
            display_cards(cards)

        if interaction == "make_offer":
            pattern = input("Entrez le motif que vous voulez échanger id :" + str(id))
            number = int(input("Entrez le nombre de cartes id :" + str(id)))
            make_offer(cards, pattern, number, id)

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


def display_cards(card_list):
    print(card_list)


def display_offers():
    print(offers)


def display_locks():
    print(offers_locks)


def make_offer(card_list, pattern, number_of_cards, id_player):

    # On vérifie d'abord que l'offre ne contient pas plus de 3 cartes (contrainte donnée dans le sujet)
    if number_of_cards > 3:
        print("You can't do that", "id :", id_player)
        return None
    # Ensuite, on vérifie que le joueur a bien les cartes qu'il veut échanger
    k = 0

    # On compte les cartes du motif donné dans le jeu du joueur
    for i in card_list:
        if i == pattern:
            k += 1

    # On teste si le nombre de cartes offertes est inféreur ou égal au nombre de cartes du même motif présentes dans le jeu du joueur
    test = number_of_cards <= k
    # Si c'est le cas, alors on peut échanger les cartes
    if test:
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
        print("You can't do that", "id :", id_player)


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
        mq.send("Accepted,"+offer[0]+","+pattern_to_exchange+","+nb_cards)

    return "Offer accepted"


if __name__ == "__main__":
    players = [(threading.Thread(target=player, args=(i,))) for i in range(2)]
    for p in players:
        p.start()
