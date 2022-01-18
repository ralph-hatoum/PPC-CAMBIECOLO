import random
import threading
import os
import time
from multiprocessing import Process, Manager, Lock, Value

import sysv_ipc

key = 129
keyConnexions = 150
keyReceiver = 130

connexion_time = True
connexions = sysv_ipc.MessageQueue(keyConnexions, sysv_ipc.IPC_CREAT)
receiver = sysv_ipc.MessageQueue(keyReceiver, sysv_ipc.IPC_CREAT)
mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

len_player = 0

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
        return (
            "\033[36mOFFER_ID = "
            + str(self.id_offer)
            + "\033[0m for \033[91m\033[1m"
            + str(self.number_of_cards)
            + " cards\033[0m"
        )


def getNumber():
    while True:
        print("How many games do you want to play ?")
        try:
            i = int(input())
            if i > 0:
                return i
        except ValueError:
            print("", end="")

# con
def connexion_receiver():
    global players, len_player
    id_player = -1
    while True:
        message, _ = connexions.receive(type=2)
        message = message.decode()
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
                    connexions.send(mes, type=1)
                    len_player += 1
        else:
            mes = "The game is running"
            mes = mes.encode()
            connexions.send(mes, type=1)
            print("tentative")


def player(id_player, offers_dict, offers_lock_dict, last_offer_id, len_player, last_offer_id_lock):

    # Intéraction avec le joueur

    while playing:
        interaction, _ = mq.receive(type=(id_player + 7))
        interaction = interaction.decode()

        if interaction == "sleep":
            time.sleep(10)

        if interaction == "ring_bell":
            ring_bell(id_player, len_player)

        if interaction == "make_offer":
            make_offer(id_player, offers_dict, offers_lock_dict, last_offer_id, len_player, last_offer_id_lock)

        if interaction == "accept_offer":
            accept_offer(id_player, offers_dict, offers_lock_dict)

        if interaction == "display_offers":
            display_offers(id_player + 2, mq, offers_dict)

        if interaction == "display_locks":
            display_locks()


def ring_bell(id_player, len_player):
    global playing
    # On récupère la conclusion du joueur
    conclusion, _ = mq.receive(type=id_player + 7)
    conclusion = conclusion.decode()
    if conclusion == "WON":
        playing_lock.acquire()
        playing = False
        for i in range(len_player):
            print(i)
            message = "player "+ str(id_player) +" won"
            message = message.encode()
            receiver.send(message, type = i+2)
        print("on a tout send")


        playing_lock.release()


def display_offers(t, message_queue, offers_dict):
    mes = "\n".join([str(offers_dict[key]) for key in offers_dict.keys()])
    mes = mes.encode()
    message_queue.send(mes, type=t)


def display_locks():
    print(offers_locks)


def make_offer(id_player, offers_dict, offers_lock_dict, last_offer_id, nbr_players, last_offer_id_lock):

    res, _ = mq.receive(type=id_player + 7)
    res = res.decode()
    offer = res.split(" ")
    number_of_cards = int(offer[0])
    pattern = offer[1]

    mes = "Offer accepted, you cannot touch the cards implied anymore"
    mes = mes.encode()
    mq.send(mes, type=id_player + 2)

    offer_lock.acquire()

    # On crée un identifiant d'offre
    with last_offer_id_lock:
        last_offer_id[0] += 1

    id_offer = last_offer_id[0]

    # On creer une offre
    offer = offre(id_offer, id_player, number_of_cards, pattern)

    # On ajoute l'offre dans le dictionnaire global des offres
    offers_dict[id_offer] = offer

    # On crée un lock pour cette offre
    offers_lock_dict[id_offer] = Manager().Lock()

    # On imprime la liste des offres pour bien montrer au joueur que son offre est ajoutée
    print()
    for i in range(nbr_players):
        display_offers(i + 2, receiver, offers_dict)

    offer_lock.release()


def accept_offer(id_player, offers_dict, offers_lock_dict):

    offer_accepted, _ = mq.receive(type=id_player + 7)
    offer_accepted = offer_accepted.decode()
    offer_a = offer_accepted.split(" ")
    offer_id = offer_a[0]
    pattern_to_exchange = offer_a[1]
    offer_id = int(offer_id)

    # On commence par récupérer l'offre
    # offers_lock_dict[offer_id].acquire()
    offer = offers_dict[offer_id]

    # On récupère le nombre de cartes
    mes = (
        str(offer.number_of_cards) + " " + str(offer.motif) + " " + str(offer.id_player)
    )
    mes = mes.encode()
    mq.send(mes, type=id_player + 2)

    # On récupère la conclusion du joueur
    conclusion, _ = mq.receive(type=id_player + 7)
    conclusion = conclusion.decode()
    if conclusion == "NO_DEAL":
        print("NO DEAL")
        return None
    else:
        # On previens le joueur que son offre est accepté
        mes = (
            str(offer.motif)
            + " "
            + str(pattern_to_exchange)
            + " "
            + str(offer.number_of_cards)
        )
        mes = mes.encode()
        receiver.send(mes, type=offer.id_player + 2)

        # On supprime cette offre
        offer_lock.acquire()
        offers_dict.pop(offer_id)

        # On release les locks
        offer_lock.release()
        # offers_lock_dict[offer_id].release()

        return "Offer accepted"


def distrib_cartes(nb_joueurs):
    motifs = ["plane", "car", "train", "bike", "shoes"]

    motifs = motifs[0:nb_joueurs]

    tas_de_cartes = []

    for i in motifs:
        for j in range(5):
            tas_de_cartes.append(i)

    cards = [""] * 5

    for i in range(nb_joueurs):
        for j in range(5):
            ranCard = random.randint(0, len(tas_de_cartes) - 1)
            cards[i] += tas_de_cartes[ranCard]
            if j != 4:
                cards[i] += ";"
            tas_de_cartes.pop(ranCard)

    return cards


if __name__ == "__main__":
    os.system("ipcrm -Q 150")
    os.system("ipcrm -Q 129")
    os.system("ipcrm -Q 130")

    print("WELCOME")

    nb_games = getNumber()

    connexions = sysv_ipc.MessageQueue(keyConnexions, sysv_ipc.IPC_CREAT)
    receiver = sysv_ipc.MessageQueue(keyReceiver, sysv_ipc.IPC_CREAT)
    mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

    manager_offres = Manager()
    manager_offres_locks = Manager()

    offers = manager_offres.dict()
    offers_locks = manager_offres_locks.dict()

    last_offer_id_lock = Lock()

    last_offer_manager = Manager()
    last_offer_id = last_offer_manager.list([0])

    conThread = threading.Thread(target=connexion_receiver)
    conThread.start()
    time.sleep(10)
    connexion_time = False
    print("FIN DES INSCRIPTIONS")
    cards = distrib_cartes(len_player)

    for i in range(len_player):
        pl = Process(target=player, args=(i, offers, offers_locks, last_offer_id, len_player, last_offer_id_lock))
        players[i] = pl
        mq.send(cards[i], type=i + 2)
        pl.start()