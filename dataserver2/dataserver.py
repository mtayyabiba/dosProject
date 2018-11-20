import socket as sc           
          
port = 6970
hostIp = '127.0.0.1'
s = sc.socket(sc.AF_INET, sc.SOCK_STREAM)               
s.connect((hostIp, port)) 
print(s.recv(1024)) 
while True:
    userI = input("Please enter something \n")
    s.sendall(userI.encode('utf-8'))

#s.close() 