from setuptools import setup, find_packages

setup(
    name='ravcom',
    version='0.1-alpha',
    packages=find_packages(),
    install_requires=[
        "SQLAlchemy==1.3.23",
        "numpy==1.20.1",
        "redis==3.5.3",
        "protobuf==3.15.5",
        "six==1.15.0",
        "aiohttp==3.6.2",
        "async-timeout==3.0.1",
        "python-engineio==3.13.0",
        "python-socketio==4.5.1",
        "requests==2.23.0",
        "sqlalchemy-utils==0.37.2"
    ],
)
