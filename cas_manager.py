"""
file: cas_manager.py
authors: Christoffer Rosen <cbr4830@rit.edu>
date: Jan. 2014
description: This module contains the CAS_manager class, which is a thread that continously checks if there
			 is work that needs to be done. Also contains supporting classes of Worker and ThreadPool used by
			 the CAS_Manager.
"""
from analyzer.analyzer import *
from ingester.ingester import *
from orm.repository import *
from caslogging import logging
from queue import *
import threading
import time

class CAS_Manager(threading.Thread):
	""" 
	Thread that continiously checks if there is work to be done and adds it to
	the thread pool work queue
	"""

	def __init__(self):
		"""Constructor"""
		threading.Thread.__init__(self)
		self.session = Session()
		numOfWorkers = int(config['system']['workers'])
		self.workQueue = ThreadPool(numOfWorkers)

	def checkIngestion(self):
		"""Check if any repo needs to be ingested"""

		repo_update_freq = int(config['repoUpdates']['freqInDays'])
		refresh_date = str(datetime.utcnow() - timedelta(days=repo_update_freq))

		repos_to_get = (self.session.query(Repository) 
							.filter( 
								(Repository.status == "Waiting to be Ingested") | 
								(Repository.ingestion_date < refresh_date) &
								(Repository.status != "Analyzing"))
							.all())

		for repo in repos_to_get:
			logging.info("Adding repo " + repo.id + " to work queue for ingesting")
			repo.status = "In Queue to be Ingested"
			self.session.commit() # update the status of repo
			self.workQueue.add_task(ingest,repo.id)

	def checkAnalyzation(self):
		"""Checks if any repo needs to be analyzed"""

		repo_update_freq = int(config['repoUpdates']['freqInDays'])
		refresh_date = str(datetime.utcnow() - timedelta(days=repo_update_freq))

		repos_to_get = (self.session.query(Repository)
						  .filter( (Repository.status == "Waiting to be Analyzed") )
						  .all()
						)
		
		for repo in repos_to_get:
			logging.info("Adding repo " + repo.id + " to work queue for analyzing.")
			repo.status = "In Queue to be Analyzed"
			self.session.commit() # update the status of repo
			self.workQueue.add_task(analyze, repo.id)

	def run(self):

		while(True):
			### --- Check repository table if there is any work to be done ---  ###
			self.checkIngestion()
			self.checkAnalyzation()
			time.sleep(60)

class Worker(threading.Thread):
	"""Thread executing tasks from a given tasks queue"""
	def __init__(self, tasks):
		threading.Thread.__init__(self)
		self.tasks = tasks
		self.daemon = True
		self.start()
	
	def run(self):

		while True:

			func, args, kargs = self.tasks.get()
			try:
				func(*args, **kargs)
			except Exception as e:
				print(e)

			self.tasks.task_done()

class ThreadPool:
	"""Pool of threads consuming tasks from a queue"""
	def __init__(self, num_threads):
		self.tasks = Queue(num_threads)
		for _ in range(num_threads): Worker(self.tasks)

	def add_task(self, func, *args, **kargs):
		"""Add a task to the queue"""
		self.tasks.put((func, args, kargs))

	def wait_completion(self):
		"""Wait for completion of all the tasks in the queue"""
		self.tasks.join()
