"""
file: commit.py
author: Ben Grawi <bjg1568@rit.edu>
date: October 2013
description: Holds the commit abstraction class and ORM
"""
from db import *

class Commit(Base):
    """
    Commit():
    description: The SQLAlchemy ORM for the commits table
    """
    __tablename__ = 'commits'
    
    commit_hash = Column(String, primary_key=True)
    tree_hash_abbreviated = Column(String)
    parent_hashes_abbreviated = Column(String)
    author_date_iso_8601  = Column(String)
    committer_date_relative  = Column(String)
    committer_email  = Column(String)
    author_name  = Column(String)
    parent_hashes = Column(String)
    commit_hash_abbreviated = Column(String)
    tree_hash = Column(String)
    author_date_unix_timestamp  = Column(String)
    author_date_relative  = Column(String)
    author_date_rfc2822_style  = Column(String)
    committer_date  = Column(String)
    author_email  = Column(String)
    author_date  = Column(String)
    subject = Column(String)
    committer_name  = Column(String)
    
    # Many-to-One Relation to repositories table
    repository_id = Column(String)
    
    def __init__(self, commitDict):
        """
        __init__(): Dictonary -> NoneType
        """
        self.__dict__.update(commitDict)
            
    def __repr__(self):
        return "<Commit('%s','%s', '%s', '%s')>" % \
            (self.commit_hash_abbreviated,
            self.author_name, 
            self.author_date, 
            self.subject)