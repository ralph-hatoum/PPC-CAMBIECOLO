import random 
import multiprocessing

offers = {}

offers_locks = {}

point_list = [0,0,0,0,0]

offer_lock = multiprocessing.Lock

playing = True

playing_lock = multiprocessing.Lock



def player(id):
    cards = ["plane","car", "car", "train", "plane"]
    while playing :
        interaction = input("Que voulez vous faire ?")
        if interaction == "ring_bell":
            ring_bell(cards, id)
        if interaction == "display_cards":
            display_cards(cards)
        if interaction == "make_offer":
            pattern = input("Entrez le motif que vous voulez échanger ")
            number = int(input("Entrez le nombre de cartes "))
            make_offer(cards, pattern, number)
        if interaction == "accept_offer":
            number_id = input("Entrez l'identifiant de l'offre ")
            accept_offer(number_id, cards)

def ring_bell(card_list, player):
    playing_lock.acquire()
    test = True
    for i in card_list :
        if i != card[0]:
            test = False
    if test :
        playing = False
    playing_lock.release()

def display_cards(card_list):
    print(card_list)

def make_offer(card_list, pattern, number_of_cards):
    if number_of_cards > 3 :
        return "You can't do that"
    k = 0
    for i in card_list:
        if i == pattern :
            k +=1
    test = (number_of_cards <= k)
    if test :
        offer_lock.acquire()
        offer = pattern+","+str(number_of_cards)
        id = len(offers)+1
        offers[id] = offer
        offer_locks[id] = multiprocessing.Lock
    else :
        return "You can't do that"

def accept_offer(offer_id, card_list):
    offers_locks[offer_id].acquire()

    offer = offers[offer_id]
    offer = offer.split(",")
    nb_cards = int(offer[1])
    cards_to_exchange = input("Entrez les "+offer[1]+" à échanger")
    cards_to_exchange = cards_to_exchange.split(" ")

    test = False

    cards_counter = {"plane": 0, "bike": 0, "train": 0, "car": 0,"walk":0}

    for i in cards_list:
        if i == "plane":
            cards_counter["plane"] +=1
        if i == "bike":
            cards_counter["bike"] +=1 
        if i == "train":
            cards_counter["train"] +=1 
        if i == "car":
            cards_counter["car"] +=1 
        if i == "walk":
            cards_counter["walk"] +=1 
    
    for i in cards_to_exchange :
        cards_counter[i] -= 1

    for i in ["plane","bike","train","car","walk"]:
        if cards_counter[i] < 0 :
            return "You can don't have the necessary cards"

    return "Offer accepted"
 

player(1)
    


        



    

