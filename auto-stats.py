#!/usr/bin/env python

# Simulated Autopoiesis in Liquid Automata
# To run:
# conda activate pybox2d
# python plot.py

import pylab as p
import numpy as np
from scipy.stats.stats import pearsonr
from time import time
from Box2D.examples.framework import main
from auto import Autopoiesis

SAMPLES = 100 # must be >= W

dataS = []
dataL = []
dataJ = []
dataT = []
t0 = time()
run = 0

class Stats(Autopoiesis):
    def __init__(self):
        super(Stats, self).__init__()
        self.step = 0

    def Step(self, settings):
        global t0, plotS, plotL, plotJ, plotX
        super(Stats, self).Step(settings)

        # sample data once per second
        if time()>t0+1:
            t0 = time()
            dataS.append(self.countS)
            dataL.append(self.countL)
            dataJ.append(self.countJ)
            dataT.append(self.step)
            self.step += 1

        if self.step==SAMPLES and run==0:

            print("{0} samples".format(SAMPLES))
            print("mean S = {0}".format(np.mean(dataS)))
            print("mean L = {0}".format(np.mean(dataL)))
            print("mean J = {0}".format(np.mean(dataJ)))

            # corrLJ = np.corrcoef(dataL, dataJ)[0,1]
            # print("Correlation coefficient = {0}".format(corrLJ))
            pearLJ, pvalueLJ = pearsonr(dataL, dataJ)
            print("Pearson Correlation coefficient for L,J= {0}".format(pearLJ))
            print("p-value = {0}".format(pvalueLJ))
            if pvalueLJ<0.01:
                print("Significant at 1% level.")
            print()

            pearLS, pvalueLS = pearsonr(dataL, dataS)
            print("Pearson Correlation coefficient for L,S = {0}".format(pearLS))
            print("p-value = {0}".format(pvalueLS))
            if pvalueLS<0.01:
                print("Significant at 1% level.")
            print()

            exit()


if __name__ == "__main__":
    main(Stats).run()
