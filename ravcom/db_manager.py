import datetime
import json
from enum import Enum

import numpy as np
import sqlalchemy as db
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database as cd, drop_database as dba

from . import config
from .utils import delete_data_file, save_data_to_file, Singleton

Base = declarative_base()


class OpStatus(Enum):
    PENDING = "pending"
    COMPUTING = "computing"
    COMPUTED = "computed"
    FAILED = "failed"


class GraphStatus(Enum):
    PENDING = "pending"
    COMPUTING = "computing"
    COMPUTED = "computed"
    FAILED = "failed"


class ClientOpMappingStatus(Enum):
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    NOT_ACKNOWLEDGED = "not_acknowledged"
    COMPUTING = "computing"
    COMPUTED = "computed"
    NOT_COMPUTED = "not_computed"
    FAILED = "failed"
    REJECTED = "rejected"


class Graph(Base):
    __tablename__ = 'graph'
    id = Column(Integer, primary_key=True)
    ops = relationship("Op", backref="graph")

    # Status of this graph 1. pending 2. computing 3. computed 4. failed
    status = Column(String(10), default="pending")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True)
    type = Column(String(20), nullable=False)
    file_path = Column(String(200), nullable=True)
    value = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Client(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True)
    client_id = Column(String(100), nullable=False)
    client_ip = Column(String(20), nullable=True)
    status = Column(String(20), nullable=False, default="disconnected")
    # 1. ravop 2. ravjs
    type = Column(String(10), nullable=True)
    client_ops = relationship("ClientOpMapping", backref="client", lazy="dynamic")

    connected_at = Column(DateTime, default=datetime.datetime.utcnow)
    disconnected_at = Column(DateTime, default=datetime.datetime.utcnow)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Op(Base):
    __tablename__ = 'op'
    id = Column(Integer, primary_key=True)

    # Op name
    name = Column(String(20), nullable=True)

    # Graph id
    graph_id = Column(Integer, ForeignKey('graph.id'))

    # 1. input 2. output 3. middle
    node_type = Column(String(10), nullable=False)

    # Store list of op ids
    inputs = Column(Text, nullable=True)

    # Store filenames - Pickle files
    outputs = Column(String(100), nullable=True)

    # Op type for no change in values
    op_type = Column(String(50), nullable=False)
    operator = Column(String(50), nullable=False)

    # 1. pending 2. computing 3. computed 4. failed
    status = Column(String(10), default="pending")
    message = Column(Text, nullable=True)

    # Dict of params
    params = Column(Text, nullable=True)

    op_mappings = relationship("ClientOpMapping", backref="op", lazy="dynamic")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ClientOpMapping(Base):
    __tablename__ = "client_op_mapping"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client.id'))
    op_id = Column(Integer, ForeignKey('op.id'))
    sent_time = Column(DateTime, default=None)
    response_time = Column(DateTime, default=None)

    # 1. computing 2. computed 3. failed
    status = Column(String(10), default="computing")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


