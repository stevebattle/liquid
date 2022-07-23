from processing_py import *
from random import random, randint, shuffle
from functools import reduce
from math import radians
from time import sleep

SIDE = 400
SIZE = 10
MARGIN = 50
SPACING = (SIDE-MARGIN*2)/10
EXTENT = SPACING - 5
DELAY = 100

# Pd an adjustable parameter of the algorithm
# A disintegration probability of less than about 0.01 per time step is required
Pd = 0.01

app = App(SIDE,SIDE)

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

class Substrate:
    def draw(self,x,y): # draw a circle
        app.pushStyle()
        app.noFill()
        app.strokeWeight(2)
        app.ellipse(x,y,EXTENT,EXTENT)
        app.popStyle()

class Catalyst:
    def draw(self,x,y): # draw an asterisk
        app.pushStyle()
        app.strokeWeight(2)
        app.pushMatrix()
        app.translate(x,y)
        for i in range(3):
            app.line(0,-EXTENT/4,0,EXTENT/4)
            app.rotate(radians(60))
        app.popMatrix()
        app.popStyle()
        
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
        app.pushStyle()
        app.noFill()
        app.strokeWeight(2)
        app.rectMode(CENTER)
        app.rect(x,y,EXTENT,EXTENT)
        app.fill(255)
        app.ellipse(x,y,EXTENT*0.7,EXTENT*0.7)
        app.popStyle()
    def drawBonds(self,x,y):
        app.pushStyle()
        app.strokeWeight(2)
        for b in self.bonds:
            app.line(x,y,x+N[b].x*SPACING/2,y+N[b].y*SPACING/2)
        app.popStyle()

# An holey array
a = [[ None for i in range(SIZE) ] for j in range(SIZE) ]

# Local neighbourhood N of adjacent cells (including diagonally adjacent)
# Designation of coordinates of neighboring space with reference to a middle space with designation 0.

N = [Vector(0,0),Vector(-1,0),Vector(0,-1),Vector(1,0),Vector(0,1),
     Vector(-1,1),Vector(-1,-1),Vector(1,-1),Vector(1,1)]

ORTHOGONAL = 5 # orthogonal neighbours only slice of N. e.g. N[1:5]

# prime neighbourhood NX 1' to 4', including middle space with designation 0 to align with N
N_PRIME = [Vector(0,0),Vector(0,-2),Vector(-2,0),Vector(0,2),Vector(2,0)]

def inRange(c,n):
    v = c.add(n)
    return v.x in range(SIZE) and v.y in range(SIZE)    

def cell(c):
    return a[c.y][c.x]

def setCell(c,v):
    a[c.y][c.x] = v

def pairBond(l,m):
    cell(l).bond(l,m)
    cell(m).bond(m,l)

def pairUnbond(l,m):
    cell(l).unbond(l,m)
    cell(m).unbond(m,l)
    
def bonded(l,m):
    d = m.subtract(l)
    return d in N and N.index(d) in cell(l).bonds

# returns None for coordinates outside the space
def neighbour(c,n):
    v = c.add(n)
    return a[v.y][v.x] if v.x in range(SIZE) and v.y in range(SIZE) else None

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

# 1. Motion, first step

def motion():
    # 1.1. Form a list of the coordinates of all holes h_i
    h = [Vector(j,i) for i in range(SIZE) for j in range(SIZE) if a[i][j] is None]
    
    # 1.2. For each h_i make a random selection n_i in the range 1 through 4, specifying a neighboring location
    n = [randint(1,4) for i in h]
    
    # 1.3. For each h_i in turn, where possible, move occupant of selected neighboring location in h_i
    for i in range(len(h)):
        # neighboring location
        ni = h[i].add(N[n[i]])
        
        # 1.3.1. If the neighbor is a hole or lies outside the space, take no action
        if not(ni.x in range(SIZE) and ni.y in range(SIZE)) or cell(ni) is None:
            continue
        if cell(h[i]) is not None: # CONFIRM h_i IS STILL A HOLE
            continue
        
        # 1.3.2. If the neighbor n_i contains a bonded L, examine the location n_i'.
        # If n_i' contains an S, move this S to h_i.
        if isinstance(cell(ni), Link) and len(cell(ni).bonds)>0:
            ni_prime = h[i].add(N_PRIME[n[i]])
            if ni_prime.x in range(SIZE) and ni_prime.y in range(SIZE) \
                and isinstance(cell(ni_prime), Substrate):
                # the bonds are permeable to S
                setCell(h[i], cell(ni_prime))
                setCell(ni_prime, None)
            continue
            
        # move occupant of selected neighboring location in h_i
        setCell(h[i], cell(ni))
        setCell(ni, None)
        
        # 1.4. Bond any moved L, if possible (rule 6)
        if isinstance(cell(h[i]), Link):
            bonding(h[i])

