#!/usr/bin/env python

# Simulated Autopoiesis in Liquid Automata
# To run:
# conda activate pybox2d
# python auto-phase.py

import pylab as p
import numpy as np
from scipy.sparse import lil_matrix
from time import time
from auto import Autopoiesis
from functools import reduce

SAMPLES = 50
DIM = 50 # dimension of sparse array for plot

plotL = []
plotS = []
plotJ = []
t0 = time()

class PhasePlot(Autopoiesis):
    def __init__(self):
        super(PhasePlot, self).__init__()
        self.step = 0

    def Step(self, settings):
        global t0, plotS, plotJ
        super(PhasePlot, self).Step(settings)

        # sample data once per second
        if time()>t0+1:
            t0 = time()
            plotL.append(self.countL)
            plotS.append(self.countS)
            plotJ.append(self.countJ)
            self.step += 1
            print(self.step)

        if self.step==SAMPLES:

            # Fig 3. Phase Plot delta S by delta J
            fig3 = p.figure()
            x = np.diff(plotJ)
            y = np.diff(plotS)
            #y = np.diff(plotL)
            dx = np.diff(x)
            dy = np.diff(y)
            n = len(dx)
            sumx = lil_matrix((DIM, DIM))
            sumy =  lil_matrix((DIM, DIM))
            sumn =  lil_matrix((DIM, DIM))
            for i in range(n):
                # index by row, col
                sumx[y[i]+(DIM/2),x[i]+(DIM/2)] += dx[i]
                sumy[y[i]+(DIM/2),x[i]+(DIM/2)] += dy[i]
                sumn[y[i]+(DIM/2),x[i]+(DIM/2)] +=1
            _x = []
            _y = []
            _dx = []
            _dy = []
            rows,cols = sumn.nonzero()
            for row,col in zip(rows,cols):
                _x.append(col-(DIM/2))
                _y.append(row-(DIM/2))
                _dx.append(sumx[row,col] / sumn[row,col] )
                _dy.append(sumy[row,col] / sumn[row,col] )

            M = np.ones(len(_x))
            p.quiver(_x,_y,_dx,_dy,M,pivot='mid', cmap=p.cm.jet)
            p.grid()
            p.xlabel('$\Delta$ bonds')
            p.ylabel('$\Delta$ substrate')
            #p.ylabel('$\Delta$ links')
            fig3.savefig('images/fig3.png')

            conv = reduce(np.add,np.gradient(_dx)) + reduce(np.add,np.gradient(_dy))
            print(_dx)

            exit()

if __name__ == "__main__":
    PhasePlot().run()