import sysv_ipc

key = 150

mq = sysv_ipc.MessageQueue(key)

message = "request_player"

message = message.encode()

mq.send(message, type = 2)

test = True

while True :
    response, _ = mq.receive(type=1)
    response = response.decode()
    print("Res =", response)
    if response == "no":
        test = False
        break
    else :
        test = True
        break

if test == True :
    print("Je suis accepté dans la partie")
else:
    print("NO")

