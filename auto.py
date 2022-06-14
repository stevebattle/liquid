#!/usr/bin/env python

# Simulation of Autopoiesis in Liquid Automata

# conda activate pybox2d
# python -m auto --backend=pygame

# K - catalyst
# S - substrate
# L - link
# BL - bonded link

from inspect import _void
from math import cos, sin, pi
import random
from Box2D.examples.framework import (Framework, Keys, main)
from Box2D import (b2World, b2DistanceJointDef, b2PrismaticJointDef, b2WheelJointDef, b2EdgeShape, b2FixtureDef, b2PolygonShape, b2CircleShape)

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

def triangle(r):
    return [(r,0),(r*cos(4*pi/3),r*sin(4*pi/3)),(r*cos(2*pi/3),r*sin(2*pi/3))]

def handleCollision(phase, a, b, arbiter):
    pass

class Autopoiesis(Framework):
    name = "Autopoiesis"
    description = "Simulation of an autopoietic system"
    bodies = []
    joints = []

    # the current set of catalyst contacts
    contacts = set()
    reserve = []
    bonds = []
    joints = []

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
        global link, sub
        super(Autopoiesis, self).Step(settings)
        for body in self.bodies:
            # Apply random 'brownian' forces to substrate at each step
            if body.userData=="sub":
                w = 1
                force = (w*cos(body.angle), w*sin(body.angle))
                body.ApplyLinearImpulse(force,body.position, True)
                #body.ApplyAngularImpulse(random.randrange(-5,5),True)
                body.angle += random.uniform(-0.3,0.3)
            # catalyst tends to the origin
            elif body.userData=="cat":
                # Pressure towards origin to avoid being trapped against the wall
                w = 8
                force = (-w*(body.position[0]-OFFSETX),-w*(body.position[1]-OFFSETY))
                body.ApplyForce(force,body.position, True)
                body.angle += random.uniform(-0.3,0.3)
        
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

        # concatenation: L0-L1- ... -Ln + L -> L0-L1- ... -Ln+1
        # bond links together
        for b in self.bonds:
            if type(b[0].userData)==int and b[0].userData<2 and \
               type(b[1].userData)==int and b[1].userData<2:
                jointDef = b2DistanceJointDef(
                    frequencyHz=4.0, dampingRatio=0.5,
                    bodyA=b[0], bodyB=b[1],
                    localAnchorA=(0,0), localAnchorB=(0,0),
                )
                j = self.world.CreateJoint(jointDef)
                self.joints.append(j)
                b[0].userData += 1
                b[1].userData += 1
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
                    # restore the second sub from the reserve
                    s = self.reserve.pop()
                    s.CreateFixture(sub)
                    s.position = b.position

    def BeginContact(self,contact):
        # Add new catalyst contacts (removed in EndContact below)
        if contact.fixtureA.body.userData=="cat" and contact.fixtureB.body.userData=="sub":
            self.contacts.add(contact.fixtureB.body)
        elif contact.fixtureB.body.userData=="cat" and contact.fixtureA.body.userData=="sub":
            self.contacts.add(contact.fixtureA.body)

        # Add new bond
        if type(contact.fixtureA.body.userData)==int and contact.fixtureA.body.userData<2 and \
           type(contact.fixtureB.body.userData)==int and contact.fixtureB.body.userData<2:
            self.bonds.append((contact.fixtureA.body,contact.fixtureB.body))

    def EndContact(self,contact):
        # The bodies may have already been removed by catalysis
        if contact.fixtureA.body.userData=="cat" and contact.fixtureB.body in self.contacts:
            self.contacts.remove(contact.fixtureB.body)
        elif contact.fixtureB.body.userData=="cat" and contact.fixtureB.body in self.contacts:
            self.contacts.remove(contact.fixtureA.body)

if __name__ == "__main__":
    main(Autopoiesis)
