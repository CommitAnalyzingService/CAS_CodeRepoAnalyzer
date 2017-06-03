"""
file: db.py
author: Ben Grawi <bjg1568@rit.edu>
date: October 2013
description: Holds the db connection info
"""
from config import *
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
                                  config['db']['database'], pool_size=100, max_overflow=0) # the value of pool_size has to be less than the max_connections to postgres.
Session.configure(bind=engine)
Base = declarative_base()