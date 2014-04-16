"""
file: Analyzer.py
author: Christoffer Rosen <cbr4830@rit.edu>
date: November 2013
description: This module contains the functions for analyzing a repo with a given id.
Currently only supports the GitHub Issue Tracker.
"""
import sys
from datetime import datetime, timedelta
from orm.repository import *
from orm.commit import *
from analyzer.bugfinder import *
from analyzer.metricsgenerator import *
from analyzer.githubissuetracker import *
from caslogging import logging
from analyzer.notifier import *
from config import config
from analyzer.git_commit_linker import *
from sqlalchemy import Date, cast
import calendar # to convert datetime to unix time

def analyze(repo_id):
	"""
	Analyze the repository with the given id. Gets the repository from the repository table
	and starts ingesting using the analyzeRepo method.
	@param repo_id		The repository id to analyze
	"""

	session = Session()

	repo_to_analyze = (session.query(Repository)
				.filter (Repository.id == repo_id)
				.all()
				)

	# Verify that repo exists
	if len(repo_to_analyze) > 0:
		analyzeRepo(repo_to_analyze[0],session)
	else:
		logging.info('Repo with id ' + repo_id_to_analyze + ' not found!')

def analyzeRepo(repository_to_analyze, session):
	"""
	Analyzes the given repository
	@param repository_to_analyze	The repository to analyze.
	@param notifier                 gmail notifier object
	@param session                  SQLAlchemy session
	@private
	"""
	notify = False
	notifier = None

	# Notify user if repo has never been analyzed previously
	if repository_to_analyze.analysis_date is None:
		notify = True

		# Create the Notifier
		gmail_user = config['gmail']['user']
		gmail_pass = config['gmail']['pass']
		notifier = Notifier(gmail_user, gmail_pass, repository_to_analyze.name)

		# Add subscribers if applicable
		if repository_to_analyze.email is not None:
			notifier.addSubscribers([repository_to_analyze.email, gmail_user])
		else:
			notifier.addSubscribers([gmail_user])
	# End notifier setup

	repo_name = repository_to_analyze.name
	repo_id = repository_to_analyze.id
	last_analysis_date = repository_to_analyze.analysis_date

	logging.info('Worker analyzing repository id ' + repo_id)

	# Update status of repo to show it is analyzing
	repository_to_analyze.status = "Analyzing"
	session.commit()


	# all commits in descending order
	all_commits = (session.query(Commit)
				.filter( Commit.repository_id == repo_id)
				.order_by( Commit.author_date_unix_timestamp.desc())
				.all()
				)

	# corrective commits in ascending order 
	# if updating, only get the corrective commits that have not been linked yet.
	# No need to re-link corrective commits that have already been linked with the bug-inducing commit.

	corrective_commits = (session.query(Commit)
				.filter( 
					( Commit.fix == "True" ) &
					( Commit.repository_id == repo_id ) &
					( Commit.linked == False )
				)
				.order_by( Commit.author_date_unix_timestamp.asc() )
				.all()
				)

	logging.info("Linking " + str(len(corrective_commits)) + " new corrective commits for repo " + repo_id)

	# use data only up to 3 months prior we won't have sufficent data to build models
	# as there may be bugs introduced in those months that haven't been fixed, skewing
	# our model.
	three_months_datetime = datetime.utcnow() - timedelta(days=30)
	three_months_unixtime = calendar.timegm(three_months_datetime.utctimetuple())

	all_commits_modeling = (session.query(Commit)
				.filter( 
					( Commit.repository_id == repo_id ) &
					( Commit.author_date_unix_timestamp < str(three_months_unixtime))
				)
				.order_by( Commit.author_date_unix_timestamp.desc() )
				.all()
				)

	logging.info("Modeling on " + str(len(all_commits_modeling)) + " commits for repo " + repo_id)

	try:
		git_commit_linker = GitCommitLinker(repo_id)
		git_commit_linker.linkCorrectiveCommits(corrective_commits, all_commits)
	except Exception as e:
		logging.exception("Got an exception linking bug fixing changes to bug inducing changes for repo " + repo_id)
		repository_to_analyze.status = "Error"
		session.commit() # update repo status
		raise

	#  Generate the metrics
	if repository_to_analyze.status != "Error":
		logging.info('Generating metrics for repository id ' + repo_id)
		
		try: 
			metrics_generator = MetricsGenerator(repo_id, all_commits_modeling)
			metrics_generator.buildAllModels()
		except Exception as e:
			logging.exception("Got an exceotion generating metrics for repository " + repo_id)
			repository_to_analyze.status = "Error"
			session.commit() # update repo status
			raise

	if repository_to_analyze.status != "Error":
 
		repository_to_analyze.status = "Analyzed" # repo successfully has been analyzed
		repository_to_analyze.analysis_date = str(datetime.now().replace(microsecond=0))

		# dump monthly data - hardcoded 30 days
		dump_refresh_date = str(datetime.utcnow() - timedelta(days=30))

		if repository_to_analyze.last_data_dump == None or repository_to_analyze.last_data_dump < dump_refresh_date:
			metrics_generator.dumpData() 
			repository_to_analyze.last_data_dump = str(datetime.now().replace(microsecond=0))

		# Update database of commits that were buggy & analysis date & status & glm probabilities
		session.commit()

		# Notify any subscribers of repo that it has been analyzed IF it has not been analyzed previously
		if notify is True and notifier is not None and repository_to_analyze.status is not "Error":
			notifier.notify()

	logging.info( 'A worker finished analyzing repo ' +
									repository_to_analyze.id )

	session.close()
