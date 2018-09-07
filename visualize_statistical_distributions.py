# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
    
from scipy.stats import norm, t, chi2

samplesize = 4
truemean = np.pi
truevariance = np.e

mean = []
variance = []

for i in range(10000):
    sample = np.random.normal(truemean, truevariance**.5, samplesize)

    mean.append(sample.mean())
    variance.append(sample.var(ddof=1))

mean = np.array(mean)
variance = np.array(variance)


fig, ax = plt.subplots()
z = (mean - truemean)/(truevariance/samplesize)**.5
y, x, patches = ax.hist(z, bins=100, density=True)
ax.plot(x, norm.pdf(x))
ax.set_title('Normal distribution')

fig, ax = plt.subplots()
z = (mean - truemean)/(variance/samplesize)**.5
y, x, patches = ax.hist(z, bins=100, density=True)
ax.plot(x, t.pdf(x, df=samplesize - 1))
ax.set_title('Student\'s t-distribution')

fig, ax = plt.subplots()
z = variance*(samplesize - 1)/truevariance
y, x, patches = ax.hist(z, bins=100, density=True)
ax.plot(x, chi2.pdf(x, df=samplesize - 1))
ax.set_title('Chi-squared distribution')

plt.show()

