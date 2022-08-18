#!/usr/bin/env python

# Simulated Autopoiesis in Liquid Automata
# To run:
# conda activate pybox2d
# python plot.py

import numpy as np
from time import sleep, time
from auto import Autopoiesis

DELTA = 15
S_POP = 700 # substrate population
SAMPLES = 500 # must be >= W

dataS = []
dataL = []
dataJ = []
t0 = time()
run = 0
RUNS = 6

sampleS = []
sampleL = []
sampleJ = []
sampleDS = []
sampleDL = []
sampleDJ = []

class TCV(Autopoiesis):
    def __init__(self,delta,N):
        super(TCV, self).__init__(N,delta=delta)
        self.step = 0

    def Step(self, settings):
        global t0, plotS, plotL, plotJ, plotX
        super(TCV, self).Step(settings)

        # sample data once per second
        if time()>t0+1:
            t0 = time()
            dataS.append(self.countS)
            dataL.append(self.countL)
            dataJ.append(self.countJ)
            self.step += 1

        elif self.step==SAMPLES:

            s = np.mean(dataS)
            l = np.mean(dataL)
            j = np.mean(dataJ)
            ds = np.mean(np.diff(dataS))
            dl = np.mean(np.diff(dataL))
            dj = np.mean(np.diff(dataJ))

            print("Sample S = {:.4f}".format(s))
            print("Sample L = {:.4f}".format(l))
            print("Sample J = {:.4f}".format(j))
            print("Sample DS = {:.4f}".format(ds))
            print("Sample DL = {:.4f}".format(dl))
            print("Sample DJ = {:.4f}".format(dj))

            sampleS.append(s)
            sampleL.append(l)
            sampleJ.append(j)
            sampleDS.append(ds)
            sampleDL.append(dl)
            sampleDJ.append(dj)

            exit()

# By varying population we are in effect varying the pressure

if __name__ == "__main__":
    pop = S_POP
    while True:
        print("run {}".format(run))
        print("population {}".format(pop))
        dataS = []
        dataL = []
        dataJ = []

        try:
            sleep(5)
            TCV(DELTA,pop).run()

        except SystemExit:
            run += 1
            pop -= 30
            if run>RUNS:
                print("pop.\tS\tL\tJ\tDelta S\tDelta L\tDelta J")
                for i in range(RUNS+1):
                    print("{}\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}".format(S_POP-i*30,sampleS[i],sampleL[i],sampleJ[i],sampleDS[i],sampleDL[i],sampleDJ[i]))
                print("mean\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}".format(np.mean(sampleS[1:]),np.mean(sampleL[1:]),np.mean(sampleJ[1:]),np.mean(sampleDS[1:]),np.mean(sampleDL[1:]),np.mean(sampleDJ[1:])))
                # calculate root mean square for each measure
                rmsdS = np.sqrt(np.mean(np.square([ s - sampleS[0] for s in sampleS[1:] ])))
                rmsdL = np.sqrt(np.mean(np.square([ l - sampleL[0] for l in sampleL[1:] ])))
                rmsdJ = np.sqrt(np.mean(np.square([ j - sampleJ[0] for j in sampleJ[1:] ])))
                rmsdDS =  np.sqrt(np.mean(np.square([ ds - sampleDS[0] for ds in sampleDS[1:] ])))
                rmsdDL =  np.sqrt(np.mean(np.square([ ds - sampleDL[0] for ds in sampleDL[1:] ])))
                rmsdDJ =  np.sqrt(np.mean(np.square([ ds - sampleDJ[0] for ds in sampleDJ[1:] ])))
                print("RMSD\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}".format(rmsdS,rmsdL,rmsdJ,rmsdDS,rmsdDL,rmsdDJ))
                normS = np.max(sampleS[1:]) - np.min(sampleS[1:])
                normL = np.max(sampleL[1:]) - np.min(sampleL[1:])
                normJ = np.max(sampleJ[1:]) - np.min(sampleJ[1:])
                normDS = np.max(sampleDS[1:]) - np.min(sampleDS[1:])
                normDL = np.max(sampleDL[1:]) - np.min(sampleDL[1:])
                normDJ = np.max(sampleDJ[1:]) - np.min(sampleDJ[1:])
                print("NRMSD\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}".format(rmsdS/normS,rmsdL/normL,rmsdJ/normJ,rmsdDS/normDS,rmsdDL/normDL,rmsdDJ/normDJ))
                break