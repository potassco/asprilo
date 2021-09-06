from threading import Thread
import socket
import select
import time
import os
import argparse
from PyQt5.QtCore import *

from clingo.symbol import parse_term

class VisualizerSocket(object):
    def __init__(self, default_host = '127.0.0.1', default_port = 5000, socket_name = 'socket'):
        self._host = default_host          
        self._port = default_port
        self._s = None
        self._timer = None
        self._socket_name = socket_name
        self._thread = None
        self._parser = None
        self._waiting = False

    def __del__(self):
        self.close()

    def set_parser(self, parser):
        self._parser = parser

    def run_script(self, command, port = None):
        self.close()
        self._thread = Thread(target = lambda: os.system(command))
        self._thread.start()
        if port is not None:
            self.connect('127.0.0.1', port)

    def join(self, wait_time):
        if self._thread is not None:
            self._thread.join(wait_time)
            self._thread = None

    def run_connection(self):
        if self._s is None:
            return
        if self._timer is not None:
            self._timer.stop()
        self._timer = QTimer()
        self._timer.timeout.connect(self.receive)
        self._timer.start(1000)

    def connect(self, host = None, port = None):
        if self.is_connected() and host == self._host and port == self._port:
            return 0
        if host is not None:
            self._host = host
        if port is not None:
            self._port = port
        self.close()
        print('Try connection with '+ self._socket_name)
        self._s = socket.socket()
        connected = False
        tryCount = 0

        while not connected:            #try to connect to the server
            try:
                self._s.connect((self._host, self._port))
                connected = True
            except(socket.error):
                if tryCount >= 5: 
                    print('Failed to connect with ' + self._socket_name)
                    self.close()
                    return -1 
                print('Failed to connect with ' + self._socket_name + ' \nRetrying in 2 sek')
                time.sleep(2)
            tryCount += 1
        print('Connect with '+ self._socket_name)
        return 0

    def send(self, msg):
        if self._s is None or msg is None:
            return
        if msg == '':
            return
        self._s.send(msg.encode('utf-8'))
        pass

    def done_step(self, step):
        if self._s is None:
            return
        self._waiting = True
        self._s.send(('%$done(' + str(step) + ').\n').encode('utf-8'))

    def model_expanded(self, msg):
        pass

    def _receive_data(self):
        breakLoop = False                                  
        data = ''
        try:
            ready = select.select([self._s], [], [], 0.1)
            while (not breakLoop) and ready[0]:
                new_data = self._s.recv(2048).decode()
                if not new_data.find('\n') == -1 or new_data == '':
                    breakLoop = True
                data += new_data
            if ready[0] and new_data == '':
                self.close()
                return None
        except socket.error as err:
            print(err)
        return data

    def receive(self):
        return

    def run(self):
        return

    def close(self):
        if self._timer is not None:
            self._timer.stop()
        if self._s is not None: 
            print('Close connection to ' + self._socket_name)
            try:
                self._s.shutdown(socket.SHUT_RDWR)
            except socket.error:
                pass
            self._s.close()
            self._s = None
            self.join(10)

    def is_connected(self):
        return self._s is not None

    def script_is_running(self):
        return self._thread is not None

    def is_waiting(self):
        return self._waiting

    def get_host(self):
        return self._host

    def get_port(self):
        return self._port

class SolverSocket(VisualizerSocket):

    def __init__(self):
        super(self.__class__, self).__init__('127.0.0.1', 5000, 'solver')
        self._model = None

    def set_model(self, model):
        self._model = model
        if model is not None:
            self._model.add_socket(self)

    def model_expanded(self, msg):
        self.send(msg)
        self._waiting = True

    def receive(self):
        if self._s is None or self._parser is None or self._model is None:
            return -1

        data = self._receive_data()
        if data is None:
            return
        if data == '':
            return
        self._waiting = False
        for str_atom in data.split('.'):
            if len(str_atom) != 0 and not (len(str_atom) == 1 and str_atom[0] == '\n'):
                if str_atom == '%$RESET':
                    self._parser.clear_model_actions(True)
                else:
                    self._parser.on_atom(parse_term(str_atom))
        self._model.update_windows()

    def solve(self):
        if self._s == None or self._model == None: return -1
        self._s.send('%$RESET.'.encode('utf-8'))
        self._model.set_editable(False)
        self._model.restart()
        for atom in self._model.to_init_str():        #send instance
            atom = atom.replace('\n', '')
            self._s.send(str(atom).encode('utf-8'))
        self._s.send('\n'.encode('utf-8'))
        self.run_connection()

    def run(self):
        self.solve()

class SimulatorSocket(VisualizerSocket):

    def __init__(self):
        super(self.__class__, self).__init__('127.0.0.1', 5001, 'simulator')

    def receive(self):
        if self._s is None or self._parser is None:
            return -1

        data = self._receive_data()
        empty = True
        reset = False
        if data is None:
            return
        if data == '':
            return
        self._waiting = False
        for str_atom in data.split('.'):
            if len(str_atom) != 0 and not (len(str_atom) == 1 and str_atom[0] == '\n'):
                if str_atom == '%$RESET':
                    self._parser.clear_model()
                    reset = True
                    empty = False
                else:
                    self._parser.on_atom(parse_term(str_atom))
                    empty = False
        if not empty:
            self._parser.done_instance(reset)

    def connect(self, host = None, port = None):
        VisualizerSocket.connect(self, host, port)
        self.run()

    def run(self):
        self.run_connection()
