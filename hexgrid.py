import math
import pygame

row, col = 8, 12

hex_radius = 50
hex_width = 2 * hex_radius
hex_height = math.sqrt(3) * hex_width / 2

class Hex:
    def __init__(self, n, m, value):
        self.n = n
        self.m = m
        offset = hex_height * 0.5
        self.cx = (n * hex_width * 0.75) + (hex_width * 0.5)
        self.cy = (m * hex_height) + (hex_height * 0.5) + (n%2 * offset)
        self.value = value
        self.points = []
        for i in range(6):
            px = self.cx + hex_radius*math.cos(i*math.pi/3)
            py = self.cy + hex_radius*math.sin(i*math.pi/3)
            p = (px, py)
            self.points.append(p)

    def draw(self):
        color = (255 * self.n / col, 255 * self.m / row, 255)
        pygame.draw.polygon(screen, color, self.points, 3)
        text = font.render("%d, %d" % (self.n, self.m), True, color)
        text_rect = text.get_rect()
        text_rect.center = (self.cx, self.cy)
        screen.blit(text, text_rect)

hexgrid = {}
v = 0
for m in range(row):
    for n in range(col):
        v += 1
        hexgrid[(n, m)] = Hex(n, m, v)

pygame.init()
screen = pygame.display.set_mode((0.75*col*hex_width + hex_width/4, row*hex_height + hex_height/2))
font = pygame.font.Font(None, 36)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    for hex in hexgrid.values():
        hex.draw()
    pygame.display.flip()

pygame.quit()
