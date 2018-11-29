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
                if event.key == pygame.K_UP:
                    Events.up = True
                elif event.key == pygame.K_LEFT:
                    Events.left = True
                elif event.key == pygame.K_RIGHT:
                    Events.right = True
                elif event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_z:
                    Events.action = True
                elif event.key == pygame.K_ESCAPE:
                    game.run = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    Events.up = False
                elif event.key == pygame.K_LEFT:
                    Events.left = False
                elif event.key == pygame.K_RIGHT:
                    Events.right = False
                elif event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_z:
                    Events.action = False


class Game:
    background = (0, 0, 1)

    def __init__(self):
        pygame.init()
        pygame.display.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=8, buffer=4096)

        self.run = True
        self.clock = pygame.time.Clock()

        self.stars = [Stars(self, [0, 0], 0.2), Stars(self, [0, 0], 0.15), Stars(self, [0, 0], 0.1)]

        self.surf = pygame.display.set_mode([width, height])
        pygame.display.set_caption("Asteroids")
        pygame.display.set_icon(pygame.image.load('img/icon.png'))

        self.ship = Ship([0, 0])
        self.ship.angle = math.pi/3

        self.explode = ParticleGen([self.ship.pos[0], self.ship.pos[1]], 0, 2 * math.pi, 0, 3, 150)
        self.asteroid_explode = ParticleGen([0, 0], 0, 2 * math.pi, 0, 2, 70)

        self.waves = [
            [["Boss", [15, 1]], "Wave 0"],
            [[[3, 1], [1, 2]], "Wave 1"],
            [[[3, 2]], "Wave 2"],
            [[[4, 1], [1, 3]], "Wave 3"],
            [[[12, 1]], "Wave 4"],
        ]

        self.last_text = [[None, None], [None, None]]

        self.start()

    def start(self):
        self.wave = Wave(self, self.waves[0][0], self.waves[0][1])
        self.nb_wave = 1

        self.ship.dead = False

        self.menu = True

        self.asteroid_explode.particles = []
        self.asteroid_explode_size = 0

        self.score = 0

        self.asteroid_explode_timer = 0
        self.wave_timer = 0
        self.end_time = -1

    def update(self):
        Events.update()

        for stars in self.stars:
            stars.update()

        if self.menu:
            self.ship.for_speed = 2
            self.ship.update()

            if Events.action:
                self.start_game()
        else:
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

            self.wave_timer += 1

            self.wave.update()

            self.asteroid_explode.update()
            if self.asteroid_explode_timer > 0:
                self.asteroid_explode.generate(speed_var=0.8)
                self.asteroid_explode_timer -= 1

            self.explode.pos = [self.ship.pos[0], self.ship.pos[1]]
            self.explode.update()

            if self.end_time > 0:
                if self.end_time > 165:
                    for i in range(5):
                        self.explode.generate(speed_var=1)

                self.end_time -= 1
            elif self.end_time == 0:
                self.start()

            if len(self.wave.tab) == 0 and self.nb_wave < len(self.waves):
                self.wave = Wave(self, self.waves[self.nb_wave][0], self.waves[self.nb_wave][1])
                self.nb_wave += 1
                self.wave_timer = 0

    def start_game(self):
        self.menu = False

        Events.action = False

        self.ship.particles.particles = []
        self.ship.pos = [400, 300]
        self.ship.angle = -math.pi / 2
        self.ship.speed = [0, 0]

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
        for stars in self.stars:
            stars.draw(self.surf)

        self.explode.draw(self.surf)
        self.asteroid_explode.draw(self.surf, size=self.asteroid_explode_size, circle=True)

        if not self.menu and not self.ship.dead:
            self.ship.draw(self.surf)

        self.wave.draw(self.surf)

        self.draw_ui()
        pygame.display.update()

    def draw_ui(self):
        if self.menu:
            self.text("(a)steroids", 1, 25, (width / 2, height / 2), True)
            self.text("press spacebar/w to (re)start", 0, 12, (width / 2, height / 2 + 20), True)
        else:
            str_score = str(self.score)
            for i in range(str_score.__len__(), 10):
                str_score = "0" + str_score
            self.text(str_score, 0, 15, (10, 10))

            if self.nb_wave == len(self.waves) and len(self.wave.tab) == 0:
                self.text("You win !", 1, 25, (width / 2, height / 2), True)
            elif self.wave_timer < 180:
                self.text(self.wave.text, 1, 25, (width / 2, height / 2), True)


game = Game()

while game.run:
    game.update()
    game.draw()

    game.clock.tick(120)
