import csv # csv module for reading in comma-seperated files

class Category():
	""" 
	represents a category used to categorize commits.
	"""

	associatedWords = [] # all words associated w/ this category
	category_name = None # name of category

	def __init__(self, fileLocation, name):
		""" 
		constructor
		reads in all associated words w/ this category from specified 
		file location
		"""
		self.category_name = name
		self.associatedWords = [] # reset the instance so that class name is visible to self reference
		self.readInAssociatedWords(fileLocation)

	def readInAssociatedWords(self, fileLocation):
		""" 
		reads in all associated words w/ this category
		"""
		with open(fileLocation, 'rt') as csvfile:
			wordreader = csv.reader(csvfile, delimiter=',', quotechar='|')
			for row in wordreader:
				for word in row:
					self.associatedWords.append(word)

	def belongs(self, commit_msg):
		"""
		checks if a commit belongs to this category by analyzing
		its commit message.
		@return boolean
		"""
		commit_msg = commit_msg.lower().split(" ") # to array

		# need to go beyond list contains i.e. fixed = fix
		for word in commit_msg:
			for assoc_word in self.associatedWords:
				if assoc_word in word:
					return True

		# No associated words found!
		return False

	def getName(self):
		""" 
		returns the name of the category
		"""
		return self.category_name



