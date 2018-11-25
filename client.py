import socket as sc
import threading           
import os
import myeditor as me

port = 6969
hostIp = '127.0.0.1'
def listcmds():
    print("1. dirlist : get directory listing \n")
    print("2. readfile : get file in read only mode\n")
    print("3. upfile : get file in write mode\n")
    print("4. delfile : delete a file\n")
    print("5. mkfile : create new file\n")


#def recvTh(soc):
#    while 1:
#        dirdict = pickle.loads(soc.recv(8192))
#        for f in dirdict:
#            for i in dirdict[f]:
#                print(i)

def readFile(inputmsg, soc):
    soc.sendall(inputmsg.encode('utf-8'))
    #print("waiting for file...\n")
    rFileStr = soc.recv(8192).decode()
    return rFileStr

def main():
    #commit_msg = me.edit(contents=filecont.encode('utf-8'))
    #print(commit_msg)
    s = sc.socket(sc.AF_INET, sc.SOCK_STREAM)               
    s.connect((hostIp, port)) 
    print(s.recv(1024).decode()) 
    #try:
    #    recvT = threading.Thread(target=recvTh,kwargs={'soc':s})
    #    recvT.start()
    #except:
    #    print("Error: unable to start thread")

    while True:
        inputmsg = input(">")
        inputmsglist = inputmsg.split(' ')
        cmd = inputmsglist[0]
        if(cmd== "help"):
            listcmds()
        elif(cmd == "exit"):
            s.send(b'exit')
            s.close()
            os._exit(0)
        elif(cmd == "dirlist"):
            s.sendall("dirlist".encode('utf-8'))
            print("waiting for directory listing...")
            dirstr= s.recv(8192).decode()
            msglist = dirstr.split(",")
            for items in msglist:
                print(items.replace("/","",1))
        elif(cmd == "readfile"):
            print(readFile(inputmsg,s)+"\n")
        elif(cmd == "updatefile"):
            rFileCmd = inputmsg.replace(cmd,"readfile",1)
            uFileStr = readFile(rFileCmd,s)
            commit_msg = me.edit(contents=uFileStr.encode('utf-8'))
            inputmsg1 = (inputmsg+" ").encode('utf-8')
            s.sendall((inputmsg1+commit_msg))


if __name__ == "__main__":
	main() 