# 2.3.2. If the location specified by n_i contains an S, the S will be displaced.
# z displaces s

def displaceS(z,s,allowExchange):
    
    # 2.3.2.1. If there is a hole adjacent to the S, it will move into it. If more than one such hole, select randomly
    # holes adjacent to S
    nh = [s.add(v) for v in N[1:] if inRange(s,v) and neighbour(s,v) is None ]
    if len(nh)>0:
        p = nh[randint(0,len(nh)-1)]
        setCell(p, cell(s)) # displaced S
        setCell(s, cell(z)) # motile z      
        setCell(z, None) # backfill with space
        return True
    
    # 2.3.2.2. If the S can be moved into a hole by passing through bonded links, as in step 1, then it will do so.
    # positions opposite orthogonally adjacent bonded links
    b = [N_PRIME[N.index(v)] for v in N[1:5] if inRange(s,v) and isinstance(neighbour(s,v),Link) and len(neighbour(s,v).bonds)>0 ]
    # holes in prime neighbourhood of S opposite bonded links
    nh = [s.add(v) for v in b if inRange(s,v) and neighbour(s,v) is None ]
    if len(nh)>0:
        p = nh[randint(0,len(nh)-1)]
        setCell(p, cell(s)) # displace S through bonded links
        setCell(s, cell(z)) # motile z      
        setCell(z, None) # backfill with space
        return True
    
    # 2.3.2.3. If the S cannot be moved into a hole, it will exchange locations with the moving L.    
    if allowExchange:
        swap = cell(s) # displaced S
        setCell(s, cell(z)) # motile z
        setCell(z, swap)
        return True
    
    return False


# Rule 2.3. Where possible, move the L occupying the location m_i into the specified neighboring location
# returns a boolean indicating if the move was successful

def moveL(l,ni,allowExchange):
    # holes adjacent to the neighbour
    nh = [ni.add(v) for v in N if inRange(ni,v) and neighbour(ni,v) is None ]
    
    # 2.3.1. If the location specified by n_i contains another L, or a K, take no action
    # 2.3.2. If the location specified by n_i contains an S, the S will be displaced.
    if isinstance(cell(ni), Substrate):
        return displaceS(l,ni,True)
        
    # 2.3.3. If the location specified by n_i is a hole, then L simply moves into it.
    elif cell(ni) is None:
        setCell(ni, cell(l)) # L moves into the hole        
        setCell(l, None)
        return True
    
    return False
                        
# 2. Motion, second step

def motionL():
    # 2.1. Form a list of the coordinates of free L's, m_i
    m = [Vector(j,i) for i in range(SIZE) for j in range(SIZE) if isinstance(a[i][j],Link) and len(a[i][j].bonds)==0 ]
    
    l = [] # list of moved L
    
    # 2.2. For each m_i make a random selection, n_i, in the range 1 through 4, specifying a neighboring location.
    n = [randint(1,4) for i in m]
    for i in range(len(m)):
        # neighbour
        ni = m[i].add(N[n[i]])
        if not(ni.x in range(SIZE) and ni.y in range(SIZE)):
            continue
        
        # 2.3. Where possible, move the L occupying the location m_i into the specified neighboring location
        if moveL(m[i],ni,True):
            l.append(ni) # moved
        
    # 2.4. Bond each moved L, if possible
    for li in l:
        if isinstance(cell(li),Link) and len(cell(li).bonds)==0:
            bonding(li)


# 3 Motion, third step

def motionK():
    # 3.1. Form a list of the coordinates of all K's, c_i
    c = [Vector(j,i) for i in range(SIZE) for j in range(SIZE) if isinstance(a[i][j],Catalyst) ]
    
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
        if isinstance(cell(ni),Link) and len(cell(ni).bonds)==0:
            # immediate neighbourhood of L
            nh = [ni.add(v) for v in N[1:] if inRange(ni,v) ]
            shuffle(nh)
            for h in nh:
                if moveL(ni,h,False): # L displaced according to the rules of 2.3 (no exchange leaves ni free)
                    setCell(ni, cell(c[i])) # K moved into its place
                    setCell(c[i], None)
                    moved = True
                    break
                
        # 3.3.3. If the location specified by n_i contains an S, then move the S by the rules of 2.3.2.
        if isinstance(cell(ni),Substrate):
            displaceS(c[i],ni,True)
            
        # 3.3.4. If the location specified by n_i contains a free L not movable by the rules of 2.3,
        # then exchange the positions of the K and the L. (Bond L if possible.)
        elif not moved and isinstance(cell(ni),Link) and len(cell(ni).bonds)==0:
            swap = cell(ni) # displaced L
            setCell(ni, cell(c[i])) # motile K
            setCell(c[i], swap)
            
        # 3.3.5. If the location specified by n_i is a hole, the K moves into it.
        elif cell(ni) is None:
            setCell(ni, cell(c[i])) # motile K 
            setCell(c[i], None)


