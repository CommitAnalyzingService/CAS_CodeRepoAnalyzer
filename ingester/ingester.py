"""
file: readRepo.py
authors: Ben Grawi <bjg1568@rit.edu>, Christoffer Rosen <cbr4830@rit.edu>
date: October 2013
description: This module contains the functions for ingesting a repository with
             a given id. 
"""
from caslogging import logging
import sys
from datetime import datetime, timedelta
from orm.commit import *
from orm.repository import *
from orm.metrics import *
from ingester.localrepository import *

def ingestRepo(repository_to_ingest, session):
  """
  Ingests a given repository
  @param repository_to_ingest   The repository to inspect
  @param session 				The SQLAlchemy session
  @private
  """
  logging.info( 'A worker is starting scan repository: ' +
                      repository_to_ingest.id )

  # Update status of repo to show it is ingesting
  repository_to_ingest.status = "Ingesting"
  session.commit()

  local_repo = LocalRepository(repository_to_ingest)
  local_repo.sync()
  session.merge(repository_to_ingest) 
  repository_to_ingest.status = "Waiting to be Analyzed" # update status
  session.commit() 

  logging.info( 'A worker finished ingesting repo ' + 
                  repository_to_ingest.id )

  session.close()

def ingest(repo_id):
  """
  Ingest a repository with the given id. Gets the repository information
  from the repository table and starts ingesting using ingestRepo method
  @param repo_id   The repository id to ingest.
  """
  session = Session()
  repo_to_analyze = (session.query(Repository)
        .filter (Repository.id == repo_id)
        .all()
        )

  # Verify that repo exists
  if len(repo_to_analyze) == 1:
  	ingestRepo(repo_to_analyze[0], session)
  else:
    logging.info('Repo with id ' + repo_id_to_analyze + ' not found!')

  session.close()