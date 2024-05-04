import math
import queue
import pygame

# parameters
ROW, COL = 13, 21
HEX_RADIUS = 40
HEX_WIDTH = 2 * HEX_RADIUS
HEX_HEIGHT = math.sqrt(3) * HEX_WIDTH / 2

class Hex:
    def __init__(self, n, m, v):
        # ROW and COL coords
        self.n = n
        self.m = m

        # translate to axial coords
        self.r = self.n - math.floor(0.5 * COL)
        self.s = -self.m - math.ceil(0.5 * self.n) + math.ceil(0.5 * COL)
        self.t = -self.r - self.s # 0=r+s+t

        # pixel coords of centerpoint
        self.cx = (n * HEX_WIDTH * 0.75) + (HEX_WIDTH * 0.5)
        self.cy = (m * HEX_HEIGHT) + (HEX_HEIGHT * 0.5) + (n%2 * HEX_HEIGHT * 0.5)

        # set initial values
        self.baseValue = v
        self.effValue = self.baseValue
        self.modified = True

        # define the vertices of the hex
        self.points = []
        for i in range(6):
            px = self.cx + HEX_RADIUS*math.cos(i*math.pi/3)
            py = self.cy + HEX_RADIUS*math.sin(i*math.pi/3)
            p = (px, py)
            self.points.append(p)

    def toString(self):
        return "(%d, %d, %d): %d (%d)" % (self.r, self.s, self.t, self.effValue, self.baseValue)

    def getNeighbors(self):
        neighbors = []

        # grab the zix surrounding hexes
        neighbors.append(hexgrid.get((self.r-1, self.s+1, self.t)))
        neighbors.append(hexgrid.get((self.r-1, self.s, self.t+1)))
        neighbors.append(hexgrid.get((self.r+1, self.s-1, self.t)))
        neighbors.append(hexgrid.get((self.r+1, self.s, self.t-1)))
        neighbors.append(hexgrid.get((self.r, self.s-1, self.t+1)))
        neighbors.append(hexgrid.get((self.r, self.s+1, self.t-1)))

        # only return real hexes
        neighbors = list(filter(lambda x: x is not None, neighbors))

        return neighbors

    def getDist(self, other):
        # manhatten distance
        dr = abs(self.r - other.r)
        ds = abs(self.s - other.s)
        dt = abs(self.t - other.t)

        # each step is a difference of two
        return (dr + ds + dt) / 2

    def setValue(self, newValue):
        self.baseValue = newValue
        self.modified = True

        q = queue.Queue()
        q.put(self)

        # breadth first propogation
        while not q.empty():
            hex = q.get()

            neighbors = hex.getNeighbors()

            # strength decays by 1 per step
            propValue = max([n.effValue for n in neighbors]) - 1

            # only propogate if a change is made
            oldValue = hex.effValue
            newValue = max(hex.baseValue, propValue, 0)
            if oldValue is not newValue:
                hex.effValue = newValue
                hex.modified = True
                for n in neighbors:
                    q.put(n)

    def incr(self):
        self.setValue(self.baseValue + 1)

    def decr(self):
        self.setValue(self.baseValue - 1)

    def setColor(self, color=None):
        if color is None:
            # shade hex based on value
            red = 255
            green = 255 - min(255 * self.effValue * 0.1, 255) if self.effValue > 0 else 255
            blue = 0
            self.color = (red, green, blue)
        else:
            self.color = color

class HexSprite(pygame.sprite.Sprite):
    def __init__(self, hex):
        # extends the base sprite class
        super().__init__()

        # creates a sprite from the associated hex
        self.hex = hex
        self.image = pygame.Surface((HEX_WIDTH, HEX_HEIGHT), pygame.SRCALPHA)
        self.draw()

    def draw(self, color=None):
        if self.hex.modified:
            # reset the drawing area to black
            pygame.draw.polygon(screen, (0, 0, 0), self.hex.points)

            # set the color to draw with
            self.hex.setColor(color)

            # draw the hex itself
            pygame.draw.polygon(screen, self.hex.color, self.hex.points, 3)

            # draw the coords along the bottom edge
            font = pygame.font.Font(None, 14)
            text = font.render(f"({self.hex.r}, {self.hex.s}, {self.hex.t})", True, self.hex.color)
            textRect = text.get_rect()
            textRect.center = (self.hex.cx, self.hex.cy + HEX_HEIGHT * 0.4)
            screen.blit(text, textRect)

            # draw the values at the center
            font = pygame.font.Font(None, 36)
            text = font.render(f"{self.hex.effValue} ({self.hex.baseValue})", True, self.hex.color)
            textRect = text.get_rect()
            textRect.center = (self.hex.cx, self.hex.cy)
            screen.blit(text, textRect)

            # changes have been recorded
            self.hex.modified = False

def pointDist(p1, p2):
    # pythagorean theorem
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def nearestHex(hexgrid, mousePos):
    # compute rough ROW COL coords
    mousex, mousey = mousePos
    n = math.floor(mousex / (HEX_WIDTH * 0.75))
    m = math.floor(mousey / HEX_HEIGHT)

    # convert to axial coords
    r = n - math.floor(0.5 * COL)
    s = -m - math.ceil(0.5 * n) + math.ceil(0.5 * COL)
    t = -r - s # 0=r+s+t

    # search rough guess and its neighbors
    guess = hexgrid.get((r, s, t))
    if guess is not None:
        candidates = [guess] + guess.getNeighbors()
    else:
        # literal edge case
        guess = Hex(n, m, 0)
        # don't include the fake hex
        candidates = guess.getNeighbors()

    # find smallest distance
    minDist = float('inf')
    nearestHex = None
    for hex in candidates:
        dist = pointDist(mousePos, (hex.cx, hex.cy))
        if dist < minDist:
            minDist = dist
            nearestHex = hex

    # only return when actually over a hex
    if minDist < HEX_RADIUS:
        return nearestHex

# setup the game screen
pygame.init()
screen = pygame.display.set_mode((0.75 * COL * HEX_WIDTH + 0.25 * HEX_WIDTH,
ROW * HEX_HEIGHT + 0.5 * HEX_HEIGHT))
screen.fill((0, 0, 0))

# create a sprite group
hexSprites = pygame.sprite.Group()

# create the map
hexgrid = {}
for m in range(ROW):
    for n in range(COL):
        hex = Hex(n, m, 0)

        # store using the axial coords
        hexgrid[(hex.r, hex.s, hex.t)] = hex

        # make a hex sprite and add to the group
        hexSprite = HexSprite(hex)
        hexSprites.add(hexSprite)

# main loop
running = True
mouse_pos = (0, 0)
activeHex = None
while running:
    # update the active hex
    oldActiveHex = activeHex
    mousePos = pygame.mouse.get_pos()
    activeHex = nearestHex(hexgrid, mousePos)

    # record the change
    if oldActiveHex:
        oldActiveHex.modified = True
    if activeHex:
        activeHex.modified = True

    # event handling
    for event in pygame.event.get():
        # check for quit
        if event.type == pygame.QUIT:
            running = False
            break

        # handle incr, decr, and reset
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # left click
                activeHex.incr()
            elif event.button == 3: # right click
                activeHex.decr()
            elif event.button == 2: # middle click
                activeHex.setValue(0)

    # render hexes
    for sprite in hexSprites:
        # active hex is blue
        sprite.draw((0, 0, 255) if sprite.hex is activeHex else None)
    pygame.display.flip()

pygame.quit()
