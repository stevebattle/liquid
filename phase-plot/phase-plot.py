#!/usr/bin/env python

# Simulated Autopoiesis in Liquid Automata
# pip install numpy
# pip install matplotlib

# To run:
# conda activate pybox2d
# python -m phase-plot --backend=pygame

# K - catalyst
# S - substrate
# L - link
# BL - bonded link

# Plots inspired by: https://scipy-cookbook.readthedocs.io/items/LoktaVolterraTutorial.html

from inspect import _void
from math import cos, sin, pi, hypot, sqrt, atan
import random
from Box2D.examples.framework import (Framework, Keys, main)
from Box2D import (b2World, b2DistanceJointDef, b2PrismaticJointDef, b2WheelJointDef, b2EdgeShape, b2FixtureDef, b2PolygonShape, b2CircleShape)
import pylab as p
import numpy as np
from time import time
from scipy.sparse import lil_matrix
from scipy.stats import norm

N = 700

# Arena dimensions/offsets
OFFSETX = 0
OFFSETY = 15
SIDE = 30

# body characteristics
MASS = 5
FRICTION = 0.2
S_RADIUS = 0.5
K_SIDE = 1.6
L_SIDE = 0.9
K_AREA = K_SIDE * sqrt(3)/4 # area of equilateral triangle
S_AREA = pi * S_RADIUS**2 # area of circle
L_AREA = L_SIDE**2 # area of square

DECAY_RATE = 0.001
CENTERING = 8

# Wiener Process parameter
DELTA = 15

# plot
SAMPLES = 500 # must be >= W
countS = N
countL = 0
countJ = 0
plotS = []
plotL = []
plotJ = []
plotX = []
step = 0
t0 = time()
fig1 = None
fig2 = None
W = 20 # moving average 'window'
DIM = 50 # dimension of sparse array for plot

lastTime = time()

def triangle(r):
    return [(r,0),(r*cos(4*pi/3),r*sin(4*pi/3)),(r*cos(2*pi/3),r*sin(2*pi/3))]

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

class Autopoiesis(Framework):
    name = "Autopoiesis"
    description = "Simulated Autopoiesis in Liquid Automata"
    bodies = []
    joints = []

    # the current set of catalyst contacts
    contacts = set()
    reserve = []
    bonds = []

