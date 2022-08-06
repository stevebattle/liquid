#!/usr/bin/env python

# Simulated Autopoiesis in Liquid Automata
# To run:
# python plot-ca.py

import pygame
from pygame.locals import *
import pylab as p
import numpy as np
from scipy.sparse import lil_matrix
from ca import CA

SIDE = 400
W = 20 # moving average 'window'
SAMPLES = 500 # must be >= W
DIM = 50 # dimension of sparse array for plot
CATALYSTS = [(4,4)] # (x,y)

# pygame color objects
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

plotS = []
plotJ = []

class Plot(CA):
    def __init__(self,C):
        super(Plot, self).__init__(C)
        self.step = 0

    def Step(self):
        global plotS, plotJ
        super(Plot, self).Step()


        plotS.append(self.countS)
        plotJ.append(self.countJ)
        self.step += 1
        #print(self.step)

        if self.step==SAMPLES:

            # Fig 3. Phase Plot delta S by delta J
            fig3 = p.figure()
            x = np.diff(plotJ)
            y = np.diff(plotS)
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
            p.xlabel('$\Delta$ joints')
            p.ylabel('$\Delta$ substrate')
            fig3.savefig('images/fig3.png')

            exit()

pygame.init()
window = pygame.display.set_mode((SIDE,SIDE))
FPS = 20
frameRate = pygame.time.Clock()

ca = Plot(CATALYSTS)
while True:
    window.fill(WHITE)
    ca.Step()
    ca.draw()
    pygame.display.update()
    # check for quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
    frameRate.tick(FPS)