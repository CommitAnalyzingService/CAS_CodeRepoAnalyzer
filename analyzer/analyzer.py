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
			notifier.addSubscribers([repository_to_analyze.email, 'cbr4830@rit.edu'])
		else:
			notifier.addSubscribers(['cbr4830@rit.edu'])
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
	metrics_generator.buildAllModels()

	# dump monthly data - hardcoded 30 days
	dump_refresh_date = str(datetime.utcnow() - timedelta(days=30))

	if repository_to_analyze.last_data_dump == None or repository_to_analyze.last_data_dump < dump_refresh_date:
		metrics_generator.dumpData()
		repository_to_analyze.last_data_dump = str(datetime.now().replace(microsecond=0))

	repository_to_analyze.status = "Analyzed"
	repository_to_analyze.analysis_date = str(datetime.now().replace(microsecond=0))

	# Update database of commits that were buggy & analysis date & status
	session.commit()

	# Notify any subscribers of repo that it has been analyzed IF it has not been analyzed previously
	if notify is True and notifier is not None:
		notifier.notify()

	logging.info( 'A worker finished analyzing repo ' +
                  repository_to_analyze.id )
