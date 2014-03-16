import rpy2.robjects as robjects # R integration to python
from analyzer.repositorymetrics import * # metrics abstraction; holds all metric values for commits
from db import *	# postgresql db information
from orm.metrics import *	# orm metrics table

class MedianModel:
  """
  Builds the median model, which saves to the metrics table the
  median values for each buggy and non buggy metric for a specific
  repository
  """

  def __init__(self, metrics, repo_id):
    """
    constructor
    @metrics : object holding all metrics value for the repository
               model is being built for.
    """
    self.metrics = metrics
    self.repo_id = repo_id

    # A p-value for wilcox test
    self.psig = 0.05

    # R functions to be used
    self.medianFn = robjects.r['median']
    self.wilcoxFn = robjects.r['wilcox.test']

  def buildModel(self):
    """
    builds the model
    """
    self.calculateMedians()

  def getMedian(self,metric):
    """
    Helper function for the method calculateMedians.
    Takes in a metric and returns a string property of the results
    @private
    """
    median_props = ""

    try:
      # R functions to be used
      medianFn = robjects.r['median']
      wilcoxFn = robjects.r['wilcox.test']

      metric_buggy = getattr(self.metrics, metric + "_buggy")
      metric_nonbuggy = getattr(self.metrics, metric + "_nonbuggy")

      # First check p-values, if signficant then calculate median
      pvalue = self.wilcoxFn(robjects.FloatVector(metric_buggy), robjects.FloatVector(metric_nonbuggy))[2][0]
      buggy_median = self.medianFn(robjects.FloatVector(metric_buggy))
      nonbuggy_median = self.medianFn(robjects.FloatVector(metric_nonbuggy))
      median_props += '"' + metric + 'buggy":"' + str(buggy_median[0]) + '", '
      median_props += '"' + metric + 'nonbuggy":"' + str(nonbuggy_median[0]) + '", '

      if pvalue <= self.psig:
        median_props += '"' + metric + '_sig":"1", '
      else:
        median_props += '"' + metric + '_sig":"0", '

    except:
      print("Skipping metric: " + metric +
        ". Please make sure you have run the latest CAS_Reader")

    return median_props


  def calculateMedians(self):
    """
    Using R through the rpy2 module, generate the medians of each metrics
    lists. If it passes the wilcox test (statistically sig), put it into
    the metrics table. Otherwise, inserts a -1.
    @private
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
