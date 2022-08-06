#!/usr/bin/env python

# Simulated Autopoiesis in Liquid Automata

# To run:
# conda activate pybox2d
# python -m auto --backend=pygame

# K - catalyst
# S - substrate
# L - link
# BL - bonded link

from inspect import _void
from math import cos, sin, pi, sqrt, atan
from scipy.stats import norm
import random
from time import time
from Box2D.examples.framework import (Framework, Keys, main)
from Box2D import (b2World, b2DistanceJointDef, b2PrismaticJointDef, b2WheelJointDef, b2EdgeShape, b2FixtureDef, b2PolygonShape, b2CircleShape)

S_POP = 700

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

def triangle(r):
    return [(r,0),(r*cos(4*pi/3),r*sin(4*pi/3)),(r*cos(2*pi/3),r*sin(2*pi/3))]

class Autopoiesis(Framework):
    name = "Autopoiesis"
    description = "Simulated Autopoiesis in Liquid Automata"
    bodies = []
    joints = []

    # the current set of catalyst contacts
    contacts = set()
    reserve = []
    bonds = []

    def __init__(self,n):
        global cat, link, sub
        super(Autopoiesis, self).__init__()

        self.countS = 0
        self.countL = 0
        self.countJ = 0
        self.lastTime = time()

        # weightless world
        self.world.gravity = (0, 0)

        # containment field
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
        for i in range(n):
            p = (random.randrange(round(-SIDE/2+OFFSETX+S_RADIUS*2),round(SIDE/2+OFFSETX-S_RADIUS*2)),
                 random.randrange(round(-SIDE/2+OFFSETY+S_RADIUS*2),round(SIDE/2+OFFSETY-S_RADIUS*2)))
            b = self.world.CreateDynamicBody(position=p,fixtures=sub, userData="sub")
            b.angle = random.uniform(0,2*pi)
            self.bodies.append(b)
            self.countS += 1

        bodies = self.bodies

    def Step(self, settings):
        global link, sub, lastTime, countS, countL, countJ
        super(Autopoiesis, self).Step(settings)

        # determine dt using the clock
        timeNow = time()
        dt = timeNow - self.lastTime
        self.lastTime = timeNow

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
            self.countS -= 2
            self.countL += 1

        # concatenation: L<super>n</super> + L -> L<super>n+1</super>
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
                self.countJ += 1
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
                        self.countJ -= 1

                    # restore the second sub from the reserve
                    s = self.reserve.pop()
                    s.CreateFixture(sub)
                    s.position = b.position
                    self.countL -= 1
                    self.countS += 2

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
    Autopoiesis(S_POP).run()
