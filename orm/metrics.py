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
    ns_sig = Column(Float)

    ndbuggy = Column(Float, unique=False, default=0)
    ndnonbuggy = Column(Float, unique=False, default=0)
    nd_sig = Column(Float)

    nfbuggy = Column(Float, unique=False, default=0)
    nfnonbuggy = Column(Float, unique=False, default=0)
    nf_sig = Column(Float)

    entrophybuggy = Column(Float, unique=False, default=0)
    entrophynonbuggy = Column(Float, unique=False, default=0)
    entrophy_sig = Column(Float)

    labuggy = Column(Float, unique=False, default=0)
    lanonbuggy = Column(Float, unique=False, default=0)
    la_sig = Column(Float)

    ldbuggy = Column(Float, unique=False, default=0)
    ldnonbuggy = Column(Float, unique=False, default=0)
    ld_sig = Column(Float)

    ltbuggy = Column(Float, unique=False, default=0)
    ltnonbuggy = Column(Float, unique=False, default=0)
    lt_sig = Column(Float)

    ndevbuggy = Column(Float, unique=False, default=0)
    ndevnonbuggy = Column(Float, unique=False, default=0)
    ndev_sig = Column(Float)

    agebuggy = Column(Float, unique=False, default=0)
    agenonbuggy = Column(Float, unique=False, default=0)
    age_sig = Column(Float)

    nucbuggy = Column(Float, unique=False, default=0)
    nucnonbuggy = Column(Float, unique=False, default=0)
    nuc_sig = Column(Float)

    expbuggy = Column(Float, unique=False, default=0)
    expnonbuggy = Column(Float, unique=False, default=0)
    exp_sig = Column(Float)

    rexpnonbuggy = Column(Float, unique=False, default=0)
    rexpbuggy = Column(Float, unique=False, default=0)
    rexp_sig = Column(Float)

    sexpbuggy = Column(Float, unique=False, default=0)
    sexpnonbuggy = Column(Float, unique=False, default=0)
    sexp_sig = Column(Float)

    def __init__(self, metricDict):
        """
        __init__(): Dictonary -> NoneType
        """
        self.__dict__.update(metricDict)

    def __repr__(self):
        return "<Metrics table: %s>" % (self.repo)
