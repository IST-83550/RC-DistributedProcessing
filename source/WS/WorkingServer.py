"""

    Intituto Superior Tecnico - 17/18
    
    Computer Networks.
    
    Programming using the Sockets interface.
    RC Distributed Processing

    83467 - Francisco Neves
    83468 - Francisco Catarrinho
    83550 - Pedro Santos

"""
import os
import socket
import glob
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'socketwrapper')))
from SocketWrapper import SocketWrapper as _socket
        
class WorkingServer:
    
    """
        Client class to encapsulate Working Server(WS) socket-related operations.

        Attributes:
            WSport: Working Server (WS) port.
            CSname: Central Server (CS) name.
            CSport: Central Server (CS) port.
            udp_socket: UDP socket.
            tcp_socket: TCP socket.
            input_directory (str): Input files directory.
            tcp_connection (tuple): TCP connections.
            data_size (int): UDP Buffer size.
        
    """
    
    # UDP socket buffer size.
    buffer_size = 1024
    
    input_directory = 'input_files/'
    
    def __init__(self, WSport, CSname, CSport):
        
        self.WSport = WSport
        self.CSname = socket.gethostbyname(CSname)
        self.CSport = CSport

        # UDP Socket.
        self.udp_socket = _socket(self).socketUDP()
        
        # TCP Socket.
        self.tcp_socket = _socket(self).socketTCP()
        self.tcp_connection = ()
        
        try:
            if not os.path.exists(self.input_directory):
                os.makedirs(self.input_directory)
                
            os.chdir(self.input_directory)
            files=glob.glob('*.txt')
            for filename in files:
                os.unlink(filename)
                
            abspath = os.path.abspath(__file__)
            dname = os.path.dirname(abspath)
            os.chdir(dname)
                
        except OSError:
            print 'File initializing error'
            pass
    
    def getWSport(self):
        return self.WSport
    
    def getCSname(self):
        return self.CSname
        
    def getCSport(self):
        return self.CSport
        
    def getUDPSocket(self):
        return self.udp_socket.getSocket()
        
    def receiveData(self):
        data, addr = self.udp_socket.recvfrom(self.buffer_size) 
        return data, addr
        
    def sendData(self, data):
        self.udp_socket.sendto(data + "\n", (self.CSname, self.CSport))
        
    def closeSocket(self):
        self.udp_socket.close()
    
    def getTCPSocket(self):
        return self.tcp_socket.getSocket()
        
    def getTCPConnection(self):
        return self.tcp_connection[0]
    
    def getTCPConAddress(self):
        return self.tcp_connection[1]
        
    def startTCPServer(self):
        self.tcp_socket.bind((str(socket.INADDR_ANY), self.WSport))
        self.tcp_socket.listen(5)

    def acceptTCPConnection(self):
        conn, addr = self.tcp_socket.accept()
        self.tcp_connection = (conn, addr)
        
    def receiveTCPData(self, bytes):
        return self.tcp_connection[0].recv(bytes, socket.MSG_WAITALL)
        
    def sendTCPData(self, message):
        self.tcp_connection[0].sendall(message + "\n")
   
    def closeTCPSocket(self):
        self.tcp_socket.close()
        
    def closeTCPConnection(self):
        self.getTCPConnection().close()
    
    def createInputFile(self, filename, data):   
        file = open(self.input_directory + filename, 'w')
        file.write(data)
        