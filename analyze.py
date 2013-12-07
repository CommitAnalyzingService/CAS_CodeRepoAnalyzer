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

# Latest time to analyze repo (1 Day)
refresh_date = str(datetime.utcnow() - timedelta(days=1))
session = Session()

reposToAnalyze = (session.query(Repository)
                  .filter( (Repository.analysis_date==None) |
                          (Repository.analysis_date < refresh_date)
                          )
                  .all()
                  )

if len(reposToAnalyze) > 0:
	for repo in reposToAnalyze:
		repo_name = repo.name
		repo_id = repo.id

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

		# Find and mark the buggy commits
		bug_finder = BugFinder(all_commits, corrective_commits)
		bug_finder.markBuggyCommits()

		# Generate the metrics
		metrics_generator = MetricsGenerator(repo_name, all_commits)
		metrics_generator.generateMetrics()

		# Update database of commits that were buggy & analysis date
		session.commit() 



