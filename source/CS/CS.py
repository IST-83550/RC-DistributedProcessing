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
import math
import sys
import socket
import select
import argparse
import glob
import time

from CentralServer import CentralServer

SOCKET_INPUTS_LIST = []
SOCKET_OUTPUTS_LIST = []

OUTPUT_DIR = 'output_files/'
INPUT_DIR = 'input_files/'



def handle_user():
    
    """
    Function to handle user request. Splits and sends data to Working Servers (WS)
    accordingly to specified command and servers availability.

    """

    central_server.closeTCPSocket()
    conn = central_server.getTCPConAddress()

    print 'Connected by ', conn

    """
       Receive and parse data input.
    """ 
    # Receive command.
    cmd = central_server.receiveNonBlockingTCPData(3)

    if cmd and cmd in central_server.getClientCommands():

        # List command.
        if cmd == 'LST':
            
            while True:
                
                remaind = central_server.receiveNonBlockingTCPData(20)
                
                if len(remaind) == 1:
                    break
                
                else:
                    central_server.sendTCPData("FPT ERR")
                    print 'Finishing connection with ', conn
                    central_server.closeTCPConnection()
                    sys.exit(0)
                    
            print 'List request: ', conn
            ptcs = central_server.getAvailableTasks()
            ptc_count = len(ptcs)
            
            if ptc_count == 0:
                central_server.sendTCPData("FPT EOF")
                print 'Finishing connection with ', conn
                central_server.closeTCPConnection()
                sys.exit(0)
            
            central_server.sendTCPData("FPT " + str(ptc_count) + " " + " ".join(ptcs))

        # Request command.
        if cmd == 'REQ':
            data_size = ''

            # Receive process task.
            ptc = central_server.receiveNonBlockingTCPData(5)

            if not ptc.strip():
                central_server.sendTCPData("REP ERR")
                print 'Finishing connection with ', conn
                central_server.closeTCPConnection()
                sys.exit(0)
            
            ptc = ptc.split()[0]
            
            if ptc not in central_server.getAvailableTasks():
                central_server.sendTCPData("REP EOF")
                print 'Finishing connection with ', conn
                central_server.closeTCPConnection()
                sys.exit(0)
            
            # Receive data size.
            while True:
                char = central_server.receiveTCPData(1)
                if char.isdigit():
                    data_size += char
                else:
                    break
                
            if len(data_size) == 0 or int(data_size) == 0:
                central_server.sendTCPData("REP ERR")
                print 'Finishing connection with ', conn
                central_server.closeTCPConnection()
                sys.exit(0)

            # Receives data from User.
            data = central_server.receiveTCPData(int(data_size))

            """             
               Stores Input data in InputFile.
            """ 
            # Store data as a file in input_files folder.
            client_pid = str(os.getpid()).zfill(5)

            central_server.createInputFile(client_pid, data)

            """             
               Splits data given WSs availability and PTCs.
            """ 
            available_working_servers = central_server.getAvailableWS(ptc)
            ws_count = len(available_working_servers)
            
            save_data_chuncks = [''] * ws_count
            
            path = INPUT_DIR + client_pid + ".txt"
            
            # Checks if file exists.
            if not os.path.isfile(path):
                central_server.sendTCPData("REP ERR")
                print 'Finishing connection with ', conn
                central_server.closeTCPConnection()
                sys.exit(0)

            num_lines_per_ws = sum(1 for line in open(path)) // ws_count
            curr_ws = 0

            with open(path, 'r') as infp:
                
                data_to_send = infp.read().split('\n')
                
                for i in range(ws_count):
                    if i == ws_count - 1:
                        save_data_chuncks[i] = '\n'.join(data_to_send[i * num_lines_per_ws:])
                    else:
                        save_data_chuncks[i] = '\n'.join(data_to_send[i * num_lines_per_ws : \
                                                    (i + 1) * num_lines_per_ws]) + '\n'
                
            """
               Sends data to selected WSs.
            """ 
            num_processes = 0

            for i in range(0, ws_count):

                pid = os.fork()
                if pid == 0:
                    central_server.connectWS(available_working_servers[i])
                    central_server.sendWSData('WRQ' + ' ' + ptc + ' ' + client_pid + str(i).zfill(3) + \
                                    '.txt ' + str(len(save_data_chuncks[i])) + ' ' + save_data_chuncks[i])

                    data_size = ''

                    cmd = central_server.recvWSData(4).split()[0]

                    if cmd == 'REP':

                        rep_rt = central_server.recvWSData(2).split()[0]

                        # Receive file size.
                        while True:
                            char = central_server.recvWSData(1)
                            if char.isdigit():
                                data_size += char
                            else:
                                break

                        # Receive data.
                        data = central_server.recvWSData(int(data_size))
                        
                        print 'Received ' + str(len(data)) + ' Bytes from working server ' + \
                                str(i) + '. Expected: ' + data_size

                        central_server.createOutputFile(client_pid + str(i).zfill(3), data)

                    central_server.disconnectWS()

                    sys.exit(0)

                else:

                    num_processes += 1

            """
               Waits for all WSs responses.
            """ 
            for _ in range(num_processes):
                os.wait()

            """
               Concatenate all WSs responses.
            """ 
            # Opens output files directory to concatenate data.
            os.chdir('output_files/')
            files = glob.glob(client_pid + '*.txt')
            os.chdir(sys.path[0])
            
            rt = ''

            # Upper and lower commands (UPP, LOW).
            if ptc in ['UPP', 'LOW']:

                final_data = ''

                # Concatenate data from all Working Servers.
                for filename in sorted(files):
                    
                    path = OUTPUT_DIR + filename
                    
                    # Checks if file exists.
                    if not os.path.isfile(path):
                        return
                    
                    final_data += open(path, 'r').read()

                data_size = str(len(final_data))
                
                rt = 'F'

            # Word count command (WCT).
            elif ptc == 'WCT': 
                               
                final_data = 0 

                # Sum all Working Servers responses.
                for filename in files:
                    
                    path = OUTPUT_DIR + filename
                    
                    # Checks if file exists.
                    if not os.path.isfile(path):
                        return
                    
                    data = open(path, 'r').read()
                    
                    if data:
                        final_data += int(data)

                # Check log domain.
                if final_data > 0:
                    digits = int(math.log10(final_data)) + 1
                else:
                    digits = 0

                data_size = str(digits)
                
                final_data = str(final_data)
                
                rt = 'R'

            # Find longest word command (FLW).
            elif ptc == 'FLW':

                data = ''
                final_data = ''

                # Concatenate responses from all Working Servers.
                for filename in files:
                    
                    path = OUTPUT_DIR + filename
                    
                    # Checks if file exists.
                    if not os.path.isfile(path):
                        return
                    
                    data += open(path, 'r').read() + " "

                # Find biggest word among all WSs responses.
                word_pattern = "\w+"

                regex = re.compile(word_pattern)
                words_found = regex.findall(data)

                if words_found:
                    final_data = max(words_found, key=lambda word: len(word))

                data_size = str(len(final_data))
                
                rt = 'R'
            
            """             
               Stores Output data in OutputFile.
            """ 
            file = open(OUTPUT_DIR + client_pid + '.txt', 'w')
            file.write(final_data)
            file.flush()
            file.close()
            
            """             
               Sends processed data back to user.
            """
            print 'Sending: ' + str(len(final_data)) + ' Bytes'
            central_server.sendTCPData("REP " + rt + " " + data_size + " " + final_data)

    else:
        central_server.sendTCPData("ERR")

    print 'Finishing connection with ', conn
    
    central_server.closeTCPConnection()

    sys.exit(0)
    


