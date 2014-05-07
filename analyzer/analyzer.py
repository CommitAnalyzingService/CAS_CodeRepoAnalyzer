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

	session.close()

def analyzeRepo(repository_to_analyze, session):
	"""
	Analyzes the given repository
	@param repository_to_analyze	The repository to analyze.
	@param session                  SQLAlchemy session
	@private
	"""
	repo_name = repository_to_analyze.name
	repo_id = repository_to_analyze.id
	last_analysis_date = repository_to_analyze.analysis_date

	# Update status of repo to show it is analyzing
	repository_to_analyze.status = "Analyzing"
	session.commit()

	logging.info('Worker analyzing repository id ' + repo_id)

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

	try:
		git_commit_linker = GitCommitLinker(repo_id)
		git_commit_linker.linkCorrectiveCommits(corrective_commits, all_commits)
	except Exception as e:
		logging.exception("Got an exception linking bug fixing changes to bug inducing changes for repo " + repo_id)
		repository_to_analyze.status = "Error"
		session.commit() # update repo status
		raise

	# Signify to CAS Manager that this repo is ready to have it's model built
	if repository_to_analyze.status != "Error":
		repository_to_analyze.status = "In Queue to Build Model"
		session.commit() # update repo status
