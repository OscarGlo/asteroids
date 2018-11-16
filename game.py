import math
import random

import pygame

width = 800
height = 600


def rotate_point(point, off, angle):
    s = math.sin(angle)
    c = math.cos(angle)

    x = off[0] * c - off[1] * s + point[0]
    y = off[0] * s + off[1] * c + point[1]

    return [x, y]


class Events:
    up = left = right = False

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
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    Events.up = False
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    Events.left = False
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    Events.right = False


# class Effects:
#     @staticmethod
#     def blur(surf, factor):
#         arr = pygame.surfarray.pixels3d(surf)
#         soften = arr
#         soften[1:, :] += arr[:-1, :] * factor
#         soften[:-1, :] += arr[1:, :] * factor
#         soften[:, 1:] += arr[:, :-1] * factor
#         soften[:, :-1] += arr[:, 1:] * factor
#         pygame.surfarray.blit_array(surf, arr)

class CyclePos:
    def __init__(self, pos):
        self.pos = pos

    def cycle(self):
        if self.pos[0] >= width:
            self.pos[0] -= width
        elif self.pos[0] <= 0:
            self.pos[0] += width

        if self.pos[1] >= height:
            self.pos[1] -= height
        elif self.pos[1] <= 0:
            self.pos[1] += height


class Particle(CyclePos):
    def __init__(self, pos, angle, speed, time, fade=True):
        super().__init__(pos)
        self.angle = angle
        self.speed = speed
        self.time = self.startTime = time
        self.fade = fade

        self.dead = False

    def update(self):
        self.pos[0] += self.speed * math.cos(self.angle)
        self.pos[1] += self.speed * math.sin(self.angle)

        if self.time <= 0:
            self.dead = True
        self.time -= 1

        self.speed *= 0.98

        self.cycle()

    def draw(self, surf):
        if self.fade:
            c = 255 * (self.time / self.startTime)
        else:
            c = 255
        pygame.draw.rect(surf, (c, c, c), pygame.rect.Rect(self.pos, (2, 2)))


class ParticleGen(CyclePos):
    def __init__(self, pos, direction, angle, delay, speed, time):
        super().__init__(pos)
        self.direction = direction
        self.angle = angle
        self.delay = delay
        self.counter = 0
        self.speed = speed
        self.time = time

        self.particles = []

    def generate(self, speed_var=0.2, time_var=0.1, fade=True):
        if self.counter == self.delay:
            self.counter = 0
            angle = self.direction + (random.random() * self.angle - self.angle / 2)
            speed = self.speed + (self.speed * random.random() - self.speed / 2) * speed_var
            time = self.time + (self.time * random.random() - self.time / 2) * time_var
            self.particles.append(Particle(self.pos, angle, speed, self.time, fade))
        else:
            self.counter += 1

        self.cycle()

    def update(self):
        for p in self.particles:
            p.update()
            if p.dead:
                self.particles.remove(p)

    def draw(self, surf):
        for particle in self.particles:
            particle.draw(surf)


class Ship:
    color = (255, 255, 255)
    rate = 0.0175

    def __init__(self, pos):
        self.pos = pos
        self.angle = -math.pi / 2
        self.speed = [0.0, 0.0]
        self.ang_speed = self.for_speed = 0

        self.particles = ParticleGen(rotate_point(self.pos, [-10, 0], self.angle),
                                     self.angle + math.pi, math.pi / 2, 5, 2, 60)

    def update(self):
        self.speed[0] = self.speed[0] * (1 - Ship.rate) + self.for_speed * math.cos(self.angle) * Ship.rate
        self.speed[1] = self.speed[1] * (1 - Ship.rate) + self.for_speed * math.sin(self.angle) * Ship.rate

        self.pos[0] += self.speed[0]
        self.pos[1] += self.speed[1]

        self.angle += self.ang_speed

        self.particles.pos = rotate_point(self.pos, [-10, 0], self.angle)
        self.particles.direction = self.angle + math.pi
        self.particles.update()
        if self.for_speed != 0:
            self.particles.generate()

        self.for_speed = 0
        self.ang_speed = 0

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
        self.particles.draw(surf)


class Game:
    background = (0, 0, 1)

    def __init__(self):
        global width, height

        self.run = True
        self.clock = pygame.time.Clock()

        pygame.display.init()
        self.surf = pygame.display.set_mode([width, height])
        pygame.display.set_caption("Asteroids")
        pygame.display.set_icon(pygame.image.load('img/icon.png'))

        self.ship = Ship([400, 300])

    def update(self):
        Events.update()

        if Events.up:
            self.ship.for_speed = 2.5
        if Events.left:
            self.ship.ang_speed = -0.025
        elif Events.right:
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
