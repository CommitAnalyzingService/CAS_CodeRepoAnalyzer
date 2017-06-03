import csv
import os
import rpy2.robjects as robjects # R integration
from rpy2.robjects.packages import importr # import the importr package from R
from orm.glmcoefficients import * # to store the glm coefficients
from db import *	# postgresql db information
import math
from caslogging import logging

class LinearRegressionModel:
  """
  builds the generalized linear regression model (GLM).
  all coefficients stored in the database under the glm_coefficients table
  probability: intercept + sum([metric_coefficient] * metric)
  """

  def __init__(self, metrics, repo_id, testingCommits):
    """
    @metrics - this is the list of metrics from the TRAINING data set.
    @repo_id - the repository repo_id
    @testingCommits - this is commits from the TESTING data set
    """
    self.metrics = metrics
    self.repo_id = repo_id
    self.stats = importr('stats', robject_translations={'format_perc': '_format_perc'})
    self.base = importr('base')
    self.readcsv = robjects.r['read.csv']
    self.sig_threshold = 0.05
    self.data = None 
    self.commits = testingCommits

  def buildModel(self):
    """
    Builds the GLM model, stores the coefficients, and calculates the probability based on model that a commit
    will introduce a bug.
    """
    self._buildDataSet()
    self._buildModelIncrementally()

  def _buildDataSet(self):
    """
    builds the data set to be used for getting the linear regression model.
    saves datasets in the datasets folder as csv files to easily be imported
    or used by R.
    """

    # to write dataset file in this directory (git ignored!)
    current_dir = os.path.dirname(__file__)
    dir_of_datasets = current_dir + "/datasets/"
    num_buggy = getattr(self.metrics, "num_buggy")
    num_nonbuggy = getattr(self.metrics, "num_nonbuggy")

    with open(dir_of_datasets + self.repo_id + ".csv", "w") as file:
      csv_writer = csv.writer(file, dialect="excel")

      # write the columns
      csv_writer.writerow(["ns","nd","nf","entrophy","la","ld","lt","ndev","age","nuc","exp","rexp","sexp","is_buggy"])

      # write the relevant data - start w/ the buggy data first
      for buggy_index in range(0,num_buggy):
        ns = self.metrics.ns_buggy[buggy_index]
        nd = self.metrics.nd_buggy[buggy_index]
        nf = self.metrics.nf_buggy[buggy_index]
        entrophy = self.metrics.entrophy_buggy[buggy_index]
        la = self.metrics.la_buggy[buggy_index]
        ld = self.metrics.ld_buggy[buggy_index]
        lt = self.metrics.lt_buggy[buggy_index]
        ndev = self.metrics.ndev_buggy[buggy_index]
        age = self.metrics.age_buggy[buggy_index]
        nuc = self.metrics.nuc_buggy[buggy_index]
        exp = self.metrics.exp_buggy[buggy_index]
        rexp = self.metrics.rexp_buggy[buggy_index]
        sexp = self.metrics.sexp_buggy[buggy_index]
        csv_writer.writerow([ns,nd,nf,entrophy,la,ld,lt,ndev,age,nuc,exp,rexp,sexp,True])
      # end buggy data

      # write the non buggy data
      for nonbuggy_index in range(0,num_nonbuggy):
        ns = self.metrics.ns_nonbuggy[nonbuggy_index]
        nd = self.metrics.nd_nonbuggy[nonbuggy_index]
        nf = self.metrics.nf_nonbuggy[nonbuggy_index]
        entrophy = self.metrics.entrophy_nonbuggy[nonbuggy_index]
        la = self.metrics.la_nonbuggy[nonbuggy_index]
        ld = self.metrics.ld_nonbuggy[nonbuggy_index]
        lt = self.metrics.lt_nonbuggy[nonbuggy_index]
        ndev = self.metrics.ndev_nonbuggy[nonbuggy_index]
        age = self.metrics.age_nonbuggy[nonbuggy_index]
        nuc = self.metrics.nuc_nonbuggy[nonbuggy_index]
        exp = self.metrics.exp_nonbuggy[nonbuggy_index]
        rexp = self.metrics.rexp_nonbuggy[nonbuggy_index]
        sexp = self.metrics.sexp_nonbuggy[nonbuggy_index]
        csv_writer.writerow([ns,nd,nf,entrophy,la,ld,lt,ndev,age,nuc,exp,rexp,sexp,False])
      # end non buggy data
    # end file

  def _isMetricSignificant(self, formula_metrics, metric):
    """
    Checks if adding a metric to the already significant metrics in formula_metrics in a GLM model is significant. If significant,
    and doesn't cause any previous metric in formula_metrics to become non significant, we return true. Otherwise, false.

    Note: The p-value is always given in the 4th column of the summary matrix!
    """
    sig_column = 4

    # Case 1: no existing metrics in the formula
    if len(formula_metrics) == 0:
      formula = "is_buggy~" + metric
      fit = self.stats.glm(formula, data=self.data, family="binomial")
      summary = self.base.summary(fit)
      # Note - first row is the intercept information so we start at second row!

      try:
        metric_sig = summary.rx2('coefficients').rx(2,sig_column)[0] # Second row, 4th column of the summary matrix.
        if metric_sig <= self.sig_threshold:
          return True
        else:
          return False

      except:
        # If we have two metrics that are perfectly collinear it will not build the model with the metrics
        # and we will get an exception when trying to find the significance of *all values*. Indeed, do not add
        # this value to the model!
        return False

    # Case 2: existing metrics in the formula    
    else:
      num_metrics = len(formula_metrics)+2 # plus one for the new metric we are adding and one for intercept
      formula = "is_buggy~" + "+".join(formula_metrics) + "+" + metric
      fit = self.stats.glm(formula, data=self.data, family="binomial")
      summary = self.base.summary(fit)

      # If any metric is now not significant, than we should not have added this metric to the formula
      # There are (intercept) + num_metrics rows in the matrix to check - starts at second row skipping intercept
      try: 
        for row in range(2,num_metrics+1):
          metric_sig = summary.rx2('coefficients').rx(row,sig_column)[0]
          if metric_sig > self.sig_threshold:
            return False
        return True # old metrics added to model ARE significant still as well as the new one being tested

      except:
        # If we have two metrics that are perfectly collinear it will not build the model with the metrics
        # and we will get an exception when trying to find the significance of *all values*. Indeed, do not add
        # this value to the model!
        return False

  def _buildModelIncrementally(self):
    """
    Builds the linear regression model incrementally. It adds one metric at the time to the formula and keeps it
    if it is significant. However, if adding it to the model casuses any other metric already added to the formula
    to become not significant anymore, we do add it to the glm forumla.
    """

    metrics_list = ["la","ld","lt","ns","nd","nf","ndev","age","nuc","exp","rexp","sexp","entrophy"]
    formula_metrics = []
    current_dir = os.path.dirname(__file__)
    dir_of_datasets = current_dir + "/datasets/"
    self.data = self.readcsv(dir_of_datasets + self.repo_id + ".csv", header=True, sep = ",")

    for metric in metrics_list:
      if self._isMetricSignificant(formula_metrics, metric):
        formula_metrics.append(metric)

    # Store coefficients of our model w/ formula containing only the sig coefficients
    self._storeCoefficients(formula_metrics)

    # Calculate all probability for each commit to introduce a bug
    self.calculateCommitRiskyness(self.commits, formula_metrics)


  def _getCoefficients(self, formula_coefs):
    """
    Builds a GLM model with a formula based on the passed in coefficients and retuns a dictionary containing each
    coefficient with its value.
    """
    coef_dict = {} # a dict containing glm coefficients {name -> value}
    formula = "is_buggy~" + "+".join(formula_coefs)
    fit = self.stats.glm(formula, data=self.data, family="binomial")

    for coef in formula_coefs:
      coef_dict[coef] = fit.rx2('coefficients').rx2(coef)[0]

    return coef_dict

  def _getInterceptValue(self, coefs):
    """
    Return the Intercept value of a GLM model and the p-value
    Assumes that model can be built!
    """
    formula = "is_buggy~" + "+".join(coefs)
    fit = self.stats.glm(formula, data=self.data, family="binomial")
    summary = self.base.summary(fit)
    return summary.rx2('coefficients').rx(1)[0], summary.rx2('coefficients').rx(1,4)[0]

  def _getCoefficientObject(self, coef_name, coef_value):
    """
    returns a JSON object representation of coefficient given the name and value. if coefficient significance, true or false
    is given depending on if it meets the significance threshold
    """
    coef_object = ""
    coef_object += '"' + str(coef_name) + '":"' + str(coef_value)
    return coef_object + '",'

  def _storeCoefficients(self, coefficient_names):
    """
    stores the glm coefficients in the database
    """
    # We are making this into JSON to simply store it in the database.
    coefs = ""
    coefs += '"repo":"' + str(self.repo_id) + '",'

    # 2 Cases: where there are NO significant coefficients and the revese case.
    if len(coefficient_names) == 0:
      coefficient_dict = {}
    else:
      coefficient_dict = self._getCoefficients(coefficient_names)

      # get the constant (aka intercept value)
      intercept_value, intercept_pvalue = self._getInterceptValue(coefficient_names)
      if intercept_pvalue <= self.sig_threshold:
        intercept_sig = 1
      else:
        intercept_sig = 0

      coefs += self._getCoefficientObject("intercept", intercept_value)
      coefs += self._getCoefficientObject("intercept_sig", intercept_sig)

    # Keep track of all and the subset of all that are significant as we need to record everything to the db
    sig_coefs = [] 
    all_coefs = ["ns", "nd", "nf", "entrophy", "la", "ld", "lt", "ndev", "age", "nuc", "exp", "rexp", "sexp"]

    # iterate through all the values in the dict containing coeficients
    for coef_name, coef_value in coefficient_dict.items():
      coefs += self._getCoefficientObject(coef_name, coef_value)
      coefs += self._getCoefficientObject(coef_name + "_sig", 1) # keep track more easily which are statistically significant in db
      sig_coefs.append(coef_name)

    # append the non significant coefficents as -1 and not significant
    for c in all_coefs:
      if c not in sig_coefs:
        coefs += self._getCoefficientObject(c, -1) 
        coefs += self._getCoefficientObject(c + "_sig", 0)

    # remove the trailing comma
    coefs = coefs[:-1]

    # Insert into the coefficient table
    coefSession = Session()
    allCoef = GlmCoefficients(json.loads('{' + coefs + '}'))

    # Copy to db
    coefSession.merge(allCoef)

    # Write
    coefSession.commit()
    coefSession.close()

  def calculateCommitRiskyness(self, commits, coefficient_names):
    """
    calcualte the probability of commits to be buggy or not
    using the linear regression model

    estimated probability = 1/[1 + exp(-a - BX)]
    """
    # 2 cases: model cannot possibly be build if no signficant coefficients available
    # in this case, we just insert -1 for the probability to indicate no glm prediction possible

    if len(coefficient_names) == 0:
      coefficient_dict = {}
      model_available = False
    else:
      coefficient_dict = self._getCoefficients(coefficient_names)
      model_available = True
      intercept_value, intercept_pvalue = self._getInterceptValue(coefficient_names)

    for commit in commits:

      if model_available == False:
        commit.glm_probability = -1
      else:
        coefs_sum = 0
        for coef_name, coef_value in coefficient_dict.items():
          coefs_sum += (coef_value * getattr(commit, coef_name))

        try:
          riskyness = 1/(1+ math.exp(-intercept_value-coefs_sum))
        except OverflowError:
          logging.error("Overflow error for repo " + self.repo_id)
          logging.error("Calculating riskyness for " + commit.commit_hash)
          logging.error("Sum of coefficients: " + str(coefs_sum))
          logging.error("Coeffiecents: " + str(coefficient_dict))
          riskyness = 0.01

        commit.glm_probability = riskyness