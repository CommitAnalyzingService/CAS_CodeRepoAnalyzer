"""
file: commit.py
author: Ben Grawi <bjg1568@rit.edu>, Christoffer Rosen <cbr4830@rit.edu>
date: Novemeber 2013
description: Holds the commit abstraction class and ORM
"""
from db import *
#from sqlalchemy import *

class Commit(Base):
    """
    Commit():
    description: The SQLAlchemy ORM for the commits table
    """
    __tablename__ = 'commits'

    commit_hash = Column(String, primary_key=True)
    author_name  = Column(String)
    author_date_unix_timestamp  = Column(String)
    author_email  = Column(String)
    author_date  = Column(String)
    commit_message = Column(String)

    fix = Column(String, unique=False)
    classification = Column(String, unique=False)
    linked = Column(Boolean, default = False)

    contains_bug = Column(Boolean, unique=False, default=False)
    fixes = Column(String, unique=False)
    ns = Column(Float, unique=False, default=0)
    nd = Column(Float, unique=False, default=0)
    nf = Column(Float, unique=False, default=0)
    entrophy = Column(Float, unique=False, default=0)
    la = Column(Float, unique=False, default=0)
    ld = Column(Float, unique=False, default=0)
    fileschanged = Column(String, unique=False, default="NULL")
    lt = Column(Float, unique=False, default=0)
    ndev = Column(Float, unique=False, default=0)
    age = Column(Float, unique=False, default=0)
    nuc = Column(Float, unique=False, default=0)
    exp = Column(Float, unique=False, default=0)
    rexp = Column(Float, unique=False, default=0)
    sexp = Column(Float, unique=False, default=0)

    # The linear regression probability of commit containing bug
    glm_probability = Column(Float, unique=False, default=0)

    # Many-to-One Relation to repositories table
    repository_id = Column(String)

    def __init__(self, commitDict):
        """
        __init__(): Dictonary -> NoneType
        """
        self.__dict__.update(commitDict)

    def __repr__(self):
        return "<Commit('%s','%s', '%s', '%s')>" % \
            (self.commit_hash,
            self.author_name,
            self.author_date,
            self.commit_message)
