import os
import socket as sc
import threading
import pickle, queue

#1. filename cant contain commas
#2. update help
#3. replication
#4. format clientConnS
#5. format recvTh in dataserver.py
#6. locks lagane hyn

hostIp = '127.0.0.1'
clientPort = 6969
dSPort = 6970
clientList = {}
dserverList = {}
globalFT = {}
writeDict = {}
dServCost = {}
buffSize = 8192
q = queue.Queue()
lock = threading.Lock()

def getdirlist(soc):
    soc.send("dirlist".encode('utf-8'))
    dirlist = pickle.loads(soc.recv(buffSize))
    socPort = soc.getpeername()[1]
    dServCost[socPort] = dirlist[-1]
    globalFT[socPort] = dirlist[:-1]

"""
def refreshDirList():
    globalFT.clear()
    for keys in dserverList:
        soc = dserverList[keys][1]
        getdirlist(soc)
"""

def dsConnS(soc):
    #get initial directory listing 
    getdirlist(soc)
    #append directory listing to global file table
    while True:
        msgFromDserver = soc.recv(buffSize).decode()
        socPeer = soc.getpeername()
        if msgFromDserver != "":
            q.put(msgFromDserver) 
        else:
            print("connection closed with ",socPeer[0],":",socPeer[1])
            #
            del dserverList[socPeer[1]]
            del globalFT[socPeer[1]]
            del dServCost[socPeer[1]]
            #
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
            #print('dsConn is ',dsConn)
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
            if i== filename:
                return f
    return 0    


def clientConnS(soc):
    msg = ""
    while True:
        msg = soc.recv(1024).decode()
        #print(msg)
        msglist = msg.split(' ')
        cmd = msglist[0]
        clientPort = soc.getpeername()[1]
        if cmd == "exit" or cmd == "":
            print("connection closed with ",soc.getpeername()[0],":",clientPort)
            #
            del clientList[clientPort]
            soc.close()
            break
        elif cmd == "dirlist":
            dirmsg = ""
            if len(globalFT)>0:
                for keys in globalFT:
                    for vals in globalFT[keys]:
                        dirmsg = dirmsg +","+vals
            else:
                dirmsg = "File table is empty"
            soc.sendall(dirmsg.replace(",","",1).encode('utf-8'))
        elif cmd == "readfile":
            filename = "/"+msglist[1]
            FileCmd(msg,soc,filename)
        elif cmd == "deletefile" or cmd == "deletefolder":
            filename = "/"+msglist[1]
            if filename not in writeDict.values():
                FileCmd(msg,soc,filename)
            else:
                soc.sendall("Given file is being edited and cannot be deleted".encode('utf-8'))
        elif cmd == "createfile" or cmd == "createfolder":
            filename = "/"+msglist[1]
            fileCheck = getFileServPort(filename)
            if fileCheck == 0:#file not exists already
                servPort = getMinServPort(filename)
                print("min serv port ",servPort)
                servSock = dserverList[servPort][1]
                servSock.sendall(msg.encode('utf-8'))
                msgq = q.get()
                soc.sendall(msgq.encode('utf-8'))
                if msgq.split(' ')[0] == "Created":
                    globalFT[servPort].append(filename)
                    if cmd == "createfile":
                        dServCost[servPort] = dServCost[servPort]+1
            else:#file already exists and cant be created
                soc.sendall("Error! Given name already exists in listing".encode('utf-8'))
        elif cmd == "updatefile":
            filename = "/"+msglist[1]
            writeDict[clientPort] = filename
            #first reading file contents from data server
            rFileCmd = msg.replace(cmd,"readfile",1) #cmd to read file content from dserver
            servPort = getFileServPort(filename)
            if servPort > 0:
                print("file found on server ",servPort)
                servSock = dserverList[servPort][1]
                servSock.sendall(rFileCmd.encode('utf-8'))
                msgq = q.get()
                #file contents or error sent to client
                soc.sendall(msgq.encode('utf-8'))
                #if no error then get updated contents from client and send to dataserver
                if msgq != "Error! Given filename is a folder":
                    updatedContent = soc.recv(buffSize).decode()
                    servSock.sendall(updatedContent.encode('utf-8'))
            elif servPort == 0:
                soc.sendall("Error! Given filename not found".encode('utf-8'))
            del writeDict[clientPort]
            

def getMinServPort(filename):
    #if first folder already exists then redirect to that server
    folder1 = filename.split('/')[1]
    servPort = getFileServPort("/"+folder1)
    print(servPort)
    if servPort >0:
        return servPort
    else:
    #else find server with min cost and create file there
        minCost = min(dServCost.values())
        for key, value in dServCost.items():
            if value == minCost:
                return key




def FileCmd(msg,soc,filename):
    servPort = getFileServPort(filename)
    cmd = msg.split(' ')[0]
    if servPort > 0:
        print("file found on server ",servPort)
        #
        servSock = dserverList[servPort][1]
        servSock.sendall(msg.encode('utf-8'))
        msgq = q.get()
        soc.sendall(msgq.encode('utf-8'))
        if msgq.split(' ')[0] == "Deleted":
            globalFT[servPort].remove(filename)
            if cmd == "deletefile":
                dServCost[servPort] = dServCost[servPort]-1
        #
    elif servPort == 0:
        soc.sendall("Error! Given filename not found".encode('utf-8'))

def clientListen():
    with sc.socket(sc.AF_INET, sc.SOCK_STREAM) as masterCSocket:
        masterCSocket.bind((hostIp,clientPort))
        masterCSocket.listen(5)
        print('listening for client sockets created on ',hostIp,':',clientPort)
        while True: 
            clientConn, clientAddr = masterCSocket.accept()      
            print ('Got client connection from', clientAddr[0],":",clientAddr[1] )
            #print("clientConn is ", clientConn)
            #
            clientList[clientAddr[1]] = [clientAddr[0],clientConn]
            #
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

    while input()!="exit":
        pass
    os._exit(0)

if __name__ == "__main__":
	main()