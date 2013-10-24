"""
file: localrepository.py
author: Ben Grawi <bjg1568@rit.edu>
date: October 2013
description: Holds the repository abstraction class
"""
from git import *
from commit import *
from datetime import datetime
import os
import logging
class LocalRepository():
    """
    Repository():
    description: Abstracts the actions done on a repository
    """
    repo = None
    adapter = None
    def __init__(self, repo):
        """
        __init__(path): String -> NoneType
        description: Abstracts the actions done on a repository
        """
        self.repo = repo
        
        # Temporary until other Repo types are added
        self.adapter = Git
        
        self.commits = {}
    
    def sync(self):
        """
        sync():
        description: Simply wraps the syncing functions together
        """
        
        # TODO: Error checking.
        firstSync = self.syncRepoFiles()
        self.syncCommits(firstSync)

        return self.repo
    
    def syncRepoFiles(self):
        """
        syncRepoFiles() -> Boolean
        description: Downloads the current repo locally, and sets the path and 
            injestion date accordingly
        returns: Boolean - if this is the first sync
        """
        path = os.path.dirname(__file__) + self.adapter.REPO_DIRECTORY + self.repo.id
        self.repo.ingestion_date = str(datetime.now().replace(microsecond=0))
        # See if repo has already been downloaded, if it is pull, if not clone
        if os.path.isdir(path):
            self.adapter.pull(self.adapter, self.repo)
            firstSync = False
        else:
            self.adapter.clone(self.adapter, self.repo)
            firstSync = True
        return firstSync

    def syncCommits(self, firstSync):
        """
        syncCommits():
        description: Makes each commit dictonary into an object and then 
            inserts them into the database
        arguments: firstSync Boolean: whether to sync all commits or after the
            ingestion date
        """
        commits = self.adapter.log(self.adapter, self.repo, firstSync)
        commitsSession = Session()
        logging.info('Saving commits to the database...')
        for commitDict in commits:
            commitDict['repository_id'] = self.repo.id
            commitsSession.merge(Commit(commitDict))
        commitsSession.commit()
        logging.info('Done saving commits to the database.')