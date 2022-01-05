import random
import threading
import sysv_ipc

key = 129

mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

offers = {}

offers_locks = {}

point_list = [0, 0, 0, 0, 0]

offer_lock = threading.Lock()

playing = True

playing_lock = threading.Lock()


def player(id):
    cards = ["plane", "car", "car", "train", "plane"]
    own_offers = []
    while playing:
        interaction = input("Que voulez vous faire ? ")

        if interaction == "ring_bell":
            ring_bell(cards, id)

        if interaction == "display_cards":
            display_cards(cards)

        if interaction == "make_offer":
            pattern = input("Entrez le motif que vous voulez échanger ")
            number = int(input("Entrez le nombre de cartes "))
            make_offer(cards, pattern, number, own_offers)

        if interaction == "accept_offer":
            number_id = input("Entrez l'identifiant de l'offre ")
            accept_offer(int(number_id), cards, own_offers)

        if interaction == "display_offers":
            display_offers()

        if interaction == "display_locks":
            display_locks()


def ring_bell(card_list, player):
    playing_lock.acquire()
    test = True
    for i in card_list:
        if i != card_list[0]:
            test = False
    if test:
        playing = False
    else:
        print("Vous n'avez pas 5 cartes identiques")
    playing_lock.release()


def display_cards(card_list):
    print(card_list)


def display_offers():
    print(offers)


def display_locks():
    print(offers_locks)


def make_offer(card_list, pattern, number_of_cards, own_offers):
    if number_of_cards > 3:
        print("You can't do that")
    k = 0
    for i in card_list:
        if i == pattern:
            k += 1
    test = number_of_cards <= k
    if test:
        offer_lock.acquire()
        offer = pattern + "," + str(number_of_cards)
        id = len(offers) + 1
        offers[id] = offer
        offers_locks[id] = threading.Lock()
        own_offers.append(id)

        print(offers)
    else:
        print("You can't do that")


def accept_offer(offer_id, card_list, own_offers):

    if len(card_list) == 5:
        print("Vous ne pouvez pas accepter d'offre si vous avez 5 cartes")
        return None

    offers_locks[offer_id].acquire()

    offer = offers[offer_id]
    if offer_id in own_offers:
        print("Vous ne pouvez pas accepter votre propre offre")
        return None
    offer = offer.split(",")
    nb_cards = int(offer[1])
    cards_to_exchange = input("Entrez les " + offer[1] + " à échanger")
    cards_to_exchange = cards_to_exchange.split(" ")

    test = False

    cards_counter = {"plane": 0, "bike": 0, "train": 0, "car": 0, "walk": 0}

    for i in card_list:
        if i == "plane":
            cards_counter["plane"] += 1
        if i == "bike":
            cards_counter["bike"] += 1
        if i == "train":
            cards_counter["train"] += 1
        if i == "car":
            cards_counter["car"] += 1
        if i == "walk":
            cards_counter["walk"] += 1

    for i in cards_to_exchange:
        cards_counter[i] -= 1

    for i in ["plane", "bike", "train", "car", "walk"]:
        if cards_counter[i] < 0:
            return "You can don't have the necessary cards"

    return "Offer accepted"


def message_receiver(id):
    while True:
        message, type = mq.receive(type=id)
        message = message.decode()
        print(message)


player(1)
