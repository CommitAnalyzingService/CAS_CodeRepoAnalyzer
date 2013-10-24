"""
file: readRepo.py
author: Ben Grawi <bjg1568@rit.edu>
date: October 2013
description: The base script to call
"""
from caslogging import logging
import sys
from datetime import datetime, timedelta
from commit import Commit
from repository import *
from localrepository import *


logging.info('Starting CASReader')

# Read the first argument and pass it in as a string
if len(sys.argv) > 1:
    arg = sys.argv[1]
else:
    arg = ''

if arg == "initDb":
    # Init the database
    logging.info('Initializing the Database...')
    Base.metadata.create_all(engine)
    logging.info('Done')
elif arg == "testRepos":
    
    logging.info('Making Test Repos')
    
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
    logging.info('Done.')
elif arg == '':
    # No args, just do scan
    logging.info('Starting Scan...')
    repoSession = Session()
    
    # Latest time to get new repo data (1 day ago)
    refresh_date = str(datetime.utcnow() - timedelta(days=1))
    
    # Get un-injested repos or repos not been updated since the refresh_date
    reposToGet = (repoSession.query(Repository)
                  .filter( (Repository.ingestion_date==None) |
                          (Repository.ingestion_date < refresh_date)
                          )
                  .all()
                  )
    #TODO: This: (downloading and parsing commit logs
    if len(reposToGet) > 0:
        for repo in reposToGet:
           localRepo = LocalRepository(repo)
           localRepo.sync()
           repoSession.merge(repo)
        repoSession.commit()
        logging.info('Done, finished everything.')
    else:
        logging.info('Nothing to do. Done.')
else:
    logging.error('Invalid Command')
