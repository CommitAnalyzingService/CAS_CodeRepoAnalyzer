"""
file: metricsgenerator.py 
author: Christoffer Rosen <cbr4830@rit.edu>
date: Novemember, 2013
description: Generats the metrics (medians) for each metric for the
non-buggy and buggy commits and outputs them into the metrics table
"""

import rpy2.robjects as robjects
from db import *
from orm.metrics import *
import json

class MetricsGenerator:
	"""
	MetricsGenerator()
	Generate the metrics for buggy & non-buggy commits
	"""
	commits = None

	# Lists of values
	ns_buggy = []
	ns_nonbuggy = []
	nd_buggy = []
	nd_nonbuggy = []
	nf_buggy = []
	nf_nonbuggy = []
	entrophy_buggy = []
	entrophy_nonbuggy = []
	la_buggy = []
	la_nonbuggy = []
	ld_buggy = []
	ld_nonbuggy = []
	lt_buggy = []
	lt_nonbuggy = []
	ndev_buggy = []
	ndev_nonbuggy = []
	age_buggy = []
	age_nonbuggy = []
	nuc_buggy = []
	nuc_nonbuggy = []
	exp_buggy = []
	exp_nonbuggy = []
	rexp_nonbuggy = []
	rexp_buggy = []
	sexp_buggy = []
	sexp_nonbuggy = []



	def __init__(self, repo_id, commits):
		"""
		Constructor
		"""
		self.repo_id = repo_id
		self.commits = commits

		# R functions to be used
		self.medianFn = robjects.r['median']
		self.wilcoxFn = robjects.r['wilcox.test']

		# A p-value
		self.psig = 0.0

	def generateMetrics(self):
		"""
		Generate the metrics and output them into the metrics table
		"""
		self.buildMetricsLists()
		self.calculateMedians()

	def buildMetricsLists(self):
		"""
		buildMetricsLists()
		Iterate through each commit storing each individual's metrics into appropriate list 
		dependingon if it contains a bug or not
		"""
		for commit in self.commits:
			
			if commit.contains_bug == True:
				self.ns_buggy.append(commit.ns)
				self.nd_buggy.append(commit.nd)
				self.nf_buggy.append(commit.nf)
				self.entrophy_buggy.append(commit.entrophy)
				self.la_buggy.append(commit.la)
				self.ld_buggy.append(commit.ld)
				self.lt_buggy.append(commit.lt)
				self.ndev_buggy.append(commit.ndev)
				self.age_buggy.append(commit.age)
				self.nuc_buggy.append(commit.nuc)
				self.exp_buggy.append(commit.exp)
				self.rexp_buggy.append(commit.rexp)
				self.sexp_buggy.append(commit.sexp)

			else:
				self.ns_nonbuggy.append(commit.ns)
				self.nd_nonbuggy.append(commit.nd)
				self.nf_nonbuggy.append(commit.nf)
				self.entrophy_nonbuggy.append(commit.entrophy)
				self.la_nonbuggy.append(commit.la)
				self.ld_nonbuggy.append(commit.ld)
				self.lt_nonbuggy.append(commit.lt)
				self.ndev_nonbuggy.append(commit.ndev)
				self.age_nonbuggy.append(commit.age)
				self.nuc_nonbuggy.append(commit.nuc)
				self.exp_nonbuggy.append(commit.exp)
				self.rexp_nonbuggy.append(commit.rexp)
				self.sexp_nonbuggy.append(commit.sexp)

	def getMedian(self,metric):
		"""
		Helper function for the method calculateMedians.
		Takes in a metric and returns a string property of the results
		"""
		median_props = ""

		try:
			# R functions to be used
			medianFn = robjects.r['median']
			wilcoxFn = robjects.r['wilcox.test']

			metric_buggy = getattr(self, metric + "_buggy")
			metric_nonbuggy = getattr(self, metric + "_nonbuggy")

			# First check p-values, if signficant then calculate median
			pvalue = self.wilcoxFn(robjects.FloatVector(metric_buggy), robjects.FloatVector(metric_nonbuggy))[2][0]
			if pvalue >= self.psig:
				buggy_median = self.medianFn(robjects.FloatVector(metric_buggy))
				nonbuggy_median = self.medianFn(robjects.FloatVector(metric_nonbuggy))
				median_props += '"' + metric + 'buggy":"' + str(buggy_median[0]) + '", '
				median_props += '"' + metric + 'nonbuggy":"' + str(nonbuggy_median[0]) + '", '
			else:
				median_props += '"' + metric + 'buggy":"-1", '
				median_props += '"' + metric + 'nonbuggy":"-1", '

		except:
			print("Skipping metric: " + metric + 
				". Please make sure you have run the latest CAS_Reader")

		return median_props

	def calculateMedians(self):
		"""
		Using R through the rpy2 module, generate the medians of each metrics
		lists. If it passes the wilcox test (statistically sig), put it into 
		the metrics table. Otherwise inserts a -1.
		"""

		# Metric objects represents the metrics as a dictionary
		metricObject = '"repo":"' + self.repo_id + '", '

		metricObject += self.getMedian("ns")
		metricObject += self.getMedian("nd")
		metricObject += self.getMedian("nf")
		metricObject += self.getMedian("entrophy")
		metricObject += self.getMedian("la")
		metricObject += self.getMedian("ld")
		metricObject += self.getMedian("lt")
		metricObject += self.getMedian("ndev")
		metricObject += self.getMedian("age")
		metricObject += self.getMedian("nuc")
		metricObject += self.getMedian("exp")
		metricObject += self.getMedian("rexp")
		metricObject += self.getMedian("sexp")

		# Remove trailing comma
		metricObject = metricObject[:-2]

		# Put into the metrics table
		metricsSession = Session()
		metrics = Metrics(json.loads('{' + metricObject + '}'))

		# Copy state of metrics object to db
		metricsSession.merge(metrics)
		
		# Write the metrics changes to the database
		metricsSession.commit()

		







