"""
file: files.py
author: Christoffer Rosen <cbr4830@rit.edu>
date: November 2013
description:        Holds the files abstraction class and ORM. Uses SQLAlchemy.
purpose:            To be able to easily see the status of files and provide quick
                    query for fast responses.
"""
from db import *
from datetime import datetime

class Files(Base):
    
    __tablename__ = 'files'
    
    repo = Column(String, primary_key=True)                     # Name of the repo
    name = Column(String, unique=False)                         # Name of the file
    loc = Column(Float, unique=False, default=0)                # LOC in the file
    lastChanged = Column(String, unique=False)                  # Last time file was modified

    
    def __init__(self, repoDict):
        """
        __init__(): Dictonary -> NoneType
        """
        self.id = str(uuid.uuid1())
        self.creation_date = str(datetime.now().replace(microsecond=0))
        self.__dict__.update(repoDict)
    
    def __repr__(self):
        return "<Files table: %s - %s>" % (self.name, self.id)