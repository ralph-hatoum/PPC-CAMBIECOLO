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


key = 150

connexions = sysv_ipc.MessageQueue(key)

message = "request_player"

message = message.encode()

connexions.send(message, type=2)

test = True


def message_receiver(id, mq):
    while True:
        message, _ = mq.receive(type=id+2)
        message = message.decode()
        print("\n -- -- -- OFFERS -- -- --")
        print(message)
        print("-- -- -- END OFFERS -- -- --")


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
    print("Je suis accepté dans la partie")
    print("En attente que le jeu commence")

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

    receiver = threading.Thread(target=message_receiver, args=(id_player,mq_receiver))
    receiver.start()

    key = 129

    mq = sysv_ipc.MessageQueue(key)

    # receiver = threading.Thread(target=message_receiver, args=(id_player,))
    # receiver.start()

    def sender(str, mq):
        str = str.encode()
        mq.send(str, type=(id_player + 7))

    interaction = input("Que voulez vous faire ? ")

    if interaction == "ring_bell":
        sender(interaction, mq)

    if interaction == "display_cards":
        sender(interaction, mq)
        cards, _ = mq.receive(type=id_player + 2)
        cards = cards.decode()
        cards = cards.split(",")
        print(cards)

    if interaction == "make_offer":
        sender(interaction, mq)
        answer, _ = mq.receive(type=id_player + 2)
        answer = answer.decode()
        interaction = input(answer)
        sender(interaction, mq)
        answer, _ = mq.receive(type=id_player + 2)
        answer = answer.decode()
        print(answer)

    if interaction == "accept_offer ":
        sender(interaction, mq)
        answer, _ = mq.receive(type=id_player + 2)
        answer = answer.decode()
        interaction = input(answer)

    if interaction == "display_offers":
        sender(interaction, mq)
        offers, _ = mq.receive(type=id_player + 2)
        offers = offers.decode()
        offers.split("\n")
        print(offers)

    if interaction == "help":
        print(how_to)

    else:
        print(how_to)


else:
    print("NO")
