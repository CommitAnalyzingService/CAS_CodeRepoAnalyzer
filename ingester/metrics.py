"""
file: metrics.py
author: Christoffer Rosen <cbr4830@rit.edu>
date: November 2013
description: Holds the metrics abstraction class and ORM
"""
from db import *
from datetime import datetime

class Metrics(Base):
    """
    Metrics():
    description: The SQLAlchemy ORM for the repository table
    """
    __tablename__ = 'metrics'
    
    repo = Column(String, primary_key=True)
    
    nsbuggy = Column(Float, unique=False, default=0)
    nsnonbuggy = Column(Float, unique=False, default=0)
    ndbuggy = Column(Float, unique=False, default=0)
    ndnonbuggy = Column(Float, unique=False, default=0)
    nfbuggy = Column(Float, unique=False, default=0)
    nfnonbuggy = Column(Float, unique=False, default=0)
    entrophybuggy = Column(Float, unique=False, default=0)
    entrophynonbuggy = Column(Float, unique=False, default=0)
    labuggy = Column(Float, unique=False, default=0)
    lanonbuggy = Column(Float, unique=False, default=0)
    ldbuggy = Column(Float, unique=False, default=0)
    ldnonbuggy = Column(Float, unique=False, default=0)
    ltbuggy = Column(Float, unique=False, default=0)
    ltnonbuggy = Column(Float, unique=False, default=0)
    ndevbuggy = Column(Float, unique=False, default=0)
    ndevnonbuggy = Column(Float, unique=False, default=0)
    agebuggy = Column(Float, unique=False, default=0)
    agenonbuggy = Column(Float, unique=False, default=0)
    nucbuggy = Column(Float, unique=False, default=0)
    nucnonbuggy = Column(Float, unique=False, default=0)
    expbuggy = Column(Float, unique=False, default=0)
    expnonbuggy = Column(Float, unique=False, default=0)
    rexpnonbuggy = Column(Float, unique=False, default=0)
    rexpbuggy = Column(Float, unique=False, default=0)
    sexpbuggy = Column(Float, unique=False, default=0)
    sexpnonbuggy = Column(Float, unique=False, default=0)
    
    def __init__(self, repoDict):
        """
        __init__(): Dictonary -> NoneType
        """
        self.id = str(uuid.uuid1())
        self.creation_date = str(datetime.now().replace(microsecond=0))
        self.__dict__.update(repoDict)
    
    def __repr__(self):
        return "<Metrics table: %s - %s>" % (self.name, self.id)