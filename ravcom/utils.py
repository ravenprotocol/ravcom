import contextlib
import glob
import os
import json
import numpy as np
import sqlalchemy

from .config import DATA_FILES_PATH, RDF_MYSQL_USER, RDF_MYSQL_DATABASE, RDF_MYSQL_PASSWORD, \
    RDF_MYSQL_PORT, RDF_MYSQL_HOST


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


def reset():
    for file_path in glob.glob("files/*"):
        if os.path.exists(file_path):
            os.remove(file_path)

    if not os.path.exists("files"):
        os.makedirs("files")


def delete_create_database():
    with sqlalchemy.create_engine('mysql://{}:{}@{}:{}/{}'.format(RDF_MYSQL_USER, RDF_MYSQL_PASSWORD,
                                                                  RDF_MYSQL_HOST, RDF_MYSQL_PORT, "mysql"),
                                  isolation_level='AUTOCOMMIT').connect() as connection:
        with contextlib.suppress(sqlalchemy.exc.ProgrammingError):
            connection.execute("DROP DATABASE {}".format(RDF_MYSQL_DATABASE))
            print("Database deleted")
            connection.execute("CREATE DATABASE {}".format(RDF_MYSQL_DATABASE))
            print("Database created")


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