# 4. Production

def production():
    # 4.1 For each catalyst c_i, form a list of the neighboring positions n_ij that are occupied by S's
    c = [Vector(j,i) for i in range(SIZE) for j in range(SIZE) if isinstance(a[i][j], Catalyst) ]
    l = []
    for i in range(len(c)):
        n = [c[i].add(v) for v in N[1:] if isinstance(neighbour(c[i],v), Substrate) ]
        
        # 4.1.1 Delete from the list of n_ij all positions for which neither adjacent neighbor position appears in the list
        # i.e. a 1 must be deleted from the list of n_ij if neither 5 nor 6 appears 
        # and a 6 must be deleted if neither 1 nor 2 appears
        n = [v for v in n if reduce(lambda a,b: a or b, map(lambda w: orthogonallyAdjacent(v, w), n)) ]
        
        # 4.2 For each c_i with a non-null list of n_ij, choose randomly one of the n_ij, let its value be p_i,
        # and at the corresponding location replace the S by a free L.
        if len(n)>0:
            pi = n[randint(0,len(n)-1)]
            setCell(pi, Link())
            l.append(pi)
            
            # 4.2.1 If the list of n_ij contains only one that is adjacent to p_i, then remove the corresponding S
            adj = [ v for v in n if orthogonallyAdjacent(pi,v) ] 
            if len(adj)==1:
                setCell(adj[0], None)
                                
            # 4.2.2 If the list of n_ij contains both locations adjacent to p_i, randomly select the S to be removed.
            else:
                setCell(adj[randint(0,len(adj)-1)], None)
            
    # 4.3 Bond each produced L if possible
    for li in l:
        assert isinstance(cell(li), Link) and len(cell(li).bonds)==0
        bonding(li)

def breakBonds(c):
    # surrounding links
    n = [c.add(v) for v in N[1:] if inRange(c,v) and isinstance(neighbour(c,v), Link) ]
    for ni in n:
        for b in cell(ni).bonds:
            if ni.add(N[b])==c:
                pairUnbond(ni,c)


# 5. Disintegration

def disintegration():
    r = []
    # 5.1 For each L, bonded or unbonded, select a random real number d in the range (0,1).
    l = [Vector(j,i) for i in range(SIZE) for j in range(SIZE) if isinstance(a[i][j], Link) ]
    for li in l:
        d = random()
        # 5.1.1. If d<= Pd (Pd an adjustable parameter of the algorithm), 
        # then remove the corresponding L, and attempt to rebond (rule 7).
        if d<=Pd:
            breakBonds(li)
            setCell(li, Substrate())
            rebond(li)
            
            # produce the second S
            # holes in the local and prime neighbourhoods
            nh = [li.add(v) for v in N[1:] if inRange(li,v) and neighbour(li,v) is None ]
            nx = [li.add(v) for v in N_PRIME[1:] if inRange(li,v) and neighbour(li,v) is None ]
            if len(nh)>0:
                p = nh[randint(0,len(nh)-1)]
                setCell(p, Substrate())

            elif len(nx)>0: # no holes in the immediate neighbourhood, check extended neighbourhood 1' to 4'
                p = nx[randint(0,len(nx)-1)]
                setCell(p, Substrate())

            else: # find any hole
                h = [Vector(j,i) for i in range(SIZE) for j in range(SIZE) if a[i][j] is None]
                p = h[randint(0,len(h)-1)]
                setCell(p, Substrate())

        # 5.1.2 Otherwise proceed to next L
        continue


# 6. Bonding

