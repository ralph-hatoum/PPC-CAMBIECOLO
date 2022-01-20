import sys

import sysv_ipc
import threading


class color:
    # String a placer dans les prints pour plus d'effets
    # ne pas oublier le end qui permet de repasser sur un format classique
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


class card:
    def __init__(self, aMotif):
        self.motif = aMotif
        self.avaiable = True

    def __str__(self):
        return self.motif


# VARIABLES GLOBALES #

# Etat du jeu
playing = True

# Identifiant du joueur (utile pour le type des messages des message queue (voir explications dans Jeu.py)
id_player = -1

# Les cartes
cards = []


# Presentation des commandes
def how_to():
    print(
        color.UNDERLINE + color.BLUE + " Commands : \n" + color.END +
        color.BOLD + color.PURPLE + "ring_bell : " + color.END + color.BLUE + "to ring the bell" +
        color.BOLD + color.PURPLE + "\n display_cards : " + color.END + color.BLUE + "to see your cards" +
        color.BOLD + color.PURPLE + "\n make_offer : " + color.END + color.BLUE + "to make an offer" +
        color.BOLD + color.PURPLE + "\n accept_offer : " + color.END + color.BLUE + "to accept an offer" +
        color.BOLD + color.PURPLE + "\n display_offers : " + color.END + color.BLUE + "to display the offers available" +
        color.END + "\n"
    )


# Verification si on a bien [number_of_cards] cartes du motif [pattern] disponibles
def cards_check(pattern, number_of_cards):
    # On vérifie d'abord que l'offre ne contient pas plus de 3 cartes (contrainte donnée dans le sujet)
    if number_of_cards > 3:
        print(" - > You can't do that, 3 cards maximum\n")
        return False
        # Ensuite, on vérifie que le joueur a bien les cartes qu'il veut échanger
    else:
        k = 0

        # On compte les cartes du motif donné dans le jeu du joueur
        for i in cards:
            if i.avaiable == True:
                if i.motif == pattern:
                    k += 1

        # On teste si le nombre de cartes offertes est inféreur ou égal au nombre de cartes du même motif
        #  présentes dans lejeu du joueur
        return number_of_cards <= k


# Bloque les cartes qui sont proposees dans une offre pour
# qu'un joueur ne puisse pas les utiliser pour en accepter une autre
def block_cards(pattern, number_of_cards):
    k = 0
    for i in cards:
        if i.avaiable == True:
            if i.motif == pattern:
                k += 1
                if k <= number_of_cards:
                    i.avaiable = False


# Lorsqu'un joueur conclut une offre, il recoit via son process les informations suivantes :
# Le motif qu'il donne (cartes qu'il doit supprimer de son jeu)
# Le motif qu'il recoit (cartes qu'il doit recreer dans son jeu)
# Combien de cartes sont echanges
# LES CARTES NE SONT PAS ECHANGEES, seulement des messages qui permettent a chaque joueur de gerer leur jeu
def switch_cards(pattern_to_drop, pattern_to_add, number_of_cards):
    i = 0
    for c in cards:
        if i < number_of_cards:
            if c.motif == pattern_to_drop and not (c.avaiable):
                cards.remove(c)
                cards.insert(0, card(pattern_to_add))
                i += 1
        else:
            break


# Ce Thread tourne en arriere plan pour gerer tout message spontanee (d'ou le Daemon)
# Les messages qui arrivent :
# Nouvelle offre // On accepte mon offre // Quelqu'un a gagne
class message_receiver(threading.Thread):
    daemon = True

    def run(self):
        global playing, cards, id_player, mq_receiver
        while True:
            message, _ = mq_receiver.receive(type=id_player + 2)
            message = message.decode()
            if message.startswith("\033[36mOFF"):
                print("\n -- -- -- \033[93mOFFERS\033[0m -- -- --")
                print(message)
                print("-- -- -- \033[93mEND OFFERS\033[0m -- -- --\n")
            elif message.startswith("player"):
                m = message.split(" ")
                if int(m[1]) != id_player:
                    print("\n" + color.RED + color.BOLD + message + color.END + "\n")
                    print("press 'ENTER' to quit")
                playing = False
            else:
                deal = message.split(" ")
                print(color.RED + "DEAL (someone accepted your offer) !\nYOU GAVE "
                      + color.YELLOW + str(deal[2]) + " " + deal[0] +
                      "\n" + color.END + color.BLUE +
                      "YOU RECEIVED " + color.DARKCYAN + str(deal[2]) + " " + deal[1] + "\n" + color.END)
                switch_cards(deal[0], deal[1], int(deal[2]))


def display_cards():
    print(color.BOLD, end="")
    for c in cards:
        if c.avaiable == True:
            print("\033[92m" + c.__str__(), end=",")
        else:
            print("\033[91m" + c.__str__(), end=",")
    print("\033[0m\n")


def make_offer():
    while True:
        # On demande l'offre jusqu'a ce qu'elle soit correctement ecrite
        interaction = input(" -- What do you give ? [Nbr Pattern]\n")
        offer = interaction.split(" ")
        try:
            number_of_cards = int(offer[0])
            pattern = offer[1]
            break
        except ValueError:
            print("An int for 1st charactere please")

    # Verification de la validite de l'offre
    if cards_check(pattern, number_of_cards):
        # Si elle est valide, on bloque les cartes impliquees
        block_cards(pattern, number_of_cards)
        # On envoie l'offre a son process du fichier jeu.py
        sender(interaction, mq)
        # Reponse positive
        answer, _ = mq.receive(type=id_player + 2)
        answer = answer.decode()
        print(answer)

    else:
        print("You can't do that, You don't have the cards")
        sender("no", mq)
        return None


