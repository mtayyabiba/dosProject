import socket as sc   
import threading  
import os, pickle, queue 
          
port = 6970
hostIp = '127.0.0.1'
pathName = 'root'
q = queue.Queue()

def list_files(startpath):
    listFiles = []
    count = 0
    for root, dirs, files in os.walk(startpath):
        absPath = root.replace(startpath,'')
        if absPath != '':
            listFiles.append(absPath)
        for f in files:
            count = count +1
            listFiles.append('{}/{}'.format(absPath,f))
    listFiles.append(count)
    print(listFiles)
    return listFiles
        

def recvTh(soc):
    initComm =False
    namelist = ["deletefile","deletefolder", "createfile" ,"createfolder", "readfile","updatefile"]
    
    while 1:
        msg=soc.recv(1024).decode()
        msglist = msg.split(' ')
        cmd = msglist[0]
        #print("command is ",cmd)
        if cmd == "dirlist":
            dirlist = list_files(pathName)
            soc.sendall(pickle.dumps(dirlist))
            if initComm == False:
                q.put("done")
                initComm = True
        elif cmd == "":
            print("Connection closed with name server")
            soc.close()
            os._exit(0)
        elif cmd in namelist:
            filename = msglist[1]
            filepath= "root/"+filename
            if cmd == "readfile":
                try:
                    f = open(filepath)
                    filecont = f.read()
                    if filecont == "":
                        soc.sendall("Requested file is empty".encode('utf-8'))
                    else:
                        soc.sendall(filecont.encode('utf-8'))
                    f.close()
                except IsADirectoryError:
                    soc.sendall("Error! Given name is a folder".encode('utf-8'))
            elif cmd == "updatefile":
                fileCont = msg.replace((cmd+" "+filename+" "),"",1)
                try:
                    f = open(filepath, 'w')
                    f.write(fileCont)
                    f.close()
                except IsADirectoryError:
                    soc.sendall("Error! Given name is a folder".encode('utf-8'))
            elif cmd == "deletefile":
                try:
                    os.remove(filepath)
                    soc.sendall(("Deleted File "+filename+" from server").encode('utf-8'))
                except IsADirectoryError:
                    soc.sendall("Error! Given name is a folder".encode('utf-8'))
            elif cmd=="deletefolder":
                try:
                    os.rmdir(filepath)
                    soc.sendall(("Deleted Folder "+filename+" from server").encode('utf-8'))
                except Exception as e: 
                    strerror = e.args
                    soc.sendall((filename+" "+strerror[1]).encode('utf-8'))
            elif cmd == "createfile" or cmd == "createfolder":
                try:
                    if cmd == "createfile":
                        f = open(filepath,"x")
                        f.close()
                    else:
                        os.mkdir(filepath)
                    soc.sendall(("Created "+filename+" on server").encode('utf-8'))
                except Exception as e: 
                    strerror = e.args
                    soc.sendall((filename+" "+strerror[1]).encode('utf-8'))

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

    delayMsg = q.get()#wait for initial msg exchange
    while input()!="exit":
        pass
    s.close()
    os._exit(0)

if __name__ == "__main__":
	main() 