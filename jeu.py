import random
import sys
import threading
import os
import time
from multiprocessing import Process, Manager, Lock, Value

import sysv_ipc

key = 129
keyConnexions = 150
keyReceiver = 130

connexion_time = True

# 3 MessageQueues :
# 1 pour gerer les connexions
connexions = sysv_ipc.MessageQueue(keyConnexions, sysv_ipc.IPC_CREAT)
# 1 pour envoyer des messages spontanement
receiver = sysv_ipc.MessageQueue(keyReceiver, sysv_ipc.IPC_CREAT)
# 1 pour communiquer et interagir avec le joueur
mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
# FONCTIONNEMENT : Pour que tous les joueurs utilisent la meme MQ mais ne lisent que leur message, on utilise les types
# Lorsqu'un joueur veut envoyer un message vers son processus - > il utilise le type ID + 7
# Lorsque le processus joueur veut envoyer un message vers le joueur - > il utilise le type ID + 2
# Pour les connexion, demande de connexion - > type 2 // reponse - > type 1

len_player = 0

point_list = [0, 0, 0, 0, 0]

offer_lock = threading.Lock()

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


# Ce Thread tourne en arriere plan pour gerer toute demande de connexion n'importe quel moment (d'ou le Daemon)
class Connexion_receiver(threading.Thread):
    daemon = True

    def run(self):
        global players, len_player, stop_thread
        id_player = -1
        while True:
            # Reception d'une demande
            message, _ = connexions.receive(type=2)
            message = message.decode()
            if connexion_time:
                # Si on est encore dans une période de connexion
                if message == "request_player":
                    id_player += 1
                    if id_player > 4:
                        # Si on est trop de joueur, on refuse la connexion
                        mes = "no"
                        mes = mes.encode()
                        connexions.send(mes, type=1)
                        print("NO")
                    else:
                        # On envoie au joueur son ID si on accepte sa connexion
                        mes = str(id_player)
                        mes = mes.encode()
                        connexions.send(mes, type=1)
                        len_player += 1
            else:
                # Le jeu est deja lance, on previent le joueur
                mes = "The game is running"
                mes = mes.encode()
                connexions.send(mes, type=1)
                print("tentative")


# Chaque joueur, lance son process qui permet d'interagir et de jouer
def player(id_player, offers_dict, last_offer_id, last_offer_id_lock, len_player, playing, is_available_dic):
    while playing.value == 1:
        # Tant que personne n'a gagne

        # On recupere l'action du joueur
        interaction, _ = mq.receive(type=(id_player + 7))
        interaction = interaction.decode()

        if interaction == "ring_bell":
            ring_bell(id_player, len_player, playing)

        if interaction == "make_offer":
            make_offer(id_player, offers_dict, last_offer_id, last_offer_id_lock, len_player, is_available_dic)

        if interaction == "accept_offer":
            accept_offer(id_player, offers_dict, is_available_dic)

        if interaction == "display_offers":
            display_offers(id_player + 2, mq, offers_dict)

        if interaction == "display_locks":
            display_locks()


# Le joueur sonne la cloche quand il a 5 cartes identiques
def ring_bell(id_player, len_player, playing):
    # On récupère la conclusion du joueur
    conclusion, _ = mq.receive(type=id_player + 7)
    conclusion = conclusion.decode()
    if conclusion == "WON":
        # Si le joueur a effectivement 5 cartes identiques

        # On stop le jeu
        playing.value = 0

        # 2 joueurs peuvent terminer et sonner la cloche en meme temps alors on accede a un lock sur la cloche
        playing_lock.acquire()

        for i in range(len_player):
            # On previent chaque joueur que joueur k a gagne par message spontanee (on utilise receiver comme MQ)
            message = "player " + str(id_player) + " won"
            message = message.encode()
            receiver.send(message, type=i + 2)
        playing_lock.release()
    # Sinon, on signale que le joueur n'a pas 5 cartes identiques, le jeu reprend


def display_offers(t, message_queue, offers_dict):
    mes = "\n".join([str(offers_dict[key]) for key in offers_dict.keys()])
    mes = mes.encode()
    message_queue.send(mes, type=t)


def display_locks():
    print(offers_locks)


