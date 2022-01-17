import sysv_ipc
import threading


class color:
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


key = 150

connexions = sysv_ipc.MessageQueue(key)

message = "request_player"

message = message.encode()

connexions.send(message, type=2)

test = True

cards = []


def cards_check(pattern, number_of_cards):
    # On vérifie d'abord que l'offre ne contient pas plus de 3 cartes (contrainte donnée dans le sujet)
    if number_of_cards > 3:
        print("You can't do that, 3 cards maximum")

        # Ensuite, on vérifie que le joueur a bien les cartes qu'il veut échanger
    else:
        k = 0

        # On compte les cartes du motif donné dans le jeu du joueur
        for i in cards:
            if i.avaiable == True:
                if i.motif == pattern:
                    k += 1
                    if k <= number_of_cards:
                        i.avaiable = False

        # On teste si le nombre de cartes offertes est inféreur ou égal au nombre de cartes du même motif
        #  présentes dans lejeu du joueur
        return number_of_cards <= k


def switch_cards(pattern_to_drop, pattern_to_add, number_of_cards):
    print("o,n est ci")
    i = 0

    for c in cards:
        if i < number_of_cards :
            print("i = ", i)
            if c.motif == pattern_to_drop and not(c.avaiable):
                print("c", str(c))
                cards.remove(c)
                cards.append(card(pattern_to_add))
                i += 1
        else:
            break


def message_receiver(id, mq):
    while True:
        message, _ = mq.receive(type=id + 2)
        message = message.decode()
        if message.startswith("OFF"):
            print("\n -- -- -- OFFERS -- -- --")
            print(message)
            print("-- -- -- END OFFERS -- -- --")
        else:
            print("Someone accepted my offer :) ")
            deal = message.split(" ")
            switch_cards(deal[0], deal[1], int(deal[2]))


def display_cards():
    for c in cards:
        if c.avaiable == True:
            print("\033[92m" + c.__str__(), end=",")
        else:
            print("\033[91m\033[1m" + c.__str__(), end=",")
    print("\033[0m")


def make_offer():
    interaction = input("Quelle offre voulez-vous faire [Nbr Motif]")

    offer = interaction.split(" ")
    number_of_cards = int(offer[0])
    pattern = offer[1]

    if cards_check(pattern, number_of_cards):
        sender(interaction, mq)
        answer, _ = mq.receive(type=id_player + 2)
        answer = answer.decode()
        print(answer)

    else:
        print("You can't do that, You don't have the cards")


def accept_offer():
    offer_id = input("Entrez l'identifiant de l'offre")
    pattern_to_exchange = input("Contre quel motif voulez vous échanger ?")
    offer_accepted = offer_id + " " + pattern_to_exchange
    sender(offer_accepted, mq)

    answer, _ = mq.receive(type=id_player + 2)
    answer = answer.decode()
    offer_received = answer.split(" ")
    if int(offer_received[2]) != id_player and cards_check(pattern_to_exchange, int(offer_received[0])):
        sender(pattern_to_exchange, mq)
        switch_cards(pattern_to_exchange, offer_received[1], int(offer_received[0]))
    else:
        print("NO YOU CANNOT")
        sender("NO_DEAL", mq)


while True:
    response, _ = connexions.receive(type=1)
    response = response.decode()
    id_player = int(response)
    if response == "no" or response == "The game is running":
        test = False
        break
    else:
        test = True
        break

if test == True:
    print("Wainting for my cards")

    key = 129
    mq = sysv_ipc.MessageQueue(key)

    cardsDistributed, _ = mq.receive(type=id_player + 2)
    cardsDistributed = cardsDistributed.decode()
    listCards = cardsDistributed.split(";")
    for c in listCards:
        cards.append(card(c))

    # Il faut attendre que les threads joueurs se lancent
    # Il faut recevoir playing

    how_to = (
        "\033[91m Mode d'emploi : \n Vous avez accès aux commandes : \n ring_bell pour sonner la cloche "
        "\n make_offer pour faire une offre \n accept_offer pour accepter une offre \n display offers pour "
        "afficher les offres \033[0m"
    )
    print(how_to)

    # tout le code suivant doit être executé while playing :

    key_receiver = 130

    mq_receiver = sysv_ipc.MessageQueue(key_receiver)

    receiver = threading.Thread(target=message_receiver, args=(id_player, mq_receiver))
    receiver.start()


    def sender(str, mq):
        str = str.encode()
        mq.send(str, type=(id_player + 7))


    playing = True
    while playing:
        interaction = input("Que voulez vous faire ? ")

        if interaction == "ring_bell":
            sender(interaction, mq)

        if interaction == "display_cards":
            display_cards()

        if interaction == "make_offer":
            sender(interaction, mq)
            make_offer()

        if interaction == "accept_offer":
            sender(interaction, mq)
            accept_offer()

        if interaction == "display_offers":
            sender(interaction, mq)
            offers, _ = mq.receive(type=id_player + 2)
            offers = offers.decode()
            offers.split("\n")
            print(offers)

        if interaction == "help":
            print(how_to)

        else:
            print("help for the commands")


else:
    print("NO")
