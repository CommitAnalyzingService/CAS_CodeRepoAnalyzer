"""
file: repository.py
author: Ben Grawi <bjg1568@rit.edu>
date: October 2013
description: Holds the repository git abstraction class
"""
import os
import subprocess
import json

class Git():
    """
    Git():
    pre-conditions: git is in the current PATH
                    self.path is set in a parent class
    description: a very basic abstraction for using git in python.
    """
    # Two backslashes to allow one backslash to be passed in the command.
    LOG_CMD = 'git log --pretty=format:\"{\
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

    def log(self):
        """
        log(): NoneType -> Dictonary
        description: a very basic abstraction for using git in python.
        """
        os.chdir( self.repo.path )
        
        # Spawn a git process and convert the output to a string
        log = str( subprocess.check_output( self.LOG_CMD, shell=True ) )
        
        # Get rid of newlines, screws up json parsing. Remove head/end clutter
        log = log.replace( '\\n', '' )
        log = log[3:-3] 

        # List of json objects
        json_list = []

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
    
        return json_list
