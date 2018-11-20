import pygame
from objects import *


class Events:
    up = left = right = action = False

    @staticmethod
    def update():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    Events.up = True
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    Events.left = True
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    Events.right = True
                elif event.key == pygame.K_SPACE:
                    Events.action = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    Events.up = False
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    Events.left = False
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    Events.right = False
                elif event.key == pygame.K_SPACE:
                    Events.action = False


class Game:
    background = (0, 0, 1)

    # print(point_in_triangle([1, 1], ([0, 0], [1, 0], [0, 1])))
    # print(point_in_triangle([0.5, 0.5], ([0, 0], [1, 0], [0, 1])))
    #
    # print(point_in_polygon([-1, -1], [1, 1], [[0, 0], [2, 0], [2, 2], [0, 2]]))
    # print(point_in_polygon([1, 0.5], [1, 1], [[0, 0], [2, 0], [2, 2], [0, 2]]))
    # print(point_in_polygon([1, 0.5], [1, 1], [[0, 0], [2, 0], [2, 2], [0, 2]]))

    def __init__(self):
        self.run = True
        self.clock = pygame.time.Clock()

        pygame.display.init()
        self.surf = pygame.display.set_mode([width, height])
        pygame.display.set_caption("Asteroids")
        pygame.display.set_icon(pygame.image.load('img/icon.png'))

        self.ship = Ship([400, 300])
        self.asteroids = Asteroid()

    def update(self):
        Events.update()

        if Events.up:
            self.ship.for_speed = 2.5

        if Events.left:
            self.ship.ang_speed = -0.025
        elif Events.right:
            self.ship.ang_speed = 0.025

        if Events.action:
            self.ship.shoot()

        self.ship.update()
        self.asteroids.update()

    def draw(self):
        self.surf.fill(Game.background)
        self.ship.draw(self.surf)
        self.asteroids.draw(self.surf, thick=3)
        pygame.display.update()


game = Game()

while game.run:
    game.update()
    game.draw()

    game.clock.tick(120)
