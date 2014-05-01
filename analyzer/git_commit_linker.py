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
    manually. A possible refactor in the future may be to use an external diff tool, so that this implementation 
    wouldn't be scm (git) specific.

    if a file was merely deleted, then there was no chunk or region changed but we do capture the file.
    however, we do not assume this is a location of a bug.

    modified means modified or deleted -- not added! We assume are lines of code modified is the location of a bug.
    """
    region_diff = {}

    # only link code source files as any type of README, etc typically have HUGE changes and reduces 
    # the performance to unacceptable levels. it's very hard to blacklist everything; much easier just to whitelist
    # code source files endings.
    list_ext_dir = os.path.join(os.path.dirname(__file__), "code_file_extentions.txt")
    file_exts_to_include = open(list_ext_dir).read().splitlines()

    for file in files_modified:

      # weed out bad files/binary files/etc
      if file != "'" and file != "":
        file_info = file.split(".")

        # get extentions
        if len(file_info) > 1:
          file_ext = (file_info[1]).lower()

          # ensure these source code file endings
          if file_ext.upper() in file_exts_to_include:
            region_diff[file] = []

    # split all the different regions 
    regions = diff.split("diff --git")[1:] # remove the clutter

    print("\n Regions: ")
    print(str(regions))

    # Next, we study each region to get file that was modified & the lines modified so we can annotate them later
    for region in regions:

      print("\n Region: ")
      print(region)


      # We begin by splitting on the beginning of double at characters, which gives us an array looking like this:
      # [file info, line info {double at characters} modified code]
      chunks_initial = region.split(":CAS_DELIMITER_START:@@")

      # if a binary file it doesn't display the lines modified (a.k.a the 'line info {double at characters} modified code' part)
      if len(chunks_initial) == 1:
        continue

      file_info = chunks_initial[0] # file info is the first 'chunk', followed by the line_info {double at characters} modified code
      file_info_split = file_info.split(" ")
      file_name = file_info_split[1][2:] # remove the 'a/ character'

      print(file_name)

      # it is possible there is a binary file being tracked or something we shouldn't care about  
      if file_name == None or file_name not in region_diff:
        continue

      # Next, we must know the lines modified so that we can annotate. To do this, we must further split the chunks_initial.
      # Specifically, we must seperate the line info from the code info. The second part of the initial chunk looks like
      # -101,30, +202,33 {double at characters} code modified info. We can be pretty certain that the line info doesnt contain
      # any at characters, so we can safely split the first set of doule at characters seen to divide this info up.

      # Iterate through - as in one file we can multiple sections modified.  
      for chunk in range(1, len(chunks_initial), 1):

        code_info_chunk = chunks_initial[chunk].split("@@",1) # split only on the first occurance of the double at characters

        print("\n Code Chunk")
        print(str(code_info_chunk))

        line_info = code_info_chunk[0] # This now contains the -101,30 +102,30 part (info about the lines modified)
        code_info = code_info_chunk[1] # This now contains the modified lines of code seperated by the delimiter we set

        # As we only care about modified lines of code, we must ignore the +/additions as they do exist in previous versions
        # and thus, we cannot even annotate them (they were added in this commit). So, we only care about the start where it was 
        # modified and we will have to study which lines where modified and keep track of them.

        mod_line_info = line_info.split(" ")[1] # remove clutter -> we only care about what line the modificatin started, first index is just empty
        mod_code_info = code_info.replace("\\n","").split(":CAS_DELIMITER:")[1:-1] # remove clutter -> first line contains info on the class and last line irrelevant

        # make sure this is legitimate. expect modified line info to start with '-'
        if mod_line_info[0] != '-':
          continue

        # remove comma from mod_line_info as we only care about the start of the modification
        if mod_line_info.find(",") != -1:
          mod_line_info = mod_line_info[0:mod_line_info.find(",")]

        current_line = abs(int(mod_line_info)) # remove the '-' in front of the line number by abs

        # now only use the code line changes that MODIFIES (not adds) in the diff
        for section in mod_code_info:

          # this lines modifies or deletes a line of code
          if section.startswith(":CAS_DELIMITER_START:-"):
            region_diff[file_name].append(str(current_line))

            # we only increment modified lines of code because we those lines did NOT exist
            # in the previous commit!
            current_line += 1 

    return region_diff


  def getModifiedRegions(self, commit):
    """
    returns the list of regions that were modified/deleted between this commit and its ancester.
    a region is simply the file and the loc in it that were modified. 

    @commit - change to get the list of regions
    """

    # diff cmd w/ no lines of context between current vs parent. 
    # pipe it into bash and echo back with our own delimiter instead of new lines to seperate each line 
    # of the git output to make parsing this a reality!
    diff_cmd = "git diff " + commit.commit_hash + "^ "+ commit.commit_hash + " --unified=0 " \
      + ' | while read; do echo ":CAS_DELIMITER_START:$REPLY:CAS_DELIMITER:"; done'

    diff = str(subprocess.check_output(diff_cmd, shell=True, cwd= self.repo_path, executable="/bin/bash" ))

    # files changed, this is used by the getLineNumbersChanged function
    diff_cmd_lines_changed = "git diff " + commit.commit_hash + "^ "+ commit.commit_hash + " --name-only"

    # get the files modified -> use this to validate if we have arrived at a new file
    # when grepping for the specific lines changed.
    files_modified = str( subprocess.check_output( diff_cmd_lines_changed, shell=True, cwd= self.repo_path )).replace("b'", "").split("\\n")

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
                            + file + "'", shell=True, cwd= self.repo_path )).split(" ")[0][2:]

          if buggy_change not in bug_introducing_changes:
            bug_introducing_changes.append(buggy_change)

    return bug_introducing_changes
