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

  heavily commented as git diff tool doesn't provide a clean way of seeing
  the specific line of code modified. therefore, we are manually forced to
  grep for this information and therefore this may be hard to understand/follow
  without many comments. we are also using the git scm tool to annotate/blame to
  track down the bug-introducing chages; therefore, it's not just python code being
  executed.

  this class assumes that GNU grep is installed on the machine running this code.
  """

  REPO_DIR = "ingester/CASRepos/git/" # locations where repo directories are stored

  def __init__(self, repoId):
    """
    constructor
    sets the repository path.
    """
    self.repo_path = os.path.join(os.path.dirname(__file__), '..', self.REPO_DIR + repoId)

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

    # mark & link the buggy commits
    logging.info("#### marking and linking the buggy commits ####")

    for commit in all_commits:
      logging.info(commit.commit_hash)

      if commit.commit_hash in linked_commits:
        logging.info("marking..")
        commit.contains_bug = True
        logging.info("fixes = " + str(linked_commits[commit.commit_hash]))
        commit.fixes = str(linked_commits[commit.commit_hash])


  def _linkCorrectiveCommit(self, commit):
    """
    links the corrective change/commit to the change/commit which was the
    cause. this is the purpose of this object

    @commit - the corrective change to link w/ the changes that introduces the
    problems/issues it fixes.
    """
    logging.info(" #### Linking commit " + commit.commit_hash + " ####")

    region_chunks = self.getModifiedRegions(commit)

    logging.info("Linkage: ")
    for k,v in region_chunks.items():
      logging.info("-- file: " + k)
      logging.info("---- regions: " + str(v))

    bug_introducing_changes = self.gitAnnotate(region_chunks, commit)
    return bug_introducing_changes

  def _getModifiedRegions(self, diff_cmd, files_modified):
    """
    returns a dict of file -> list of line numbers modified. helper function for getModifiedRegions
    heavily commented as it may seem a bit janky. git diff doesn't provide a clean way of simply
    getting the specific lines that were modified, so we are doing so here manually using grep. A possible
    refactor in the future may be to use an external diff tool, so that this implementation wouldn't be scm
    specific.

    if a file was merely deleted, then there was no chunk or region changed but we do capture the file.
    however, we do not assume this is a location of a bug.
    """
    logging.info("Getting modified regions..")
    region_diff = {}

    # initialize the dictionary with the files -> lists
    for file in files_modified:

      if file != "'" and file != "":
        region_diff[file] = []

    # grep for the file and line number changed by looking for the '@@' and also
    # grepping the line above it, which if this is a new file will show us this.
    # we see that its so by checking if it matches one of the files modified, which is passed
    # in to the function.
    grep_cmd = "grep '@@' -B 1"

    # this is just dividing each region up in a very unfiltered manner
    # example on how a region may look: "b'+++ b/{filename}\\n@@ {lines_modified_info} @@ {class}"
    modified_regions = str( subprocess.check_output( diff_cmd + " | " + grep_cmd, shell=True ) ).split("--")

    # keep track of the last modified file, as if there are multiple regions modified within a file
    # it will not list the same file again in the line before the modified liens of code.
    last_modified_file = None

    for region in modified_regions:

      # splits the information into three chuncks: line before the grep that may contain
      # the file information, the place containing the lines of code modified, and the third
      # chunck we don't care for.
      region_info = region.split("@@")

      # if we arrived at a new file, we will see it here; otherwise, it will just contain
      # un-interesting information grepped before the lines modified information.
      possible_file_info = region_info[0]
      lines_modified_info = region_info[1]

      # logging.info("lines modified info: " + lines_modified_info)

      # check to see if this is a file name -> if so, replace the last_modified_file
      start_index = possible_file_info.find("b/")

      if start_index != -1:
        possible_file_info = possible_file_info[start_index+2:] # move passed b/

        # remove newline at end if existent
        end_index = possible_file_info.find("\\n")
        if end_index != -1:
          possible_file_info = possible_file_info[:end_index]

        #logging.info("verifying that possible file: " + possible_file_info + " is acceptable.")

        # verify that this is indeed a valid file and not just something random grepped.
        if possible_file_info in region_diff:
        #  logging.info("verified")
          last_modified_file = possible_file_info # set it as the last modified file.

      # it is possible there is a binary file being tracked.
      if last_modified_file != None:
        # logging.info("last modified file: " + last_modified_file)
        # logging.info(str(lines_modified_info.split(" ")))

        # get the starting line of code that was modified
        line_introduction = lines_modified_info.split(" ")[1][1:] # also remove the '-' in front of line #

        # also remove the comma; we only use the start of the modification/deletion.
        if (line_introduction.find(",") != -1):
          line_introduction = line_introduction[0:line_introduction.find(",")]

        region_diff[last_modified_file].append(line_introduction)

    return region_diff

  def getModifiedRegions(self, commit):
    """
    returns the list of regions that were modified/deleted between this commit and its ancester.
    ex: [10,25]; this shows that regions starting at lines 10 and 25 were modified/deleted.

    @commit - change to get the list of regions
    """
    # change directory to repo directory
    os.chdir(self.repo_path)

    # diff cmd w/ no lines of context between current vs parent
    diff_cmd = "git diff " + commit.commit_hash + "^ "+ commit.commit_hash + " --unified=0"

    # files changed, this is used by the getLineNumbersChanged function
    diff_cmd_lines_changed = "git diff " + commit.commit_hash + "^ "+ commit.commit_hash + " --name-only"

    # get the files modified -> use this to validate if we have arrived at a new file
    # when grepping for the specific lines changed.
    files_modified = str( subprocess.check_output( diff_cmd_lines_changed, shell=True )).replace("b'", "").split("\\n")

    # now, let's get the file and the line number changed in the commit
    return self._getModifiedRegions(diff_cmd, files_modified)


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

        # assume if region starts at beginning its a deletion or rename and ignore
        if line != 0 and line != "0" :

          # we need to git blame with the --follow option so that it follows renames in the file, and the '-l'
          # option gives us the complete commit hash. additionally, start looking at the commit's direct ancestor.
          buggy_change = str( subprocess.check_output( "git blame -L" + line + ",+1 " + commit.commit_hash + "^ -l -- " \
                            + file, shell=True )).split(" ")[0][2:]

          if buggy_change not in bug_introducing_changes:
            logging.info("blamming " + buggy_change + " for line "+ str(line) + " in file " + file + " in commit " + commit.commit_hash)
            bug_introducing_changes.append(buggy_change)

    return bug_introducing_changes
