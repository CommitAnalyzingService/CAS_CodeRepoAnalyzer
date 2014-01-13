"""
file: config.py
author: Ben Grawi <bjg1568@rit.edu>
date: November 2013
description: Reads the config.json info into a varible
"""
import json
#from StringIO import StringIO
config = json.load(open('./config.json'))