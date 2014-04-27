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
import calendar # to convert datetime to unix time
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
		self.modelQueue = Queue()

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

	def checkModel(self):
		"""Check if any repo needs metrics to be generated"""

		repos_to_get = (self.session.query(Repository) 
							.filter( 
								(Repository.status == "In Queue to Build Model") )
							.all())

		for repo in repos_to_get:
			logging.info("Adding repo " + repo.id + " to model queue to finish analyzing")
			repo.status = "Building Model"
			self.session.commit() # update status of repo
			self.modelQueue.put(repo)

	def checkBuildModel(self):
		""" Checks if any repo is awaiting to build model. 
			We are using a queue because we can't concurrently access R """

		if self.modelQueue.empty() != True:
			repo = self.modelQueue.get()
			repo_id = repo.id 

			# use data only up to 3 months prior we won't have sufficent data to build models
			# as there may be bugs introduced in those months that haven't been fixed, skewing
			# our model.
			three_months_datetime = datetime.utcnow() - timedelta(days=30)
			three_months_unixtime = calendar.timegm(three_months_datetime.utctimetuple())

			all_commits_modeling = (self.session.query(Commit)
						.filter( 
							( Commit.repository_id == repo_id ) &
							( Commit.author_date_unix_timestamp < str(three_months_unixtime))
						)
						.order_by( Commit.author_date_unix_timestamp.desc() )
						.all())

			all_commits = (self.session.query(Commit)
						.filter(
							( Commit.repository_id == repo_id ))
						.all())
	
			try: 
				metrics_generator = MetricsGenerator(repo_id, all_commits_modeling, all_commits)
				metrics_generator.buildAllModels()

				# montly data dump
				dump_refresh_date = str(datetime.utcnow() - timedelta(days=30))
				if repo.last_data_dump == None or repo.last_data_dump < dump_refresh_date:
					logging.info("Generating a monthly data dump for repository: " + repo_id)
					metrics_generator.dumpData()
					repo.last_data_dump = str(datetime.now().replace(microsecond=0))

			except Exception as e:
				logging.exception("Got an exception building model for repository " + repo_id)
				repo.status = "Error"
				session.commit() # update repo status
				raise

			logging.info("Repo " + repo_id + " finished analyzing.")
			repo.analysis_date = str(datetime.now().replace(microsecond=0))
			repo.status = "Analyzed"
			self.session.commit() # update status of repo
			self.notify(repo)
		# End of if statement

	def notify(self, repo):
		""" Send e-mail notifications if applicable to a repo 
			used by checkBuildModel """
		notify = False
		notifier = None

		# Notify user if repo has never been analyzed previously
		if repo.analysis_date is None:

			# Create the Notifier
			gmail_user = config['gmail']['user']
			gmail_pass = config['gmail']['pass']
			notifier = Notifier(gmail_user, gmail_pass, repo.name)

			# Add subscribers if applicable
			if repo.email is not None:
				notifier.addSubscribers([repo.email, gmail_user])
			else:
				notifier.addSubscribers([gmail_user])

			notifier.notify()

	def run(self):

		while(True):
			### --- Check repository table if there is any work to be done ---  ###
			self.checkIngestion()
			self.checkAnalyzation()
			self.checkModel()
			self.checkBuildModel()
			time.sleep(10)

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
