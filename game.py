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


class Stars:
    def __init__(self, pos):
        self.pos = pos
        self.stars = []
        off = 50
        rand = 40
        for i in range(math.floor(width/off)):
            for j in range(math.floor(height/off)):
                self.stars.append([i * off + math.floor(random.random() * rand),
                                   j * off + math.floor(random.random() * rand)])

    def draw(self, surf):
        for star in self.stars:
            c = 100
            pygame.draw.rect(surf, (c, c, c),
                             pygame.rect.Rect(((self.pos[0] + star[0]) % width, (self.pos[1] + star[1]) % height),
                                              (2, 2)))


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

        self.stars = Stars([0, 0])

        self.ship = Ship([400, 300])
        self.asteroids = []

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

        pos1 = [self.ship.pos[0], self.ship.pos[1]]

        self.ship.update()
        for asteroid in self.asteroids:
            asteroid.update()

        self.stars.pos[0] += (self.ship.pos[0] - pos1[0]) % width / 5
        self.stars.pos[1] += (self.ship.pos[1] - pos1[1]) % height / 5

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
        for asteroid in self.asteroids:
            asteroid.draw(self.surf, thick=3)

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
