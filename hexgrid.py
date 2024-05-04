import math
import queue
import pygame

# parameters
row, col = 13, 21
hex_radius = 40
hex_width = 2 * hex_radius
hex_height = math.sqrt(3) * hex_width / 2

class Hex:
    def __init__(self, n, m, v):
        # row and col coords
        self.n = n
        self.m = m

        # translate to axial coords
        self.r = self.n - math.floor(0.5 * col)
        self.s = -self.m - math.ceil(0.5 * self.n) + math.ceil(0.5 * col)
        self.t = -self.r - self.s # 0=r+s+t

        # pixel coords of centerpoint
        self.cx = (n * hex_width * 0.75) + (hex_width * 0.5)
        self.cy = (m * hex_height) + (hex_height * 0.5) + (n%2 * hex_height * 0.5)

        # set initial values
        self.baseValue = v
        self.effValue = self.baseValue

        # define the vertices of the hex
        self.points = []
        for i in range(6):
            px = self.cx + hex_radius*math.cos(i*math.pi/3)
            py = self.cy + hex_radius*math.sin(i*math.pi/3)
            p = (px, py)
            self.points.append(p)

    def toString(self):
        return "(%d, %d, %d): %d (%d)" % (self.r, self.s, self.t, self.effValue, self.baseValue)

    def draw(self, color=None):
        self.setColor(color)

        # draw the hex itself
        pygame.draw.polygon(screen, self.color, self.points, 3)

        # draw the coords
        font = pygame.font.Font(None, 14)
        text = font.render("(%d, %d, %d)" % (self.r, self.s, self.t), True, self.color)
        text_rect = text.get_rect()
        text_rect.center = (self.cx, self.cy + hex_height * 0.4)
        screen.blit(text, text_rect)

        # draw the value
        font = pygame.font.Font(None, 36)
        text = font.render("%d (%d)" % (self.effValue, self.baseValue), True, self.color)
        text_rect = text.get_rect()
        text_rect.center = (self.cx, self.cy)
        screen.blit(text, text_rect)

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
            newValue = max(hex.baseValue, propValue)
            if oldValue is not newValue:
                hex.effValue = newValue
                for n in neighbors:
                    q.put(n)

    def incr(self):
        self.setValue(self.baseValue + 1)

    def decr(self):
        self.setValue(self.baseValue - 1)

    def setColor(self, color):
        if color is None:
            # shade hex based on value
            red = 255
            green = 255 - min(255 * self.effValue * 0.1, 255) if self.effValue > 0 else 255
            blue = 0
            self.color = (red, green, blue)
        else:
            self.color = color

def pointDist(p1, p2):
    # pythagorean theorem
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def nearestHex(hexgrid, mousePos):
    # compute rough row col coords
    mousex, mousey = mousePos
    n = math.floor(mousex / (hex_width * 0.75))
    m = math.floor(mousey / hex_height)

    # convert to axial coords
    r = n - math.floor(0.5 * col)
    s = -m - math.ceil(0.5 * n) + math.ceil(0.5 * col)
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
    if minDist < hex_radius:
        return nearestHex

# create the map
hexgrid = {}
for m in range(row):
    for n in range(col):
        hex = Hex(n, m, 0)
        hexgrid[(hex.r, hex.s, hex.t)] = hex

# setup the game screen
pygame.init()
screen = pygame.display.set_mode((0.75 * col * hex_width + 0.25 * hex_width,
    row * hex_height + 0.5 * hex_height))
clock = pygame.time.Clock()

# main loop
running = True
mouse_pos = (0, 0)
activeHex = None
while running:
    clock.tick(30)

    mousePos = pygame.mouse.get_pos()
    activeHex = nearestHex(hexgrid, mousePos)

    # handle incr, decr, and reset
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                activeHex.incr()
            elif event.button == 3:
                activeHex.decr()
            elif event.button == 2:
                activeHex.setValue(0)

    # render hexes
    screen.fill((0, 0, 0))
    for hex in hexgrid.values():
        if hex is  not activeHex:
            hex.draw()
    # draw the active hex in blue
    if activeHex:
        activeHex.draw((0, 0, 255))
    pygame.display.flip()

pygame.quit()
