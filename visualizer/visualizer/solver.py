#! /usr/bin/env python
#This script is an example for a solver for the asprilo visualizer.
#It contains 3 different ways to solve instances and delivers plans for visualization.
#All solvers use a given encoding to solve the problems. The solvers use the networking
#interface from the visualizer and are written to work along with it. 
#This script provides an one shot varaint, an incremental and an interactive solver variant.

import argparse
import select
import socket
import clingo
import time

VERSION = '0.2.1'
#default one shot solver
class Solver(object):
    def __init__(self):
        self._parser = argparse.ArgumentParser()
        self._parser.add_argument('-p', '--port', help='the port the solver will send the anwsers to',
                            type=int, default = 5000)
        self._parser.add_argument('-v', '--version',
                            help='show the current version', action='version',
                            version=VERSION)
        self._parser.add_argument('-e', '--encoding',
                            help='the name of the encoding the solver shall use to solve instances', 
                            type = str, default = './encoding.lp')
        self._parser.add_argument('-m', '--mode',
                            help='the mode that the solver should use to solve instances', 
                            type = str, choices=['default', 'incremental', 'interactive', 'online'], default = 'default')
        self._parser.add_argument('-t', '--timeout',
                            help='The maxmimal number of seconds the solver waits for a solution. 0 is no maximum.', 
                            type = int, default = 0)
        self._args = None

        #socket properties
        self._host = '127.0.0.1'
        self._port = '5000'
        self._socket = None
        self._connection = None
        self._name = 'solver'

        #clingo interface
        self._control = clingo.Control()
        #time for timeout
        self._solve_start = time.clock()

        #saves the raw sended data
        self._raw_data = ''
        #array of processed data
        self._data = []
        #this dictonary contains all occurs atoms
        #the key is the time step in which they should be sended to the visualizer
        self._to_send = {}
        #the last sended time step
        self._sended = -1
        self._args = self._parser.parse_args()
        self._port = self._args.port

    def __del__(self):
        self.close()

    #return the solver mode
    def get_mode(self):
        return self._args.mode

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
    #not used yet
    def on_connect(self):
        pass

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
                        self.on_control_symbol(clingo.parse_term(atom))
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
            #resets the solver to receive a new instance and discard old data
            #the visualizer will send this symbol when it is sending a new instance afterwards
            self._to_send = {}
            self._data = []
            self._control = clingo.Control()
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
        #only sends data if it was not send yet
        if step in self._to_send and step > self._sended:
            self._sended = step
            #send the atoms
            for atom in self._to_send[step]:
                self._connection.send((str(atom) + '.').encode())
        #send the '\n' charater to show end of sending
        self._connection.send('\n'.encode())

    #handels the asp atoms
    def on_data(self, data):
        #add atoms to clingo
        for atom in data:
            self._control.add('base', [], atom + '.')
        if not self.solve().satisfiable:
            return
        #send data to the visualizer after solving
        self.send('%$RESET.')
        self.send_step(0)

    #solve the instance
    def solve(self):
        #loads the given encoding and ground
        self._control.load(self._args.encoding)
        self._control.ground([('base', [])])
        solve_future = self._control.solve(on_model = self.on_model, async_ = True)
        self._solve_start = time.clock()
        #check if data was sended to the solver while solving to interrupt solving if needed
        while(True):
            if self.is_ready_to_read():
                solve_future.cancel()
                return solve_future.get()
            finished = solve_future.wait(5.0)
            if finished:
                return solve_future.get()
            #check timeout
            elif self._args.timeout > 0 and (time.clock() - self._solve_start) > self._args.timeout:
                print('solver timeout after ' , time.clock() - self._solve_start, 'secounds')
                return solve_future.get()

    #model callback for self._control.solve in self.solve
    def on_model(self, model):
        print('found solution')
        #add empty entry to dictonary
        self._to_send[0] = []
        #append all occurs atoms to the self._to_send dictonary
        #Note: all atoms are added to the key 0 to send all atoms immeditly after solving
        #this is different in the interactive variant
        for atom in model.symbols(atoms=True):
            if (atom.name == 'occurs' 
                and len(atom.arguments) == 3 
                and atom.arguments[0].name == 'object' 
                and atom.arguments[1].name == 'action'):

                self._to_send[0].append(atom)
        return True

    #solver main function
    def run(self):
        print('Start ' + self._name) 
        self.connect()
        #loop to receive data
        while(True):
            if self.receive(1.0) != 0:
                return

