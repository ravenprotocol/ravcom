import socketio


class RavOPNamespace(socketio.ClientNamespace):
    def on_connect(self):
        # print('Connected to the server')
        pass

    def on_disconnect(self):
        # print('Disconnected from the server')
        pass

    def on_message(self, data):
        # print('Message received:', data)
        pass

    def on_result(self, data):
        print(data)


class SocketClient(object):
    def __init__(self, server_url):
        self.client = None
        self.url = server_url

    def connect(self):
        self.client = socketio.Client()
        self.client.register_namespace(RavOPNamespace('/ravop'))
        self.client.connect(self.url+"?client_name=ravop")
        return self.client

    def disconnect(self):
        self.client.disconnect()
