"""
file: readRepo.py
authors: Ben Grawi <bjg1568@rit.edu>, Christoffer Rosen <cbr4830@rit.edu>
date: October 2013
description: This module contains the Ingester thread class. Used to create thread workers
             that will ingest a repository from the repository table given a repo id.
"""
from caslogging import logging
import sys
import threading
from datetime import datetime, timedelta
from commit import Commit
from repository import *
from metrics import *
from localrepository import *

class Ingester(threading.Thread):
  """
  Class that represents an ingester worker. Given a repository id, it will
  ingest the repo and put all changes into the changes table.
  """

  def __init__(self, args):
    """
    Constructor.
    @param args - expects a repository id as an argument
    """
    threading.Thread.__init__(self)
    self.session = Session()
    self.args = args

  def run(self):
    """
    Thread run method - ingest the repository id given to the worker
    """
    self.ingest(self.args)

  def ingestRepo(self, repository_to_ingest):
    """
    Ingests the given repository
    @param repository_to_ingest   The repository to inspect
    """
    logging.info( 'A worker is starting scan repository: ' +
                        repository_to_ingest.id )

    # Update status of repo to show it is ingesting
    repository_to_ingest.status = "Ingesting"
    self.session.commit()

    # get update frequency from the config file
    repo_update_freq = int(config['repoUpdates']['freqInDays'])
    refresh_date = str(datetime.utcnow() - timedelta(days=repo_update_freq))

    local_repo = LocalRepository(repository_to_ingest)
    local_repo.sync()
    self.session.merge(repository_to_ingest) 
    repository_to_ingest.status = "Waiting to be Analyzed" # update status
    self.session.commit() 

    logging.info( 'A worker finished ingesting repo ' + 
                    repository_to_ingest.id )

  def ingest(self, args):
    """
    Ingest the repository with the given id. Gets the repository information
    from the repository table and starts ingesting using ingestRepo method
    @param args   The repository id to ingest.
    """

    if len(args) != 2:
      logging.info("No repo id was given!")
    else:

      repo_id_to_analyze = sys.argv[1]
      repo_to_analyze = (self.session.query(Repository)
            .filter (Repository.id == repo_id_to_analyze)
            .all()
            )

      # Verify that repo exists
      if len(repo_to_analyze) == 1:
        self.ingestRepo(repo_to_analyze[0])
      else:
        logging.info('Repo with id ' + repo_id_to_analyze + ' not found!')