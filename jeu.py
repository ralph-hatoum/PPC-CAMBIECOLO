import random
import threading
import os
import time
from multiprocessing import Process

import sysv_ipc

key = 129
keyConnexions = 150
keyReceiver = 130
os.system("ipcrm -Q 150")
os.system("ipcrm -Q 129")
os.system("ipcrm -Q 130")
connexions = sysv_ipc.MessageQueue(keyConnexions, sysv_ipc.IPC_CREAT)
receiver = sysv_ipc.MessageQueue(keyReceiver, sysv_ipc.IPC_CREAT)

connexion_time = True

mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

last_offer_id = 0

offers = {}

offers_locks = {}

point_list = [0, 0, 0, 0, 0]

offer_lock = threading.Lock()

playing = True

playing_lock = threading.Lock()

players = {}


class offre:
    def __init__(self, aId_offer, aId_player, aNumber_of_cards, aMotif):
        self.id_offer = aId_offer
        self.id_player = aId_player
        self.number_of_cards = aNumber_of_cards
        self.motif = aMotif
    def __str__(self):
        return "OFFER_ID = " + str(self.id_offer) + " for " + str(self.number_of_cards) + " cards"

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
                    mes = mes.encode()
                    print(id_player)
                    connexions.send(mes, type=1)
                    pl = threading.Thread(target=player, args=(id_player,))
                    players[id_player] = pl
        else:
            mes = "The game is running"
            mes = mes.encode()
            connexions.send(mes, type=1)
            print("tentative")


def player(id_player):

    # Cartes du joueur
    cards = ["plane", "plane", "plane", "plane", "plane"]

    # Intéraction avec le joueur

    while playing:
        print("Playing")
        interaction, _ = mq.receive(type=(id_player + 7))
        interaction = interaction.decode()
        print(interaction)

        if interaction == "sleep":
            time.sleep(10)

        if interaction == "ring_bell":
            ring_bell(cards, id_player, playing)

        if interaction == "make_offer":
            make_offer(id_player)

        if interaction == "accept_offer":
            accept_offer(id_player)

        if interaction == "display_offers":
            display_offers(id_player+2, mq)

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


def display_offers(t, message_queue):
    l = offers
    mes = "\n".join([str(offers[key]) for key in l])
    mes = mes.encode()
    print("message =", mes)
    message_queue.send(mes, type=t)
    print("Yes we did it")


def display_locks():
    print(offers_locks)


def make_offer(id_player):
    global last_offer_id
    res, _ = mq.receive(type=id_player+7)
    res = res.decode()
    offer = res.split(" ")
    number_of_cards = int(offer[0])
    pattern = offer[1]

    mes = "Offer accepted, you cannot touch the cards implied anymore"
    mes = mes.encode()
    mq.send(mes, type=id_player + 2)

    print("la ?")
    offer_lock.acquire()

    # On crée un identifiant d'offre
    last_offer_id = last_offer_id+1
    id_offer = last_offer_id

    # On creer une offre
    offer = offre(id_offer, id_player, number_of_cards, pattern)

    # On ajoute l'offre dans le dictionnaire global des offres
    offers[id_offer] = offer

    # On crée un lock pour cette offre
    offers_locks[id_offer] = threading.Lock()

    # On imprime la liste des offres pour bien montrer au joueur que son offre est ajoutée
    print("ici ?")
    for i in range(len(players)):
        display_offers(i+2, receiver)

    offer_lock.release()


def accept_offer(id_player):

    offer_accepted, _ = mq.receive(type=id_player+7)
    offer_accepted = offer_accepted.decode()
    print("l'offre que l'on veut accepter, et le motif en echange", offer_accepted)
    offer_a = offer_accepted.split(" ")
    offer_id = offer_a[0]
    pattern_to_exchange = offer_a[1]
    offer_id = int(offer_id)

    # On commence par récupérer l'offre
    offers_locks[offer_id].acquire()
    offer = offers[offer_id]

    # On récupère le nombre de cartes
    mes = str(offer.number_of_cards) + " " + str(offer.motif) + " " + str(offer.id_player)
    mes = mes.encode()
    mq.send(mes, type=id_player + 2)

    # On récupère la conclusion du joueur
    conclusion, _ = mq.receive(type=id_player+7)
    conclusion = conclusion.decode()
    if conclusion == "NO_DEAL":
        print("NO DEAL")
        return None
    else :
        print("Ok offer accepted")
        print("Joueur dont on prend l'offre : ", str(offer.id_player))
        print("Motif donné par celui qui a crée l'offre :", str(offer.motif))
        print("Nombre de cartes :", str(offer.number_of_cards))
        print("Joueur qui accepte l'offre : ", str(id_player))
        print("Motif donné par celui qui accepte :", str(pattern_to_exchange))

        # On previens le joueur que son offre est accepté
        mes = str(offer.motif) + " " + str(pattern_to_exchange) + " " + str(offer.number_of_cards)
        mes = mes.encode()
        receiver.send(mes, type=offer.id_player + 2)

        # On supprime cette offre
        offer_lock.acquire()
        offers.pop(offer_id)

        # On release les locks
        offer_lock.release()
        offers_locks[offer_id].release()

        return "Offer accepted"

"""
        for i in range(nb_cards):
            if card_list[i] == pattern_to_exchange:
                card_list.pop(i)
        print(card_list)
        for i in range(nb_cards):
            card_list.append(offer[0])
        print(card_list)
        mq.send("Accepted," + offer[0] + "," + pattern_to_exchange + "," + nb_cards)
"""


def distrib_cartes(nb_joueurs):
    motifs = ["plane", "car", "train", "bike", "shoes"]

    motifs = motifs[0:nb_joueurs]

    tas_de_cartes = []

    for i in motifs:
        for j in range(5):
            tas_de_cartes.append(i)

    cards = [""] *5

    for i in range(nb_joueurs):
        for j in range(5):
            ranCard = random.randint(0, len(tas_de_cartes) - 1)
            cards[i] += tas_de_cartes[ranCard]
            if j != 4:
                cards[i] += ";"
            tas_de_cartes.pop(ranCard)

    return cards


if __name__ == "__main__":

    conThread = threading.Thread(target=connexion_receiver)
    conThread.start()
    time.sleep(5)
    connexion_time = False
    print("FIN DES INSCRIPTIONS")
    print(players)
    cards = distrib_cartes(len(players))
    for i in range(len(players)):
        mq.send(cards[i], type=i+2)
        players[i].start()

