import re
import os
import subprocess
from orm.commit import *
from caslogging import logging
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

      if commit.commit_hash in linked_commits:
        commit.contains_bug = True
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

    logging.info("Linkage for commit " + commit.commit_hash)
    for k,v in region_chunks.items():
      logging.info("-- file: " + k)
      logging.info("---- loc modified: " + str(v))

    bug_introducing_changes = self.gitAnnotate(region_chunks, commit)
    return bug_introducing_changes

  def _getModifiedRegionsOnly(self, diff, files_modified):
    """
    returns a dict of file -> list of line numbers modified. helper function for getModifiedRegions
    git diff doesn't provide a clean way of simply getting the specific lines that were modified, so we are doing so here 
    manually using grep. A possible refactor in the future may be to use an external diff tool, so that this implementation 
    wouldn't be scm (git) specific.

    if a file was merely deleted, then there was no chunk or region changed but we do capture the file.
    however, we do not assume this is a location of a bug.

    modified means modified or deleted -- not added! We assume are lines of code modified is the location of a bug.
    """
    region_diff = {}
    file_exts_to_ignore = ["txt", "pdf", "png", "jpg", "md", "html"] # not source code files and these can substentially slow algo

    for file in files_modified:

      # weed out bad files/binary files/etc
      if file != "'" and file != "":
        file_info = file.split(".")

        # get extentions
        if len(file_info) > 1:
          file_ext = (file_info[1]).lower()

          # ensure these are not a readme/txt type file
          if file_ext not in file_exts_to_ignore:
            region_diff[file] = []

    # split all the different regions 
    regions = diff.split("diff --git")[1:] # remove the clutter

    for region in regions:
      chunks = re.split(r'@@ |@@\\n', region)

      # if a binary file it doesn't display the lines modified (a.k.a the '@@' part)
      if len(chunks) == 1:
        continue

      file_info = chunks[0] # file info is the first 'chunk', followed by the sections of code modified

      # start with extracting the file name
      name_start_index = file_info.find("b/")
      file_name = file_info[name_start_index+2:]
      name_end_index = file_name.find("\\n")
      file_name = file_name[:name_end_index]

      # it is possible there is a binary file being tracked or something we shouldn't care about  
      if file_name == None or file_name not in region_diff:
        continue

      # iterate through the following chunks to extract the section of code modified. 
      for chunk in range(1, len(chunks), 2):

        mod_line_info = chunks[chunk].split(" ")[0] # remove clutter
        mod_code_info = chunks[chunk+1].split("\\n")[1:-1] # remove clutter

        # remove comma from mod_line_info as we only care about the start of the modification
        if mod_line_info.find(",") != -1:
          mod_line_info = mod_line_info[0:mod_line_info.find(",")]

        current_line = abs(int(mod_line_info)) # remove the '-' in front of the line number by abs

        # now only use the code line changes that MODIFIES (not adds) in the diff
        for section in mod_code_info:

          # this lines modifies or deletes a line of code
          if section[0] == "-":
            #logging.info("modifying section found : " + str(section))

            # weed out false positives by ignoring new line/ deletion of lines modifications
            if len(section) > 2:
              region_diff[file_name].append(str(current_line))

            # we only increment modified lines of code because we those lines did NOT exist
            # in the previous commit!
            current_line += 1 

          #logging.info("current line: " + str(current_line))

    return region_diff


  def getModifiedRegions(self, commit):
    """
    returns the list of regions that were modified/deleted between this commit and its ancester.
    a region is simply the file and the loc in it that were modified. 

    @commit - change to get the list of regions
    """
    # change directory to repo directory
    os.chdir(self.repo_path)

    # diff cmd w/ no lines of context between current vs parent
    diff_cmd = "git diff " + commit.commit_hash + "^ "+ commit.commit_hash + " --unified=0"
    diff = str(subprocess.check_output(diff_cmd, shell=True))

    # files changed, this is used by the getLineNumbersChanged function
    diff_cmd_lines_changed = "git diff " + commit.commit_hash + "^ "+ commit.commit_hash + " --name-only"

    # get the files modified -> use this to validate if we have arrived at a new file
    # when grepping for the specific lines changed.
    files_modified = str( subprocess.check_output( diff_cmd_lines_changed, shell=True )).replace("b'", "").split("\\n")

    # now, let's get the file and the line number changed in the commit
    return self._getModifiedRegionsOnly(diff, files_modified)


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
          # option gives us the complete commit hash. additionally, start looking at the commit's ancestor 
          buggy_change = str( subprocess.check_output( "git blame -L" + line + ",+1 " + commit.commit_hash + "^ -l -- '" \
                            + file + "'", shell=True )).split(" ")[0][2:]

          if buggy_change not in bug_introducing_changes:
            bug_introducing_changes.append(buggy_change)

    return bug_introducing_changes
