import socket as sc
import threading           
import os, queue
import myeditor as me

port = 6969
hostIp = '127.0.0.1'
q = queue.Queue()

def listcmds():
    print('Following commands are available')
    print("1. dirlist : get directory listing")
    print("2. readfile : get file in read only mod")
    print("3. updatefile : get file in write mod")
    print("4. deletefile : delete a file")
    print("5. deletefolder : delete an empty folder")
    print("6. createfile : create new file")
    print("7. createfolder : create new folder")
    print("8. exit : exit the program")
    print("9. help : list all available commands")


def recvTh(soc):
    while 1:
        msgFromserver = soc.recv(8192).decode()
        if msgFromserver != "":
            q.put(msgFromserver)
        else:
            print("Connection closed with server...Exiting program")
            soc.close()
            os._exit(0)
        

def sendRecv(inputmsg, soc):
    soc.sendall(inputmsg)
    return  q.get()

def main():
    s = sc.socket(sc.AF_INET, sc.SOCK_STREAM)               
    s.connect((hostIp, port)) 
    print(s.recv(1024).decode()) 
    listcmds()
    namelist = ["deletefile","deletefolder", "createfile" ,"createfolder", "readfile","updatefile"]
    try:
        recvT = threading.Thread(target=recvTh,kwargs={'soc':s})
        recvT.start()
    except:
        print("Error: unable to start thread")

    while True:
        cmd = input(">")
        if(cmd== "help"):
            listcmds()
        elif(cmd == "exit"):
            s.send(b'exit')
            s.close()
            os._exit(0)
        elif(cmd == "dirlist"):
            s.sendall(cmd.encode('utf-8'))
            dirstr= q.get()
            msglist = dirstr.split(",")
            for items in msglist:
                print(items.replace("/","",1))
        elif cmd in namelist:
            fileName = input("Enter Name:")
            if ',' in fileName:
                print("File/Folder name can not contain ','")
            else:
                inputmsg = cmd+" "+fileName
                if cmd != "updatefile":
                    s.sendall(inputmsg.encode('utf-8'))
                    print("\n"+q.get())
                elif(cmd == "updatefile"):
                    s.sendall(inputmsg.encode('utf-8'))
                    uFileStr = q.get()
                    errorCheck = uFileStr.split('!')[0]
                    if errorCheck != "Error":
                        if uFileStr == "Requested file is empty":
                            uFileStr = ""
                        commit_msg = me.edit(contents=uFileStr.encode('utf-8'))
                        noCommit = (inputmsg+" ").encode('utf-8')
                        s.sendall((noCommit+commit_msg))
                        print("File updated successfully!\n")
                    else:
                        print(uFileStr)
        else:
            print("Wrong command")

if __name__ == "__main__":
	main() 