"""
file: gitissuetracker.py 
author: Christoffer Rosen <cbr4830@rit.edu>
date: December, 2013
description: Represents a Github Issue tracker object used 
for getting the dates issues were opened. 

12/12/13: Doesn't currently support private repos/ authentication
"""

import requests, json, dateutil.parser

class GithubIssueTracker:
	"""
	GitIssueTracker()
	Represents a Github Issue Tracker Object
	"""

	owner = None									# Owner of the github repo
	repo = None										# The repo name 
	request_url = "https://api.github.com/repos"	# Request url to get issue info

	def __init__(self, owner, repo):
		"""
		Constructor
		"""
		self.owner = owner
		self.repo = repo

	def getDateOpened(self, issueNumber):
		"""
		getDateOpened()
		Gets the date the issue number was opened in unix time
		If issue cannot be found, returns null.
		"""

		try:
			r = requests.get(self.request_url + "/" + self.owner + "/" + 
				self.repo + "/issues/" + issueNumber)
			data = r.json()
			date = dateutil.parser.parse(data.get('created_at')).timestamp()

		except:
			date = None

		return date

