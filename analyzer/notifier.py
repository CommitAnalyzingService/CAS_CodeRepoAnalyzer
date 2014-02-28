"""
file: notifier.py 
author: Christoffer Rosen <cbr4830@rit.edu>
date: December, 2013
description: Notification system using gmail to notify subscribers that
a repo's analysis has been completed. 
"""

import smtplib
from caslogging import logging

class Notifier:


	def __init__(self, gmail_user, gmail_pwd, repo):
		"""
		Constructor
		"""
		self.gmail_user = gmail_user
		self.gmail_pwd = gmail_pwd
		self.repo = repo
		self.subscribers = []

	def addSubscribers(self, users):
		"""
		Subscribes a list of users to be notified next time, overriding 
		previous subscribers
		@param users: an array containing e-mail address of future subscribers
		"""

		self.subscribers = users

	def notify(self):
		"""
		Notify all subscribers that repo has been analyzed and is ready
		to be viewed
		"""

		FROM = "cas.notifier@gmail.com"
		TO = self.subscribers
		SUBJECT = "Your repository has been analyzed"
		TEXT = "Your analyzed repository is now ready to be viewed at http://kiwi.se.rit.edu/repo/" + self.repo

		# prepare actual message
		message = """\From: %s\nTo: %s\nSubject: %s\n\n%s""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
		
		try:
			server = smtplib.SMTP("smtp.gmail.com", 587)
			server.ehlo()
			server.starttls()
			server.login(self.gmail_user, self.gmail_pwd) 
			server.sendmail(FROM, TO, message)
			server.quit()

			logging.info("Notification sent successfully")

		except:
			logging.error("Failed to send notification")




