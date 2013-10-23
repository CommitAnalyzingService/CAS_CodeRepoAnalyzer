"""
file: readRepo.py
author: Ben Grawi <bjg1568@rit.edu>
date: October 2013
description: The base script to call
"""
import sys
from datetime import datetime
from commit import Commit
from repository import *
import localrepository


# Read the first argument and pass it in as a string
if len(sys.argv) > 1:
    arg = sys.argv[1]
else:
    arg = ''

if arg == "initDb":
    # Init the database
    Base.metadata.create_all(engine)
if arg == "testRepos":
    # Make Test Repos
    testRepos = [{'name':'Ghost',
                  'url':'https://github.com/TryGhost/Ghost.git',
                  'path':None,
                  'ingestion_date':None,
                  'analysis_date':None
                  },
                 {'name':'Bootstrap',
                  'url':'https://github.com/twbs/bootstrap.git',
                  'path':None,
                  'ingestion_date':None,
                  'analysis_date':None
                  },
                 ]
    session = Session()
    for repo in testRepos:
        session.merge(Repository(repo))
    session.commit()
else:
    session = Session()
    reposToGet = (session.query(Repository)
                  .filter(Repository.ingestion_date==None)
                  .all()
                  )
    #TODO: This: (downloading and parsing commit logs
    """for repo in reposToGet:
       localRepo = LocalRepository(repo)
       repo.download()
       repo.parseLog()
       repo.syncCommits()"""
    
