"""
file: gitissuetracker.py 
author: Christoffer Rosen <cbr4830@rit.edu>
date: December, 2013
description: Represents a Github Issue tracker object used 
for getting the dates issues were opened. 

12/12/13: Doesn't currently support private repos
"""

import requests, json, dateutil.parser, time
from caslogging import logging

class GithubIssueTracker:
	"""
	GitIssueTracker()
	Represents a Github Issue Tracker Object
	"""

	owner = None											# Owner of the github repo
	repo = None												# The repo name 
	request_repos = "https://api.github.com/repos"			# Request url to get issue info
	request_auth = "https://api.github.com/authorizations" 	# Request url for auth

	def __init__(self, owner, repo):
		"""
		Constructor
		"""
		self.owner = owner
		self.repo = repo
		self.auth_token = None  
		self.authenticate() # Authenticate our app

	def authenticate(self):
		"""
		authenticate()
		Authenticates this application to github using
		the cas-user git user credentials. This is hopefully temporary!
		"""

		s = requests.Session()
		s.auth = ("cas-user", "riskykiwi1")
		payload = {"scopes": ["repo"]}
		r = s.get(self.request_auth, params=payload)

		if r.headers.get('x-ratelimit-remaining') == '0':
			logging.info("Github quota limit hit -- waiting")

			# Wait up to a hour until we can continue..
			while r.headers.get('x-ratelimit-remaining') == '0':
				time.sleep(600) # Wait 10 minutes and try again
				r = s.get(self.request_auth, params=payload)
				data = r.json()

		data = r.json()[0]

		if r.status_code >= 400:
			msg = data.get('message')
			logging.error("Failed to authenticate issue tracker: \n" +msg)
			return # Exit
		else:
			self.auth_token = data.get("token")
			requests_left = r.headers.get('x-ratelimit-remaining')
			logging.info("Analyzer has " + requests_left + " issue tracker calls left this hour")


	def getDateOpened(self, issueNumber):
		"""
		getDateOpened()
		Gets the date the issue number was opened in unix time
		If issue cannot be found for whichever reason, returns null.
		"""
		header = {'Authorization': 'token ' + self.auth_token}
		r = requests.get(self.request_repos + "/" + self.owner + "/" + 
				self.repo + "/issues/" + issueNumber, headers=header)

		data = r.json()

		# If forbidden
		if r.status_code == 403:

			# Check the api quota 
			if r.headers.get('x-ratelimit-remaining') == '0':
				logging.info("Github quota limit hit -- waiting")

				# Wait up to a hour until we can continue..
				while r.headers.get('x-ratelimit-remaining') == '0':
					time.sleep(600) # Wait 10 minutes and try again
					r = requests.get(self.request_repos + "/" + self.owner + "/" + 
						self.repo + "/issues/" + issueNumber, headers=header)
					data = r.json()

		# Check for other error codes
		elif r.status_code >= 400:
			msg = data.get('message')
			logging.error("ISSUE TRACKER FAILURE: \n" + msg)
			return None
		else:
			try:
				date = (dateutil.parser.parse(data.get('created_at'))).timestamp()
				return date
			except:
				logging.error("ISSUE TRACKER FAILURE: Could not get created_at from github issues API")
				return None
