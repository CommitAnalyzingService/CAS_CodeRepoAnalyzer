"""
file: bugfinder.py
author: Christoffer Rosen <cbr4830@rit.edu>
date: November 2013
description: Links changes that introduces bugs by identifying changes
that fix problems.
"""

import re
from orm.commit import *
from caslogging import logging
from analyzer.git_commit_linker import *

class BugFinder:
	"""
	BugFinder():
	description: Links changes that introduces bugs.
	"""

	def __init__(self, allCommits, correctiveCommits, issueTracker):
		"""
		Constructor

		@param commits: All commits in ascending order by date
		@param correctiveCommits: All commits/changes which are identified
		as fixing problems.
		@param issueTracker: Issue tracker (e.g., GitHub Issues)
		"""
		self.allCommits = allCommits
		self.correctiveCommits = correctiveCommits
		self.issueTracker = issueTracker

	def findIssueOpened(self, correctiveCommit):
		"""
		findIssueIds()
		If the corrective change/commit links to a issue in the issue tracker, returns
		the date of oldest open issue found otherwise returns none
		"""
		issue_opened = None

		if(self.issueTracker is None or hasattr(self.issueTracker, "getDateOpened") == False):
			return None

		idMatch = re.compile('#[\d]+')
		issue_ids = idMatch.findall(correctiveCommit.commit_message)
		issue_ids = [issue_id.strip('#') for issue_id in issue_ids] # Remove the '#' from ids

		if len(issue_ids) > 0:
			issue_opened = self.issueTracker.getDateOpened(issue_ids[0])
			# Use the oldest open bug
			for issue_id in issue_ids:
				logging.info('Searching for issue id: ' + issue_id)
				curr_issue_opened = self.issueTracker.getDateOpened(issue_id)

				# Verify that an issue was found.
				if curr_issue_opened is not None:
					if int(curr_issue_opened) < int(issue_opened):
						issue_opened = curr_issue_opened

		return issue_opened

	def searchForBuggyCommit(self, correctiveCommit):
		"""
		Finds the buggy commit based on the bug fixing commit
		Helper method for markBuggyCommits. If commir links to an
		issue tracker, we check files changed prior to this date.
		Otherwise, me only check date prior to the fix.

		@param correctiveCommits: the bug fixing commit
		"""
		bug_introduced_prior = correctiveCommit.author_date_unix_timestamp
		issue_opened = self.findIssueOpened(correctiveCommit)

		if issue_opened is not None:
			bug_introduced_prior = issue_opened

		correctiveFiles = correctiveCommit.fileschanged.split(",CAS_DELIMITER,")

		for commit in self.allCommits:

			if int(commit.author_date_unix_timestamp) < int(bug_introduced_prior):
				commitFiles = commit.fileschanged.split(",CAS_DELIMITER,")

				for commitFile in commitFiles:

					# This introudced the bug!
					if commitFile in correctiveFiles:
						return commit

		return -1 # Not found

	def markBuggyCommits(self):
		"""
		Finds bug inducing commits based on those that are
		bug fixing. It checks commits prior to this and determines
		it to be bug inducing if it changes the same file in a bug fixing
		commit
		"""

		for correctiveCommit in self.correctiveCommits:
			buggyCommit = self.searchForBuggyCommit(correctiveCommit)
			if buggyCommit is not -1:
				buggyCommit.contains_bug = True
			#else:
				#print("Cound not find the bug inducing commit for: " +
					#	correctiveCommit.commit_message)
