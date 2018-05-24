# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import scipy.stats

def mcnemar_midp(b, c):
    """Compute McNemar's test using the "mid-p" variant suggested by:

    M.W. Fagerland, S. Lydersen, P. Laake. 2013. The McNemar test for binary
    matched-pairs data: Mid-p and asymptotic are better than exact conditional. BMC
    Medical Research Methodology 13: 91.

    `b` is the number of observations correctly labeled by the first---but not
    the second---system; `c` is the number of observations correctly labeled by the
    second---but not the first---system.

    Copied from https://gist.github.com/kylebgorman/c8b3fb31c1552ecbaafb
    """
    n = b + c
    x = min(b, c)
    dist = scipy.stats.binom(n, .5)
    p = 2. * dist.cdf(x)
    midp = p - dist.pmf(x)
    return midp

