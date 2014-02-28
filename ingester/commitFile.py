"""
A common base class for representing a single commit file
"""

class CommitFile:

	def __init__(self, name, loc, authors, lastchanged):
		self.name = name									# File name
		self.loc = loc										# LOC in file
		self.authors = authors								# Array of authors 
		self.lastchanged = lastchanged						# unix time stamp of when last changed