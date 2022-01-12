import sysv_ipc

key = 150

mq = sysv_ipc.MessageQueue(key)

message = "request_player"

message = message.encode()

mq.send(message, type=2)

test = True

while True:
    print("hello")
    response, _ = mq.receive(type=1)
    print("there")
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
else:
    print("NO")
