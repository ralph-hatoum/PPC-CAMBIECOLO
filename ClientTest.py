import sysv_ipc

key = 150

mq = sysv_ipc.MessageQueue(key)

message = "request_player"

message = message.encode()

mq.send(message, type = 2)

test = True

while True :
    response, _ = mq.receive(type=2)
    if response.decode() == "no":
        test = False
        break
    else :
        test = True
        break

if test == True :
    print("Je suis accepté dans la partie")
else:
    print("NO")

