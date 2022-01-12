import sysv_ipc

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
    if response == "no":
        test = False
        break
    else:
        test = True
        break

if test == True:
    print("Je suis accepté dans la partie")
    print("En attente que le jeu commence")

    print(
        "\033[91m"
        + "Mode d'emploi : \n Vous avez accès aux commandes : \n ring_bell pour sonner la cloche \n make_offer pour faire une offre \n accept_offer pour accepter une offre \n display offers pour afficher les offres"
        + "\033[0m"
    )
else:
    print("NO")
