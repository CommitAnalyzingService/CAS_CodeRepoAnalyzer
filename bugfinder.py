"""
file: bugfinder.py 
author: Christoffer Rosen <cbr4830@rit.edu>
date: November 2013
description: Identifies buggy commits
"""

from commit import *

class BugFinder: 
	"""
	BugFinder():
	description: Finds commits that are buggy
	"""

	def __init__(self, allCommits, correctiveCommits):
		"""
		Constructor

		@param commits: All commits in ascending order by date
		@param correctiveCommits: All commits which all bug fixing
		"""
		self.allCommits = allCommits
		self.correctiveCommits = correctiveCommits

	def searchForBuggyCommit(self, correctiveCommit):
		"""
		Finds the buggy commit based on the bug fixing commit 
		Helper method for markBuggyCommits.

		@param correctiveCommits: the bug fixing commit
		"""
		correctiveFiles = correctiveCommit.fileschanged.split(",")
		for commit in self.allCommits:

			if commit.author_date_unix_timestamp < correctiveCommit.author_date_unix_timestamp:
				commitFiles = commit.fileschanged.split(",")

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
				# We should probably log it..
		
			