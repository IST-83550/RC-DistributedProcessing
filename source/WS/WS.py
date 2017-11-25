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
import re
import sys
import math
import signal
import socket
import select
import argparse

from WorkingServer import WorkingServer

INPUTS = [sys.stdin]
INPUT_DIR = 'input_files/'


def signal_handler(signal, frame):
    
    """
    Signal Handler (SIGINT).

    """
    
    working_server.sendData("UNR " + working_server.getCSname() + " " + \
                                str(working_server.getWSport()))
    data = working_server.receiveData()
    print data[0]
    working_server.closeSocket()
    sys.exit(0)

def processText(filename, ptc):
    
    """
    Function to process text. Word count, find longest word, upper, lower.

    """
    
    path = INPUT_DIR + filename
    
    # Checks if file exists.
    if not os.path.isfile(path):
        return
    
    data = open(path, 'r').read()
    
    # Word count request.
    if ptc == 'WCT':
        word_pattern = "\w+"
        
        words = re.findall(word_pattern, data.lower())
        
        length = len(words)
        
        # Check log domain.
        if length > 0:
            digits = int(math.log10(length)) + 1
        else:
            digits = 0
                
        data_size = str(digits)
        
        working_server.sendTCPData("REP R " + data_size + " " + str(length))
        
        return 'Number of words: ' + str(length)
    
    # Find longest word request.
    elif ptc == 'FLW':
        word_pattern = "\w+"

        regex = re.compile(word_pattern)
        words_found = regex.findall(data)
        
        if words_found:
            longest_word = max(words_found, key=lambda word: len(word))
            
            data_size = str(len(longest_word))
                
            working_server.sendTCPData("REP R " + data_size + " " + longest_word)
            
            return 'Longest word: ' + longest_word
            
        return
    
    # Upper request.
    elif ptc == 'UPP':
        
        write_data = data.upper()
        
        file = open(path, 'w')
        file.write(write_data)
        
        data_size = str(len(data))
        
        working_server.sendTCPData("REP F " + data_size + " " + write_data)
        
        return data_size + ' Bytes received'
    
    # Lower request.
    elif ptc == 'LOW':
        
        write_data = data.lower()
        
        file = open(path, 'w')
        file.write(write_data)
        
        data_size = str(len(data))
        
        working_server.sendTCPData("REP F " + data_size + " " + write_data)
        
        return data_size + ' Bytes received'
    
    
def handleRequest():
    
    """
    Function to handle request.
    
    """

    conn =  working_server.getTCPConAddress()
    print 'Connected by ', conn
    
    # Parse received data.
    # Receive command.
    cmd = working_server.receiveTCPData(3)
    
    # Working request command.
    if cmd == 'WRQ':
        filename = ''
        data_size = ''
        char = ''
        
        # Receive process task.
        ptc = working_server.receiveTCPData(5).split()[0]
        
        # Receive filename.
        while char != ' ':
            filename += char
            char = working_server.receiveTCPData(1)
        
        # Receive file size.
        while True:
            char = working_server.receiveTCPData(1)
            if char.isdigit():
                data_size += char
            else:
                break
        
        print 'Received ' + data_size + ' Bytes.'
        
        # Receive data.
        data = working_server.receiveTCPData(int(data_size))
        
        working_server.createInputFile(filename, data)
        
        processed = processText(filename, ptc)
            
    print 'Finishing connection with ', conn



if __name__ == "__main__":
    
    """
        Main method.
    """
    
    # Parse arguments.
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-p',  metavar='WSport', type=int, required=False, default=59000,
                        help='WSport is the well-known port where the WS server accepts \
                        requests from  users. This is an optional argument. If omitted, \
                        it assumes the value 59000.')
                        
    parser.add_argument('-n', metavar='CSname', type=str, required=False,
                        default=socket.gethostbyname(socket.gethostname()),
                        help='CSname is the  name  of  the  machine  where  the central \
                        server  (CS)  runs. This  is  an  optional  argument.  If  this \
                        argument  is  omitted,  the  CS  should  be running on the same \
                        machine.')
    
    parser.add_argument('-e', metavar='CSport', type=int, required=False, default=58039,
                        help='CSport is the well-known port where the CS server accepts \
                        user requests, in  TCP. This  is  an  optional  argument.  If   \
                        omitted, it  assumes the  value 58000+GN, where GN is the group \
                        number.')
    
    parser.add_argument('tasks', metavar='Available tasks', type=str, nargs='*')
    
    FLAGS = parser.parse_args()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Unpack arguments.
    WSport, CSname, CSport, availableTasks = FLAGS.p, FLAGS.n , FLAGS.e, FLAGS.tasks
    
    working_server = WorkingServer(WSport, CSname, CSport)
    
    # Register WS with CS (UDP).
    try:
        working_server.sendData("REG " + " ".join(availableTasks) + " " + \
        working_server.getCSname() + " " + str(working_server.getWSport()))
        
        working_server.getUDPSocket().settimeout(3)
        
    except socket.timeout:
        
        print 'Timeout: Unable to establish connection with CS.'
        sys.exit(0)
    
    data = working_server.receiveData()
    
    print data[0]
    
    if data[0] == "RAK OK\n":
        working_server.startTCPServer()
        
    elif data[0] == "RAK NOK\n":
        print data[0]
        working_server.closeSocket()
        sys.exit(0)
        
    
    INPUTS.append(working_server.getTCPSocket())
    
    
    cmd = ''
    
    while cmd != 'exit':
        
        ready_to_read, ready_to_write, in_error =  select.select(INPUTS, [], [])
        
        for sock in ready_to_read:
            
            if sock == working_server.getTCPSocket():
                
                working_server.acceptTCPConnection()
                handleRequest()
                working_server.closeTCPConnection()
                
            elif sock == sys.stdin:
                cmd = raw_input("")

    working_server.closeSocket()