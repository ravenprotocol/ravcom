import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_FILES_PATH = os.path.join(BASE_DIR, "files")

RDF_REDIS_HOST = os.environ.get("RDF_REDIS_HOST", "localhost")
RDF_REDIS_PORT = os.environ.get("RDF_REDIS_PORT", "6379")
RDF_REDIS_DB = os.environ.get("RDF_REDIS_DB", "0")

RDF_MYSQL_HOST = os.environ.get("RDF_MYSQL_HOST", "localhost")
RDF_MYSQL_PORT = os.environ.get("RDF_MYSQL_PORT", "3306")
RDF_MYSQL_USER = os.environ.get("RDF_MYSQL_USER", "root")
RDF_MYSQL_PASSWORD = os.environ.get("RDF_MYSQL_PASSWORD", "password")
RDF_MYSQL_DATABASE = os.environ.get("RDF_MYSQL_PASSWORD", "rdf")

QUEUE_HIGH_PRIORITY = "queue:high_priority"
QUEUE_LOW_PRIORITY = "queue:low_priority"
QUEUE_COMPUTING = "queue:computing"
