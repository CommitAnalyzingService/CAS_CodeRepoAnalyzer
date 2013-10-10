"""
file: db.py
author: Ben Grawi <bjg1568@rit.edu>
date: October 2013
description: Holds the db connection info
"""
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()
engine = sqlalchemy.create_engine('postgresql+pypostgresql://cas_user:REDACTED@localhost:5432/cas')
Session.configure(bind=engine)
Base = declarative_base()