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
    ns_sig = Column(Boolean)

    nd = Column(Float, unique=False, default=0)
    nd_sig = Column(Boolean)

    nf = Column(Float, unique=False, default=0)
    nf_sig = Column(Boolean)

    entrophy = Column(Float, unique=False, default=0)
    entrophy_sig = Column(Boolean)

    la = Column(Float, unique=False, default=0)
    la_sig = Column(Boolean)

    ld = Column(Float, unique=False, default=0)
    ld_sig = Column(Boolean)

    lt = Column(Float, unique=False, default=0)
    lt_sig = Column(Boolean)

    ndev = Column(Float, unique=False, default=0)
    ndev_sig = Column(Boolean)

    age = Column(Float, unique=False, default=0)
    age_sig = Column(Boolean)

    nuc = Column(Float, unique=False, default=0)
    nuc_sig = Column(Boolean)
    
    exp = Column(Float, unique=False, default=0)
    exp_sig = Column(Boolean)

    rexp = Column(Float, unique=False, default=0)
    rexp_sig = Column(Boolean)

    sexp = Column(Float, unique=False, default=0)
    sexp_sig = Column(Boolean)

    def __init__(self, glmCoefficientsDict):
        """
        __init__(): Dictonary -> NoneType
        """
        self.__dict__.update(glmCoefficientsDict)

    def __repr__(self):
        return "<Repository id: %s>" % (self.repo)
