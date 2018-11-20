import socket as sc
import threading           
import os

port = 6969
hostIp = '127.0.0.1'

def listcmds():
    print("1. listdir : get directory listing \n")
    print("2. readfile : get file in read only mode\n")
    print("3. upfile : get file in write mode\n")
    print("4. delfile : delete a file\n")
    print("5. mkfile : create new file\n")


def recvTh(soc):
    while 1:
        print(soc.recv(1024).decode())

def main():
    s = sc.socket(sc.AF_INET, sc.SOCK_STREAM)               
    s.connect((hostIp, port)) 
    print(s.recv(1024).decode()) 
    try:
        recvT = threading.Thread(target=recvTh,kwargs={'soc':s})
        recvT.start()
    except:
        print("Error: unable to start thread")

    while True:
        inputmsg = input(">")
        if(inputmsg == "help"):
            listcmds()
        elif(inputmsg == "exit"):
            s.send(b'exit')
            s.close()
            os._exit(0)
        else:
            s.sendall(inputmsg.encode('utf-8'))
    


if __name__ == "__main__":
	main() 