def handle_workingServer():
    
    """
    Function to handle working servers(WS) registration.

    """

    data, addr = central_server.receiveUDPData()
    cmd = data.split()

    if cmd[0] in central_server.getWSCommands():

        # WS registration.
        if cmd[0] == 'REG':
            ws_tasks = cmd[1:-2]
            ws_conn = cmd[-2:]
            
            total_ws = central_server.getTotalWS()
            
            if total_ws <= 10:
            
                rak_status = central_server.registerWS(ws_tasks, ws_conn)
                print '+' + " ".join(ws_tasks) + " " +  ws_conn[0] + " " + str(ws_conn[1])
                central_server.sendUDPData("RAK OK", addr)
            
            else:
                central_server.sendUDPData("RAK NOK", addr)
                print 'Working server limit reached.'

        # WS deregistration.
        elif cmd[0] == 'UNR':
            
            central_server.sendUDPData("UAK OK", addr)
            ws_tasks = central_server.removeWS((cmd[1], cmd[2]))
            print '-' + " ".join(ws_tasks) + " " + cmd[1] + " " + str(cmd[2])



if __name__ == "__main__":
    
    """
    Main Method.

    """
    
    # Parse arguments.
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', metavar='CSport', type=int, required=False, default=58039,
                        help='CSport is the well-known port where the CS server accepts user requests, in  TCP. \
                        This  is  an  optional  argument.  If  omitted,  it  assumes  the  value 58000+GN, where\
                        GN is the group number.')

    FLAGS = parser.parse_args()

    CSport = FLAGS.p

    central_server = CentralServer(CSport)

    SOCKET_INPUTS_LIST.append(central_server.getTCPSocket())
    SOCKET_INPUTS_LIST.append(central_server.getUDPSocket())

    central_server.startTCPServer()
    central_server.startUDPServer()

    while True:

        ready_to_read, ready_to_write, in_error =  select.select(SOCKET_INPUTS_LIST, SOCKET_OUTPUTS_LIST, [], 0)

        for sock in ready_to_read:
            if sock == central_server.getTCPSocket():
                central_server.acceptTCPConnection()
                pid = os.fork()

                if pid == 0:
                    handle_user()
                    sys.exit(0)

                else:
                    central_server.closeTCPConnection()

            elif sock == central_server.getUDPSocket():
                handle_workingServer()
