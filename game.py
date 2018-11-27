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
                elif event.key == pygame.K_ESCAPE:
                    game.run = False
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

    def __init__(self):
        pygame.init()
        
        self.run = True
        self.clock = pygame.time.Clock()

        pygame.display.init()
        self.surf = pygame.display.set_mode([width, height])
        pygame.display.set_caption("Asteroids")
        pygame.display.set_icon(pygame.image.load('img/icon.png'))

        self.ship = Ship([400, 300])


        self.waves = [
            Wave(self, [[1, 2]]),
            Wave(self, [[3, 1], [1, 2]]),
            Wave(self, [[3, 2]]),
            Wave(self, [[2, 1], [1, 3]]),
            Wave(self, [[12, 1]]),
        ]


        self.wave = self.waves[0]
        self.nb_wave = 0

        self.stars = Stars(self, [0, 0])

        self.last_text = [None, None]

        self.score = 0
        self.timer = 0

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

        self.stars.update()

        self.wave.update()
        if(len(self.wave.tab) == 0):
            self.wave = self.waves[self.nb_wave]
            self.nb_wave += 1

        self.timer += 1

    def text(self, text, size, pos):
        if text != self.last_text[0]:
            font = pygame.font.Font("font/kongtext.ttf", size)
            self.last_text[0] = text
            self.last_text[1] = font.render(text, False, (255, 255, 255))
        rect = self.last_text[1].get_rect()
        rect.left = pos[0]
        rect.top = pos[1]
        self.surf.blit(self.last_text[1], rect)

    def draw(self):
        self.surf.fill(Game.background)
        self.stars.draw(self.surf)
        
        self.ship.draw(self.surf)

        self.wave.draw(self.surf)

        self.draw_ui()
        pygame.display.update()

    def draw_ui(self):
        str_score = str(self.score)
        for i in range(str_score.__len__(), 10):
            str_score = "0" + str_score
        self.text(str_score, 15, (10, 10))


game = Game()

while game.run:
    game.update()
    game.draw()

    game.clock.tick(120)
