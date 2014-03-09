"""
file: script.py
author: Christoffer Rosen <cbr4830@rit.edu>, Ben Grawi <bjg1568@rit.edu>
date: Jan. 2014
description: base script to call.
"""
from cas_manager import *
from analyzer.analyzer import *
from orm.feedback import *
from orm.user import *

if len(sys.argv) > 1:
	arg = sys.argv[1]
else:
	arg = ''

if arg == "initDb":
    # Init the database
    logging.info('Initializing the Database...')
    Base.metadata.create_all(engine)
    logging.info('Done')

else:
	logging.info("Starting CAS Manager")
	cas_manager = CAS_Manager()
	cas_manager.start()
