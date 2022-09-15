#!/usr/bin/env python

# Simulated Autopoiesis in Liquid Automata

# To run:
# conda activate pybox2d
# python -m auto --backend=pygame

from inspect import _void
from math import cos, sin, pi, sqrt, atan
from re import A
from scipy.stats import norm
import random
from time import time
from Box2D.examples.framework import (Framework, Keys, main)
from Box2D import *
import pygame

pygame.init()

L_sounds = [
    pygame.mixer.Sound("sounds/diamond_1.mp3"), 
    pygame.mixer.Sound("sounds/diamond_2.mp3"), 
    pygame.mixer.Sound("sounds/diamond_3.mp3"), 
    pygame.mixer.Sound("sounds/diamond_4.mp3"),
    pygame.mixer.Sound("sounds/diamond_5.mp3"),
    pygame.mixer.Sound("sounds/diamond_6.mp3"),
    pygame.mixer.Sound("sounds/diamond_7.mp3"),
    pygame.mixer.Sound("sounds/diamond_8.mp3") ]

S_sound = pygame.mixer.Sound("sounds/crack.mp3")
BL_sound =  pygame.mixer.Sound("sounds/gravity_change.mp3")
amoeba_sound = pygame.mixer.Sound("sounds/amoeba.mp3")
closure_sound = pygame.mixer.Sound("sounds/diamond_key_collect.mp3")

K_POP = 2
S_POP = 700

# Arena dimensions/offsets
OFFX = 0
OFFY = 15
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
DELTA = 10

# A fixture binds a shape to a body and adds material properties such as density, friction, restitution. 
# The components are ranked by increasing 'mass' as S, L, K.

def triangle(r):
    return [(r,0),(r*cos(4*pi/3),r*sin(4*pi/3)),(r*cos(2*pi/3),r*sin(2*pi/3))]

# K - catalyst
# S - substrate
# L - link
# BL - bonded link
S = b2FixtureDef(shape=b2CircleShape(radius=S_RADIUS), density=MASS/S_AREA, friction=FRICTION, userData="S")
L = b2FixtureDef(shape=b2PolygonShape(box=(L_SIDE,L_SIDE)), density=2*MASS/L_AREA, friction=FRICTION, userData="L")
K = b2FixtureDef(shape=b2PolygonShape(vertices=triangle(K_SIDE)), density=3*MASS/K_AREA, friction=FRICTION, userData="K")


