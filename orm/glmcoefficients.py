"""
file: glmcoefficients.py
description: Holds the glm coefficients abstraction class and ORM
"""
import uuid
from db import *
from datetime import datetime

class GlmCoefficients(Base):

    __tablename__ = 'glm_coefficients'

    repo = Column(String, primary_key=True)

    intercept = Column(Float, unique=False, default=0)
    ns = Column(Float, unique=False, default=0)
    nd = Column(Float, unique=False, default=0)
    nf = Column(Float, unique=False, default=0)
    entrophy = Column(Float, unique=False, default=0)
    la = Column(Float, unique=False, default=0)
    ld = Column(Float, unique=False, default=0)
    lt = Column(Float, unique=False, default=0)
    ndev = Column(Float, unique=False, default=0)
    age = Column(Float, unique=False, default=0)
    nuc = Column(Float, unique=False, default=0)
    exp = Column(Float, unique=False, default=0)
    rexp = Column(Float, unique=False, default=0)
    sexp = Column(Float, unique=False, default=0)

    def __init__(self, glmCoefficientsDict):
        """
        __init__(): Dictonary -> NoneType
        """
        self.__dict__.update(glmCoefficientsDict)

    def __repr__(self):
        return "<Repository id: %s>" % (self.repo)
