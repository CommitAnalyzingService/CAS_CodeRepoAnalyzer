"""
file: repository.py
author: Ben Grawi <bjg1568@rit.edu>
date: October 2013
description: Holds the repository git abstraction class
"""
import os
import subprocess
import json
import re
class Git():
    """
    Git():
    pre-conditions: git is in the current PATH
                    self.path is set in a parent class
    description: a very basic abstraction for using git in python.
    """
    # Two backslashes to allow one backslash to be passed in the command.
    LOG_CMD = 'git log --pretty=format:\"{\
    \\"commit_hash\\": \\"%H\\",\
    \\"commit_hash_abbreviated\\": \\"%h\\",\
    \\"tree_hash\\": \\"%T\\",\
    \\"tree_hash_abbreviated\\": \\"%t\\",\
    \\"parent_hashes\\": \\"%P\\",\
    \\"parent_hashes_abbreviated\\": \\"%p\\",\
    \\"author_name\\": \\"%an\\",\
    \\"author_email\\": \\"%ae\\",\
    \\"author_date\\": \\"%ad\\",\
    \\"author_date_rfc2822_style\\": \\"%aD\\",\
    \\"author_date_relative\\": \\"%ar\\",\
    \\"author_date_unix_timestamp\\": \\"%at\\",\
    \\"author_date_iso_8601\\": \\"%ai\\",\
    \\"committer_name\\": \\"%cn\\",\
    \\"committer_email\\": \\"%ce\\",\
    \\"committer_date\\": \\"%cd\\",\
    \\"committer_date_relative\\": \\"%cr\\",\
    \\"commit_message\\": \\"%b\\",\
    \\"subject\\": \\"%s\\"\
    },\"'

    def log(self):
        """
        log(): NoneType -> Dictonary
        description: a very basic abstraction for using git in python.
        """
        os.chdir( self.path )
        
        # Spawn a git process and convert the output to a string
        log = str( subprocess.check_output( self.LOG_CMD, shell=True ) )
        
        # Get rid of newlines, screws up json parsing. Remove head/end clutter
        log = log.replace( '\\n', '' )
        log = log[3:-3] 

        # List of json objects
        json_list = []

        # Serialize each object to JSON format
        commitList = log.split("},{")
        for commit in commitList:
            #commit = commit.replace('    ','')
            # Remove invalid json escape characters
            commit = commit.replace('\\x', '\\u00')

            # Remove quotes in JSON properties
            propValues = commit.split(',    "')
            commitFixed = ""
            for propValue in propValues:
                props = propValue.split('": "')
                propStr = ''
                for prop in props:
                    propStr = propStr + '"' + prop.replace('"','') + '":'
              
                commitFixed = commitFixed + "," + propStr[0:-1]
     
         
            commitFixed = commitFixed[1:].replace('    ','')

            # Handle all other invalid escape sequences
            regex = re.compile(r'\\(?![/u"])')
            commitFixed = regex.sub(r"\\\\",commitFixed)

            json_list.append(json.loads('{' + commitFixed + '}'))
    
        return json_list
