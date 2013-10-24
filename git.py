"""
file: repository.py
author: Ben Grawi <bjg1568@rit.edu>
date: October 2013
description: Holds the repository git abstraction class
"""
import os
import subprocess
import json
import logging
class Git():
    """
    Git():
    pre-conditions: git is in the current PATH
                    self.path is set in a parent class
    description: a very basic abstraction for using git in python.
    """
    # Two backslashes to allow one backslash to be passed in the command.
    LOG_FORMAT = '--pretty=format:\"{\
    \\"commit_hash\\"CAS_READER_PROP_DELIMITER: \\"%H\\",CAS_READER_PROP_DELIMITER2\
    \\"commit_hash_abbreviated\\"CAS_READER_PROP_DELIMITER: \\"%h\\",CAS_READER_PROP_DELIMITER2\
    \\"tree_hash\\"CAS_READER_PROP_DELIMITER: \\"%T\\",CAS_READER_PROP_DELIMITER2\
    \\"tree_hash_abbreviated\\"CAS_READER_PROP_DELIMITER: \\"%t\\",CAS_READER_PROP_DELIMITER2\
    \\"parent_hashes\\"CAS_READER_PROP_DELIMITER: \\"%P\\",CAS_READER_PROP_DELIMITER2\
    \\"parent_hashes_abbreviated\\"CAS_READER_PROP_DELIMITER: \\"%p\\",CAS_READER_PROP_DELIMITER2\
    \\"author_name\\"CAS_READER_PROP_DELIMITER: \\"%an\\",CAS_READER_PROP_DELIMITER2\
    \\"author_email\\"CAS_READER_PROP_DELIMITER: \\"%ae\\",CAS_READER_PROP_DELIMITER2\
    \\"author_date\\"CAS_READER_PROP_DELIMITER: \\"%ad\\",CAS_READER_PROP_DELIMITER2\
    \\"author_date_rfc2822_style\\"CAS_READER_PROP_DELIMITER: \\"%aD\\",CAS_READER_PROP_DELIMITER2\
    \\"author_date_relative\\"CAS_READER_PROP_DELIMITER: \\"%ar\\",CAS_READER_PROP_DELIMITER2\
    \\"author_date_unix_timestamp\\"CAS_READER_PROP_DELIMITER: \\"%at\\",CAS_READER_PROP_DELIMITER2\
    \\"author_date_iso_8601\\"CAS_READER_PROP_DELIMITER: \\"%ai\\",CAS_READER_PROP_DELIMITER2\
    \\"committer_name\\"CAS_READER_PROP_DELIMITER: \\"%cn\\",CAS_READER_PROP_DELIMITER2\
    \\"committer_email\\"CAS_READER_PROP_DELIMITER: \\"%ce\\",CAS_READER_PROP_DELIMITER2\
    \\"committer_date\\"CAS_READER_PROP_DELIMITER: \\"%cd\\",CAS_READER_PROP_DELIMITER2\
    \\"committer_date_relative\\"CAS_READER_PROP_DELIMITER: \\"%cr\\",CAS_READER_PROP_DELIMITER2\
    \\"commit_message\\"CAS_READER_PROP_DELIMITER: \\"%b\\",CAS_READER_PROP_DELIMITER2\
    \\"subject\\"CAS_READER_PROP_DELIMITER: \\"%s\\"\
    }CAS_READER_JSON_DELIMITER,\"'
    
    CLONE_CMD = 'git clone --no-checkout {!s} {!s}'
    
    PULL_CMD = 'git pull origin master'
    
    REPO_DIRECTORY = "/CASRepos/git/"
    
    
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
        
        # Get rid of newlines, screws up json parsing. Remove head/end clutter
        log = log.replace( '\\n', '' )
        log = log[3:-3] 

        # List of json objects
        json_list = []
        
        # Make sure there are commits to parse
        if len(log) == 0:
            return []
        
        # JSON won't be able to read as is - clean each commit and append to json_list
        commitList = log.split("}CAS_READER_JSON_DELIMITER,{")
        for commit in commitList:
          
            # Remove invalid json escape characters
            commit = commit.replace('\\x', '\\u00')

            # Remove quotes in JSON properties
            propValues = commit.split(',CAS_READER_PROP_DELIMITER2    "')
            commitFixed = ""
            for propValue in propValues:
                props = propValue.split('"CAS_READER_PROP_DELIMITER: "')
                propStr = ''
                for prop in props:
                    prop = prop.replace('\\','') # json doesn't like escapes..
                    propStr = propStr + '"' + prop.replace('"','') + '":'
              
                commitFixed = commitFixed + "," + propStr[0:-1]
     
         
            commitFixed = commitFixed[1:].replace('    ','')
            json_list.append(json.loads('{' + commitFixed + '}'))
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
    def pull(self, repo):
        """
        pull(repo): Repository -> String
        description:Takes the current repo and pulls it into the
            `clone_directory/the_repo_id`
        arguments: repo Repository: the repository to pull
        pre-conditions: The repo has already been created
        """
        # Go to the repo directory
        os.chdir(os.path.dirname(__file__) + self.REPO_DIRECTORY + repo.id)
        # Run the pull command and return the results
        logging.info('Git pulling repo: '+ str(repo) )
        pullResult = str(subprocess.check_output( 
                  self.PULL_CMD,
                  shell=True ) )
        logging.info('Done pulling.')
        #logging.debug("Git pull result:\n" + cloneResult)

        # TODO: only return true on success, else return false
        return True