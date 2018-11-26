import socket as sc   
import threading  
import os, pickle, queue 
          
port = 6970
hostIp = '127.0.0.1'
pathName = 'root'
q = queue.Queue()

def list_files(startpath):
    listFiles = []
    for root, dirs, files in os.walk(startpath):
        absPath = root.replace(startpath,'')
        if absPath != '':
            listFiles.append(absPath)
        for f in files:
            listFiles.append('{}/{}'.format(absPath,f))
    print(listFiles)
    return listFiles
        

def recvTh(soc):
    while 1:
        msg=soc.recv(1024).decode()
        cmd = msg.split(' ')[0]
        #print("command is ",cmd)
        if msg == "dirlist":
            dirlist = list_files(pathName)
            soc.sendall(pickle.dumps(dirlist))
            q.put("done")
        elif cmd == "readfile":
            filepath= "root/"+msg.split(' ')[1]
            f = open(filepath)
            filecont = f.read()
            soc.sendall(filecont.encode('utf-8'))
            f.close()
        elif cmd == "updatefile":
            filename = msg.split(' ')[1]
            filepath= "root/"+filename
            fileCont = msg.replace(cmd+" "+filename+" ","",1)
            f = open(filepath, 'w')
            f.write(fileCont)
            f.close()
        elif cmd == "deletefile":
            filename = msg.split(' ')[1]
            filepath= "root/"+filename
            os.remove(filepath)
            soc.sendall((filename+" deleted from server").encode('utf-8'))
        elif msg == "":
            print("Connection closed with name server")
            soc.close()
            os._exit(0)




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

    delayMsg = q.get()
    while input()!="exit":
        pass
    s.close()
    os._exit(0)

if __name__ == "__main__":
	main() 