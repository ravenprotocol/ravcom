import contextlib
import glob
import os

import sqlalchemy

from .config import QUEUE_LOW_PRIORITY, QUEUE_HIGH_PRIORITY, QUEUE_COMPUTING, RDF_MYSQL_HOST, RDF_MYSQL_DATABASE, \
    RDF_MYSQL_PASSWORD, RDF_MYSQL_USER, RDF_MYSQL_PORT, RDF_REDIS_DB, RDF_REDIS_HOST, RDF_REDIS_PORT
from .db_manager import OpStatus, GraphStatus, ClientOpMappingStatus, Op, Graph, Data, Client, \
    ClientOpMapping, DBManager
from .redis_manager import RavQueue, clear_redis_queues
from .utils import dump_data, delete_data_file, save_data_to_file, inform_server


def delete_create_database():
    with sqlalchemy.create_engine('mysql://{}:{}@{}:{}/{}'.format(RDF_MYSQL_USER, RDF_MYSQL_PASSWORD,
                                                                  RDF_MYSQL_HOST, RDF_MYSQL_PORT, "mysql"),
                                  isolation_level='AUTOCOMMIT').connect() as connection:
        with contextlib.suppress(sqlalchemy.exc.ProgrammingError):
            connection.execute("DROP DATABASE {}".format(RDF_MYSQL_DATABASE))
            print("Database deleted")
            connection.execute("CREATE DATABASE {}".format(RDF_MYSQL_DATABASE))
            print("Database created")


def reset():
    for file_path in glob.glob("files/*"):
        if os.path.exists(file_path):
            os.remove(file_path)

    if not os.path.exists("files"):
        os.makedirs("files")

    # Delete and create database
    delete_create_database()

    # Clear redis queues
    clear_redis_queues()


ravcom = DBManager.Instance()
