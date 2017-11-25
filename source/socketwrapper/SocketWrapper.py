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
import os
import errno
    
class SocketWrapper:
    
    """
        SocketWrapper class to encapsulate OS socket operations and handle errors
        that may occur.

        Attributes:
            owner (class): the class that is opperating this socket. 
            socket: socket which will be manipulated.
        
    """
    
    def __init__(self, owner):
        self.owner = owner

    def socketTCP(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            return self
        except socket.error as e:
            self.handleError(e)

    def socketUDP(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return self
        except socket.error as e:
            self.handleError(e)
            
    def getSocket(self):
        return self.socket
        
    def setsockopt(self, arg1, arg2, arg3):
        try:
            self.socket.setsockopt(arg1, arg2, arg3)
        except socket.error as e:
            self.handleError(e)
        
    def connect(self, addr):
        try:
            self.socket.connect(addr)
        except socket.error as e:
            self.handleError(e)
        
    def sendall(self, data):
        try:
            self.socket.send(data)
        except socket.error as e:
            self.handleError(e)
        
    def recv(self, size, flag=None):
        try:
            return self.socket.recv(size) if not flag else self.socket.recv(size, flag)
        except socket.error as e:
            self.handleError(e)
        
    def sendto(self, data, conn):
        try:
            self.socket.sendto(data, conn)
        except socket.error as e:
            self.handleError(e)
        
    def recvfrom(self, size):
        try:
            return self.socket.recvfrom(size)
        except socket.error as e:
            self.handleError(e)
            
    def close(self):
        try:
            self.socket.close()
        except socket.error as e:
            self.handleError(e)
        
    def bind(self, (ip, port)):
        try:
            self.socket.bind((ip, port))
        except socket.error as e:
            self.handleError(e)
    
    def listen(self, backlog):
        try:
            self.socket.listen(backlog)
        except socket.error as e:
            self.handleError(e)
        
    def accept(self):
        try:
            return self.socket.accept()
        except socket.error as e:
            self.handleError(e)
    
    def ownedByCentralServer(self):
        return self.owner.__class__.__name__ == 'CentralServer'
        
    def handleError(self, e):
        """
        Function that digests the error occured and kills the process for safety,
        if it is not a CentralServer (which should be kept alive as much as possible)
        
        """
        if e.errno == errno.ECONNREFUSED:
            print '[SOCKET ERROR] Connection refused'
            return True if self.ownedByCentralServer() else sys.exit(0)
            
        elif e.errno == errno.EADDRINUSE:
            print '[SOCKET ERROR] Address already in use'
            return True if self.ownedByCentralServer() else sys.exit(0)
            
        elif e.errno == errno.EPIPE:
            print '[SOCKET ERROR] Broken pipe'
            return True if self.ownedByCentralServer() else sys.exit(0)
            
        elif e.errno == errno.ECONNRESET:
            print '[SOCKET ERROR] Connection reset by peer'
            return True if self.ownedByCentralServer() else sys.exit(0)
            
        elif e.errno == errno.ETIMEDOUT:
            print '[SOCKET ERROR] Connection timed out'
            return True if self.ownedByCentralServer() else sys.exit(0)
            
        else:
            print '[SOCKET ERROR] Unkown. Errno: ', e.errno
            return True if self.ownedByCentralServer() else sys.exit(0)