@Singleton
class DBManager(object):
    def __init__(self):
        self.create_database()
        self.engine, self.session = self.connect()

    def connect(self):
        engine = db.create_engine(config.RDF_DATABASE_URI, isolation_level="READ UNCOMMITTED")
        connection = engine.connect()
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        return engine, session

    def create_database(self):
        if not database_exists(config.RDF_DATABASE_URI):
            cd(config.RDF_DATABASE_URI)
            print("Database created")

    def drop_database(self):
        if database_exists(config.RDF_DATABASE_URI):
            dba(config.RDF_DATABASE_URI)
            print("Database dropped")

    def create_session(self):
        """
        Create a new session
        """
        DBSession = sessionmaker(bind=self.engine)
        return DBSession()

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def refresh(self, obj):
        """
        Refresh an object
        """
        self.session.refresh(obj)
        return obj

    def get(self, name, id):
        if name == "op":
            obj = self.session.query(Op).get(id)
        elif name == "data":
            obj = self.session.query(Data).get(id)
        elif name == "graph":
            obj = self.session.query(Graph).get(id)
        elif name == "client":
            obj = self.session.query(Client).get(id)
        else:
            obj = None

        return obj

    def add(self, name, **kwargs):
        if name == "op":
            obj = Op()
        elif name == "data":
            obj = Data()
        elif name == "graph":
            obj = Graph()
        elif name == "client":
            obj = Client()
        else:
            obj = None

        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.session.add(obj)
        self.session.commit()

        return obj

    def update(self, name, id, **kwargs):
        if name == "op":
            obj = self.session.query(Op).get(id)
        elif name == "data":
            obj = self.session.query(Data).get(id)
        elif name == "graph":
            obj = self.session.query(Graph).get(id)
        elif name == "client":
            obj = self.session.query(Client).get(id)
        else:
            obj = None

        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.session.commit()
        return obj

    def delete(self, obj):
        self.session.delete(obj)
        self.session.commit()

    def create_op(self, **kwargs):
        op = Op()

        for key, value in kwargs.items():
            setattr(op, key, value)

        self.session.add(op)
        self.session.commit()
        return op

    def get_op(self, op_id):
        """
        Get an existing op
        """
        return self.session.query(Op).get(op_id)

    def update_op(self, op, **kwargs):
        for key, value in kwargs.items():
            setattr(op, key, value)

        self.session.commit()
        return op

    def create_data(self, **kwargs):
        data = Data()

        for key, value in kwargs.items():
            setattr(data, key, value)

        self.session.add(data)
        self.session.commit()
        return data

    def get_data(self, data_id):
        """
        Get an existing data
        """
        return self.session.query(Data).get(data_id)

    def update_data(self, data, **kwargs):
        for key, value in kwargs.items():
            setattr(data, key, value)

        self.session.commit()
        return data

    def delete_data(self, data_id):
        data = self.session.query(Data).get(data_id)
        self.session.delete(data)
        self.session.commit()

    def create_data_complete(self, data, data_type):
        # print("Creating data:", data)

        if isinstance(data, (np.ndarray, np.generic)):
            if data.ndim == 1:
                data = data[..., np.newaxis]

        d = self.create_data(type=data_type)

        # Save file
        file_path = save_data_to_file(d.id, data, data_type)

        # Update file path
        self.update(d, file_path=file_path)

        return d

    def get_op_status(self, op_id):
        status = self.session.query(Op).get(op_id).status
        return status

    def get_graph(self, graph_id):
        """
        Get an existing graph
        """
        return self.session.query(Graph).get(graph_id)

    def create_graph(self):
        """
        Create a new graph
        """
        graph = Graph()
        self.session.add(graph)
        self.session.commit()
        return graph

    def get_graph_ops(self, graph_id):
        return self.session.query(Op).filter(Op.graph_id == graph_id).all()

    def delete_graph_ops(self, graph_id):
        print("Deleting graph ops")
        ops = self.get_graph_ops(graph_id=graph_id)

        for op in ops:
            print("Op id:{}".format(op.id))
            data_ids = json.loads(op.outputs)
            if data_ids is not None:
                for data_id in data_ids:
                    print("Data id:{}".format(data_id))

                    # Delete data file
                    delete_data_file(data_id)

                    # Delete data object
                    self.delete_data(data_id)

            # Delete op object
            self.delete(op)

    def create_client(self, **kwargs):
        obj = Client()

        for key, value in kwargs.items():
            setattr(obj, key, value)

        self.session.add(obj)
        self.session.commit()
        return obj

    def get_client(self, client_id):
        """
        Get an existing client
        """
        return self.session.query(Client).get(client_id)

    def get_client_by_sid(self, sid):
        """
        Get an existing client by sid
        """
        return self.session.query(Client).filter(Client.client_id == sid).first()

    def update_client(self, client, **kwargs):
        for key, value in kwargs.items():
            setattr(client, key, value)
        self.session.commit()
        return client

    def get_all_clients(self):
        return self.session.query(Client).order_by(Client.created_at.desc()).all()

    def get_all_graphs(self):
        return self.session.query(Graph).order_by(Graph.created_at.desc()).all()

    def get_all_ops(self):
        return self.session.query(Op).order_by(Op.id.desc()).all()

    # def deactivate_all_graphs(self):
    #     for graph in self.session.query(Graph).all():
    #         graph.status = "inactive"
    #
    #     self.session.commit()
    #
    # def deactivate_graph(self, graph_id):
    #     graph = self.get_graph(graph_id=graph_id)
    #     graph.status = "inactive"
    #     self.session.commit()

    def disconnect_all_clients(self):
        for cliet in self.session.query(Client).all():
            cliet.status = "disconnected"

        self.session.commit()

    def disconnect_client(self, client_id):
        client = self.get_client(client_id=client_id)
        client.status = "disconnected"
        self.session.commit()

    def get_ops_by_name(self, op_name, graph_id=None):
        if graph_id is not None:
            ops = self.session.query(Op).filter(Op.graph_id == graph_id).filter(Op.name.contains(op_name)).all()
        else:
            ops = self.session.query(Op).filter(Op.name.contains(op_name)).all()

        return ops

    def get_op_readiness(self, op):
        """
        Get op readiness
        """
        inputs = json.loads(op.inputs)
        params = json.loads(op.params)

        cs = 0
        for input_op in inputs:
            input_op1 = self.get_op(op_id=input_op)
            if input_op1.status in ["pending", "computing"]:
                return "parent_op_not_ready"
            elif input_op1.status == "failed":
                return "parent_op_failed"
            elif input_op1.status == "computed":
                cs += 1

        for index, value in params.items():
            if type(value).__name__ == "int":
                cop = self.get_op(op_id=value)
                if cop.status in ["pending", "computing"]:
                    return "parent_op_not_ready"
                elif cop.status == "failed":
                    return "parent_op_failed"
                elif cop.status == "computed":
                    cs += 1
            else:
                cs += 1

        if cs == len(inputs) + len(params.keys()):
            return "ready"
        else:
            return "not_ready"

    def get_ops_without_graph(self, status=None):
        """
        Get a list of all ops not associated to any graph
        """
        if status is not None:
            return self.session.query(Op).filter(Op.graph_id is None).filter(Op.status == status).all()
        else:
            return self.session.query(Op).filter(Op.graph_id is None).all()

    def get_graphs(self, status=None):
        """
        Get a list of graphs
        """
        if status is not None:
            return self.session.query(Graph).filter(Graph.status == status).all()
        else:
            self.session.query(Graph).all()

    def get_clients(self, status=None):
        """
        Get a list of clients
        """
        if status is not None:
            return self.session.query(Client).filter(Client.status == status).all()
        else:
            return self.session.query(Client).all()

    def get_available_clients(self):
        """
        Get all clients which are available
        """
        clients = self.session.query(Client).filter(Client.status == "connected").all()

        client_list = []
        for client in clients:
            client_ops = client.client_ops.filter(or_(ClientOpMapping.status == ClientOpMappingStatus.SENT,
                                                      ClientOpMapping.status == ClientOpMappingStatus.ACKNOWLEDGED.value,
                                                      ClientOpMapping.status == ClientOpMappingStatus.COMPUTING.value))
            if client_ops.count() == 0:
                client_list.append(client)

        return client_list

    def get_ops(self, graph_id=None, status=None):
        """
        Get a list of ops based on certain parameters
        """
        if graph_id is None and status is None:
            return self.session.query(Op).all()
        elif graph_id is not None and status is not None:
            return self.session.query(Op).filter(Op.graph_id == graph_id).filter(Op.status == status).all()
        else:
            if graph_id is not None:
                return self.session.query(Op).filter(Op.graph_id == graph_id).all()
            elif status is not None:
                return self.session.query(Op).filter(Op.status == status).all()
            else:
                return self.session.query(Op).all()

    def create_client_op_mapping(self, **kwargs):
        mapping = ClientOpMapping()

        for key, value in kwargs.items():
            setattr(mapping, key, value)

        self.session.add(mapping)
        self.session.commit()
        return mapping

    def update_client_op_mapping(self, client_op_mapping_id, **kwargs):
        mapping = self.session.query(ClientOpMapping).get(client_op_mapping_id)
        for key, value in kwargs.items():
            setattr(mapping, key, value)
        self.session.commit()
        return mapping

    def find_client_op_mapping(self, client_id, op_id):
        mapping = self.session.query(ClientOpMapping).filter(ClientOpMapping.client_id == client_id,
                                                             ClientOpMapping.op_id == op_id).first()
        return mapping

    def get_incomplete_op(self):
        ops = self.session.query(Op).filter(Op.status == OpStatus.COMPUTING.value).all()

        for op in ops:
            op_mappings = op.op_mappings
            if op_mappings.filter(ClientOpMapping.status == ClientOpMappingStatus.SENT.value).count() >= 3 or \
                    op_mappings.filter(ClientOpMapping.status == ClientOpMappingStatus.COMPUTING.value).count() >= 2 \
                    or op_mappings.filter(ClientOpMapping.status == ClientOpMappingStatus.REJECTED.value).count() >= 5 \
                    or op_mappings.filter(ClientOpMapping.status == ClientOpMappingStatus.FAILED.value).count() >= 3:
                continue

            return op
        return None

    def get_op_status_final(self, op_id):
        op = self.get_op(op_id=op_id)
        op_mappings = op.op_mappings
        if op_mappings.filter(ClientOpMapping.status == ClientOpMappingStatus.FAILED.value).count() >= 3:
            return "failed"

        return "computing"

    def get_first_graph_op(self, graph_id):
        """
        Return the first graph op
        """
        ops = self.get_graph_ops(graph_id=graph_id)
        return ops[0]

    def get_last_graph_op(self, graph_id):
        """
        Return the last graph op
        """
        ops = self.get_graph_ops(graph_id=graph_id)
        return ops[-1]
