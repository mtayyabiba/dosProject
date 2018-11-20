import os, select
import socket as sc

hostIp = '127.0.0.1'
clientPort = 6969

def main():
    with sc.socket(sc.AF_INET, sc.SOCK_STREAM) as masterClientSocket:
        masterClientSocket.bind((hostIp,clientPort))
        masterClientSocket.listen(5)
        inputs = [masterClientSocket]
        outputs = []
        print('client listening socket created on ',hostIp,':',clientPort)
        while True: 
            #clientConn, clientAddr = masterClientSocket.accept()      
            #print ('Got connection from', clientAddr )
            #clientConn.send('Thank you for connecting')
            #clientConn.close()
            readable, writable, exceptional = select.select(
        inputs, outputs, inputs)
            for s in readable:
                if s is masterClientSocket:
                    connection, client_address = s.accept()
                    connection.setblocking(0)
                    inputs.append(connection)
                    connection.sendall(b'Server')
                else:
                    data = s.recv(1024)
                    if data:
                        print(data)
                    else:
                        print("connection closed ",s.getpeername())
                        inputs.remove(s)
                        s.close()

if __name__ == "__main__":
	main()
