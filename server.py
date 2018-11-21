import os
import socket as sc
import threading
import pickle

hostIp = '127.0.0.1'
clientPort = 6969
dSPort = 6970
clientList = {}
dserverList = {}
globalFT = {}

#get directory listing from data server
#example {36368: ['/reviews_1000-ds2.txt', '/folder2-ds2', '/folder2-ds2/folder2-2-ds2']}
def getdirlist(soc):
    soc.send("dirlist".encode('utf-8'))
    dirlist = pickle.loads(soc.recv(8192))
    socPort = soc.getpeername()[1]
    globalFT[socPort] = dirlist
    print(globalFT)


def dsConnS(soc):
    #get initial directory listing 
    getdirlist(soc)
    #append directory listing to global file table
    while True:
        msg = soc.recv(1024).decode()
        print(msg)
        
def dSListen():
    with sc.socket(sc.AF_INET, sc.SOCK_STREAM) as masterDSSocket:
        masterDSSocket.bind((hostIp,dSPort))
        masterDSSocket.listen(5)
        print('listening for dataserver sockets created on ',hostIp,':',dSPort)
        while True: 
            dsConn, dsAddr = masterDSSocket.accept()      
            print ('Got dataserver connection from', dsAddr[0], ":", dsAddr[1] )
            dserverList[dsAddr[1]] = [dsAddr[0],dsConn]
            dsConn.send(b'Connection established with name server')
            dsThreads = []
            try:
                dsConnT = threading.Thread(target=dsConnS,kwargs={'soc':dsConn})
                dsThreads.append(dsConnT)
                dsConnT.start()
            except:
                print("Error: unable to start thread")


def clientConnS(soc):
    msg = ""
    while True:
        msg = soc.recv(1024).decode()
        print(msg)
        if msg == "exit":
            soc.close()
            break
        elif msg == "dirlist":
            dirmsg = ""
            for f in globalFT:
                for i in globalFT[f]:
                    dirmsg = dirmsg +","+i
            soc.sendall(dirmsg.replace(",","",1).encode('utf-8'))


def clientListen():
    with sc.socket(sc.AF_INET, sc.SOCK_STREAM) as masterCSocket:
        masterCSocket.bind((hostIp,clientPort))
        masterCSocket.listen(5)
        print('listening for client sockets created on ',hostIp,':',clientPort)
        while True: 
            clientConn, clientAddr = masterCSocket.accept()      
            print ('Got client connection from', clientAddr[0],":",clientAddr[1] )
            clientList[clientAddr[1]] = [clientAddr[0],clientConn]
            #sending connection confirmation
            clientConn.send(b'Connection established with name server')
            clientThreads = []
            try:
                clientConnT = threading.Thread(target=clientConnS,kwargs={'soc':clientConn})
                clientThreads.append(clientConnT)
                clientConnT.start()
            except:
                print("Error: unable to start thread")



def main(): 
    mainthreads = []
    try:
        clientT = threading.Thread(target=clientListen)
        mainthreads.append(clientT)
        clientT.start()
        dataserverT = threading.Thread(target=dSListen)
        mainthreads.append(dataserverT)
        dataserverT.start()
    except:
        print("Error: unable to start thread")

    while 1:
        pass

if __name__ == "__main__":
	main()