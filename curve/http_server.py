import socket
import threading
import inspect
import sys
import re


# Escuchar peticiones de clients
def http_listening(app, client_connection, client_address):
    try:
        request = client_connection.recv(1024).decode('utf-8')
        app.set_request(request)
        for x in app.responses:
            client_connection.send(x)
        client_connection.close()
    except:
        client_connection.close()


# Iniciar servidor
class init_server:
    def __init__(self, app, module, port = 80, address = '127.0.0.1', **kwargs):
        self.app = app
        self.module = kwargs.get('module')
        self.port = kwargs.get('port')
        self.address = kwargs.get('address')

        for name, action in inspect.getmembers(sys.modules[module]):
            if re.compile("^route_([a-zA-Z0-9\_])*$").match(name):
                action()

        http_socket = socket.socket()
        http_socket.bind((address, port))
        print(f'Server running on {address}:{port}')
        http_socket.listen(5)

        # Threading para clients
        while True:
            client_connection, client_address = http_socket.accept()
            threading.Thread(target = http_listening, args = (app, client_connection, client_address)).start()
