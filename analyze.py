"""
file: analyze.py
description: Creates a analyzer worker to analyze a repo with passed in repository id.
For test purposes only!
"""
from analyzer import *
thread1 = Analyzer(sys.argv)
thread1.start()
thread1.join()
print("Fin!")