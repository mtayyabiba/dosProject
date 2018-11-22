import os
import socket as sc
import threading
import pickle, queue

hostIp = '127.0.0.1'
clientPort = 6969
dSPort = 6970
clientList = {}
dserverList = {}
globalFT = {}
buffSize = 8192
q = queue.Queue()
#get directory listing from data server
def getdirlist(soc):
    soc.send("dirlist".encode('utf-8'))
    dirlist = pickle.loads(soc.recv(buffSize))
    socPort = soc.getpeername()[1]
    globalFT[socPort] = dirlist
    print(globalFT)


def dsConnS(soc):
    #get initial directory listing 
    getdirlist(soc)
    #append directory listing to global file table
    while True:
        msgFromDserver = soc.recv(buffSize).decode()
        if msgFromDserver != "":
            #print("dsConnS "+ msgFromDserver)
            q.put(msgFromDserver)
        else:
            print("connection closed with ",soc.getpeername()[0],":",soc.getpeername()[1])
            del dserverList[soc.getpeername()[1]]
            soc.close()
            break
        
def dSListen():
    with sc.socket(sc.AF_INET, sc.SOCK_STREAM) as masterDSSocket:
        masterDSSocket.bind((hostIp,dSPort))
        masterDSSocket.listen(5)
        print('listening for dataserver sockets created on ',hostIp,':',dSPort)
        while True: 
            dsConn, dsAddr = masterDSSocket.accept()      
            print ('Got dataserver connection from', dsAddr[0], ":", dsAddr[1] )
            print('dsConn is ',dsConn)
            dserverList[dsAddr[1]] = [dsAddr[0],dsConn]
            dsConn.send(b'Connection established with name server')
            dsThreads = []
            try:
                dsConnT = threading.Thread(target=dsConnS,kwargs={'soc':dsConn})
                dsThreads.append(dsConnT)
                dsConnT.start()
            except:
                print("Error: unable to start thread")

def getFileServPort(filename):
    for f in globalFT:
        for i in globalFT[f]:
            if i == filename:
                return f
    return 0    


def clientConnS(soc):
    cmd = ""
    while True:
        cmd = soc.recv(1024).decode()
        print(cmd)
        if cmd == "exit":
            soc.close()
            break
        elif cmd == "dirlist":
            dirmsg = ""
            for f in globalFT:
                for i in globalFT[f]:
                    dirmsg = dirmsg +","+i
            soc.sendall(dirmsg.replace(",","",1).encode('utf-8'))
        elif cmd.split(' ')[0] == "readfile":
            filename = "/"+cmd.split(' ')[1]
            servPort = getFileServPort(filename)
            if servPort != 0:
                print("file found on server ",servPort)
                servSock = dserverList[servPort]
                servSock[1].sendall(cmd.encode('utf-8'))
                #filecont = servSock[1].recv(buffSize)
                msgq = q.get()
                soc.sendall(msgq.encode('utf-8'))
            else:
                print("file not found..")
        elif cmd == "":
            print("connection closed with ",soc.getpeername()[0],":",soc.getpeername()[1])
            del clientList[soc.getpeername()[1]]
            soc.close()
            break


def clientListen():
    with sc.socket(sc.AF_INET, sc.SOCK_STREAM) as masterCSocket:
        masterCSocket.bind((hostIp,clientPort))
        masterCSocket.listen(5)
        print('listening for client sockets created on ',hostIp,':',clientPort)
        while True: 
            clientConn, clientAddr = masterCSocket.accept()      
            print ('Got client connection from', clientAddr[0],":",clientAddr[1] )
            print("clientConn is ", clientConn)
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