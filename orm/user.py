"""
file: user.py
description: Holds the user abstraction class and ORM
"""
import uuid
from db import *
from datetime import datetime

class User(Base):
    """
    User():
    description: The SQLAlchemy ORM for the user table
    """
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    email = Column(String)
    password = Column(String)

    def __init__(self, userDict):
        """
        __init__(): Dictonary -> NoneType
        """
        self.__dict__.update(userDict)

    def __repr__(self):
        return "<User id: %s>" % (self.id)
