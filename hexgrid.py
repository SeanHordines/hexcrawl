import math
import pygame

# parameters
row, col = 13, 21
hex_radius = 40
hex_width = 2 * hex_radius
hex_height = math.sqrt(3) * hex_width / 2

class Hex:
    def __init__(self, n, m, v, c=(255, 255, 255)):
        # row and col coords
        self.n = n
        self.m = m

        # axial coords
        self.r = self.n - math.floor(0.5 * col)
        self.s = -self.m - math.ceil(0.5 * self.n) + math.ceil(0.5 * col)
        self.t = -self.r - self.s

        # pixel coords of centerpoint
        self.cx = (n * hex_width * 0.75) + (hex_width * 0.5)
        self.cy = (m * hex_height) + (hex_height * 0.5) + (n%2 * hex_height * 0.5)

        self.v = v
        self.c = c

        # define the vertices of the hex
        self.points = []
        for i in range(6):
            px = self.cx + hex_radius*math.cos(i*math.pi/3)
            py = self.cy + hex_radius*math.sin(i*math.pi/3)
            p = (px, py)
            self.points.append(p)

    def draw(self):
        # color based on hex parameters
        color = (255, 255 - 255 * self.v / 10, 0)

        # draw the hex itself
        pygame.draw.polygon(screen, (255, 255, 255), self.points, 3)

        # draw the coords
        font = pygame.font.Font(None, 14)
        text = font.render("(%d, %d, %d)" % (self.r, self.s, self.t), True, color)
        text_rect = text.get_rect()
        text_rect.center = (self.cx, self.cy + hex_height * 0.4)
        screen.blit(text, text_rect)

        # draw the value
        font = pygame.font.Font(None, 36)
        text = font.render("%d" % (self.v), True, color)
        text_rect = text.get_rect()
        text_rect.center = (self.cx, self.cy)
        screen.blit(text, text_rect)

    def setValue(self, v):
        self.v = v

        # no need to propogate 0
        if self.v == 1:
            return

        neighbors = self.getNeighbors()
        for n in neighbors:
            if n is None: # skip if out of bounds
                continue
            if n.v >= self.v: # skip if change would be lower
                continue
            n.setValue(self.v - 1)

    def getNeighbors(self):
        neighbors = []

        neighbors.append(hexgrid.get((self.r-1, self.s+1, self.t)))
        neighbors.append(hexgrid.get((self.r-1, self.s, self.t+1)))
        neighbors.append(hexgrid.get((self.r+1, self.s-1, self.t)))
        neighbors.append(hexgrid.get((self.r+1, self.s, self.t-1)))
        neighbors.append(hexgrid.get((self.r, self.s-1, self.t+1)))
        neighbors.append(hexgrid.get((self.r, self.s+1, self.t-1)))

        return neighbors

    def getDist(self, other):
        dr = abs(self.r - other.r)
        ds = abs(self.s - other.s)
        dt = abs(self.t - other.t)
        return (dr + ds + dt) / 2

# create the map
hexgrid = {}
for m in range(row):
    for n in range(col):
        hex = Hex(n, m, 0)
        hexgrid[(hex.r, hex.s, hex.t)] = hex

# hexgrid.get((0, 0, 0)).setValue(10)
hexgrid.get((2, 3, -5)).setValue(10)
print(hexgrid.get((0, 0, 0)).getDist(hexgrid.get((2, 3, -5))))

# setup the game screen
pygame.init()
screen = pygame.display.set_mode((0.75 * col * hex_width + 0.25 * hex_width,
    row * hex_height + 0.5 * hex_height))

# main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # render hexes
    screen.fill((0, 0, 0))
    for hex in hexgrid.values():
        hex.draw()
    pygame.display.flip()

pygame.quit()
