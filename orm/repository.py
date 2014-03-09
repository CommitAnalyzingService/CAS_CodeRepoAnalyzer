"""
file: repository.py
author: Ben Grawi <bjg1568@rit.edu>
date: October 2013
description: Holds the repository abstraction class and ORM
"""
import uuid
from db import *
from datetime import datetime

class Repository(Base):
    """
    Commit():
    description: The SQLAlchemy ORM for the repository table
    """
    __tablename__ = 'repositories'

    id = Column(String, primary_key=True)
    name = Column(String)
    url = Column(String)

    creation_date = Column(String)
    ingestion_date = Column(String)
    analysis_date = Column(String)
    status = Column(String)
    email = Column(String)
    listed = Column(Boolean)
    last_data_dump = Column(String)

    def __init__(self, repoDict):
        """
        __init__(): Dictonary -> NoneType
        """
        self.id = str(uuid.uuid1())
        self.creation_date = str(datetime.now().replace(microsecond=0))
        self.__dict__.update(repoDict)

    def __repr__(self):
        return "<Repository: %s - %s>" % (self.name, self.id)
