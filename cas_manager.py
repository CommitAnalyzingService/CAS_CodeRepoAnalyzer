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
from monthdelta import MonthDelta

class CAS_Manager(threading.Thread):
	""" 
	Thread that continiously checks if there is work to be done and adds it to
	the thread pool work queue
	"""

	def __init__(self):
		"""Constructor"""
		threading.Thread.__init__(self)
		numOfWorkers = int(config['system']['workers'])
		self.workQueue = ThreadPool(numOfWorkers)
		self.modelQueue = Queue()

	def checkIngestion(self):
		"""Check if any repo needs to be ingested"""

		session = Session()
		repo_update_freq = int(config['repoUpdates']['freqInDays'])
		refresh_date = str(datetime.utcnow() - timedelta(days=repo_update_freq))

		repos_to_get = (session.query(Repository) 
							.filter( 
								(Repository.status == "Waiting to be Ingested") | 
								(Repository.ingestion_date < refresh_date) &
								(Repository.status != "Error") &
								(Repository.status != "Analyzing"))
							.all())

		for repo in repos_to_get:
			logging.info("Adding repo " + repo.id + " to work queue for ingesting")
			repo.status = "In Queue to be Ingested"
			session.commit() # update the status of repo
			self.workQueue.add_task(ingest,repo.id)

		session.close()

	def checkAnalyzation(self):
		"""Checks if any repo needs to be analyzed"""

		session = Session()
		repo_update_freq = int(config['repoUpdates']['freqInDays'])
		refresh_date = str(datetime.utcnow() - timedelta(days=repo_update_freq))

		repos_to_get = (session.query(Repository)
						  .filter( (Repository.status == "Waiting to be Analyzed") )
						  .all()
						)
		
		for repo in repos_to_get:
			logging.info("Adding repo " + repo.id + " to work queue for analyzing.")
			repo.status = "In Queue to be Analyzed"
			session.commit() # update the status of repo
			self.workQueue.add_task(analyze, repo.id)

		session.close()

	def checkModel(self):
		"""Check if any repo needs metrics to be generated"""

		session = Session()
		repos_to_get = (session.query(Repository) 
							.filter( 
								(Repository.status == "In Queue to Build Model") )
							.all())

		for repo in repos_to_get:
			logging.info("Adding repo " + repo.id + " to model queue to finish analyzing")
			repo.status = "Building Model"
			session.commit() # update status of repo
			self.modelQueue.put(repo.id)

		session.close()

	def checkBuildModel(self):
		""" Checks if any repo is awaiting to build model. 
			We are using a queue because we can't concurrently access R """

		session = Session()

		if self.modelQueue.empty() != True:
			repo_id = self.modelQueue.get()
			repo = (session.query(Repository).filter(Repository.id == repo_id).first())

			# use data only up to X months prior we won't have sufficent data to build models
			# as there may be bugs introduced in those months that haven't been fixed, skewing
			# our model.
			glm_model_time =  int(config['glm_modeling']['months']) 
			data_months_datetime = datetime.utcnow() - MonthDelta(glm_model_time)
			data_months_unixtime = calendar.timegm(data_months_datetime.utctimetuple())
		
			# all commits for repo prior to current time - glm model time
			training_commits = (session.query(Commit)
						.filter( 
							( Commit.repository_id == repo_id ) &
							( Commit.author_date_unix_timestamp < str(data_months_unixtime))
						)
						.order_by( Commit.author_date_unix_timestamp.desc() )
						.all())

			# all commits for repo after or on current time - glm model time
			testing_commits = (session.query(Commit)
						.filter(
							( Commit.repository_id == repo_id ) &
							( Commit.author_date_unix_timestamp >= str(data_months_unixtime)))
						.all())
	
			try: 
				metrics_generator = MetricsGenerator(repo_id, training_commits, testing_commits)
				metrics_generator.buildAllModels()

				# montly data dump - or rather, every 30 days.
				dump_refresh_date = str(datetime.utcnow() - timedelta(days=30))
				if repo.last_data_dump == None or repo.last_data_dump < dump_refresh_date:
					logging.info("Generating a monthly data dump for repository: " + repo_id)

					# Get all commits for the repository
					all_commits = (session.query(Commit)
						.filter( 
							( Commit.repository_id == repo_id )
						)
						.order_by( Commit.author_date_unix_timestamp.desc() )
						.all())

					metrics_generator.dumpData(all_commits)
					repo.last_data_dump = str(datetime.now().replace(microsecond=0))
					
				# Notify user if repo has never been analyzed previously
				if repo.analysis_date is None:
					self.notify(repo)
	
				logging.info("Repo " + repo_id + " finished analyzing.")
				repo.analysis_date = str(datetime.now().replace(microsecond=0))
				repo.status = "Analyzed"
				session.commit() # update status of repo
				session.close()

			# uh-oh
			except Exception as e:
				logging.exception("Got an exception building model for repository " + repo_id)

				repo.status = "Error"
				session.commit() # update repo status
				session.close()

	def notify(self, repo):
		""" Send e-mail notifications if applicable to a repo 
			used by checkBuildModel """

		notify = False
		notifier = None
		logging.info("Notifying subscribed users for repository " + repo.id)

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
