import pygame
from pygame.locals import *
from random import random, randint, shuffle
from functools import reduce
from math import radians, sin, cos
from time import sleep

SIDE = 400
SIZE = 10
MARGIN = 50
SPACING = (SIDE-MARGIN*2)/10
EXTENT = SPACING - 5
CATALYSTS = [(4,4)] # (x,y)

# Pd an adjustable parameter of the algorithm
# A disintegration probability of less than about 0.01 per time step is required
Pd = 0.01

# pygame color objects
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

pygame.init()
window = pygame.display.set_mode((SIDE,SIDE))
FPS = 10
frameRate = pygame.time.Clock()
frameCount = 0


def inRange(c,n):
    v = c.add(n)
    return v.x in range(SIZE) and v.y in range(SIZE) 

def orthogonallyAdjacent(a,b):
    # manhattan distance = 1
    return abs(a.x - b.x) + abs(a.y - b.y) == 1

# orthogonally or diagnoally adjacent
def adjacent(a,b):
    # manhattan distance <=2
    return abs(a.x - b.x) + abs(a.y - b.y) <= 2 and abs(a.x - b.x)<2 and abs(a.y - b.y)<2

def acute(a,b):
    # manhattan distance > 1
    return abs(a.x - b.x) + abs(a.y - b.y) > 1

def powerset(s):
    return reduce(lambda z, x: z + [y + [x] for y in z], s, [[]])

def commonCell(a,b):
    return (a[0]==b[0] or a[0]==b[1] or a[1]==b[0] or a[1]==b[1]) and not a==b


class Vector:
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def __str__(self):
        return '({0},{1})'.format(self.x,self.y)
    def __repr__(self): # representation within lists
        return self.__str__()
    def add(self,v):
        return Vector(self.x + v.x, self.y + v.y)
    def subtract(self,v):
        return Vector(self.x - v.x, self.y - v.y)
    def __eq__(self,other):
        return self.x==other.x and self.y==other.y

# Moore Neighbourhood
# Local neighbourhood N of adjacent cells (including diagonally adjacent)
# Designation of coordinates of neighboring space with reference to a middle space with designation 0.

N = [Vector(0,0),Vector(-1,0),Vector(0,-1),Vector(1,0),Vector(0,1),
     Vector(-1,1),Vector(-1,-1),Vector(1,-1),Vector(1,1)]

ORTHOGONAL = 5 # orthogonal neighbours only slice of N. e.g. N[1:5]

# prime neighbourhood NX 1' to 4', including middle space with designation 0 to align with N
N_PRIME = [Vector(0,0),Vector(0,-2),Vector(-2,0),Vector(0,2),Vector(2,0)]

class Substrate:
    def draw(self,x,y): # draw a circle
        pygame.draw.circle(window, BLACK, (x,y), EXTENT/2, width=2)

class Catalyst:
    def draw(self,x,y): # draw an asterisk
        r = EXTENT/3
        pygame.draw.line(window, BLACK, (x,y-r), (x,y+r), width=2)
        a = radians(60)
        pygame.draw.line(window, BLACK, (x+r*sin(a),y-r*cos(a)), (x-r*sin(a),y+r*cos(a)), width=2)
        a = radians(-60)
        pygame.draw.line(window, BLACK, (x+r*sin(a),y-r*cos(a)), (x-r*sin(a),y+r*cos(a)), width=2)
        
class Link:
    def __init__(self):
        self.bonds = []
    def bond(self,l,m):
        assert len(self.bonds)<2
        n = N.index(m.subtract(l))
        assert n not in self.bonds
        self.bonds.append(n)
    def unbond(self,l,m):
        n = N.index(m.subtract(l))
        assert n in self.bonds
        self.bonds.remove(n)
    def draw(self,x,y): # square the circle
        pygame.draw.circle(window, BLACK, (x,y), EXTENT/2*0.7, width=2)
        pygame.draw.rect(window, BLACK, (x-EXTENT/2, y-EXTENT/2, EXTENT, EXTENT), 2)
    def drawBonds(self,x,y):
        for b in self.bonds:
            pygame.draw.line(window, BLACK, (x,y), (x+N[b].x*SPACING/2,y+N[b].y*SPACING/2), width=2)