#incremental solver
#overrides only the solve function
class SolverInc(Solver):
    def __init__(self):
        super(SolverInc, self).__init__()

    def solve(self):
        #loads the given encoding
        self._control.load(self._args.encoding)
        result = None
        step = 0

        #solve incremental
        self._solve_start = time.clock()
        while True:
            print('ground: ' + str(step))
            if step == 0:
                self._control.ground([('base', []), ('init', []), 
                                      ('step', [step]),('check', [step])])
            else:
                self._control.ground([('step', [step]),('check', [step])])                
            self._control.assign_external(clingo.Function('query', [step]), True)

            print('solve: ' + str(step))
            solve_future = self._control.solve(on_model = self.on_model, async_ = True)
            #check if data was sended to the solver while solving to interrupt solving if needed
            while(True):
                if self.is_ready_to_read():
                    solve_future.cancel()
                    print('solving interrupted')
                    return solve_future.get()
                finished = solve_future.wait(5.0)
                if finished:
                    result = solve_future.get()
                    print(result)
                    break
                #check timeout
                elif self._args.timeout > 0 and (time.clock() - self._solve_start) > self._args.timeout:
                    print('solver timeout after ' , time.clock() - self._solve_start, 'secounds')
                    return solve_future.get()

            self._control.assign_external(clingo.Function('query', [step]), False)
            step += 1
            if not result.unsatisfiable:
                return result

#interactive solver
#uses solve function from the incremental solver
#but implements own model callback and data callback functions
class SolverInt(SolverInc):
    def __init__(self):
        super(SolverInt, self).__init__()
        #saves initial data
        self._inits = []

    #handels the asp atoms
    def on_data(self, data):
        #add atoms to the inits list
        for atom in data:
            self._inits.append(atom)
        #reset clingo
        self._control = clingo.Control()

        #add inits to clingo
        for atom in self._inits:
            self._control.add('base', [], atom + '.')
        #add finished steps to clingo
        for ii in range(0, self._sended + 1):
            if ii in self._to_send:
                for atom in self._to_send[ii]:
                    self._control.add('base', [], str(atom) + '.')

        if not self.solve().satisfiable:
            return
        #send step to the visualizer after solving
        if self._sended + 1 in self._to_send:
            self.send_step(self._sended + 1)
        elif self._sended + 2 in self._to_send:
            self.send_step(self._sended + 2)

    #model callback for self._control.solve in self.solve
    def on_model(self, model):
        print('found solution')
        #clear self._so_send
        self._to_send = {}
        #append all occurs atoms to the self._to_send dictonary
        #Note: all atoms are added to the step in which their occur
        #so the self._send_step function sends only the atoms for the next step
        for atom in model.symbols(atoms=True):
            if (atom.name == 'occurs' 
                and len(atom.arguments) == 3 
                and atom.arguments[0].name == 'object' 
                and atom.arguments[1].name == 'action'):
                step = atom.arguments[2].number
                #add step to dictonary
                if step not in self._to_send:
                    self._to_send[step] = []
                self._to_send[step].append(atom)
        return True

#main
def main():
    solver = Solver()
    mode = solver.get_mode()
    #choose solver mode
    if mode == 'default':
        pass
    elif mode == 'incremental':
        solver = SolverInc()
    elif mode == 'interactive':
        solver = SolverInt()
    elif mode == 'online':
        solver = SolverInt()
    solver.run()

if __name__ == "__main__":
    main()
