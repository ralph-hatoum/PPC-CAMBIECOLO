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

#test = True
playing = True
game = True

cards = []

points = 0


def how_to():
    print(
        color.UNDERLINE + color.BLUE + " Mode d'emploi : \n" + color.END +
        color.BLUE + " Vous avez accès aux commandes : \n " +
        color.BOLD + color.PURPLE + "ring_bell : " + color.END + color.BLUE + "pour sonner la cloche " +
        color.BOLD + color.PURPLE + "\n make_offer : " + color.END + color.BLUE + " pour faire une offre " +
        color.BOLD + color.PURPLE + "\n accept_offer : " + color.END + color.BLUE + " pour accepter une offre " +
        color.BOLD + color.PURPLE + "\n display_offers : " + color.END + color.BLUE + " pour afficher les offres " +
        color.END + "\n"
        )


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


def block_cards(pattern, number_of_cards):
    k = 0
    for i in cards:
        if i.avaiable == True:
            if i.motif == pattern:
                k += 1
                if k <= number_of_cards:
                    i.avaiable = False


def switch_cards(pattern_to_drop, pattern_to_add, number_of_cards):
    i = 0
    for c in cards:
        if i < number_of_cards :
            if c.motif == pattern_to_drop and not(c.avaiable):
                cards.remove(c)
                cards.insert(0, card(pattern_to_add))
                i += 1
        else:
            break


def message_receiver(id, mq):
    global playing
    while True:
        message, _ = mq.receive(type=id + 2)
        message = message.decode()
        if message.startswith("\033[36mOFF"):
            print("\n -- -- -- \033[93mOFFERS\033[0m -- -- --")
            print(message)
            print("-- -- -- \033[93mEND OFFERS\033[0m -- -- --\n")
        elif message.startswith("player"):
            m = message.split(" ")
            if int(m[1]) != id:
                print("\n" + color.RED + color.BOLD + message + color.END + "\n")
                print("Press enter for the next game")
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
    interaction = input(" -- Quelle offre voulez-vous faire [Nbr Motif]\n")

    offer = interaction.split(" ")
    number_of_cards = int(offer[0])
    pattern = offer[1]

    if cards_check(pattern, number_of_cards):
        block_cards(pattern, number_of_cards)
        sender(interaction, mq)
        answer, _ = mq.receive(type=id_player + 2)
        answer = answer.decode()
        print(answer)

    else:
        print("You can't do that, You don't have the cards")


def display_offers():
    offers, _ = mq.receive(type=id_player + 2)
    offers = offers.decode()
    offers.split("\n")
    print("\n -- -- -- \033[93mOFFERS\033[0m -- -- --")
    print(str(offers))
    print("-- -- -- \033[93mEND OFFERS\033[0m -- -- --\n")


def accept_offer():
    offer_id = input(" -- Entrez l'identifiant de l'offre\n")
    pattern_to_exchange = input(" -- Contre quel motif voulez vous échanger ?\n")
    offer_accepted = offer_id + " " + pattern_to_exchange
    sender(offer_accepted, mq)

    answer, _ = mq.receive(type=id_player + 2)
    answer = answer.decode()
    offer_received = answer.split(" ")
    if int(offer_received[2]) != id_player and cards_check(pattern_to_exchange, int(offer_received[0])):
        block_cards(pattern_to_exchange, int(offer_received[0]))
        sender(pattern_to_exchange, mq)
        print(color.RED + "DEAL !\nYOU GAVE " + color.YELLOW + str(offer_received[0]) + " " + pattern_to_exchange +
              "\n" + color.END + color.BLUE +
              "YOU RECEIVED " + color.DARKCYAN + str(offer_received[0]) + " " + offer_received[1] + "\n" + color.END)
        switch_cards(pattern_to_exchange, offer_received[1], int(offer_received[0]))
    else:
        print("NO YOU CANNOT")
        sender("NO_DEAL", mq)


def ring_bell():
    test = True
    i = 0
    while test and i < 4:
        test = cards[i].motif == cards[i+1].motif
        i += 1
    return test


def sender(str, mq):
    str = str.encode()
    mq.send(str, type=(id_player + 7))


if __name__ == "__main__":
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
        while game:
            print("Wainting for my cards")

            key = 129
            mq = sysv_ipc.MessageQueue(key)

            cardsDistributed, _ = mq.receive(type=id_player + 2)
            cardsDistributed = cardsDistributed.decode()
            listCards = cardsDistributed.split(";")
            for c in listCards:
                cards.append(card(c))
            playing = True

        # Il faut attendre que les threads joueurs se lancent
        # Il faut recevoir playing

            how_to()

        # tout le code suivant doit être executé while playing :

            key_receiver = 130

            mq_receiver = sysv_ipc.MessageQueue(key_receiver)

            receiver = threading.Thread(target=message_receiver, args=(id_player, mq_receiver))
            receiver.start()

            while playing:
                print("ICI")
                interaction = input(" -- Que voulez vous faire ? \n")

                if interaction == "ring_bell":
                    sender(interaction, mq)
                    if ring_bell():
                        sender("WON", mq)
                        points += 1
                        print(color.RED + color.BOLD + "YOU WON" + color.END)
                        print(color.GREEN + "you have " + str(points) + "points" +color.END)
                        break
                    else:
                        print("not yet, you need 5 identicals cards")
                        sender("NO", mq)

                elif interaction == "display_cards":
                    display_cards()

                elif interaction == "make_offer":
                    sender(interaction, mq)
                    make_offer()

                elif interaction == "accept_offer":
                    sender(interaction, mq)
                    accept_offer()

                elif interaction == "display_offers":
                    sender(interaction, mq)
                    display_offers()

                elif interaction == "help":
                    how_to()

                elif interaction == "":
                    print("", end="")

                else:
                    print(" - > Wrong command ! Tap \033[92mhelp\033[0m\n")
        else:
            print(" - > NO\n")