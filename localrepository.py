"""
file: localrepository.py
author: Ben Grawi <bjg1568@rit.edu>
date: October 2013
description: Holds the repository abstraction class
"""
from git import *
from commit import *
class LocalRepository(Git):
    """
    Repository(Git):
    description: Abstracts the actions done on a repository
    """
    DOWNLOAD_LOCATION = "./CASRepos/"
    repo = None
    commits = {}
    
    def __init__(self, repo):
        """
        __init__(path): String -> NoneType
        description: Abstracts the actions done on a repository
        """
        self.repo = repo
        self.commits = {}
    def download(self):
        git.clone(self.url)
    def parseLog(self):
        """
        parseLog(): NoneType -> List
        description: Calls the Git log command for the repository
        """
        self.commits = Git.log(self)
        return self.commits
    def syncCommits(self):
        """
        syncCommits(): NoneType -> Boolean
        description: Makes each commit dictonary into an object and then 
                    inserts them into the database
        """
        session = Session()
        for commitDict in self.commits:
            session.merge(Commit(commitDict))
        return session.commit()