def display_offers():
    offers, _ = mq.receive(type=id_player + 2)
    offers = offers.decode()
    offers.split("\n")
    print("\n -- -- -- \033[93mOFFERS\033[0m -- -- --")
    print(str(offers))
    print("-- -- -- \033[93mEND OFFERS\033[0m -- -- --\n")


def accept_offer():
    offer_id = input(" -- Enter the offer's id\n")

    # On envoie a son process l'offre que l'on veut accepter
    sender(offer_id, mq)

    # Le process nous repond une premiere fois sur la disponibilite de l'offre
    go, _ = mq.receive(type=id_player + 2)
    go = go.decode()
    if go == "NOPE":
        print("Too bad ! Someone is already bargaining on this offer !")
        return None

    # On demande ce que l'on echange
    pattern_to_exchange = input(" -- What do you want to give ?\n")
    offer_accepted = offer_id + " " + pattern_to_exchange
    # On renvoi l'id de l'offre
    sender(offer_accepted, mq)

    # On recoit toutes les infos liees a l'offre, si l'id ne correspond a aucune, on recoit "no"
    answer, _ = mq.receive(type=id_player + 2)
    answer = answer.decode()
    if answer == "no":
        print("This offer doesn't exist !\n")
        return None

    offer_received = answer.split(" ")
    # On verifie si le deal peut etre honore
    if int(offer_received[2]) != id_player and cards_check(pattern_to_exchange, int(offer_received[0])):
        # Si oui on bloque les cartes impliquees
        block_cards(pattern_to_exchange, int(offer_received[0]))
        # On envoie a son process le motif que l'on offre en echange pour qu'il puisse le communiquer au joueur qui a
        # cree l'offre
        sender(pattern_to_exchange, mq)
        print(color.RED + "DEAL !\nYOU GAVE " + color.YELLOW + str(offer_received[0]) + " " + pattern_to_exchange +
              "\n" + color.END + color.BLUE +
              "YOU RECEIVED " + color.DARKCYAN + str(offer_received[0]) + " " + offer_received[1] + "\n" + color.END)
        # On effectue les changements au niveau de ses cartes
        switch_cards(pattern_to_exchange, offer_received[1], int(offer_received[0]))
    else:
        print("NO YOU CANNOT")
        sender("NO_DEAL", mq)


# Pour verifier si un joueur peut reellement sonner la fin de la partie
def ring_bell():
    test = True
    i = 0
    while test and i < 4:
        test = cards[i].motif == cards[i + 1].motif
        i += 1
    return test


# Methode qui envoie le message via la MQ avec le bon type et l'encode
def sender(str, mq):
    str = str.encode()
    mq.send(str, type=(id_player + 7))


# Les differentes actions que peut faire le joueur
def play():
    global mq, cards, playing
    interaction = input(" -- What do you want to do ? \n")

    if interaction == "ring_bell" or interaction == "rb":
        sender("ring_bell", mq)
        if ring_bell():
            sender("WON", mq)
            print(color.RED + color.BOLD + "YOU WON" + color.END)
            playing = False
        else:
            print("not yet, you need 5 identicals cards")
            sender("NO", mq)

    elif interaction == "display_cards" or interaction == "dc":
        display_cards()

    elif interaction == "make_offer" or interaction == "mo":
        sender("make_offer", mq)
        make_offer()

    elif interaction == "accept_offer" or interaction == "ao":
        sender("accept_offer", mq)
        accept_offer()

    elif interaction == "display_offers" or interaction == "do":
        sender("display_offers", mq)
        display_offers()

    elif interaction == "help" or interaction == "h":
        how_to()

    elif interaction == "":
        sender(interaction, mq)
    else:
        sender(interaction, mq)
        print(" - > Wrong command ! Tap \033[92mhelp\033[0m\n")


if __name__ == "__main__":

    # Message queue pour demander la connexion
    key = 150
    connexions = sysv_ipc.MessageQueue(key)

    # On commence par une requete de connexion
    message = "request_player"
    message = message.encode()
    connexions.send(message, type=2)

    # On attend la reponse du jeu
    response, _ = connexions.receive(type=1)
    response = response.decode()
    try:
        # Si notre connexion est accepte, on recoit l'ID on peut donc le convertir
        id_player = int(response)
        test = True
    except ValueError:
        # Si nous ne somme pas accepte, la ValueError sera raise et nous ne pourrons pas joueur
        print(response)
        test = False

    if test == True:
        # Si nous sommes connecte :
        print("-- -- -- -- -- -- -- --")
        print("   N E W  G A M E !")
        print("-- -- -- -- -- -- -- --")

        print("\nWaiting for my cards")

        key = 129
        mq = sysv_ipc.MessageQueue(key)

        # On recuper nos cartes
        cardsDistributed, _ = mq.receive(type=id_player + 2)
        cardsDistributed = cardsDistributed.decode()
        listCards = cardsDistributed.split(";")
        for c in listCards:
            cards.append(card(c))

        # Presentation des commandes
        how_to()

        print("Your cards :")
        display_cards()

        # Message queue pour communiquer avec son process attribue
        key_receiver = 130
        mq_receiver = sysv_ipc.MessageQueue(key_receiver)

        # On lance le thread qui recupere les messages spontanee
        message_receiver().start()

        while playing:
            # On lance les interactions
            play()
    else:
        print("")
    sys.exit()
