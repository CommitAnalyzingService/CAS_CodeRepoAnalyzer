import re
import os
import subprocess
from orm.commit import *
from caslogging import logging
import json
import re

class GitCommitLinker:
  """
  links a corrective change/commit from a git repository
  to a change that introduced the problem or caused the
  corrective commit to be made

  assumes that regions where modified or deleted source code
  in a corrective fix is the location of a bug.

  heavily commented as git diff tool doesn't provide a clean way of seeing
  the specific line of code modified. we are also using the git scm tool to annotate/blame to
  track down the bug-introducing changes
  """

  REPO_DIR = "ingester/CASRepos/git/" # locations where repo directories are stored

  def __init__(self, repoId):
    """
    constructor
    sets the repository path.
    """
    self.repo_path = os.path.join(os.path.dirname(__file__), '..', self.REPO_DIR + repoId)
    self.repo_id = repoId

  def linkCorrectiveCommits(self, corrective_commits, all_commits):
    """
    links all corrective changes/commits to the change that introduced the problem
    note: a bug introducing change may have introduced more than one bug.
    """
    linked_commits = {} # dict of buggy commit hash -> [corrective commits]

    # find all bug introducing commits
    for corrective_commit in corrective_commits:
      buggy_commits = self._linkCorrectiveCommit(corrective_commit)

      for buggy_commit in buggy_commits:
        
        if buggy_commit in linked_commits:
          linked_commits[buggy_commit].append(corrective_commit.commit_hash)
        else:
          linked_commits[buggy_commit] = [corrective_commit.commit_hash]

      corrective_commit.linked = True # mark that we have linked this corrective commit.

    for commit in all_commits:

      if commit.commit_hash in linked_commits:
        commit.contains_bug = True
        commit.fixes = json.dumps(linked_commits[commit.commit_hash])

  def _linkCorrectiveCommit(self, commit):
    """
    links the corrective change/commit to the change/commit which was the
    cause. this is the purpose of this object

    @commit - the corrective change to link w/ the changes that introduces the
    problems/issues it fixes.
    """
    region_chunks = self.getModifiedRegions(commit)

    # logging.info("Linkage for commit " + commit.commit_hash)
    # for k,v in region_chunks.items():
    #   logging.info("-- file: " + k)
    #   logging.info("---- loc modified: " + str(v))

    bug_introducing_changes = self.gitAnnotate(region_chunks, commit)
    return bug_introducing_changes


  def _isCodeFile(self, file_name):
    """ 
    Returns true if file name ending matches that of a code/script file name extentions, 
    such as .py for python. This improves performance of the SZZ algorithm as READMEs 
    and such typically have huge changes to annotate. 

    Also returns false if the file name is /dev/null for obvious reason!
    """
    if file_name == "/dev/null":
      return False

    code_ext_dir = os.path.join(os.path.dirname(__file__), "code_file_extentions.txt")
    code_exts = open(code_ext_dir).read().splitlines()

    file_digestion = file_name.split(".")
    if len(file_digestion) > 1:
      file_extention = (file_digestion[1]).upper()
      if file_extention in code_exts:
        return True

    return False # Not a code or script file to our best knowledge.

  def _getModifiedRegionsOnly(self, diff):
    """
    returns a dict of file -> list of line numbers modified. helper function for getModifiedRegions
    git diff doesn't provide a clean way of simply getting the specific lines that were modified, so we are doing so here 
    manually by using our own bash script. It's output is what is being passed in here. Please see diff-lines.sh if curious

    modified means modified or deleted -- not added! We assume are lines of code modified is the location of a bug.
    """
    region_diff = {}
    modifications = diff.split('\\n')[1:-1]

    for mod in modifications:
      logging.info("MODIFICATION:")
      logging.info(mod)

      region = mod.split(":CASDELIMITER:")

      file_path = region[0]
      line = region[1]
      code = region[2] 

      logging.info("File path: " + str(file_path))
      logging.info("Line: " + str(line))
      logging.info("Code: " + str(code))

      # Ignore files that are just completely deleted as we cannot annotate a file that does not exist 
      # and also those that are file renames (this file won't exist yet)
      if code == " No newline at end of file" or code == "--- /dev/null":
        continue

      # Ignore files that are not code/script files
      if self._isCodeFile(file_path) == False:
        continue

      if file_path in region_diff:
        region_diff[file_path].append(line)
      else:
        region_diff[file_path] = [line]

    logging.info(str(region_diff))

    return region_diff


  def getModifiedRegions(self, commit):
    """
    returns the list of regions that were modified/deleted between this commit and its ancester.
    a region is simply the file and the loc in it that were modified. 

    @commit - change to get the list of regions
    """

    # diff cmd w/ no lines of context between current vs parent
    # we then pass this into a bash script that modifies the output to show
    # only the modified lines of code changes in the following format. {file path}:{line number of code}:{code}
    diff_cmd = "git diff " + commit.commit_hash + "^ "+ commit.commit_hash + " --unified=0 | " \
                + os.path.dirname(os.path.abspath(__file__)) + "/diff-lines.sh"

    diff = str(subprocess.check_output(diff_cmd, shell=True, cwd= self.repo_path ))

    # now, let's get the file and the line number changed in the commit
    return self._getModifiedRegionsOnly(diff)


  def gitAnnotate(self, regions, commit):
    """
    tracks down the origin of the deleted/modified loc in the regions dict using
    the git annotate (now called git blame) feature of git and a list of commit
    hashes of the most recent revision in which the line identified by the regions
    was modified. these discovered commits are identified as bug-introducing changes.

    git blame command is set up to start looking back starting from the commit BEFORE the 
    commit that was passed in. this is because a bug MUST have occured prior to this commit.

    @regions - a dict of {file} -> {list of line numbers that were modified}
    @commit - commit that belongs to the passed in chucks/regions.
    """
    bug_introducing_changes = []

    for file, lines in regions.items():
      for line in lines:

   #     logging.info("I am " + self.repo_id + " and my cwd is: " + self.repo_path ) 

        # assume if region starts at beginning its a deletion or rename and ignore
        if line != 0 and line != "0" :

          # we need to git blame with the --follow option so that it follows renames in the file, and the '-l'
          # option gives us the complete commit hash. additionally, start looking at the commit's ancestor 
          buggy_change = str( subprocess.check_output( "git blame -L" + line + ",+1 " + commit.commit_hash + "^ -l -- '" \
                            + file + "'", shell=True, cwd= self.repo_path )).split(" ")[0][2:]

          if buggy_change not in bug_introducing_changes:
            bug_introducing_changes.append(buggy_change)

    return bug_introducing_changes
