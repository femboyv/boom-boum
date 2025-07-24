import socket
import threading
import json
import pygame


class server_class:
    def __init__(self):
        self.address = socket.gethostbyname(socket.gethostname())  # it's the host
        self.port = 5000  # could be changed

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.address, self.port))
        self.socket.listen(1)  # 1 is the number of people to listen
        print("listening on", self.port, ",", self.address)

    def loop_to_accept(self):
        (client_socket, client_address) = self.socket.accept()
        print(
            "connected to", client_address[1]
        )  # [1] to only get the ip, idk what's the second number
        self.create_client(client_socket, client_address)

    def create_client(self, client_socket: socket.socket, client_address):
        thread_of_discussion = threading.Thread(
            target=client_class,
            args=(
                client_socket,
                client_address,
            ),  # should be a tuple 'cause it only accepts iterable not tuple
        )
        thread_of_discussion.start()  # not run


all_client_connected = {}


class client_class:

    def __init__(self, client_socket: socket.socket, client_address: str):
        self.socket = client_socket
        self.is_client_connected_to_server = True
        self.address = client_address
        print(self.address, "connected to server")

        message = self.receive_from_client()  # first message to initialize everything
        self.load_message(message)

        self.id = self.info["id"]
        all_client_connected[self.id] = self

        while self.is_client_connected_to_server:  # constant loop
            self.step()

    def __str__(self):
        return json.dumps(self.info)

    def __repr__(self):
        return self.__str__()

    def receive_from_client(self, intro_length: int = 4):
        """the intro length is the number of number that is received at start of message to give the length of the message \n
        it should be the same in the server and in the client"""
        length_of_message = self.socket.recv(intro_length)
        length_of_message = length_of_message.decode("utf-8")

        if length_of_message == "":  # 'cause it's disconnected if it receive that
            return None

        length_of_message = int(length_of_message)

        output = self.socket.recv(length_of_message)

        output = output.decode("utf-8")

        return output

    def load_message(self, message: str):

        dict_message = json.loads(message)
        dict_message: dict

        match dict_message["type"]:  # to add more type (shoot bullet etc)
            case "player info":
                self.info = dict_message
        return self.info

    def get_0_before_int(self, number: int | str, length_expected: int) -> str:
        """get 0 before the int so it correspond to a certain length (eg: input 1,4 it will output 0001)"""
        if isinstance(number, int):
            number = str(number)

        number_length = len(number)
        if number_length > length_expected:
            raise ValueError(
                "Number length is greater to expected length, increment expected length or lower number"
            )
        for _ in range(length_expected - number_length):
            number = "0" + number

        return number

    def send_to_client(self, info: str, intro_length: int = 4):
        """the intro length is the number of number that is sent at start of message to give the length of the message \n
        it should be the same in the server and in the client"""

        output_to_send = self.get_0_before_int(info.__len__(), intro_length) + info

        self.socket.send(output_to_send.encode("utf-8"))

    def step(self):
        print(all_client_connected)

        message = self.receive_from_client()

        self.load_message(message)

        if message == None:
            self.disconnect()

        message_to_send = all_client_connected.copy()

        self.send_to_client(str(message_to_send))

    def disconnect(self):
        print(self.address, "disconnected :<")
        self.socket.shutdown(1)
        self.socket.close()

        self.is_client_connected_to_server = False
        all_client_connected.remove(self)


server = server_class()

while True:
    server.loop_to_accept()
