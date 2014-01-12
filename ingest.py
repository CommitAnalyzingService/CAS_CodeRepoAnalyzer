"""
file: ingester.py
description: Created a ingester worker thread to ingest a repo with id 
passed in the parameter. Used for test purposes only!
"""
from ingester import *

thread1 = Ingester(sys.argv)
thread1.start() 
thread1.join()
print("finished!")