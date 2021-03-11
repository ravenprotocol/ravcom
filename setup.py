from setuptools import setup, find_packages

setup(
    name='ravcom',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        "SQLAlchemy==1.3.23",
        "numpy==1.20.1",
        "redis==3.5.3",
        "mysql-connector-python==8.0.23",
        "mysqlclient==2.0.1",
        "protobuf==3.15.5",
        "six==1.15.0"
    ],
)