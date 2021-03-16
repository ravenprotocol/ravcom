import json
import os

import numpy as np

from ravcom.socket_client import SocketClient
from .config import DATA_FILES_PATH, RAVSOCK_SERVER_URL


def save_data_to_file(data_id, data):
    """
    Method to save data in a pickle file
    """
    file_path = os.path.join(DATA_FILES_PATH, "data_{}.json".format(data_id))

    if os.path.exists(file_path):
        os.remove(file_path)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        if isinstance(data, np.ndarray):
            data = data.tolist()
        json.dump(data, f)

    return file_path


def load_data_from_file():
    pass


def delete_data_file(data_id):
    file_path = os.path.join(DATA_FILES_PATH, "data_{}.json".format(data_id))
    if os.path.exists(file_path):
        os.remove(file_path)


class Singleton:
    def __init__(self, cls):
        self._cls = cls

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)


def dump_data(data_id, value):
    """
    Dump ndarray to file
    """
    file_path = os.path.join(DATA_FILES_PATH, "data_{}.pkl".format(data_id))
    if os.path.exists(file_path):
        os.remove(file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    value.dump(file_path)
    return file_path


def inform_server():
    socket_client = SocketClient(server_url=RAVSOCK_SERVER_URL).connect()
    socket_client.emit("inform_server", data={"type": "event"}, namespace="/ravop")
