"""
file: db.py
author: Ben Grawi <bjg1568@rit.edu>
date: October 2013
description: Holds the db connection info
"""
from config import config
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()
engine = sqlalchemy.create_engine(config['db']['type'] + '+' +
                                  config['db']['adapter'] + '://' + 
                                  config['db']['username'] + ':' +
                                  config['db']['password'] + '@' +
                                  config['db']['host'] + ':' +
                                  config['db']['port'] + '/' +
                                  config['db']['database'])
Session.configure(bind=engine)
Base = declarative_base()