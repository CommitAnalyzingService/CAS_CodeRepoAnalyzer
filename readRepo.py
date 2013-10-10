"""
file: readRepo.py
author: Ben Grawi <bjg1568@rit.edu>
date: October 2013
description: Holds the repository abstraction class
"""
import sys
from commit import Commit
from repository import *

# Read the first argument and pass it in as a string
repo = Repository(sys.argv[1])
repo.parseLog()
repo.syncCommits()
print('{"success":"true", "name":"CAS Web"}')
