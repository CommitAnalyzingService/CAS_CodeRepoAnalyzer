"""
file: analyze.py 
author: Christoffer Rosen <cbr4830@rit.edu>
date: November 2013
description: Base script to call. Looks at the Repository table for
repositories that need to be analyzed, analyzes it, and places 
results in the metrics table.
"""

import sys
from datetime import datetime, timedelta
from repository import *
from commit import *
from bugfinder import *
from metricsgenerator import *
from githubissuetracker import *
from caslogging import logging
from notifier import *
from config import config

logging.info('Starting CASAnalyzer')

# Latest time to analyze repo (1 Day)
refresh_date = str(datetime.utcnow() - timedelta(days=1))
session = Session()

reposToAnalyze = (session.query(Repository)
                  .filter( (Repository.analysis_date==None) |
                          (Repository.analysis_date < refresh_date)
                          )
                  .all()
                  )

# Create the Notifier
gmail_user = config['gmail']['user']
gmail_pass = config['gmail']['pass']
notifier = Notifier(gmail_user, gmail_pass)

if len(reposToAnalyze) > 0:
	for repo in reposToAnalyze:
		repo_name = repo.name
		repo_id = repo.id

		# Add if applicable subscriber
		notifier.addSubscribers(['cbr4830@rit.edu'])

		logging.info('Analyzing ' + repo_name)

		repo.analysis_date = str(datetime.now().replace(microsecond=0))

		# all commits in descending order
		all_commits = (session.query(Commit)
					.filter( Commit.repository_id == repo_id)
					.order_by( Commit.author_date_unix_timestamp.desc())
					.all()
					)

		# corrective commits in ascending order
		corrective_commits = (session.query(Commit)
					.filter( Commit.repository_id == repo.id )
					.filter( Commit.fix == "True") 
					.filter( Commit.repository_id == repo_id)
					.order_by( Commit.author_date_unix_timestamp.asc())
					.all()
					)

		# Issue Tracker 

		# If using github, for now we just assume use of github issue tracker
		if("github" in repo.url):
			github_info = repo.url.split("https://github.com/")[1].split("/")
			owner = github_info[0]
			repo = github_info[1][0:-4] # Remove the .git
			issue_tracker = GithubIssueTracker(owner,repo)
		else:
			issue_tracker = None

		# Find and mark the buggy commits
		bug_finder = BugFinder(all_commits, corrective_commits, issue_tracker)
		bug_finder.markBuggyCommits()

		# Generate the metrics
		logging.info('Generating metrics... ' + repo_name)
		metrics_generator = MetricsGenerator(repo_name, all_commits)
		metrics_generator.generateMetrics()

		# Update database of commits that were buggy & analysis date
		session.commit() 

		# Notify any subscribers of repo that it has been analyzed 
		notifier.notify()
else:
	logging.info('Nothing to do. Done')



