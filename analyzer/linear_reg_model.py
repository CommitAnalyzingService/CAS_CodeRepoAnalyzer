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

  def __init__(self, metrics, repo_id):
    self.metrics = metrics
    self.repo_id = repo_id
    self.stats = importr('stats')
    self.base = importr('base')
    self.readcsv = robjects.r['read.csv']
    self.sig_threshold = 0.05
    self.coef = {} # a dict containing glm coefficients
    self.ready = False

  def buildModel(self):
    self._buildDataSet()
    self._getCoefficients()

  def _buildDataSet(self):
    """
    builds the data set to be used for getting the linear regression model.
    saves datasets in the datasets folder as csv files to easily be imported
    or used by R.

    @private
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

  def _getCoefficients(self):
    """
    builds the linear regression model & stores them
    @private
    """
    current_dir = os.path.dirname(__file__)
    dir_of_datasets = current_dir + "/datasets/"

    data = self.readcsv(dir_of_datasets + self.repo_id + ".csv", header=True, sep = ",")
    formula = "is_buggy~ns+nd+nf+entrophy+la+ld+lt+ndev+age+nuc+exp+rexp+sexp"
    fit = self.stats.glm(formula, data=data, family="binomial")
    summary = self.base.summary(fit)

    try:
      self.coef['intercept'] = summary.rx2('coefficients').rx(1)[0]
      self.coef['intercept_sig'] = summary.rx2('coefficients').rx(1,4)[0]
      self.coef['ns'] = summary.rx2('coefficients').rx(2)[0]
      self.coef['ns_sig'] = summary.rx2('coefficients').rx(2,4)[0]
      self.coef['nd'] = summary.rx2('coefficients').rx(3)[0]
      self.coef['nd_sig'] = summary.rx2('coefficients').rx(3,4)[0]
      self.coef['nf'] = summary.rx2('coefficients').rx(4)[0]
      self.coef['nf_sig'] = summary.rx2('coefficients').rx(4,4)[0]
      self.coef['entrophy'] = summary.rx2('coefficients').rx(5)[0]
      self.coef['entrophy_sig'] = summary.rx2('coefficients').rx(5,4)[0]
      self.coef['la'] = summary.rx2('coefficients').rx(6)[0]
      self.coef['la_sig'] = summary.rx2('coefficients').rx(6,4)[0]
      self.coef['ld'] = summary.rx2('coefficients').rx(7)[0]
      self.coef['ld_sig'] = summary.rx2('coefficients').rx(7,4)[0]
      self.coef['lt'] = summary.rx2('coefficients').rx(8)[0]
      self.coef['lt_sig'] = summary.rx2('coefficients').rx(8,4)[0]
      self.coef['ndev'] = summary.rx2('coefficients').rx(9)[0]
      self.coef['ndev_sig'] = summary.rx2('coefficients').rx(9,4)[0]
      self.coef['age'] = summary.rx2('coefficients').rx(10)[0]
      self.coef['age_sig'] = summary.rx2('coefficients').rx(10,4)[0]
      self.coef['nuc'] = summary.rx2('coefficients').rx(11)[0]
      self.coef['nuc_sig'] = summary.rx2('coefficients').rx(11,4)[0]
      self.coef['exp'] = summary.rx2('coefficients').rx(12)[0]
      self.coef['exp_sig'] = summary.rx2('coefficients').rx(12,4)[0]
      self.coef['rexp'] = summary.rx2('coefficients').rx(13)[0]
      self.coef['rexp_sig'] = summary.rx2('coefficients').rx(13,4)[0]
      self.coef['sexp'] = summary.rx2('coefficients').rx(14)[0]
      self.coef['sexp_sig'] = summary.rx2('coefficients').rx(14,4)[0]
      self._storeCoefficients()

    except:
      logging.error("singularity found, skipping coefficients...")

  def _getCoefficientObject(self, coef_name, coef_value):
    """
    returns a JSON object representation of coefficient given
    the name and value. if coefficient significance, true or false
    is given depending on if it meets the significance threshold
    """
    coef_object = ""

    # Is this a real coefficient or a p-value/sig coefficient?
    if "sig" in coef_name:

      if coef_value <= self.sig_threshold:
        coef_object += '"' + str(coef_name) + '":"1'

        # update the coeficient dict, as this is used when
        # calcuating estimated probabilities
        self.coef[coef_name] = 1

      else:
        coef_object += '"' + str(coef_name) + '":"0'

        # update the coeficient dict, as this is used when
        # calcuating estimated probabilities
        self.coef[coef_name] = 0

    else:
      coef_object += '"' + str(coef_name) + '":"' + str(coef_value)

    return coef_object + '",'

  def _storeCoefficients(self):
    """
    stores the glm coefficients in the database
    @private
    """
    coefs = ""
    coefs += '"repo":"' + str(self.repo_id) + '",'

    # iterate through all the values in the dict containing coeficients
    for coef_name, coef_value in self.coef.items():
      coefs += self._getCoefficientObject(coef_name, coef_value)

    # remove the trailing comma
    coefs = coefs[:-1]

    # Insert into the coefficient table
    coefSession = Session()
    allCoef = GlmCoefficients(json.loads('{' + coefs + '}'))

    # Copy to db
    coefSession.merge(allCoef)

    # Write
    coefSession.commit()
    self.ready = True

  def calculateProbCommits(self, commits):
    """
    calcualte the probability of commits to be buggy or not
    using the linear regression model

    estimated probability = 1/[1 + exp(-a - BX)]
    """
    if (self.ready != True):
      return

    for commit in commits:


        coefs =   (commit.ns * self.coef["ns"] * self.coef["ns_sig"]) \
                + (commit.nd * self.coef["nd"] * self.coef["nd_sig"]) \
                + (commit.nf * self.coef["nf"] * self.coef["nf_sig"]) \
                + (commit.entrophy * self.coef["entrophy"] * self.coef["entrophy_sig"]) \
                + (commit.la * self.coef["la"] * self.coef["la_sig"]) \
                + (commit.ld * self.coef["ld"] * self.coef["ld_sig"]) \
                + (commit.lt * self.coef["lt"] * self.coef["lt_sig"]) \
                + (commit.ndev * self.coef["ndev"] * self.coef["ndev_sig"]) \
                + (commit.age * self.coef["age"] * self.coef["age_sig"]) \
                + (commit.nuc * self.coef["nuc"] * self.coef["nuc_sig"]) \
                + (commit.exp * self.coef["exp"] * self.coef["exp_sig"]) \
                + (commit.rexp * self.coef["rexp"] * self.coef["rexp_sig"]) \
                + (commit.sexp * self.coef["sexp"] * self.coef["sexp_sig"])

        try:
          constant = (self.coef["intercept"] * self.coef["intercept_sig"])
          est_probability = 1/(1 + math.exp(-constant-coefs))
          commit.glm_probability = est_probability

        except:
          commit.glm_probability = 0.5
