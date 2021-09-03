#! /usr/bin/env python
#This script is an example for a simulator for the asprilo visualizer.
#The simulator uses a given instance to produce the problems. The simulator uses the networking
#interface from the visualizer and is written to work along with it.

import argparse
import select
import socket

from clingo.control import Control
from clingo.symbol import parse_term

VERSION = '0.2.1'

class Simulator(object):
    def __init__(self):
        super(Simulator, self).__init__()
        self._name = 'simulator'

        self._parser = argparse.ArgumentParser()
        self._parser.add_argument('-p', '--port', 
                            help='the port the solver will send the anwsers to',
                            type=int, default = 5000)
        self._parser.add_argument('-v', '--version',
                            help='show the current version', action='version',
                            version=VERSION)
        self._parser.add_argument('-t', '--templates',
                            help='files to load',
                            nargs='+',
                            type=str, default = '')
        self._args = None

        #socket properties
        self._host = '127.0.0.1'
        self._port = '5000'
        self._socket = None
        self._connection = None
        self._name = 'simulator'

        #saves the raw sended data
        self._raw_data = ''
        #array of processed data
        self._data = []
        #this dictonary contains all occurs atoms
        #the key is the time step in which they should be sended to the visualizer
        self._to_send = {}
        #the last sended time step
        self._sended = -1

    def __del__(self):
        self.close()

    #open the socket and wait for an incomming connection
    def connect(self):
        try:
            self._socket = socket.socket()
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((self._host, self._port))
            self._socket.listen(1)
            self._connection, addr = self._socket.accept()
            print('Connection with: ' + str(addr))
            self.on_connect()
        except socket.error as error:
            self.close()
            print(error)
            return -1
        return 0

    #is called when a connection is etablished
    #resets the visualizer and sends the new instance to it
    def on_connect(self):
        self.send('%$RESET.')
        self.send_step(0)

    #close the connection and the socket
    def close(self):
        if self._connection is not None:
            try:
                self._connection.shutdown(socket.SHUT_RDWR)
            except socket.error as error:
                print(error)
            self._connection.close()
            self._connection = None
            print('close ' + self._name)

        if self._socket is not None:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except socket.error as error:
                print(error)
            self._socket.close()
            self._socket = None

    #checks whether data can be read from the socket
    def is_ready_to_read(self, time_out = 0.1):
        if self._connection is None: 
            return False
        ready = select.select([self._connection], [], [], time_out)
        if ready[0]:
            return True
        else:
            return False

    #sends data to the visualizer
    def send(self, data):
        if self._connection is None:
            return
        self._connection.send(data.encode())

    #receive data from the visualizer
    def receive(self, time_out):
        if self._connection is None:
            return -1
        try:
            #checks whether new data is available
            if self.is_ready_to_read(time_out):
                while True:
                    #read data
                    new_data = self._connection.recv(2048).decode()
                    #close the socket if the visualizer closed the socket
                    if not new_data or new_data == '':
                        self.close()
                        return 1
                    self._raw_data += new_data
                    #process the data if the visualizer finished sending
                    #the visualizer ends every sending process with the '\n' character
                    if not new_data.find('\n') == -1:
                        self.on_raw_data(self._raw_data)
                        return 0
            else:
                return 0

        except socket.error as error:
            self.close()
            print(error)
            return -1

    #process the raw data received by the receive function
    #primally splits data in seperate control symbols and asp atoms
    def on_raw_data(self, raw_data):
        #the visualizer seperates every atom and control symbol with the '.' character
        data = raw_data.split('.')
        for atom in data:
            if len(atom) > 0:
                if not (len(atom) == 1 and atom[0] == '\n'):    #the split function returns the string "\n" as last string which should not be processed
                    if atom[0] == '%' and atom[1] == '$':       #strings that begin with '%$' are control symbols and are handles by the on_control_symbol function
                        atom = atom[2 :].lower()
                        self.on_control_symbol(parse_term(atom))
                    else:
                        self._data.append(atom)
        self._raw_data = ''
        if len(self._data) > 0:
            #processed asp atoms
            self.on_data(self._data)
        self._data = []

    #process received control symbols
    def on_control_symbol(self, symbol):
        if symbol.name == 'reset':
            #resets the simulator discard all data
            #the visualizer will send this symbol when it is loading a new instance
            self._to_send = {}
            self._data = []
            self._control = Control()
            self._sended = - 1
        elif symbol.name == 'done' and len(symbol.arguments) == 1:
            try:
                #the visualizer sends 'done([time step])' after it has visualized the time step [time step]
                #sends the data from the _to_send dictonary
                #the key is the next time step
                self.send_step(symbol.arguments[0].number + 1)
            except:
                return

    #sends the data from the _to_send dictonary
    def send_step(self, step):
        #only sends data if it wasn´t send yet
        if step in self._to_send and step > self._sended:
            self._sended = step
            #send the atoms
            for atom in self._to_send[step]:
                self._connection.send((str(atom) + '.').encode())
        #send the '\n' charater to show end of sending
        self._connection.send('\n'.encode())

    #the simulator ignores all data sended by the visualizer
    #it only handels control symbols in on_control_symbol
    def on_data(self, data):
        pass

    #model callback for loaded instances, see __init__
    def on_model(self, model):
        #add empty entry to dictonary
        self._to_send[0] = []
        for atom in model.symbols(atoms=True):
            #handels all atoms with a timestamp
            #all atoms are added to a specific timestamp
            #the simulator will send these after the visulaizer visualized a few timesteps
            if (atom.name == 'init'
                and len(atom.arguments) == 3
                and atom.arguments[0].name == 'object'
                and atom.arguments[1].name == 'value'):
                step = 0
                try:
                    step = int(atom.arguments[2].number)
                except Exception as error:
                    print(error)
                    continue
                #add the timestamp to the dictonary
                if step not in self._to_send:
                    self._to_send[step] = []
                self._to_send[step].append('init(' + str(atom.arguments[0]) + ',' 
                                                   + str(atom.arguments[1]) + ')')
            #handels all atoms without a timestamp
            #all atoms are added to the key 0 to send all atoms immeditly
            else:
                self._to_send[0].append(atom)
        return True

    #simulator main function
    def run(self):
        self._args = self._parser.parse_args()
        self._port = self._args.port

        #load all instance files
        self._control = Control()
        for file_name in self._args.templates:
            self._control.load(file_name)

        #ground and solve
        self._control.ground([('base', [])])
        self._control.solve(on_model = self.on_model)

        print('Start ' + self._name)
        self.connect()
        #loop to receive data
        while(True):
            if self.receive(1.0) != 0:
                return

#main
def main():
    simulator = Simulator()
    simulator.run()   

if __name__ == "__main__":
    main()
