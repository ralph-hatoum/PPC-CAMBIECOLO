import sysv_ipc


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

mq = sysv_ipc.MessageQueue(key)

message = "request_player"

message = message.encode()

mq.send(message, type=2)

test = True

while True:
    response, _ = mq.receive(type=1)
    print(response.decode(), "= responseEncode")
    response = response.decode()
    print("Res =", response)
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

    how_to = "\033[91m"
    +"Mode d'emploi : \n Vous avez accès aux commandes : \n ring_bell pour sonner la cloche \n make_offer pour faire une offre \n accept_offer pour accepter une offre \n display offers pour afficher les offres"
    +"\033[0m"
    print(how_to)

    def sender(str, mq):
        str = str.encode()
        mq.send(
            str,
        )

    # tout le code suivant doit être executé while playing :

    interaction = input("Que voulez vous faire ? ")

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
    else:
        print(how_to)


else:
    print("NO")
