import csv
import os
import rpy2.robjects as robjects # R integration

class LinearRegressionModel:
  """
  builds the linear regression model
  """

  def __init__(self,metrics,repo_id):
    self.metrics = metrics
    self.repo_id = repo_id

    # R functions to be used
    self.glm = robjects.r['glm']
    self.readcsv = robjects.r['read.csv']
    self.coef = robjects.r['coef'] # get coefficients

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
    builds the linear regression model
    @private
    """
    current_dir = os.path.dirname(__file__)
    dir_of_datasets = current_dir + "/datasets/"

    data = self.readcsv(dir_of_datasets + self.repo_id + ".csv", header=True, sep = ",")
    formula = "is_buggy~ns+nd+nf+entrophy+la+ld+lt+ndev+age+nuc+exp+rexp+sexp"
    glm_model = self.glm(formula, data=data, family="binomial")
    coef = self.coef(glm_model)
 
