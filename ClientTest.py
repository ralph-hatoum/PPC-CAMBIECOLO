import sysv_ipc

key = 150

mq = sysv_ipc.MessageQueue(key)

message = "request_player"

message = message.encode()

mq.send(message,type = 0)

test = True

while True :
    response = mq.receive(type = 0)
    if response.encode() == "no":
        test = False
        break
    else :
        test = True
        break

if test = True :
    print("Je suis accepté dans la partie")

