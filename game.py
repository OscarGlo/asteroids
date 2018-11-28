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
            Wave(self, [[3, 2]], "Wave 0"),
            Wave(self, [[3, 1], [1, 2]], "Wave 1"),
            Wave(self, [[3, 2]], "Wave 2"),
            Wave(self, [[2, 1], [1, 3]], "Wave 3"),
            Wave(self, [[12, 1]], "Wave 4"),
        ]

        self.wave = self.waves[0]
        self.nb_wave = 0

        self.stars = Stars(self, [0, 0])

        self.explode = ParticleGen([self.ship.pos[0], self.ship.pos[1]], 0, 2 * math.pi, 0, 3, 150)

        self.last_text = [[None, None], [None, None]]

        self.score = 0
        self.wave_timer = 0
        self.end_time = -1

    def update(self):
        Events.update()

        if not self.ship.dead:
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

        self.wave_timer += 1

        self.wave.update()

        self.explode.pos = [self.ship.pos[0], self.ship.pos[1]]
        self.explode.update()

        if self.end_time > 0:
            if self.end_time > 165:
                for i in range(5):
                    self.explode.generate(speed_var=1)

            self.end_time -= 1
        elif self.end_time == 0:
            self.__init__()

        if len(self.wave.tab) == 0 and self.nb_wave < len(self.waves) - 1:
            self.wave = self.waves[self.nb_wave]
            self.nb_wave += 1
            self.wave_timer = 0

    def text(self, text, slot, size, pos, center=False):
        if text != self.last_text[slot][0]:
            font = pygame.font.Font("font/kongtext.ttf", size)
            self.last_text[slot][0] = text
            self.last_text[slot][1] = font.render(text, False, (255, 255, 255))
        rect = self.last_text[slot][1].get_rect()
        if center:
            rect.centerx = pos[0]
            rect.centery = pos[1]
        else:
            rect.left = pos[0]
            rect.top = pos[1]
        self.surf.blit(self.last_text[slot][1], rect)

    def draw(self):
        self.surf.fill(Game.background)
        self.stars.draw(self.surf)

        self.explode.draw(self.surf)

        if not self.ship.dead:
            self.ship.draw(self.surf)

        self.wave.draw(self.surf)

        self.draw_ui()
        pygame.display.update()

    def draw_ui(self):
        str_score = str(self.score)
        for i in range(str_score.__len__(), 10):
            str_score = "0" + str_score
        self.text(str_score, 0, 15, (10, 10))

        if self.wave_timer < 180:
            self.text(self.wave.text, 1, 25, (width/2, height/2), True)


game = Game()

while game.run:
    game.update()
    game.draw()

    game.clock.tick(120)
