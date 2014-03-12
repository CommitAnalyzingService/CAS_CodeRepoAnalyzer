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
    intercept_sig = Column(Float)

    ns = Column(Float, unique=False, default=0)
    ns_sig = Column(Float)

    nd = Column(Float, unique=False, default=0)
    nd_sig = Column(Float)

    nf = Column(Float, unique=False, default=0)
    nf_sig = Column(Float)

    entrophy = Column(Float, unique=False, default=0)
    entrophy_sig = Column(Float)

    la = Column(Float, unique=False, default=0)
    la_sig = Column(Float)

    ld = Column(Float, unique=False, default=0)
    ld_sig = Column(Float)

    lt = Column(Float, unique=False, default=0)
    lt_sig = Column(Float)

    ndev = Column(Float, unique=False, default=0)
    ndev_sig = Column(Float)

    age = Column(Float, unique=False, default=0)
    age_sig = Column(Float)

    nuc = Column(Float, unique=False, default=0)
    nuc_sig = Column(Float)

    exp = Column(Float, unique=False, default=0)
    exp_sig = Column(Float)

    rexp = Column(Float, unique=False, default=0)
    rexp_sig = Column(Float)

    sexp = Column(Float, unique=False, default=0)
    sexp_sig = Column(Float)

    def __init__(self, glmCoefficientsDict):
        """
        __init__(): Dictonary -> NoneType
        """
        self.__dict__.update(glmCoefficientsDict)

    def __repr__(self):
        return "<Repository id: %s>" % (self.repo)
