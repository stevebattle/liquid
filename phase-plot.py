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
from math import cos, sin, pi, hypot
import random
from Box2D.examples.framework import (Framework, Keys, main)
from Box2D import (b2World, b2DistanceJointDef, b2PrismaticJointDef, b2WheelJointDef, b2EdgeShape, b2FixtureDef, b2PolygonShape, b2CircleShape)
import pylab as p
import numpy as np
import time
from scipy.sparse import lil_matrix 

N = 700

# Arena dimensions/offsets
OFFSETX = 0
OFFSETY = 15
SIDE = 30

# body characteristics
SUB_RADIUS = 0.5
CAT_SIDE = 1.6
LINK_SIDE = 0.9
DENSITY = 4
FRICTION = 0.2
DECAY_RATE = 0.0005

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
t0 = time.time()
fig1 = None
fig2 = None
W = 20
DIM = 30 # dimension of sparse array for plot

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
        sub = b2FixtureDef(shape=b2CircleShape(radius=SUB_RADIUS), density=DENSITY, friction=FRICTION)
        cat = b2FixtureDef(shape=b2PolygonShape(vertices=triangle(CAT_SIDE)), density=DENSITY, friction=FRICTION)
        link = b2FixtureDef(shape=b2PolygonShape(box=(LINK_SIDE,LINK_SIDE)), density=DENSITY, friction=FRICTION, userData="link")

        # The N body problem
        self.bodies = [ self.world.CreateDynamicBody(position=(OFFSETX,OFFSETY),fixtures=cat, userData="cat") ]
        for i in range(N):
            p = (random.randrange(round(-SIDE/2+OFFSETX+SUB_RADIUS*2),round(SIDE/2+OFFSETX-SUB_RADIUS*2)),
                 random.randrange(round(-SIDE/2+OFFSETY+SUB_RADIUS*2),round(SIDE/2+OFFSETY-SUB_RADIUS*2)))
            b = self.world.CreateDynamicBody(position=p,fixtures=sub, userData="sub")
            b.angle = random.uniform(0,2*pi)
            self.bodies.append(b)

        bodies = self.bodies

    def Step(self, settings):
        global link, sub, step, plotS, plotL, plotJ, plotX, fig1, countS, countL, countJ, t0
        super(Autopoiesis, self).Step(settings)
        for body in self.bodies:
            # Apply random 'brownian' forces to substrate at each step
            if body.userData=="sub":
                # Random angle change 'Brownian motion'
                body.angle += random.uniform(-0.3,0.3)
                w = 1
                force = (w*cos(body.angle), w*sin(body.angle))
                body.ApplyLinearImpulse(force,body.position, True)
                
            # catalyst tends to the origin
            elif body.userData=="cat":
                body.angle += random.uniform(-0.3,0.3)
                # Pressure towards origin to avoid being trapped against the wall
                w = 8
                force = (-w*(body.position[0]-OFFSETX),-w*(body.position[1]-OFFSETY))
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
        if time.time()>t0+1 and fig1==None:
            t0 = time.time()
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
            p.plot(t, s[:n], 'r-', label='Substrate')
            p.plot(t, l[:n], 'g-', label='Links')
            p.plot(t, j[:n], 'b-', label='Joints')
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
            p.xlabel('Joints')
            p.ylabel('Substrate')
            fig2.savefig('fig2.png')

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