class CA:
    def __init__(self,c):
        # An holey array
        self.a = [[ None for i in range(SIZE) ] for j in range(SIZE) ]
        # initialsie counters
        self.countS = 0
        self.countL = 0
        self.countJ = 0
        for i in range(SIZE):
            for j in range(SIZE):
                if (j,i) in c:
                    self.a[i][j] = Catalyst()
                else:
                    self.a[i][j] = Substrate()
                    self.countS += 1

    def cell(self,c):
        return self.a[c.y][c.x]

    def setCell(self,c,v):
        self.a[c.y][c.x] = v

    def pairBond(self,l,m):
        self.cell(l).bond(l,m)
        self.cell(m).bond(m,l)
        self.countJ += 1

    def pairUnbond(self,l,m):
        self.cell(l).unbond(l,m)
        self.cell(m).unbond(m,l)
        self.countJ -= 1
    
    def bonded(self,l,m):
        d = m.subtract(l)
        return d in N and N.index(d) in self.cell(l).bonds

    # returns None for coordinates outside the space
    def neighbour(self,c,n):
        v = c.add(n)
        return self.cell(v) if v.x in range(SIZE) and v.y in range(SIZE) else None

    # 1. Motion, first step

    def motion(self):
        # 1.1. Form a list of the coordinates of all holes h_i
        h = [Vector(j,i) for i in range(SIZE) for j in range(SIZE) if self.a[i][j] is None]
        
        # 1.2. For each h_i make a random selection n_i in the range 1 through 4, specifying a neighboring location
        n = [randint(1,4) for i in h]
        
        # 1.3. For each h_i in turn, where possible, move occupant of selected neighboring location in h_i
        for i in range(len(h)):
            # neighboring location
            ni = h[i].add(N[n[i]])
            
            # 1.3.1. If the neighbor is a hole or lies outside the space, take no action
            if not(ni.x in range(SIZE) and ni.y in range(SIZE)) or self.cell(ni) is None:
                continue
            if self.cell(h[i]) is not None: # CONFIRM h_i IS STILL A HOLE
                continue
            
            # 1.3.2. If the neighbor n_i contains a bonded L, examine the location n_i'.
            # If n_i' contains an S, move this S to h_i.
            if isinstance(self.cell(ni), Link) and len(self.cell(ni).bonds)>0:
                ni_prime = h[i].add(N_PRIME[n[i]])
                if ni_prime.x in range(SIZE) and ni_prime.y in range(SIZE) \
                    and isinstance(self.cell(ni_prime), Substrate):
                    # the bonds are permeable to S
                    self.setCell(h[i], self.cell(ni_prime))
                    self.setCell(ni_prime, None)
                continue
                
            # move occupant of selected neighboring location in h_i
            self.setCell(h[i], self.cell(ni))
            self.setCell(ni, None)
            
            # 1.4. Bond any moved L, if possible (rule 6)
            if isinstance(self.cell(h[i]), Link):
                self.bonding(h[i])

    # 2.3.2. If the location specified by n_i contains an S, the S will be displaced.
    # z displaces s

    def displaceS(self,z,s,allowExchange):
        
        # 2.3.2.1. If there is a hole adjacent to the S, it will move into it. If more than one such hole, select randomly
        # holes adjacent to S
        nh = [s.add(v) for v in N[1:] if inRange(s,v) and self.neighbour(s,v) is None ]
        if len(nh)>0:
            p = nh[randint(0,len(nh)-1)]
            self.setCell(p, self.cell(s)) # displaced S
            self.setCell(s, self.cell(z)) # motile z      
            self.setCell(z, None) # backfill with space
            return True
        
        # 2.3.2.2. If the S can be moved into a hole by passing through bonded links, as in step 1, then it will do so.
        # positions opposite orthogonally adjacent bonded links
        b = [N_PRIME[N.index(v)] for v in N[1:5] if inRange(s,v) and \
            isinstance(self.neighbour(s,v),Link) and len(self.neighbour(s,v).bonds)>0 ]
        # holes in prime neighbourhood of S opposite bonded links
        nh = [s.add(v) for v in b if inRange(s,v) and self.neighbour(s,v) is None ]
        if len(nh)>0:
            p = nh[randint(0,len(nh)-1)]
            self.setCell(p, self.cell(s)) # displace S through bonded links
            self.setCell(s,self. cell(z)) # motile z      
            self.setCell(z, None) # backfill with space
            return True
        
        # 2.3.2.3. If the S cannot be moved into a hole, it will exchange locations with the moving L.    
        if allowExchange:
            swap = self.cell(s) # displaced S
            self.setCell(s, self.cell(z)) # motile z
            self.setCell(z, swap)
            return True
        
        return False


    # Rule 2.3. Where possible, move the L occupying the location m_i into the specified neighboring location
    # returns a boolean indicating if the move was successful

    def moveL(self,l,ni,allowExchange):
        # holes adjacent to the neighbour
        nh = [ni.add(v) for v in N if inRange(ni,v) and self.neighbour(ni,v) is None ]
        
        # 2.3.1. If the location specified by n_i contains another L, or a K, take no action
        # 2.3.2. If the location specified by n_i contains an S, the S will be displaced.
        if isinstance(self.cell(ni), Substrate):
            return self.displaceS(l,ni,True)
            
        # 2.3.3. If the location specified by n_i is a hole, then L simply moves into it.
        elif self.cell(ni) is None:
            self.setCell(ni, self.cell(l)) # L moves into the hole        
            self.setCell(l, None)
            return True
        
        return False
                        
    # 2. Motion, second step

    def motionL(self):
        # 2.1. Form a list of the coordinates of free L's, m_i
        m = [Vector(j,i) for i in range(SIZE) for j in range(SIZE) \
            if isinstance(self.a[i][j],Link) and len(self.a[i][j].bonds)==0 ]
        
        l = [] # list of moved L
        
        # 2.2. For each m_i make a random selection, n_i, in the range 1 through 4, specifying a neighboring location.
        n = [randint(1,4) for i in m]
        for i in range(len(m)):
            # neighbour
            ni = m[i].add(N[n[i]])
            if not(ni.x in range(SIZE) and ni.y in range(SIZE)):
                continue
            
            # 2.3. Where possible, move the L occupying the location m_i into the specified neighboring location
            if self.moveL(m[i],ni,True):
                l.append(ni) # moved
            
        # 2.4. Bond each moved L, if possible
        for li in l:
            if isinstance(self.cell(li),Link) and len(self.cell(li).bonds)==0:
                self.bonding(li)


    # 3 Motion, third step

    def motionK(self):
        # 3.1. Form a list of the coordinates of all K's, c_i
        c = [Vector(j,i) for i in range(SIZE) for j in range(SIZE) if isinstance(self.a[i][j],Catalyst) ]
        
        # 3.2. For each c_i, make a random selection n_i, in the range 1 through 4, specifying a neighboring location
        n = [randint(1,4) for i in c]
        
        # 3.3. Where possible, move the K into the selected neighboring location
        for i in range(len(c)):
            # neighbour
            ni = c[i].add(N[n[i]])
            if not(ni.x in range(SIZE) and ni.y in range(SIZE)):
                continue
            
            # 3.3.1. If the location specified by n_i contains a BL or another K, take no action
            # 3.3.2. If the location specified by n_i contains a free L that may be displaced according to the rules of 2.3,
            # then the L will be moved, and the K moved into its place. (Bond the moved L if possible.)
            moved = False
            if isinstance(self.cell(ni),Link) and len(self.cell(ni).bonds)==0:
                # immediate neighbourhood of L
                nh = [ni.add(v) for v in N[1:] if inRange(ni,v) ]
                shuffle(nh)
                for h in nh:
                    if self.moveL(ni,h,False): # L displaced according to the rules of 2.3 (no exchange leaves ni free)
                        self.setCell(ni, self.cell(c[i])) # K moved into its place
                        self.setCell(c[i], None)
                        self.bonding(h) # Bond the moved L if possible
                        moved = True
                        break
                    
            # 3.3.3. If the location specified by n_i contains an S, then move the S by the rules of 2.3.2.
            if isinstance(self.cell(ni),Substrate):
                self.displaceS(c[i],ni,True)
                
            # 3.3.4. If the location specified by n_i contains a free L not movable by the rules of 2.3,
            # then exchange the positions of the K and the L. (Bond L if possible.)
            elif not moved and isinstance(self.cell(ni),Link) and len(self.cell(ni).bonds)==0:
                swap = self.cell(ni) # displaced L
                self.setCell(ni, self.cell(c[i])) # motile K
                self.setCell(c[i], swap)
                self.bonding(c[i]) # Bond L if possible
                
            # 3.3.5. If the location specified by n_i is a hole, the K moves into it.
            elif self.cell(ni) is None:
                self.setCell(ni, self.cell(c[i])) # motile K 
                self.setCell(c[i], None)


    # 4. Production

    def production(self):
        # 4.1 For each catalyst c_i, form a list of the neighboring positions n_ij that are occupied by S's
        # We interpret neighboring positions to include the extended, prime neighbourhood
        c = [Vector(j,i) for i in range(SIZE) for j in range(SIZE) if isinstance(self.a[i][j], Catalyst) ]
        l = []
        NHOOD = N[1:] + N_PRIME[1:] # Use prime neighbourhood to achieve results closer to POBA
        for i in range(len(c)):
            n = [c[i].add(v) for v in NHOOD if isinstance(self.neighbour(c[i],v), Substrate) ]
            
            # 4.1.1 Delete from the list of n_ij all positions for which neither adjacent neighbor position appears in the list
            # i.e. a 1 must be deleted from the list of n_ij if neither 5 nor 6 appears 
            # and a 6 must be deleted if neither 1 nor 2 appears
            n = [v for v in n if reduce(lambda a,b: a or b, map(lambda w: orthogonallyAdjacent(v, w), n)) ]
            
            # 4.2 For each c_i with a non-null list of n_ij, choose randomly one of the n_ij, let its value be p_i,
            # and at the corresponding location replace the S by a free L.
            if len(n)>0:
                pi = n[randint(0,len(n)-1)]
                self.setCell(pi, Link())
                l.append(pi)
                self.countS -= 1
                self.countL += 1
                
                # 4.2.1 If the list of n_ij contains only one that is adjacent to p_i, then remove the corresponding S
                adj = [ v for v in n if orthogonallyAdjacent(pi,v) ] 
                if len(adj)==1:
                    self.setCell(adj[0], None)
                    self.countS -= 1
                                    
                # 4.2.2 If the list of n_ij contains both locations adjacent to p_i, randomly select the S to be removed.
                else:
                    self.setCell(adj[randint(0,len(adj)-1)], None)
                    self.countS -= 1
                
        # 4.3 Bond each produced L if possible
        for li in l:
            assert isinstance(self.cell(li), Link) and len(self.cell(li).bonds)==0
            self.bonding(li)


    def breakBonds(self, c):
        # surrounding links
        n = [c.add(v) for v in N[1:] if inRange(c,v) and isinstance(self.neighbour(c,v), Link) ]
        for ni in n:
            for b in self.cell(ni).bonds:
                if ni.add(N[b])==c:
                    self.pairUnbond(ni,c)


    # 5. Disintegration

    def disintegration(self):
        r = []
        # 5.1 For each L, bonded or unbonded, select a random real number d in the range (0,1).
        l = [Vector(j,i) for i in range(SIZE) for j in range(SIZE) if isinstance(self.a[i][j], Link) ]
        for li in l:
            d = random()
            # 5.1.1. If d<= Pd (Pd an adjustable parameter of the algorithm), 
            # then remove the corresponding L, and attempt to rebond (rule 7).
            if d<=Pd:
                self.breakBonds(li)
                self.setCell(li, Substrate())
                self.rebond(li)
                self.countL -= 1
                self.countS += 1
                
                # produce the second S
                # holes in the local and prime neighbourhoods
                nh = [li.add(v) for v in N[1:] if inRange(li,v) and self.neighbour(li,v) is None ]
                nx = [li.add(v) for v in N_PRIME[1:] if inRange(li,v) and self.neighbour(li,v) is None ]
                if len(nh)>0:
                    p = nh[randint(0,len(nh)-1)]
                    self.setCell(p, Substrate())
                    self.countS += 1

                elif len(nx)>0: # no holes in the immediate neighbourhood, check prime neighbourhood 1' to 4'
                    p = nx[randint(0,len(nx)-1)]
                    self.setCell(p, Substrate())
                    self.countS += 1

                else: # find any hole
                    h = [Vector(j,i) for i in range(SIZE) for j in range(SIZE) if self.a[i][j] is None]
                    p = h[randint(0,len(h)-1)]
                    self.setCell(p, Substrate())
                    self.countS += 1

            # 5.1.2 Otherwise proceed to next L
            continue


    # 6. Bonding

    def bonding(self,li):
        # 6.1. Form a list of the neighboring positions n_i that contain free L's 
        # and the neighboring positions m_i that contain singly bonded L's.
        # all Varela's examples in POBC show an orthologonal bonding neighbourhood N[1:ORTHOGONAL]
        # Alternatively use N[1:] to include diagonally orthogonal cells (but this suffers from crossovers)
        m = [li.add(v) for v in N[1:] if inRange(li,v) and \
            isinstance(self.neighbour(li,v), Link) and len(self.neighbour(li,v).bonds)==1 ]
        n = [li.add(v) for v in N[1:] if inRange(li,v) and \
            isinstance(self.neighbour(li,v), Link) and len(self.neighbour(li,v).bonds)==0 ]
        
        # 6.2. Drop from the m_i any that would result in a bond angle less that 90 degrees.
        # This is unnecessary if bonds can only form orthogonally
        m = [ v for v in m if acute(li,v.add(N[self.cell(v).bonds[0]])) ]
            
        # 6.3. If there are two or more of the m_i, select two, form the corresponding bonds, and exit.
        shuffle(m)
        if len(m)>=2:
            # run through all possible pairings, ruling out pairs already bonded to each other
            for i in range(len(m)):
                for j in range(i+1,len(m)):
                    if acute(m[i],m[j]) and not self.bonded(m[i],m[j]):
                        self.pairBond(li,m[i])
                        self.pairBond(li,m[j])
                        return

        # 6.4. If there is exactly one m_i, form the corresponding bond.
        if len(m)==1:
            self.pairBond(li,m[0])
            
            # 6.4.1. Remove from the n_i any that would now result in a bond angle of less than 90 degrees
            n = [ v for v in n if acute(v,li.add(N[self.cell(li).bonds[0]])) ]
        
            # 6.4.2. If there are no n_i, exit
            if len(n)==0:
                return
            
            # 6.4.3. Select one of the n_i, form the bond and exit.
            self.pairBond(li,n[randint(0,len(n)-1)])
            return
            
        # 6.5. If there are no n_i, exit
        if len(n)==0:
            return
        
        # 6.6. Select one of the n_i, form the corresponding bond, and drop it from the list
        shuffle(n)
        self.pairBond(li,n.pop())
            
        # 6.6.1. If the n_i list is non-null, execute steps 6.4.1 through 6.4.3
        if len(n)>0:
            n = [ v for v in n if acute(v,li.add(N[self.cell(li).bonds[0]])) ]
            if len(n)>0:
                self.pairBond(li,n[randint(0,len(n)-1)])
            
        # 6.6.2. Exit.
        return


    # 7. Rebond
        
    def rebond(self, c):       
        # 7.1. Form a list of all neighbor positions m_i, occupied by singly bonded L's
        m = [c.add(v) for v in N[1:] if inRange(c,v) and \
            isinstance(self.neighbour(c,v), Link) and len(self.neighbour(c,v).bonds)==1 ]
        
        # 7.2. Form a second list, p_u, of pairs of the m_i that can be bonded
        # pairs must be adjacent and unbonded to each other
        p = [ (m[i],m[j]) for i in range(len(m)-1) for j in range(i+1,len(m)) \
            if orthogonallyAdjacent(m[i],m[j]) and not self.bonded(m[i],m[j]) ]
            
        # 7.3. If there are any p_u, choose a maximal subset and form the bonds. Remove the L's involved from the list m_i.
        # No pairs should share a common cell
        s = [s for s in powerset(p) for pu in s if not reduce(lambda a,b: a or b, map(lambda x: commonCell(pu, x), s)) ]
        s = sorted(s, key=lambda x: len(x), reverse=True) # maximal subset will be first in the list
        if len(s)>0:
            for pair in s[0]: # form a bonded pair
                self.pairBond(pair[0],pair[1])
                m.remove(pair[0])
                m.remove(pair[1])
        
        # 7.4. Add to the bond m_i any neighbor locations occupied by free L's
        m = m + [c.add(v) for v in N[1:] if inRange(c,v) and \
            isinstance(self.neighbour(c,v), Link) and len(self.neighbour(c,v).bonds)==0 ]
    
        # 7.5. Execute steps 7.1 (7.2) through 7.3; then exit
        p = [ (m[i],m[j]) for i in range(len(m)-1) for j in range(i+1,len(m)) \
            if orthogonallyAdjacent(m[i],m[j]) and not self.bonded(m[i],m[j]) ]
        s = [s for s in powerset(p) for pu in s if not reduce(lambda a,b: a or b, map(lambda x: commonCell(pu, x), s)) ]
        s = sorted(s, key=lambda x: len(x), reverse=True) # maximal subset will be first in the list
        if len(s)>0:
            for pair in s[0]: # form a bonded pair
                self.pairBond(pair[0],pair[1])

    def Step(self):
        self.motion()
        self.motionL()
        #self.motionK() # results closer to the examples in POBC without K actively moving
        self.production()
        self.disintegration()

    def drawBonds(self):
        for i in range(SIZE):
            for j in range(SIZE):
                if isinstance(self.a[i][j],Link):
                    self.a[i][j].drawBonds(j*SPACING+MARGIN+EXTENT/2,i*SPACING+MARGIN+EXTENT/2)
                    
    def drawCells(self):
        for i in range(SIZE):
            for j in range(SIZE):
                if self.a[i][j] is not None:
                    self.a[i][j].draw(j*SPACING+MARGIN+EXTENT/2,i*SPACING+MARGIN+EXTENT/2)

    def draw(self):
        # draw bonds first so they appear behind the circles
        self.drawBonds()
        self.drawCells()    

if __name__ == "__main__":
    ca = CA(CATALYSTS)
    while True:
        window.fill(WHITE)
        ca.Step()
        ca.draw()
        pygame.display.update()
        frameCount += 1
        #pygame.image.save(window, "frames/frame"+str(frameCount)+".png")
        # check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        frameRate.tick(FPS)
