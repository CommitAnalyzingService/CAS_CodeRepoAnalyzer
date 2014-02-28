from classifier.category import *
import os 

class Classifier():
	"""
	Classifier classifies commit messages into their appropriate
	category. ALso defines the categories to be used.
	"""

	categories = [] # array of possible commit categories

	def __init__(self):
		"""
		constructor
		create all categories which commits can be categorized in.
		"""

		# Get directory of the csv files of associated words for categories
		current_dir = os.path.dirname(__file__)
		dir_of_cats = current_dir + '/Categories'

		# Create the categories - takes in the location of the csv that defines associated words
		#for the category & classification name
		merge = Category(dir_of_cats + "/merge.csv", "Merge")
		corrective = Category(dir_of_cats + "/corrective.csv", "Corrective")
		feature_addition = Category(dir_of_cats + "/feature_addition.csv", "Feature Addition")
		non_functional = Category(dir_of_cats + "/non_functional.csv", "Non Functional")
		perfective = Category(dir_of_cats + "/perfective.csv", "Perfective")
		perventive = Category(dir_of_cats + "/preventative.csv", "Preventative")

		# add to list of categories
		self.categories.extend([merge, corrective,feature_addition,non_functional,perfective,perventive])

	def categorize(self, commit_msg):
		"""
		returns the category of a commit_msg
		"""
		category_found = False

		# See if commmit message belongs to any category
		for category in self.categories:
			if category.belongs(commit_msg):
				return category.getName()

		# doesn't classify to any of the above
		return "None"

