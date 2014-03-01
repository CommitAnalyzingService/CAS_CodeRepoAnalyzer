
class RepositoryMetrics:
  """
  Holds all the metrics values for a repository
  """

  def __init__(self):

    self.ns_buggy = []
    self.ns_nonbuggy = []
    self.nd_buggy = []
    self.nd_nonbuggy = []
    self.nf_buggy = []
    self.nf_nonbuggy = []
    self.entrophy_buggy = []
    self.entrophy_nonbuggy = []
    self.la_buggy = []
    self.la_nonbuggy = []
    self.ld_buggy = []
    self.ld_nonbuggy = []
    self.lt_buggy = []
    self.lt_nonbuggy = []
    self.ndev_buggy = []
    self.ndev_nonbuggy = []
    self.age_buggy = []
    self.age_nonbuggy = []
    self.nuc_buggy = []
    self.nuc_nonbuggy = []
    self.exp_buggy = []
    self.exp_nonbuggy = []
    self.rexp_nonbuggy = []
    self.rexp_buggy = []
    self.sexp_buggy = []
    self.sexp_nonbuggy = []
    self.num_buggy = 0
    self.num_nonbuggy = 0
