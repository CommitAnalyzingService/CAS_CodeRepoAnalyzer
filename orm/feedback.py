"""
file: feedback.py
description: Holds the feedback abstraction class and ORM
"""
import uuid
from db import *
from datetime import datetime

class Feedback(Base):
    """
    Commit():
    description: The SQLAlchemy ORM for the feedback table
    """
    __tablename__ = 'feedback'

    id = Column(String, primary_key=True)
    commit_hash = Column(String)
    score = Column(Integer)
    comment = Column(String)

    def __init__(self, feedbackDict):
        """
        __init__(): Dictonary -> NoneType
        """
        self.__dict__.update(feedbackDict)

    def __repr__(self):
        return "<Feedback id: %s>" % (self.id)