class Autopoiesis(Framework):
    name = "Autopoiesis"
    description = "Simulated Autopoiesis in Liquid Automata"
    bodies = []
    joints = []

    # the current set of catalyst contacts
    contacts = set()
    reserve = []
    bonds = []

    def __init__(self):
        global link, sub
        super(Autopoiesis, self).__init__()

        # weightless world
        self.world.gravity = (0, 0)

        # confinement field
        border = self.world.CreateStaticBody(
            shapes=[b2EdgeShape(vertices=[(-SIDE/2+OFFSETX, -SIDE/2+OFFSETY), (SIDE/2+OFFSETX, -SIDE/2+OFFSETY)]),
                    b2EdgeShape(vertices=[(-SIDE/2+OFFSETX, -SIDE/2+OFFSETY), (-SIDE/2+OFFSETX, SIDE/2+OFFSETY)]),
                    b2EdgeShape(vertices=[(SIDE/2+OFFSETX, -SIDE/2+OFFSETY), (SIDE/2+OFFSETX, SIDE/2+OFFSETY)]),
                    b2EdgeShape(vertices=[(-SIDE/2+OFFSETX, SIDE/2+OFFSETY), (SIDE/2+OFFSETX, SIDE/2+OFFSETY)]),
                    ])

        # A fixture binds a shape to a body and adds material properties such as density, friction, restitution. 
        sub = b2FixtureDef(shape=b2CircleShape(radius=S_RADIUS), density=MASS/S_AREA, friction=FRICTION)
        cat = b2FixtureDef(shape=b2PolygonShape(vertices=triangle(K_SIDE)), density=MASS/K_AREA, friction=FRICTION)
        link = b2FixtureDef(shape=b2PolygonShape(box=(L_SIDE,L_SIDE)), density=2*MASS/L_AREA, friction=FRICTION, userData="link")

        # The N body problem
        self.bodies = [ self.world.CreateDynamicBody(position=(OFFSETX,OFFSETY),fixtures=cat, userData="cat") ]
        for i in range(N):
            p = (random.randrange(round(-SIDE/2+OFFSETX+S_RADIUS*2),round(SIDE/2+OFFSETX-S_RADIUS*2)),
                 random.randrange(round(-SIDE/2+OFFSETY+S_RADIUS*2),round(SIDE/2+OFFSETY-S_RADIUS*2)))
            b = self.world.CreateDynamicBody(position=p,fixtures=sub, userData="sub")
            b.angle = random.uniform(0,2*pi)
            self.bodies.append(b)

        bodies = self.bodies


    def Step(self, settings):
        global link, sub, lastTime, step, plotS, plotL, plotJ, plotX, fig1, countS, countL, countJ, t0

        super(Autopoiesis, self).Step(settings)

        # determine dt by the clock
        timeNow = time()
        dt = timeNow - lastTime
        lastTime = timeNow

        for body in self.bodies:
            # Apply random 'brownian' forces (Wiener process) to substrate at each step
            # see https://scipy-cookbook.readthedocs.io/items/BrownianMotion.html
            force = (norm.rvs(scale=DELTA**2*dt), norm.rvs(scale=DELTA**2*dt))
            body.ApplyLinearImpulse(force,body.position, True)
                
            # catalyst pressure towards origin to avoid being trapped against the wall
            if body.userData=="cat":
                force = (-CENTERING*(body.position[0]-OFFSETX),-CENTERING*(body.position[1]-OFFSETY))
                body.ApplyForce(force,body.position, True)
        
        # composition: K + 2S -> K + L
        # convert substrate pair to link
        if len(self.contacts)>=2:
            # convert the first sub into a link
            c = self.contacts.pop()
            c.userData = 0
            c.DestroyFixture(c.fixtures[0])
            c.CreateFixture(link)
            # put the second sub on the reserve list (we need it for decay)
            c1 = self.contacts.pop()
            c1.DestroyFixture(c1.fixtures[0])
            self.reserve.append(c1)
            countS -= 2
            countL += 1

        # concatenation: L<sub>n</sub> + L -> L<sub>n+1</sub>
        # bond links together
        for b in self.bonds:
            bodyA = b.fixtureA.body
            bodyB = b.fixtureB.body
            if type(bodyA.userData)==int and bodyA.userData<2 and \
               type(bodyB.userData)==int and bodyB.userData<2:
                j = self.world.CreateJoint(b2DistanceJointDef(
                    frequencyHz=4.0, dampingRatio=0.5,
                    bodyA=bodyA, bodyB=bodyB,
                    localAnchorA=(0,0), localAnchorB=(0,0)
                ))
                self.joints.append(j)
                bodyA.userData += 1
                bodyB.userData += 1
                countJ += 1
        self.bonds = []

        # disintegration:  L -> 2S
        # random decay of links and bonds
        for b in self.bodies:
            # links have userData = 0, bonded links have userData = 1,2
            if type(b.userData)==int:
                if random.uniform(0,1) < DECAY_RATE:
                    b.userData = "sub"
                    # destroy the link fixture and replace it with a substrate fixture
                    b.DestroyFixture(b.fixtures[0])
                    b.CreateFixture(sub)
                    # now delete any associated joints
                    joints2go = []
                    for j in self.joints:
                        if j.bodyA == b or j.bodyB == b:
                            joints2go.append(j)
                    for j in joints2go:
                        if j.bodyA == b:
                            j.bodyB.userData -= 1
                        if j.bodyB == b:
                            j.bodyA.userData -= 1
                        self.joints.remove(j)
                        self.world.DestroyJoint(j)
                        countJ -= 1
                    # restore the second sub from the reserve
                    s = self.reserve.pop()
                    s.CreateFixture(sub)
                    s.position = b.position
                    countL -= 1
                    countS += 2

        # sample data once per second
        if time()>t0+1 and fig1==None:
            t0 = time()
            plotS.append(countS)
            plotL.append(countL)
            plotJ.append(countJ)
            plotX.append(step)
            step += 1
            print(step)

        if step == SAMPLES and fig1==None:

            fig1 = p.figure()
            # A long average 20-30 secs highlights the L,J lag.
            s = moving_average(np.diff(plotS),W)
            l = moving_average(np.diff(plotL),W)
            j = moving_average(np.diff(plotJ),W)
            n = min(len(s),100) # plot at most 100 samples
            t = plotX[:n]
            p.plot(t, s[:n], 'r-', label='substrate')
            p.plot(t, l[:n], 'g-', label='links')
            p.plot(t, j[:n], 'b-', label='joints')
            p.legend(loc='best')
            p.xlabel('time')
            p.ylabel('rate of change ('+str(W)+' sec moving avg)')
            p.grid()
            fig1.savefig('fig1.png')

            fig2 = p.figure()
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
                #print((row,col), sumn[row,col], sumx[row,col], sumy[row,col])
                _x.append(col-(DIM/2))
                _y.append(row-(DIM/2))
                _dx.append(sumx[row,col] / sumn[row,col] )
                _dy.append(sumy[row,col] / sumn[row,col] )

            # M = [hypot(_dx[i],_dy[i]) for i in range(len(_x))]
            # M[ M == 0] = 1.
            M = np.ones(len(_x))
            p.quiver(_x,_y,_dx,_dy,M,pivot='mid', cmap=p.cm.jet)
            p.grid()
            p.xlabel('$\Delta$ joints')
            p.ylabel('$\Delta$ substrate')
            fig2.savefig('fig2.png')

            n = min(SAMPLES,100) # plot at most 100 samples
            t = plotX[:n]
            fig3, ax1 = p.subplots()
            ax2 = ax1.twinx()
            ax1.plot(t, plotS[:n], label='substrate', color='red')
            ax2.plot(t, plotL[:n], label='links', color='green')
            ax2.plot(t, plotJ[:n], label='joints', color='blue')
            ax1.set_xlabel('time')
            ax1.set_ylabel('substrate')
            ax2.set_ylabel('links and joints')
            fig3.legend(loc='upper left')
            #fig3.tight_layout()
            p.grid()
            fig3.savefig('fig3.png')

    def BeginContact(self,contact):
        # Add new catalyst contacts (removed in EndContact below)
        if contact.fixtureA.body.userData=="cat" and contact.fixtureB.body.userData=="sub":
            self.contacts.add(contact.fixtureB.body)
        elif contact.fixtureB.body.userData=="cat" and contact.fixtureA.body.userData=="sub":
            self.contacts.add(contact.fixtureA.body)

        # Add new bond
        if type(contact.fixtureA.body.userData)==int and contact.fixtureA.body.userData<2 and \
           type(contact.fixtureB.body.userData)==int and contact.fixtureB.body.userData<2:
            self.bonds.append(contact)

    def EndContact(self,contact):
        # The bodies may have already been removed by catalysis
        if contact.fixtureA.body.userData=="cat" and contact.fixtureB.body in self.contacts:
            self.contacts.remove(contact.fixtureB.body)
        elif contact.fixtureB.body.userData=="cat" and contact.fixtureB.body in self.contacts:
            self.contacts.remove(contact.fixtureA.body)

if __name__ == "__main__":
    main(Autopoiesis)
