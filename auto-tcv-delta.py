#!/usr/bin/env python

# Simulated Autopoiesis in Liquid Automata
# To run:
# conda activate pybox2d
# python plot.py

from csv import list_dialects
import numpy as np
from time import sleep, time
from auto import Autopoiesis

SAMPLES = 50 # must be >= W

dataS = []
dataL = []
dataJ = []
t0 = time()

class TCV(Autopoiesis):
    def __init__(self):
        super(TCV, self).__init__()
        self.step = 0

    def Step(self, settings):
        global t0, plotS, plotL, plotJ, plotX, prevS
        super(TCV, self).Step(settings)

        # sample data once every ten seconds
        if time()>t0+10:
            t0 = time()
            dataS.append(self.countS)
            dataL.append(self.countL)
            dataJ.append(self.countJ)
            self.step += 1
            print("{} {} {} {} {}".format(self.step,self.delta,self.countS,self.countL,self.countJ))
            self.delta += 0.25


        elif self.step==SAMPLES:

            # calculate root mean square for each measure
            rmsS = np.sqrt(np.mean(np.square([dataS[i]-dataS[0] for i in range(1,SAMPLES)])))
            rmsL = np.sqrt(np.mean(np.square([dataL[i]-dataL[0] for i in range(1,SAMPLES)])))
            rmsJ = np.sqrt(np.mean(np.square([dataJ[i]-dataJ[0] for i in range(1,SAMPLES)])))
            print("{:.4f} {:.4f} {:.4f}".format(rmsS,rmsL,rmsJ))

            nrmsS = rmsS / np.mean(dataS[1:])
            nrmsL = rmsL / np.mean(dataL[1:])
            nrmsJ = rmsJ / np.mean(dataJ[1:])
            print("{:.4f} {:.4f} {:.4f}".format(nrmsS,nrmsL,nrmsJ))

            nrmsS = rmsS / (np.max(dataS[1:]) - np.min(dataS[1:]))
            nrmsL = rmsL / (np.max(dataL[1:]) - np.min(dataL[1:]))
            nrmsJ = rmsJ / (np.max(dataJ[1:]) - np.min(dataJ[1:]))
            print("{:.4f} {:.4f} {:.4f}".format(nrmsS,nrmsL,nrmsJ))

            print()
            # calculate root mean square of difference lists
            rmsS = np.sqrt(np.mean(np.square(np.diff(dataS))))
            rmsL = np.sqrt(np.mean(np.square(np.diff(dataL))))
            rmsJ = np.sqrt(np.mean(np.square(np.diff(dataJ))))
            print("{:.4f} {:.4f} {:.4f}".format(rmsS,rmsL,rmsJ))

            nrmsS = rmsS / (np.max(np.diff(dataS) - np.min(np.diff(dataS))))
            nrmsL = rmsL / (np.max(np.diff(dataL) - np.min(np.diff(dataL))))
            nrmsJ = rmsJ / (np.max(np.diff(dataJ) - np.min(np.diff(dataJ))))
            print("{:.4f} {:.4f} {:.4f}".format(nrmsS,nrmsL,nrmsJ))

            exit()

# By varying delta we are in effect varying the temperature

if __name__ == "__main__":
    dataS = []
    dataL = []
    dataJ = []
    TCV().run()