def bonding(li):
    # 6.1. Form a list of the neighboring positions n_i that contain free L's 
    # and the neighboring positions m_i that contain singly bonded L's.
    # all Varela's examples show an orthologonal bonding neighbourhood N[1:ORTHOGONAL]
    m = [li.add(v) for v in N[1:ORTHOGONAL] if inRange(li,v) and isinstance(neighbour(li,v), Link) and len(neighbour(li,v).bonds)==1 ]
    n = [li.add(v) for v in N[1:ORTHOGONAL] if inRange(li,v) and isinstance(neighbour(li,v), Link) and len(neighbour(li,v).bonds)==0 ]
    
    # 6.2. Drop from the m_i any that would result in a bond angle less that 90 degrees.
    # This is unnecessary if bonds can only form orthogonally
    m = [ v for v in m if acute(li,v.add(N[cell(v).bonds[0]])) ]
        
    # 6.3. If there are two or more of the m_i, select two, form the corresponding bonds, and exit.
    shuffle(m)
    if len(m)>=2:
        # run through all possible pairings, ruling out pairs already bonded to each other
        for i in range(len(m)):
            for j in range(i+1,len(m)):
                if acute(m[i],m[j]) and not bonded(m[i],m[j]):
                    pairBond(li,m[i])
                    pairBond(li,m[j])
                    return

    # 6.4. If there is exactly one m_i, form the corresponding bond.
    if len(m)==1:
        pairBond(li,m[0])
        
        # 6.4.1. Remove from the n_i any that would now result in a bond angle of less than 90 degrees
        n = [ v for v in n if acute(v,li.add(N[cell(li).bonds[0]])) ]
    
        # 6.4.2. If there are no n_i, exit
        if len(n)==0:
            return
        
        # 6.4.3. Select one of the n_i, form the bond and exit.
        pairBond(li,n[randint(0,len(n)-1)])
        return
        
    # 6.5. If there are no n_i, exit
    if len(n)==0:
        return
    
    # 6.6. Select one of the n_i, form the corresponding bond, and drop it from the list
    shuffle(n)
    pairBond(li,n.pop())
        
    # 6.6.1. If the n_i list is non-null, execute steps 6.4.1 through 6.4.3
    if len(n)>0:
        n = [ v for v in n if acute(v,li.add(N[cell(li).bonds[0]])) ]
        if len(n)>0:
            pairBond(li,n[randint(0,len(n)-1)])
        
    # 6.6.2. Exit.
    return

def commonCell(a,b):
    return (a[0]==b[0] or a[0]==b[1] or a[1]==b[0] or a[1]==b[1]) and not a==b

# 7. Rebond
    
def rebond(c):       
    # 7.1. Form a list of all neighbor positions m_i, occupied by singly bonded L's
    m = [c.add(v) for v in N[1:] if inRange(c,v) and isinstance(neighbour(c,v), Link) and len(neighbour(c,v).bonds)==1 ]
    
    # 7.2. Form a second list, p_u, of pairs of the m_i that can be bonded
    # pairs must be adjacent and unbonded to each other
    p = [ (m[i],m[j]) for i in range(len(m)-1) for j in range(i+1,len(m)) if orthogonallyAdjacent(m[i],m[j]) and not bonded(m[i],m[j]) ]
        
    # 7.3. If there are any p_u, choose a maximal subset and form the bonds. Remove the L's involved from the list m_i.
    # No pairs should share a common cell
    s = [s for s in powerset(p) for pu in s if not reduce(lambda a,b: a or b, map(lambda x: commonCell(pu, x), s)) ]
    s = sorted(s, key=lambda x: len(x), reverse=True) # maximal subset will be first in the list
    if len(s)>0:
        for pair in s[0]: # form a bonded pair
            pairBond(pair[0],pair[1])
            m.remove(pair[0])
            m.remove(pair[1])
    
    # 7.4. Add to the bond m_i any neighbor locations occupied by free L's
    m = m + [c.add(v) for v in N[1:] if inRange(c,v) and isinstance(neighbour(c,v), Link) and len(neighbour(c,v).bonds)==0 ]
   
    # 7.5. Execute steps 7.1 through 7.3; then exit
    p = [ (m[i],m[j]) for i in range(len(m)-1) for j in range(i+1,len(m)) if orthogonallyAdjacent(m[i],m[j]) and not bonded(m[i],m[j]) ]
    s = [s for s in powerset(p) for pu in s if not reduce(lambda a,b: a or b, map(lambda x: commonCell(pu, x), s)) ]
    s = sorted(s, key=lambda x: len(x), reverse=True) # maximal subset will be first in the list
    if len(s)>0:
        for pair in s[0]: # form a bonded pair
            pairBond(pair[0],pair[1])

def step():
    motion()
    motionL()
    motionK()
    production()
    disintegration()

def drawBonds():
    # draw bonds so they appear behind the circles
    for i in range(SIZE):
        for j in range(SIZE):
            if  isinstance(a[i][j],Link):
                a[i][j].drawBonds(j*SPACING+MARGIN+EXTENT/2,i*SPACING+MARGIN+EXTENT/2)
                
def drawCells():
    for i in range(SIZE):
        for j in range(SIZE):
            if a[i][j] is not None:
                a[i][j].draw(j*SPACING+MARGIN+EXTENT/2,i*SPACING+MARGIN+EXTENT/2)

def setup():
    for i in range(SIZE):
        for j in range(SIZE):
            a[i][j] = Catalyst() if i==4 and j==4 else Substrate()

setup()
while True:
    app.background(255)
    app.fill(0)
    step()
    drawBonds()
    drawCells()
    app.redraw()