class Autopoiesis(Framework):
    name = "Autopoiesis"
    description = "Simulated Autopoiesis in Liquid Automata"
    bodies = []
    joints = []

    # the current set of catalyst contacts
    contacts = set()
    reserve = []
    bonds = []

    def __init__(self,n=S_POP,delta=DELTA):
        global S,L,K
        super(Autopoiesis, self).__init__()

        self.countS = 0
        self.countL = 0
        self.countJ = 0
        self.lastTime = time()
        self.delta = delta # Wiener process

        # weightless world
        self.world.gravity = (0, 0)

        # containment field
        border = self.world.CreateStaticBody(
            shapes=[b2EdgeShape(vertices=[(-SIDE/2+OFFX, -SIDE/2+OFFY), (SIDE/2+OFFX, -SIDE/2+OFFY)]),
                    b2EdgeShape(vertices=[(-SIDE/2+OFFX, -SIDE/2+OFFY), (-SIDE/2+OFFX, SIDE/2+OFFY)]),
                    b2EdgeShape(vertices=[(SIDE/2+OFFX, -SIDE/2+OFFY), (SIDE/2+OFFX, SIDE/2+OFFY)]),
                    b2EdgeShape(vertices=[(-SIDE/2+OFFX, SIDE/2+OFFY), (SIDE/2+OFFX, SIDE/2+OFFY)]),
                    ])

        for i in range(K_POP):
            p = (random.randrange(round(-SIDE/2+OFFX+S_RADIUS*2),round(SIDE/2+OFFX-S_RADIUS*2)),
                 random.randrange(round(-SIDE/2+OFFY+S_RADIUS*2),round(SIDE/2+OFFY-S_RADIUS*2)))
            b = self.world.CreateDynamicBody(position=p,fixtures=K)
            self.bodies.append(b)

        # The N body problem
        for i in range(n):
            p = (random.randrange(round(-SIDE/2+OFFX+S_RADIUS*2),round(SIDE/2+OFFX-S_RADIUS*2)),
                 random.randrange(round(-SIDE/2+OFFY+S_RADIUS*2),round(SIDE/2+OFFY-S_RADIUS*2)))
            b = self.world.CreateDynamicBody(position=p,fixtures=S)
            b.angle = random.uniform(0,2*pi)
            self.bodies.append(b)
            self.countS += 1

        bodies = self.bodies

    # eliminates triangular compositions
    def acute(self,bodyA,bodyB):
        a = [i.bodyB for i in self.joints if i.bodyA==bodyA] + \
            [j.bodyA for j in self.joints if j.bodyB==bodyA]
        b = [i.bodyB for i in self.joints if i.bodyA==bodyB] + \
            [j.bodyA for j in self.joints if j.bodyB==bodyB]
        # list intersection - any body joined to both A and B
        intersect = [i for i in a if i in b]
        return len(intersect)>0

    def joinedTo(self,bodyA):
        return [i.bodyB for i in self.joints if i.bodyA==bodyA] + \
            [j.bodyA for j in self.joints if j.bodyB==bodyA]
    
    def closure(self,bodyA):
        a = bodyA
        b = self.joinedTo(a)
        while len(b)>0:
            c = self.joinedTo(b[0])
            if a in c:
                c.remove(a)
            a = b[0]
            b = c
            if a==bodyA:
                return True
        return False

    def Step(self, settings):
        global S, L, lastTime, countS, countL, countJ
        super(Autopoiesis, self).Step(settings)

        # determine dt using the clock
        timeNow = time()
        dt = timeNow - self.lastTime
        self.lastTime = timeNow

        for body in self.bodies:
            if len(body.fixtures)==1:
                # Apply random 'brownian' forces (Wiener process) to substrate at each step
                # see https://scipy-cookbook.readthedocs.io/items/BrownianMotion.html
                force = (norm.rvs(scale=self.delta**2*dt), norm.rvs(scale=self.delta**2*dt))
                body.ApplyLinearImpulse(force,body.position, True)
                    
                # catalyst pressure towards origin to avoid being trapped against the wall
                if body.fixtures[0].userData=="K":
                    force = (-CENTERING*(body.position[0]-OFFX),-CENTERING*(body.position[1]-OFFY))
                    body.ApplyForce(force,body.position, True)
        
        # composition: K + 2S -> K + L
        # convert substrate pair to link
        if len(self.contacts)>=2:
            # convert the first substrate into a link
            c = self.contacts.pop()
            c.DestroyFixture(c.fixtures[0])
            c.CreateFixture(L)
            c.userData = 0 # bond counter
            # put the second substrate on the reserve list (we need it for decay)
            c1 = self.contacts.pop()
            c1.DestroyFixture(c1.fixtures[0])
            self.reserve.append(c1)
            self.countS -= 2
            self.countL += 1
            pygame.mixer.Sound.play(L_sounds[random.randint(0,7)])

        # concatenation: L<super>n</super> + L -> L<super>n+1</super>
        # bond links together
        for b in self.bonds:
            bodyA = b.fixtureA.body
            bodyB = b.fixtureB.body
            if b.fixtureA.userData=="L" and bodyA.userData<2 and \
               b.fixtureB.userData=="L" and bodyB.userData<2 and not(self.acute(bodyA,bodyB)):
                j = self.world.CreateJoint(b2DistanceJointDef(
                    frequencyHz=4.0, dampingRatio=0.5,
                    bodyA=bodyA, bodyB=bodyB,
                    localAnchorA=(0,0), localAnchorB=(0,0)
                ))
                self.joints.append(j)
                bodyA.userData += 1
                bodyB.userData += 1
                self.countJ += 1
                pygame.mixer.Sound.play(BL_sound)
                if self.closure(bodyA):
                    pygame.mixer.Sound.play(closure_sound)


        self.bonds = []

        # disintegration:  L -> 2S
        # random decay of links and bonds
        for b in self.bodies:
            # links have a single fixture with userData = "L"
            if len(b.fixtures)==1 and b.fixtures[0].userData=="L":
                if random.uniform(0,1) < DECAY_RATE:
                    # destroy the link fixture and replace it with a substrate fixture
                    b.DestroyFixture(b.fixtures[0])
                    b.CreateFixture(S)
                    # now delete any associated joints
                    joints2go = []
                    for j in self.joints:
                        if j.bodyA == b or j.bodyB == b:
                            joints2go.append(j)
                    for j in joints2go:
                        if j.bodyA == b and isinstance(j.bodyB.userData, int):
                            j.bodyB.userData -= 1
                        if j.bodyB == b and isinstance(j.bodyA.userData, int):
                            j.bodyA.userData -= 1
                        self.joints.remove(j)
                        self.world.DestroyJoint(j)
                        self.countJ -= 1

                    # restore the second substrate from the reserve
                    s = self.reserve.pop()
                    s.CreateFixture(S)
                    s.position = b.position
                    self.countL -= 1
                    self.countS += 2

                    pygame.mixer.Sound.play(S_sound)


    def BeginContact(self,contact):
        # Add new catalyst contacts (removed in EndContact below)
        if contact.fixtureA.userData=="K" and contact.fixtureB.userData=="S":
            self.contacts.add(contact.fixtureB.body)
        elif contact.fixtureB.userData=="K" and contact.fixtureA.userData=="S":
            self.contacts.add(contact.fixtureA.body)

        # Add new bond
        if contact.fixtureA.userData=="L" and contact.fixtureA.body.userData<2 and \
           contact.fixtureB.userData=="L" and contact.fixtureB.body.userData<2:
            self.bonds.append(contact)

    def EndContact(self,contact):
        # The bodies may have already been removed by catalysis
        if contact.fixtureA.userData=="K" and contact.fixtureB.body in self.contacts:
            self.contacts.remove(contact.fixtureB.body)
        elif contact.fixtureB.userData=="K" and contact.fixtureB.body in self.contacts:
            self.contacts.remove(contact.fixtureA.body)


if __name__ == "__main__":
    pygame.mixer.Sound.play(amoeba_sound,-1)
    main(Autopoiesis).run()
