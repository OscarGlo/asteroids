import pygame
import math

width = 800
height = 600


def rotate_point(point, off, angle):
    s = math.sin(angle)
    c = math.cos(angle)

    x = off[0] * c - off[1] * s + point[0]
    y = off[0] * s + off[1] * c + point[1]

    return [x, y]


class Events:
    def __init__(self):
        self.up = self.left = self.right = False

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.up = True
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.left = True
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.right = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.up = False
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.left = False
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.right = False


class Ship:
    color = (255, 255, 255)
    rate = 0.0175

    def __init__(self, pos):
        self.pos = pos
        self.angle = math.pi/2
        self.speed = [0.0, 0.0]
        self.ang_speed = self.for_speed = 0

    def update(self):
        self.speed[0] = self.speed[0] * (1 - Ship.rate) + self.for_speed * math.cos(self.angle) * Ship.rate
        self.speed[1] = self.speed[1] * (1 - Ship.rate) + self.for_speed * math.sin(self.angle) * Ship.rate

        self.pos[0] += self.speed[0]
        self.pos[1] += self.speed[1]

        self.angle += self.ang_speed

        self.for_speed = 0
        self.ang_speed = 0

        # Cycle position
        if self.pos[0] >= width:
            self.pos[0] -= width
        elif self.pos[0] <= 0:
            self.pos[0] += width

        if self.pos[1] >= height:
            self.pos[1] -= height
        elif self.pos[1] <= 0:
            self.pos[1] += height

    def draw_one(self, surf, pos):
        pygame.draw.lines(surf, Ship.color, True, [
                                rotate_point(pos, [15, 0], self.angle),
                                rotate_point(pos, [-15, -15], self.angle),
                                rotate_point(pos, [-10, 0], self.angle),
                                rotate_point(pos, [-15, 15], self.angle)
                            ], 2)

    def draw(self, surf):
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                self.draw_one(surf, (self.pos[0] + width * i, self.pos[1] + height * j))


class Game:
    background = (0, 0, 1)

    def __init__(self):
        global width, height

        self.run = True
        self.clock = pygame.time.Clock()
        self.events = Events()

        pygame.display.init()
        pygame.display.set_mode([width, height])
        pygame.display.set_caption("Asteroids")
        pygame.display.set_icon(pygame.image.load('img/icon.png'))

        self.surf = pygame.display.get_surface()

        self.ship = Ship([400, 300])

    def update(self):
        self.events.update()

        if self.events.up:
            self.ship.for_speed = 2.5
        if self.events.left:
            self.ship.ang_speed = -0.025
        elif self.events.right:
            self.ship.ang_speed = 0.025

        self.ship.update()

    def draw(self):
        self.surf.fill(Game.background)
        self.ship.draw(self.surf)
        pygame.display.update()


game = Game()

while game.run:
    game.update()
    game.draw()

    game.clock.tick(120)
