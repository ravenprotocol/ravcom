import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_FILES_PATH = os.path.join(BASE_DIR, "files")

RDF_REDIS_HOST = os.environ.get("RDF_REDIS_HOST", "localhost")
RDF_REDIS_PORT = os.environ.get("RDF_REDIS_PORT", "6379")
RDF_REDIS_DB = os.environ.get("RDF_REDIS_DB", "0")

QUEUE_HIGH_PRIORITY = "queue:high_priority"
QUEUE_LOW_PRIORITY = "queue:low_priority"
QUEUE_COMPUTING = "queue:computing"

RAVSOCK_SERVER_URL = os.environ.get("RAVSOCK_SERVER_URL", "http://0.0.0.0:9999")

RDF_DATABASE_URI = os.environ.get("RDF_DATABASE_URI", None)
