import argparse
import select
import socket
import clingo

VERSION = '0.1.1'

class Network(object):
    def __init__(self):
        self._parser = argparse.ArgumentParser()
        self.set_argument_parser_arguments(self._parser)
        self._args = self._parser.parse_args()

        self._host = '127.0.0.1'
        self._port = self._args.port
        self._socket = None
        self._connection = None
        self._name = 'server'

        self._reset = False
        self._raw_data = ''
        self._data = []
        self._to_send = {}
        self._sended = -1

    def __del__(self):
        self.close()

    def set_argument_parser_arguments(self, parser):
        parser.add_argument('-p', '--port', help='the port the solver will send the anwsers to',
                            type=int, default = 5000)
        parser.add_argument('-v', '--version',
                            help='show the current version', action='version',
                            version=VERSION)

    def is_ready_to_read(self, time_out = 0.1):
        if self._connection is None: 
            return False
        ready = select.select([self._connection], [], [], time_out)
        if ready[0]:
            return True
        else:
            return False

    def receive(self, time_out):
        if self._connection is None:
            return -1
        try:
            if self.is_ready_to_read(time_out):
                while True:
                    new_data = self._connection.recv(2048)
                    if not new_data or new_data == '':
                        self.close()
                        return 1
                    self._raw_data += new_data
                    if not new_data.find('\n') == -1:
                        self.on_raw_data(self._raw_data)
                        return 0
            else:
                return 0

        except socket.error as error:
            self.close()
            print error
            return -1

    def send(self, data):
        if self._connection is None:
            return
        self._connection.send(data)

    def connect(self):
        try:
            self._socket = socket.socket()
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((self._host, self._port))
            self._socket.listen(1)
            self._connection, addr = self._socket.accept()
            self._control = clingo.Control()
            print 'Connection with: ' + str(addr)
            self.on_connect()
        except socket.error as error:
            self.close()
            print error
            return -1
        return 0

    def close(self):
        if self._connection is not None:
            try:
                self._connection.shutdown(socket.SHUT_RDWR)
            except socket.error:
                pass
            self._connection.close()
            self._connection = None
            print 'close ' + self._name

        if self._socket is not None:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except socket.error:
                pass
            self._socket.close()
            self._socket = None

    def run(self):
        print 'Start ' + self._name 
        self.connect()
        while(True):
            if self.receive(1.0) != 0:
                return

    def on_control_symbol(self, symbol):
        if symbol.name == 'reset':
            self._reset = True
            self._to_send = {}
            self._data = []
        elif symbol.name == 'done' and len(symbol.arguments) == 1:
            try:
                self.send_step(symbol.arguments[0].number + 1)
            except:
                return

    def on_raw_data(self, raw_data):
        data = raw_data.split('.')
        for atom in data:
            if len(atom) > 0:
                if not (len(atom) == 1 and atom[0] == '\n'):
                    if atom[0] == '%' and atom[1] == '$':
                        atom = atom[2 :].lower()
                        self.on_control_symbol(clingo.parse_term(atom))
                    else:
                        self._data.append(atom)
        self._raw_data = ''
        if len(self._data) > 0:
            self.on_data(self._data)
        self._data = []

    def on_data(self, data):
        pass

    def on_connect(self):
        pass

    def send_step(self, step):
        if step in self._to_send and step > self._sended:
            self._sended = step
            for atom in self._to_send[step]:
                self._connection.send(str(atom) + '.')
        self._connection.send('\n')
