import socket as sc   
import threading  
import os, pickle  
          
port = 6970
hostIp = '127.0.0.1'

def recvTh(soc):
    while 1:
        msg=soc.recv(1024).decode()
        print("command received > ",msg)
        if msg == "dirlist":
            dirlist = os.listdir('root')
            soc.sendall(pickle.dumps(dirlist))

def main():
    s = sc.socket(sc.AF_INET, sc.SOCK_STREAM)               
    s.connect((hostIp, port))
    #connection confirmation
    print(s.recv(1024).decode()) 
    try:
        recvT = threading.Thread(target=recvTh,kwargs={'soc':s})
        recvT.start()
    except:
        print("Error: unable to start thread")

    while True:
        pass

if __name__ == "__main__":
	main() 