def make_offer(id_player, offers_dict, last_offer_id, last_offer_id_lock, nbr_players, is_available_dic):
    # On recoit l'offre du joueur, si elle n'est pas valable, on recoit "no"
    res, _ = mq.receive(type=id_player + 7)
    res = res.decode()
    if res == "no":
        return None

    # Decomposition de l'offre
    offer = res.split(" ")
    number_of_cards = int(offer[0])
    pattern = offer[1]

    # On previent le joueur que l'offre est acceptee
    mes = "Offer accepted, you cannot touch the cards implied anymore"
    mes = mes.encode()
    mq.send(mes, type=id_player + 2)

    # Les offres sont stockees dans un dictionnaire, plusieurs process joueur peuvent y ecrire en meme temps, on
    # passe alors par un lock pour eviter tout probleme
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
    is_available_dic[id_offer] = True

    # On imprime la liste des offres pour bien montrer au joueur que son offre est ajoutée
    for i in range(nbr_players):
        display_offers(i + 2, receiver, offers_dict)

    offer_lock.release()


def accept_offer(id_player, offers_dict, is_available_dic):
    offer_id, _ = mq.receive(type=id_player + 7)
    offer_id = offer_id.decode()
    offer_id = int(offer_id)

    try:
        if is_available_dic[offer_id] == True:
            is_available_dic[offer_id] = False
            mes = "YUP".encode()
            mq.send(mes, type=id_player + 2)

        elif is_available_dic[offer_id] == False:
            mes = "NOPE".encode()
            mq.send(mes, type=id_player + 2)
            return None

        offer_accepted, _ = mq.receive(type=id_player + 7)
        offer_accepted = offer_accepted.decode()
    except KeyError:
        mes = "NOPE".encode()
        mq.send(mes, type=id_player + 2)
        return None

    # On verifie si l'offre en echange est valide
    try:
        offer_a = offer_accepted.split(" ")
        offer_id = offer_a[0]
        pattern_to_exchange = offer_a[1]
        offer_id = int(offer_id)

        # On commence par récupérer l'offre
        offer = offers_dict[offer_id]
    except KeyError:
        mes = "no"
        is_available_dic[offer_id] = False
        mes = mes.encode()
        mq.send(mes, type=id_player + 2)
        return None

    # On envoie au joueur les details de l'offre
    mes = (str(offer.number_of_cards) + " " + str(offer.motif) + " " + str(offer.id_player))
    mes = mes.encode()
    mq.send(mes, type=id_player + 2)

    # On récupère la conclusion du joueur (Est ce qu'il echange assez de cartes ?)
    conclusion, _ = mq.receive(type=id_player + 7)
    conclusion = conclusion.decode()
    if conclusion == "NO_DEAL":
        return None
    else:
        # On previens le joueur qui a fait l'offre du deal par message spontanee
        mes = (str(offer.motif) + " " + str(pattern_to_exchange) + " " + str(offer.number_of_cards))
        mes = mes.encode()
        receiver.send(mes, type=offer.id_player + 2)

        # On supprime cette offre
        offer_lock.acquire()
        offers_dict.pop(offer_id)

        # On release le lock sur les offres
        offer_lock.release()

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

    # Fermeture des 3 mq que l'on utilise pour eviter tout probleme du a un message qui trainerait
    os.system("ipcrm -Q 150")
    os.system("ipcrm -Q 129")
    os.system("ipcrm -Q 130")
    print("The game is in progress")

    # (Re) Creation de 3 nouvelles mq
    connexions = sysv_ipc.MessageQueue(keyConnexions, sysv_ipc.IPC_CREAT)
    receiver = sysv_ipc.MessageQueue(keyReceiver, sysv_ipc.IPC_CREAT)
    mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

    # On lance le thread qui gere les connexions
    Connexion_receiver().start()

    # MANAGERS ET MEMOIRE PARTAGEE
    manager_offres = Manager()
    manager_offres_locks = Manager()
    manager_playing = Manager()
    last_offer_manager = Manager()
    availability_manager = Manager()
    # -
    offers = manager_offres.dict()
    offers_locks = manager_offres_locks.dict()
    playing = manager_playing.Value('i', 1)
    last_offer_id = last_offer_manager.list([0])
    is_available_dic = availability_manager.dict()
    # LOCK
    last_offer_id_lock = Lock()

    # Timeout qui permet aux joueurs de se connecter
    time.sleep(15)
    # On change ce boolean qui permet au thread de savoir Connexion_receiver que le temps de connexion est fini
    connexion_time = False

    # Distribution des cartes
    cards = distrib_cartes(len_player)

    # Pour chaque joueur connecte :
    for j in range(len_player):
        # On lance son process
        pl = Process(target=player, args=(j, offers, last_offer_id, last_offer_id_lock, len_player, playing,
                                          is_available_dic))
        # On rajoute le joueur dans la liste des joueurs
        players[j] = pl
        # On lui envoie ses cartes
        mq.send(cards[j], type=j + 2)
        # On lance le process
        pl.start()

    for i in range(len_player):
        players[i].join()

    print("The game is over")

    os.system("ipcrm -Q 129")
    os.system("ipcrm -Q 130")
    sys.exit()
