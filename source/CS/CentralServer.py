"""

    Intituto Superior Tecnico 17/18
    
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

#sys.path.append('../socketwrapper')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'socketwrapper')))
from SocketWrapper import SocketWrapper as _socket

class CentralServer:
    
    """
        Client class to encapsulate Central Server(CS) socket-related operations.

        Attributes:
            CSname: Central Server (CS) name.
            CSport: Central Server (CS) port.
            tcp_socket: TCP socket.
            udp_socket: UDP socket.
            buffer_size (int): UDP socket buffer size.
            client_commands (list): Client commands.
            ws_commands (list): Working Servers commands.
            file_processing_tasks (str): file processing tasks file.
            input_directory (str): Input files directory.
            output_directory (str): Output files directory.
        
    """
    
    # UDP socket buffer size.
    buffer_size = 1024
    
    client_commands = ['LST', 'REQ']
    ws_commands = ['REG', 'RAK', 'UNR', 'UAK']
    
    file_processing_tasks = "file_processing_tasks.txt"
    input_directory = 'input_files/'
    output_directory = 'output_files/'
    
    
    def __init__(self, CSport):
        
        self.CSname = str(socket.INADDR_ANY)
        self.CSport = CSport
        
        # TCP Socket.
        self.tcp_socket = _socket(self).socketTCP()
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # UDP Socket.
        self.udp_socket = _socket(self).socketUDP()
        
        self.tcp_connection = ()
        
        try:
            os.remove(self.file_processing_tasks)
                
        except OSError:
            pass
        
        try:
            if not os.path.exists(self.input_directory):
                os.makedirs(self.input_directory)
                
            if not os.path.exists(self.output_directory):
                os.makedirs(self.output_directory)
            
            create_tasks_file = open(self.file_processing_tasks, 'w+')    
            
            os.chdir(self.input_directory)
            files=glob.glob('*.txt')
            for filename in files:
                os.unlink(filename)
                
            abspath = os.path.abspath(__file__)
            dname = os.path.dirname(abspath)
            os.chdir(dname)
            
            os.chdir(self.output_directory)
            files=glob.glob('*.txt')
            for filename in files:
                os.unlink(filename)
                
            abspath = os.path.abspath(__file__)
            dname = os.path.dirname(abspath)
            os.chdir(dname)
        except OSError:
            print 'File initializing error'
            pass
              
    def getCSname(self):
        return self.CSname
        
    def getCSport(self):
        return self.CSport
        
    def getClientCommands(self):
        return self.client_commands
        
    # ---------- TCP WS operations ----------
    
    def connectWS(self, addr):
        self.ws_socket = _socket(self).socketTCP()
        self.ws_socket.connect(addr)
        
    def sendWSData(self,data):
        self.ws_socket.sendall(data + "\n")
        
    def recvWSData(self, data_size):
        return self.ws_socket.recv(data_size, socket.MSG_WAITALL)
        
    def disconnectWS(self):
        self.ws_socket.close()
        
    def getWSCommands(self):
        return self.ws_commands
       
    def registerWS(self, ws_tasks, ws_conn):
        with open(self.file_processing_tasks, 'a') as file:
            for task in ws_tasks:
                file.write(task + " " + ws_conn[0] + " " + str(ws_conn[1]) + "\n")

    def removeWS(self, ws_addr):
        new_processing_tasks = ''
        ws_tasks = []
        with open(self.file_processing_tasks) as current:
            for line in current:
                if not all(word in line for word in ws_addr):
                    new_processing_tasks += line
                else:
                    ws_tasks.append(line.split()[0])

        new_processing_tasks_file = open(self.file_processing_tasks, 'w')
        new_processing_tasks_file.write(new_processing_tasks)
        return ws_tasks
    
    def getAvailableWS(self, task):
        available_ws = []
        with open(self.file_processing_tasks, 'r') as file:
                for line in file:
                    line_content = line.split()
                    if task == line_content[0]:
                        available_ws.append((line_content[1], int(line_content[2])))
        return available_ws
        
    def getTotalWS(self):
        ws_list = []
        with open(self.file_processing_tasks, 'r') as file:
            for line in file:
                line_content = line.split()
                addr = (line_content[1], int(line_content[2]))
                if addr not in ws_list:
                    ws_list.append(addr)
        return len(ws_list)
    
    # ----------- Client Commands  -----------
    
    def getAvailableTasks(self):
        available_tasks = []
        if os.path.isfile(self.file_processing_tasks):
            with open(self.file_processing_tasks, 'r') as file:
                for line in file:
                    task = line.split()[0]
                    if task not in available_tasks:
                        available_tasks.append(task)
            return available_tasks
        else:
            return available_tasks
        
    def createInputFile(self, filename, data):   
        file = open(self.input_directory + filename + '.txt', 'w')
        file.write(data)
        file.flush()
        os.fsync(file.fileno())
        file.close()
        
    def createOutputFile(self, filename, data):
        file = open(self.output_directory + filename + '.txt', 'w')
        file.write(data)
        file.flush()
        os.fsync(file.fileno())
        file.close()
            
    # ------------ TCP  ------------
    
    def getTCPSocket(self):
        return self.tcp_socket.getSocket()
        
    def getTCPConnection(self):
        return self.tcp_connection[0]
    
    def getTCPConAddress(self):
        return self.tcp_connection[1]
        
    def startTCPServer(self):
        self.tcp_socket.bind((self.CSname, self.CSport))
        self.tcp_socket.listen(5)

    def acceptTCPConnection(self):
        conn, addr = self.tcp_socket.accept()
        self.tcp_connection = (conn, addr)
        
    def receiveTCPData(self, bytes):
        return self.tcp_connection[0].recv(bytes, socket.MSG_WAITALL)
        
    def receiveNonBlockingTCPData(self, bytes):
        return self.tcp_connection[0].recv(bytes)
        
    def sendTCPData(self, message):
        self.tcp_connection[0].sendall(message + "\n")

    def closeTCPSocket(self):
        self.tcp_socket.close()
        
    def closeTCPConnection(self):
        self.getTCPConnection().close()
        
    # ------------ UDP  ------------
        
    def getUDPSocket(self):
        return self.udp_socket.getSocket()
        
    def startUDPServer(self):
        self.udp_socket.bind((self.CSname, self.CSport))
        
    def sendUDPData(self, data, conn):
        self.udp_socket.sendto(data + "\n", conn)
        
    def receiveUDPData(self):
        data, addr = self.udp_socket.recvfrom(self.buffer_size) 
        return data, addr
        
    def closeUDPSocket(self):
        self.udp_socket.close()