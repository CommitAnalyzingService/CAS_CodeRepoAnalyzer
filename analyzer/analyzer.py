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

	logging.info('Worker analyzing repository id ' + repo_id)

	# Update status of repo to show it is analyzing
	repository_to_analyze.status = "Analyzing"
	session.commit()

	# use data only up to 3 months prior as we won't have data until then.
	three_months = str(datetime.utcnow() - timedelta(days=30))

	# all commits in descending order
	all_commits = (session.query(Commit)
				.filter( Commit.repository_id == repo_id)
				.filter( Commit.author_date_unix_timestamp < three_months)
				.order_by( Commit.author_date_unix_timestamp.desc())
				.all()
				)

	# corrective commits in ascending order
	corrective_commits = (session.query(Commit)
				.filter( Commit.fix == "True")
				.filter( Commit.repository_id == repo_id)
				.filter( Commit.author_date_unix_timestamp < three_months)
				.order_by( Commit.author_date_unix_timestamp.asc())
				.all()
				)


	try:
		git_commit_linker = GitCommitLinker(repo_id)
		git_commit_linker.linkCorrectiveCommits(corrective_commits, all_commits)
	except Exception as e:
		logging.error("Error linking bug fixing changes to bug inducing changes for repo " + repo_id)
		logging.error(e)
		repository_to_analyze.status = "Error"
		session.commit() # update repo status
		sys.exit(0)


	#  Generate the metrics
	logging.info('Generating metrics for repository id ' + repo_id)
	
	try: 
		metrics_generator = MetricsGenerator(repo_id, all_commits)
		metrics_generator.buildAllModels()
	except Exception as e:
		logging.error("Error generating metrics & building models for repository " + repo_id)
		logging.error(e)
		repository_to_analyze.status = "Error"
		session.commit() # update repo status
		sys.exit(0)

	repository_to_analyze.status = "Analyzed"
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
