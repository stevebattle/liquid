#!/usr/bin/env python

# Simulated Autopoiesis in Liquid Automata
# To run:
# python plot-ca.py

import pygame
from pygame.locals import *
import pylab as p
import numpy as np
from ca import CA

SIDE = 400
W = 20 # moving average 'window'
SAMPLES = 100 # must be >= W
CATALYSTS = [(4,4)] # (x,y)

# pygame color objects
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

plotS = []
plotL = []
plotJ = []
plotX = []

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

class Plot(CA):
    def __init__(self,C):
        super(Plot, self).__init__(C)
        self.step = 0

    def Step(self):
        global plotS, plotL, plotJ, plotX
        super(Plot, self).Step()


        plotS.append(self.countS)
        plotL.append(self.countL)
        plotJ.append(self.countJ)
        plotX.append(self.step)
        self.step += 1
        print(self.step)

        if self.step==SAMPLES+W:
            n = SAMPLES
            t = plotX[:n]

            # Fig 1. Plot S,L,J by time
            fig1, ax1 = p.subplots()
            ax2 = ax1.twinx()
            ax1.plot(t, plotS[:n], label='substrate', color='red')
            ax2.plot(t, plotL[:n], label='links', color='green')
            ax2.plot(t, plotJ[:n], label='joints', color='blue')
            ax1.set_xlabel('time')
            ax1.set_ylabel('substrate')
            ax2.set_ylabel('links and joints')
            fig1.legend(loc='upper left')
            p.grid()
            fig1.savefig('images/fig1.png')

            # Fig 2. Plot rate of change S,L,J by time
            fig2 = p.figure()
            s = moving_average(np.diff(plotS),W)
            l = moving_average(np.diff(plotL),W)
            j = moving_average(np.diff(plotJ),W)
            p.plot(t, s[:n], 'r-', label='substrate')
            p.plot(t, l[:n], 'g-', label='links')
            p.plot(t, j[:n], 'b-', label='joints')
            p.legend(loc='best')
            p.xlabel('time')
            p.ylabel('rate of change ('+str(W)+' sec moving avg)')
            p.grid()
            fig2.savefig('images/fig2.png')

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