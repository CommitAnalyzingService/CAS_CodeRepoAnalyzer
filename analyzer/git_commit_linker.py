import re
import os
import subprocess
from orm.commit import *
from caslogging import logging

class GitCommitLinker:
  """
  links a corrective change/commit from a git repository
  to a change that introduced the problem or caused the
  corrective commit to be made

  assumes that regions where modified or deleted source code
  in a corrective fix is the location of a bug.
  """

  REPO_DIR = "/CASRepos/git/" # locations where repo directories are stored

  os.chdir(os.path.dirname(__file__) + self.REPO_DIRECTORY + repo.id)

  def __init__(self, repoId):
    """
    constructor
    """
    self.repo_path = os.path.dirname(__file__) + "/CASReos/git/" + repo.id

  def linkCorrectiveCommit(self, commit):
    """
    links the corrective change/commit to the change/commit which was the
    cause

    @commit - the corrective change to link w/ the changes that introduces the
    problems/issues it fixes.
    """

    # change directory to repo directory
    os.chdir(self.repo_path)

    # diff cmd
    diff_cmd = "git diff " + commit.commit_hash + " ^" + commit.commit_hash

    # get the diff
    diff_output = str( subprocess.check_output(diff_cmd, shell=True ) )


  def getListOfRegions(self, commit):
    """
    returns the list of regions that were modified/deleted between this commit and its ancester.
    ex: [10,25]; this shows that regions starting at lines 10 and 25 were modified/deleted.

    @commit - change to get the list of regions
    """
    pass

  def getBlame(self, listOfRegions, commit):
    """
    returns the commit ids that most recently modified the regions in the
    list of regions for the passed in commit.

    @listOfRegions - a list containing the starting line numbers of each hunk of source code
    that differed in a diff between commit and its ancester
    @commit - the corrective commit
    """
    pass
