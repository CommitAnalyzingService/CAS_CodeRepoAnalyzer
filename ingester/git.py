import os
import subprocess
import json
import logging
import math                              # Required for the math.log function
from ingester.commitFile import *                 # Represents a file
import time

"""
file: repository.py
authors: Ben Grawi <bjg1568@rit.edu>, Christoffer Rosen <cbr4830@rit.edu>
date: October 2013
description: Holds the repository git abstraction class
"""

class Git():
    """
    Git():
    pre-conditions: git is in the current PATH
                    self.path is set in a parent class
    description: a very basic abstraction for using git in python.
    """
    # Two backslashes to allow one backslash to be passed in the command.
    # This is given as a command line option to git for formatting output.

    # A commit mesasge in git is done such that first line is treated as the subject,
    # and the rest is treated as the message. We combine them under field commit_message

    # We want the log in ascending order, so we call --reverse
    # Numstat is used to get statistics for each commit
    LOG_FORMAT = '--pretty=format:\" CAS_READER_STARTPRETTY\
    \\"commit_hash\\"CAS_READER_PROP_DELIMITER: \\"%H\\",CAS_READER_PROP_DELIMITER2\
    \\"author_name\\"CAS_READER_PROP_DELIMITER: \\"%an\\",CAS_READER_PROP_DELIMITER2\
    \\"author_email\\"CAS_READER_PROP_DELIMITER: \\"%ae\\",CAS_READER_PROP_DELIMITER2\
    \\"author_date\\"CAS_READER_PROP_DELIMITER: \\"%ad\\",CAS_READER_PROP_DELIMITER2\
    \\"author_date_unix_timestamp\\"CAS_READER_PROP_DELIMITER: \\"%at\\",CAS_READER_PROP_DELIMITER2\
    \\"commit_message\\"CAS_READER_PROP_DELIMITER: \\"%s%b\\"\
    CAS_READER_STOPPRETTY \" --numstat --reverse '
    
    CLONE_CMD = 'git clone -q --mirror {!s} {!s}'     # git clone command w/o downloading src code
    FETCH_CMD = 'git fetch -q origin master:master'         # git fetch command 
    REPO_DIRECTORY = "/CASRepos/git/"            # directory in which to store repositories

    correctiveWords = ['fix','bug']   #TODO: we should read this from a flat file to allow easy modification
    
    def getCommitStatsProperties( stats, commitFiles, devExperience, author, unixTimeStamp ):
        """ 
        getCommitStatsProperties
        Helper method for log. Caclulates statistics for each change/commit and
        returns them as a comma seperated string. Log will add these to the commit object
        properties

        @param stats            These are the stats given by --numstat as an array
        @param commitFiles      These are all tracked commit files 
        @param devExperience    These are all tracked developer experiences
        @param author           The author of the commit
        @param unixTimeStamp    Time of the commit
        """

        statProperties = ""

        # Data structures to keep track of info needed for stats
        subsystemsSeen = []                         # List of system names seen
        directoriesSeen = []                        # List of directory names seen
        locModifiedPerFile = []                     # List of modified loc in each file seen 
        authors = []                                # List of all unique authors seen for each file
        fileAges = []                               # List of the ages for each file in a commit

        # Stats variables 
        la = 0                                      # lines added
        ld = 0                                      # lines deleted
        nf = 0                                      # Number of modified files
        ns = 0                                      # Number of modified subsystems
        nd = 0                                      # number of modified directories
        entrophy = 0                                # entrophy: distriubtion of modified code across each file
        lt = 0                                      # lines of code in each file (sum) before the commit
        ndev = 0                                    # the number of developers that modifed the files in a commit
        age = 0                                     # the average time interval between the last and current change
        nuc = 0                                     # the number of unique changes to the modified files
        exp = 0                                     # number of changes made by author previously
        rexp = 0                                    # experience weighted by age of files ( 1 / (n + 1))
        sexp = 0                                    # changes made previous by author in same subsystem
        totalLOCModified = 0                        # Total modified LOC across all files
        filesSeen = ""                              # files seen in change/commit

        for stat in stats:

            if( stat == ' ' or stat == '' ):
                continue

            fileStat = stat.split("\\t")

             # Check that we are only looking at file stat (i.e., remove extra newlines)
            if( len(fileStat) < 2):
                continue

            # catch the git "-" line changes
            try:
                fileLa = int(fileStat[0])                
                fileLd = int(fileStat[1])
            except:
                fileLa = 0
                fileLd = 0

            # Remove oddities in filename so we can process it
            fileName = (fileStat[2].replace("'",'').replace('"','').replace("\\",""))

            totalModified = fileLa + fileLd

            if(fileName in commitFiles):
                prevFileChanged = commitFiles[fileName]
                prevLOC = getattr(prevFileChanged, 'loc')
                prevAuthors = getattr(prevFileChanged, 'authors')
                prevChanged = getattr(prevFileChanged, 'lastchanged')
                lt += prevLOC

                for prevAuthor in prevAuthors:
                    if prevAuthor not in authors:
                        authors.append(prevAuthor)

                if prevChanged not in fileAges:
                    nuc += 1

                # Convert age to days instead of seconds
                age += ( (int(unixTimeStamp) - int(prevChanged)) / 86400 )    
                fileAges.append(prevChanged)

                # Update the file info
                setattr(prevFileChanged, 'loc', prevLOC + fileLa - fileLd) 
                setattr(prevFileChanged, 'authors', authors)
                setattr(prevFileChanged, 'lastchanged', unixTimeStamp)

            else: 

                if(author not in authors):
                    authors.append(author)

                if(unixTimeStamp not in fileAges):
                    fileAges.append(unixTimeStamp)

                fileObject = CommitFile(fileName, fileLa - fileLd, authors, unixTimeStamp)
                commitFiles[fileName] = fileObject

            locModifiedPerFile.append(totalModified) # Required for entrphy
            totalLOCModified += totalModified
            fileDirs = fileName.split("/")

            if( len(fileDirs) == 1 ):
                subsystem = "root"
                directory = "root"
            else:
                subsystem = fileDirs[0]
                directory = "/".join(fileDirs[0:-1])

            if( subsystem not in subsystemsSeen ):
                subsystemsSeen.append( subsystem )

            if( author in devExperience ):
                experiences = devExperience[author]
                exp += sum(experiences.values())

                if( subsystem in experiences ):
                    sexp = experiences[subsystem]
                    experiences[subsystem] += 1
                else:
                    experiences[subsystem] = 1

                try:
                    rexp += (1 / (age) + 1)
                except:
                    rexp += 0

            else:
                devExperience[author] = {subsystem: 1}
        
            if( directory not in directoriesSeen ):
                directoriesSeen.append( directory )

            # Update file-level metrics
            la += fileLa 
            ld += fileLd
            nf += 1
            filesSeen += fileName + ",CAS_DELIMITER,"

        # End stats loop

        if( nf < 1):
            return ""

        # Update commit-level metrics
        ns = len(subsystemsSeen)
        nd = len(directoriesSeen)
        ndev = len(authors)
        lt = lt / nf
        age = age / nf
        exp = exp / nf
        rexp = rexp / nf

        # Update entrophy
        for fileLocMod in locModifiedPerFile:
            if (fileLocMod != 0 ):
                avg = fileLocMod/totalLOCModified
                entrophy -= ( avg * math.log( avg,2 ) )

        # Add stat properties to the commit object
        statProperties += ',"la":"' + str( la ) + '\"'
        statProperties += ',"ld":"' + str( ld ) + '\"'
        statProperties += ',"fileschanged":"' + filesSeen[0:-1] + '\"'
        statProperties += ',"nf":"' + str( nf ) + '\"'
        statProperties += ',"ns":"' + str( ns ) + '\"'
        statProperties += ',"nd":"' + str( nd ) + '\"'
        statProperties += ',"entrophy":"' + str(  entrophy ) + '\"'
        statProperties += ',"ndev":"' + str( ndev ) + '\"'
        statProperties += ',"lt":"' + str( lt ) + '\"'
        statProperties += ',"nuc":"' + str( nuc ) + '\"'
        statProperties += ',"age":"' + str( age ) + '\"'
        statProperties += ',"exp":"' + str( exp ) + '\"'
        statProperties += ',"rexp":"' + str( rexp ) + '\"'
        statProperties += ',"sexp":"' + str( sexp ) + '\"'

        return statProperties
    # End stats

    def log(self, repo, firstSync):
        """
        log(): Repository, Boolean -> Dictionary                                                                                                                                              
        arguments: repo Repository: the repository to clone
                   firstSync Boolean: whether to sync all commits or after the
            ingestion date
        description: a very basic abstraction for using git in python.
        """
        os.chdir(os.path.dirname(__file__) + self.REPO_DIRECTORY + repo.id)
        
        logging.info('Getting/parsing git commits: '+ str(repo) )
        # Spawn a git process and convert the output to a string
        if not firstSync:
            cmd = 'git log --after="' + repo.ingestion_date + '" '
        else:
            cmd = 'git log '
        
        log = str( subprocess.check_output(cmd + self.LOG_FORMAT, shell=True ) )
        log = log[2:-1]   # Remove head/end clutter
        
        # List of json objects
        json_list = []
        
        # Make sure there are commits to parse
        if len(log) == 0:
            return []

        # keep track of ALL file changes
        commitFiles = {} 

        # Keep track of ALL developer experience
        devExperience = {}

        commitList = log.split("CAS_READER_STARTPRETTY") 
        for commit in commitList:
            author = ""                                 # author of commit
            unixTimeStamp = 0                           # timestamp of commit
            fix = False                                 # whether or not the change is a defect fix

            commit = commit.replace('\\x', '\\u00')   # Remove invalid json escape characters

            splitCommitStat = commit.split("CAS_READER_STOPPRETTY")  # split the commit info and its stats

            # The first split will contain an empty list
            if(len(splitCommitStat) < 2):
                continue

            prettyCommit = splitCommitStat[0]
            statCommit = splitCommitStat[1]
            commitObject = ""

            # Start with the commit info (i.e., commit hash, author, date, subject, etc)
            prettyInfo = prettyCommit.split(',CAS_READER_PROP_DELIMITER2    "')
            for propValue in prettyInfo:
                props = propValue.split('"CAS_READER_PROP_DELIMITER: "')
                propStr = ''
                for prop in props:
                    prop = prop.replace('\\','').replace("\\n", '')  # avoid escapes & newlines for JSON formatting
                    propStr = propStr + '"' + prop.replace('"','') + '":'

                values = propStr[0:-1].split(":")

                if(values[0] == '"author_name"'):
                    author = values[1].replace('"', '')

                if(values[0] == '"author_date_unix_timestamp"'):
                    unixTimeStamp = values[1].replace('"','')

                # Check if it is a 'fix' commit
                if(values[0] == '"commit_message"'):
                    for word in self.correctiveWords: 
                        if word.lower() in values[1].lower():
                            fix = True
                            break

                commitObject += "," + propStr[0:-1]
                # End property loop
            # End pretty info loop

            # Get the stat properties
            stats = statCommit.split("\\n")
            commitObject += self.getCommitStatsProperties(stats, commitFiles, devExperience, author, unixTimeStamp)

             # Update whether commit was a fix or not
            commitObject += ',"fix":"' + str( fix ) + '\"'

            # Remove first comma and extra space
            commitObject = commitObject[1:].replace('    ','')                      

            # Add commit object to json_list
            json_list.append(json.loads('{' + commitObject + '}'))
        # End commit loop

        logging.info('Done getting/parsing git commits.')
        return json_list

    def clone(self, repo):
        """
        clone(repo): Repository -> String
        description:Takes the current repo and clones it into the
            `clone_directory/the_repo_id`
        arguments: repo Repository: the repository to clone
        pre-conditions: The repo has not been already created
        """
        # Go to the repo directory
        os.chdir(os.path.dirname(__file__) + self.REPO_DIRECTORY)
        # Run the clone command and return the results
        
        logging.info('Git cloning repo: '+ str(repo) )
        cloneResult = str(subprocess.check_output( 
                  self.CLONE_CMD.format(repo.url, './' + repo.id),
                  shell=True ) )
        logging.info('Done cloning.')
        #logging.debug("Git clone result:\n" + cloneResult)
        
        # Reset path for next repo

        # TODO: only return true on success, else return false
        return True

    def fetch(self, repo):
        """
        fetch(repo): Repository -> String
        description:Takes the current repo and pulls it into the
            `clone_directory/the_repo_id`
        arguments: repo Repository: the repository to pull
        pre-conditions: The repo has already been created
        """
        # Go to the repo directory
        os.chdir(os.path.dirname(__file__) + self.REPO_DIRECTORY + repo.id)
        # Run the pull command and return the results
        logging.info('Git fetching repo: '+ str(repo) )
        fetchResult = str(subprocess.check_output( 
                  self.FETCH_CMD,
                  shell=True ) )
        logging.info('Done fetching.')
        #logging.debug("Git pull result:\n" + cloneResult)

        # TODO: only return true on success, else return false
        return True