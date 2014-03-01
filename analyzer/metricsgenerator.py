"""
file: metricsgenerator.py
author: Christoffer Rosen <cbr4830@rit.edu>
date: Novemember, 2013
description: Generats the metrics (medians) for each metric for the
non-buggy and buggy commits and outputs them into the metrics table
"""

from analyzer.repositorymetrics import * # metrics abstraction; holds all metric values for commits
from analyzer.medianmodel import * # builds the median model
from analyzer.linear_reg_model import *
import json

class MetricsGenerator:
	"""
	MetricsGenerator()
	Generate the metrics for buggy & non-buggy commits
	"""
	commits = None

	def __init__(self, repo_id, commits):
		"""
		Constructor
		"""
		self.repo_id = repo_id
		self.commits = commits

		# metrics
		self.metrics = RepositoryMetrics()

	def buildAllModels(self):
		"""
		builds all models and stores them in the metrics table
		"""
		self.fetchAllMetrics() # first get all metrics

		median_model = MedianModel(self.metrics, self.repo_id)
		linear_reg_model = LinearRegressionModel(self.metrics, self.repo_id)

		median_model.buildModel()
		linear_reg_model.buildModel()

	def fetchAllMetrics(self):
		"""
		fetchAllMetrics()
		Iterate through each commit storing each individual's metrics into the metrics object,
		to hold all metrics information necessary to build models.
		@private
		"""
		for commit in self.commits:

			# Exclude merge commits where no lines of code where changed
			if commit.classification == "Merge" and commit.la == 0 and commit.ld == 0:
				continue

			else:

				if commit.contains_bug == True:
					self.metrics.ns_buggy.append(commit.ns)
					self.metrics.nd_buggy.append(commit.nd)
					self.metrics.nf_buggy.append(commit.nf)
					self.metrics.entrophy_buggy.append(commit.entrophy)
					self.metrics.la_buggy.append(commit.la)
					self.metrics.ld_buggy.append(commit.ld)
					self.metrics.lt_buggy.append(commit.lt)
					self.metrics.ndev_buggy.append(commit.ndev)
					self.metrics.age_buggy.append(commit.age)
					self.metrics.nuc_buggy.append(commit.nuc)
					self.metrics.exp_buggy.append(commit.exp)
					self.metrics.rexp_buggy.append(commit.rexp)
					self.metrics.sexp_buggy.append(commit.sexp)
					self.metrics.num_buggy += 1

				else:
					self.metrics.ns_nonbuggy.append(commit.ns)
					self.metrics.nd_nonbuggy.append(commit.nd)
					self.metrics.nf_nonbuggy.append(commit.nf)
					self.metrics.entrophy_nonbuggy.append(commit.entrophy)
					self.metrics.la_nonbuggy.append(commit.la)
					self.metrics.ld_nonbuggy.append(commit.ld)
					self.metrics.lt_nonbuggy.append(commit.lt)
					self.metrics.ndev_nonbuggy.append(commit.ndev)
					self.metrics.age_nonbuggy.append(commit.age)
					self.metrics.nuc_nonbuggy.append(commit.nuc)
					self.metrics.exp_nonbuggy.append(commit.exp)
					self.metrics.rexp_nonbuggy.append(commit.rexp)
					self.metrics.sexp_nonbuggy.append(commit.sexp)
					self.metrics.num_nonbuggy += 1
