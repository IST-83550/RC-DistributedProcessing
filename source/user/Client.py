"""

    Intituto Superior Tecnico - 17/18
    
    Computer Networks.
    
    Programming using the Sockets interface.
    RC Distributed Processing

    83467 - Francisco Neves
    83468 - Francisco Catarrinho
    83550 - Pedro Santos

"""
import socket
import sys

sys.path.append('../socketwrapper')
from SocketWrapper import SocketWrapper as _socket

class Client:
    
    """
        Client class to encapsulate Client(User) socket-related operations.

        Attributes:
            CSname: Central Server (CS) name.
            CSport: Central Server (CS) port.
            socket: TCP socket.
            commands (dict): Allowed commands list.
            ptcs (list): Allowed process task code list.
        
    """

    commands = {'list': 'LST', 'request': 'REQ', 'exit': '_'}
    ptcs = ['UPP', 'LOW', 'WCT', 'FLW']
    
    def __init__(self, CSname, CSport):
        
        self.CSname = socket.gethostbyname(CSname)
        self.CSport = CSport
        self.socket = None
        
    def getCSname(self):
        return self.CSname
        
    def getCSport(self):
        return self.CSport
        
    def getSocket(self):
        return self.socket.getSocket()
    
    def getCommands(self):
        return self.commands
    
    def getPtcs(self):
        return self.ptcs
    
    def connect(self):
        self.socket = _socket(self).socketTCP()
        self.socket.connect((self.CSname, self.CSport))
        
    def sendData(self, message):
        self.socket.sendall(message + "\n")
        
    def receiveData(self, bytes):
        return self.socket.recv(bytes, socket.MSG_WAITALL)
        
    def disconnect(self):
        self.socket.close()
        