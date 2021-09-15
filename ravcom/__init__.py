import glob
import os

from .config import QUEUE_LOW_PRIORITY, QUEUE_HIGH_PRIORITY, QUEUE_COMPUTING, RDF_REDIS_DB, RDF_REDIS_HOST, \
    RDF_REDIS_PORT, DATA_FILES_PATH
from .db_manager import OpStatus, GraphStatus, ClientOpMappingStatus, Op, Graph, Data, Client, \
    ClientOpMapping, DBManager
from .redis_manager import RavQueue, clear_redis_queues
from .utils import dump_data, delete_data_file, save_data_to_file, inform_server, Singleton, copy_data

ravdb = DBManager.Instance()


def reset_database():
    ravdb.drop_database()
    ravdb.create_database()
    ravdb.create_tables()


def reset():
    for file_path in glob.glob("files/*"):
        if os.path.exists(file_path):
            os.remove(file_path)

    if not os.path.exists("files"):
        os.makedirs("files")

    # Delete and create database
    reset_database()

    # Clear redis queues
    clear_redis_queues()


@Singleton
class Globals(object):
    def __init__(self):
        self._default_graph_id = None

    @property
    def graph_id(self):
        return self._default_graph_id

    @property
    def ravop_log_file(self):
        return self._ravop_log_file

    @graph_id.setter
    def graph_id(self, id):
        self._default_graph_id = id

    @graph_id.deleter
    def graph_id(self):
        del self._default_graph_id


globals = Globals.Instance()
