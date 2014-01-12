"""
file: Analyzer.py
author: Christoffer Rosen <cbr4830@rit.edu>
date: November 2013
description: This module contains the Analyzer thread class. Used to create thread workers
			 that will analyze a repository from the repository table given a repo id.
"""
import sys
import threading
from datetime import datetime, timedelta
from repository import *
from commit import *
from bugfinder import *
from metricsgenerator import *
from githubissuetracker import *
from caslogging import logging
from notifier import *
from config import config

class Analyzer(threading.Thread):
	""" 
	Class that represents a an analyzer worker. Given a repository id, analyze the repo 
	and determine the commits that were buggy and generate the metrics outputing this to 
	the metrics table.
	"""

	def __init__(self, args):
		""" 
		Constructor
		@param args - expects a repository id as an argument
		"""
		threading.Thread.__init__(self)
		self.args = args
		self.session = Session()

		# Create the Notifier
		gmail_user = config['gmail']['user']
		gmail_pass = config['gmail']['pass']
		self.notifier = Notifier(gmail_user, gmail_pass)

	def run(self):
		""" 
		Worker run method - analyze the given repository id given to the worker
		"""
		self.analyze(self.args)

	def analyze(self, args):
		"""
		Analyze the repository with the given id. Gets the repository from the repository table
		and starts ingesting using the analyzeRepo method.
		@param args		The repository id to analyze
		"""

		if len(args) != 2:
			logging.info("No repo id was given!")
		else:
			repo_id_to_analyze = sys.argv[1]
			repo_to_analyze = (self.session.query(Repository)
						.filter (Repository.id == repo_id_to_analyze)
						.all()
						)
			# Verify that repo exists
			if len(repo_to_analyze) > 0:
				self.analyzeRepo(repo_to_analyze[0])
			else:
				logging.info('Repo with id ' + repo_id_to_analyze + ' not found!')

	def analyzeRepo(self, repository_to_analyze):
		"""
		Analyzes the given repository
		@param repository_to_analyze	The repository to analyze. 
		"""
		repo_name = repository_to_analyze.name
		repo_id = repository_to_analyze.id

		# Add if applicable subscriber
		if repository_to_analyze.email is not None:
			self.notifier.addSubscribers([repository_to_analyze.email, 'cbr4830@rit.edu'])
		else:
			self.notifier.addSubscribers(['cbr4830@rit.edu'])

		logging.info('Analyzing repository id ' + repo_id)

		# Update status of repo to show it is analyzing
		repository_to_analyze.status = "Analyzing"
		self.session.commit()

		# all commits in descending order
		all_commits = (self.session.query(Commit)
					.filter( Commit.repository_id == repo_id)
					.order_by( Commit.author_date_unix_timestamp.desc())
					.all()
					)

		# corrective commits in ascending order
		corrective_commits = (self.session.query(Commit)
					.filter( Commit.fix == "True") 
					.filter( Commit.repository_id == repo_id)
					.order_by( Commit.author_date_unix_timestamp.asc())
					.all()
					)

		#### Issue Tracker ####

		# If using github, assume use of github issue tracker
		if("github" in repository_to_analyze.url):
			github_info = repository_to_analyze.url.split("https://github.com/")[1].split("/")
			owner = github_info[0]
			repo = github_info[1][0:-4] # Remove the .git
			issue_tracker = GithubIssueTracker(owner,repo)
		else:
			issue_tracker = None

		# Find and mark the buggy commits
		bug_finder = BugFinder(all_commits, corrective_commits, issue_tracker)
		bug_finder.markBuggyCommits()

		# Generate the metrics
		logging.info('Generating metrics for repository id ' + repo_id)
		metrics_generator = MetricsGenerator(repo_id, all_commits)
		metrics_generator.generateMetrics()

		repository_to_analyze.status = "Analyzed"
		repository_to_analyze.analysis_date = str(datetime.now().replace(microsecond=0))

		# Update database of commits that were buggy & analysis date & status
		self.session.commit() 
		
		# Notify any subscribers of repo that it has been analyzed 
		self.notifier.notify()


