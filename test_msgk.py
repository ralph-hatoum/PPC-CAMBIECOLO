import multiprocessing
import sysv_ipc
import time

mq = sysv_ipc.MessageQueue(128, sysv_ipc.IPC_CREAT)

def message_receiver(id):
    while True :
        message, t = mq.receive()
        message = message.decode()
        print(message+str(id))

def message_sender():
    message = "Hello".encode()
    mq.send(message)



if __name__=="__main__":
    with multiprocessing.Pool(processes = 3) as pool :
        ids = [1,2]
        receiver_1 = multiprocessing.Process(target=message_receiver, args=(1,))
        receiver_2 = multiprocessing.Process(target=message_receiver, args=(2,))
        receiver_3 = multiprocessing.Process(target=message_receiver, args=(3,))
        receiver_1.start()
        receiver_1.start()
        receiver_2.start()
        sender = multiprocessing.Process(target=message_sender)
        sender.start()
