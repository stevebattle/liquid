#!/usr/bin/env python

# Simulated Autopoiesis in Liquid Automata
# To run:
# conda activate pybox2d
# python plot.py

import pylab as p
import numpy as np
from scipy.stats.stats import pearsonr
from time import time
from auto import Autopoiesis

S_POP = 700 # substrate population
W = 20 # moving average 'window'
SAMPLES = 100 # must be >= W

dataS = []
dataL = []
dataJ = []
dataT = []
t0 = time()

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

class Plot(Autopoiesis):
    def __init__(self,N):
        super(Plot, self).__init__(N)
        self.step = 0

    def Step(self, settings):
        global t0, plotS, plotL, plotJ, plotX
        super(Plot, self).Step(settings)

        # sample data once per second
        if time()>t0+1:
            t0 = time()
            dataS.append(self.countS)
            dataL.append(self.countL)
            dataJ.append(self.countJ)
            dataT.append(self.step)
            self.step += 1
            print(self.step)

        if self.step==SAMPLES:

            print("{0} samples".format(SAMPLES))
            # corrLJ = np.corrcoef(dataL, dataJ)[0,1]
            # print("Correlation coefficient = {0}".format(corrLJ))
            pearLJ, pvalueLJ = pearsonr(dataL, dataJ)
            print("Pearson Correlation coefficient for L,J= {0}".format(pearLJ))
            print("p-value = {0}".format(pvalueLJ))
            if pvalueLJ<0.5:
                print("Significant at 5% level.")
            print()

            pearLS, pvalueLS = pearsonr(dataL, dataS)
            print("Pearson Correlation coefficient for L,S = {0}".format(pearLS))
            print("p-value = {0}".format(pvalueLS))
            if pvalueLS<0.5:
                print("Significant at 5% level.")
            print()



            exit()

if __name__ == "__main__":
    Plot(S_POP).run()