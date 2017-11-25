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
import argparse

from Client import Client

def handleUserCommand(cmd):
    
    """
    Function to handle user command. Receives parsed input and sends data to
    Central Server (CS) accordingly to specified command.

    Parameters:
        cmd (str): User command.
    
    """

    """             
       Receive and parse input.
    """ 
    cmd = cmd.split()
    
    if cmd and cmd[0] in client.getCommands():
        
        task = cmd[0]
        
        client.connect()
        
        # Exit command.
        if task == "exit":
            client.disconnect()
            os._exit(0)
        
        # List command.
        elif task == "list":
            cs_cmd = client.getCommands()[task]
            client.sendData(cs_cmd)
            
            handleCSResponses(None, None)
        
        # Request command.
        elif task == "request":
            
            if len(cmd) == 3 and cmd[1] in client.getPtcs():

                args = cmd[1:]

                # Checks if file exists.
                if not os.path.isfile(args[1]):
                    print 'ERROR: File Not found'
                    return
                    
                data = open(args[1]).read()
                cs_cmd = client.getCommands()[task]
                data_size = str(len(data))
                
                print '\t', data_size, 'bytes to transmit.'
                
                client.sendData(cs_cmd + " " + args[0] + " " + data_size + " " + data)
                
                handleCSResponses(args[1], args[0])
                
            else:
                print 'Invalid request format.'
                
    else:
        print "No such command."



def handleCSResponses(filename, ptc):
    
    """
    Function to handle Central Server responses. Handles received answer from
    the Central Server (CS) and displays them.
    
    Parameters:
        filename (str): user input file name.
        ptc (str): processing task code.   
    
    """
    
    cmd = client.receiveData(3)
            
    # List command CS response.
    if cmd == "FPT":
        
        # Read space.
        client.receiveData(1) 
        
        ptc_count = ''
        message = ''
        
        while True:
            char = client.receiveData(1)
            if char.isdigit():
                ptc_count += char
            else:
                message += char
                break
            
        if ptc_count == '':
            
            while True:
                char = client.receiveData(1)
                
                if char == '\n':
                    
                    if message == 'ERR':
                        print "Error: FPT ERR."
                        client.disconnect()
                        return
                    
                    elif message == 'EOF':
                        print "Error: FPT EOF."
                        client.disconnect()
                        return
                    
                else:
                    message += char
        
        ptcs = []
        
        for i in range(int(ptc_count)):
            ptcs.append(client.receiveData(4).split()[0])
        
        for i in range(int(ptc_count)):
            print str(i + 1) + " - " + ptcs[i]
            
    # Request command CS response.
    elif cmd == "REP":
        
        # Read space.
        client.receiveData(1)
        
        rt = client.receiveData(1)
        
        if rt not in ['F', 'R']:
            err = rt + client.receiveData(2)
            
            if err == 'ERR':
                print "Error: REP ERR."
                client.disconnect()
                return
            
            elif err == 'EOF':
                print "Error: REP EOF."
                client.disconnect()
                return
        
        # Read space.
        client.receiveData(1)
        
        data_size = ''
        
        while True:
            char = client.receiveData(1)
            
            if char.isdigit():
                data_size += char
            else:
                break
            
        # Receive  CS data.
        data = client.receiveData(int(data_size))
            
        # Upper or Lower command output.
        if rt == 'F':
            
            received_file = filename[:-4] + "_" + ptc + '.txt'
            
            print 'received file ' + received_file
            #print '\t' + data_size + ' Bytes expected. Received: ' + str(len(data))
            
            # Write result to file.
            file = open(received_file, 'w')
            file.write(data)
            file.flush()
            os.fsync(file.fileno())
            file.close()
            
        # Word count command output.
        elif ptc == 'WCT':
            print 'Number of words: ' + data
            
        # Find longest Word command output.
        elif ptc == 'FLW':
            print 'Longest word: ' + data
        
    client.disconnect()



if __name__ == "__main__":
    
    """
    Main Method.

    """

    # Parse arguments.
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-n', metavar='CSname', type=str, required=False,
                        default=str(socket.INADDR_ANY),
                        help='CSname is  the  name  of  the  machine  where  the  central \
                        server  (CS)  runs. This  is  an  optional  argument.  If  this   \
                        argument  is  omitted,  the  CS  should  be running on the same   \
                        machine.')
    
    parser.add_argument('-p',  metavar='CSport', type=int, required=False, default=58039,
                        help='CSport is the well-known port where the CS server accepts   \
                        user requests, in  TCP. This  is  an  optional  argument.  If     \
                        omitted,  it  assumes  the  value 58000+GN, where GN is the group \
                        number.')
    
    FLAGS = parser.parse_args()
    
    # Unpack arguments.
    CSname, CSport = FLAGS.n, FLAGS.p
    
    client = Client(CSname, CSport)
    
    # Input parse.
    while True:
        
        cmd = raw_input("> ")
        
        handleUserCommand(cmd)