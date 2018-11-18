import math
import random

import pygame

width = 800
height = 600


def rotate_point(origin, off, angle):
    s = math.sin(angle)
    c = math.cos(angle)

    x = off[0] * c - off[1] * s + origin[0]
    y = off[0] * s + off[1] * c + origin[1]

    return [x, y]


def rotate_points(origin, points, angle):
    tmp_points = []
    for i in range(len(points)):
        tmp_points.append(rotate_point(origin, points[i], angle))

    return tmp_points


def sign(point1, point2, point3):
    return (point1[0] - point3[0]) * (point2[1] - point3[1]) - (point2[0] - point3[0]) * (point1[1] - point3[1])


def pointInTriangle(pointT, pointV1, pointV2, pointV3):

    d1 = sign(pointT, pointV1, pointV2)
    d2 = sign(pointT, pointV2, pointV3)
    d3 = sign(pointT, pointV3, pointV1)

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not(has_neg and has_pos)


def pointInPolygon(pointToTest, center, pointsOfPolygon):
    i = 0

    while i < len(pointsOfPolygon)-1:
        if pointInTriangle(pointToTest, center, pointsOfPolygon[i], pointsOfPolygon[i + 1]):
            return [True, i, i + 1]
        i += 1
    if pointInTriangle(pointToTest, center, pointsOfPolygon[i], pointsOfPolygon[0]):
        return [True, i, 0]

    return [False, [0, 0], [0, 0]]


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


class CyclePos:
    def __init__(self, pos, off=(0, 0)):
        self.pos = pos
        self.off = off

    def cycle(self):
        if self.pos[0] >= width + self.off[0]:
            self.pos[0] -= width + self.off[0] * 2
        elif self.pos[0] <= -self.off[0]:
            self.pos[0] += width + self.off[0] * 2

        if self.pos[1] >= height + self.off[1]:
            self.pos[1] -= height + self.off[1] * 2
        elif self.pos[1] <= -self.off[1]:
            self.pos[1] += height + self.off[1] * 2


class PointsObject:
    def __init__(self, points, pos, angle):
        self.points = points
        self.pos = pos
        self.angle = angle
        self.speed = [0.0, 0.0]
        self.ang_speed = 0

    def update(self):
        self.pos[0] += self.speed[0]
        self.pos[1] += self.speed[1]

        self.angle += self.ang_speed

    def draw(self, surf, off=(0, 0), thick=2):
        pygame.draw.lines(surf, Asteroid.color, True, rotate_points((self.pos[0] + off[0], self.pos[1] + off[1]),
                                                                    self.points, self.angle), thick)


class Particle(CyclePos):
    def __init__(self, pos, angle, speed, time, fade=True, size=2):
        super().__init__(pos)
        self.angle = angle
        self.speed = speed
        self.time = self.startTime = time
        self.fade = fade
        self.size = size

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
            c = math.floor(255 * (self.time / self.startTime))
        else:
            c = 255
        if c < 0:
            c = 0
        pygame.draw.rect(surf, (c, c, c), pygame.rect.Rect(self.pos, (self.size, self.size)))


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

    def generate(self, speed_var=0.2, time_var=0.1, fade=True, size=2):
        if self.counter == self.delay:
            self.counter = 0
            angle = self.direction + (random.random() * self.angle - self.angle / 2)
            speed = self.speed + (self.speed * random.random() - self.speed / 2) * speed_var
            time = self.time + (self.time * random.random() - self.time / 2) * time_var
            self.particles.append(Particle(self.pos, angle, speed, time, fade, size))

        self.cycle()

    def update(self):
        if self.counter < self.delay:
            self.counter += 1

        for p in self.particles:
            p.update()
            if p.dead:
                self.particles.remove(p)

    def draw(self, surf):
        for particle in self.particles:
            particle.draw(surf)


class Asteroid(PointsObject, CyclePos):
    color = (255, 255, 255)

    def __init__(self):
        if random.random() > 0.5:
            self.pos = [random.random() * width, -100]
        else:
            self.pos = [-100, random.random() * height]

        CyclePos.__init__(self, self.pos, (100, 100))

        PointsObject.__init__(self, [
            [-45, -52],
            [-31, -47],
            [43, -61],
            [42, -29],
            [19, -13],
            [42, -29],
            [43, -61],
            [64, -40],
            [58, -22],
            [62, 15],
            [41, 7],
            [48, 0],
            [41, 7],
            [68, 30],
            [17, 68],
            [-13, 60],
            [-22, 45],
            [-13, 60],
            [-22, 73],
            [-51, 75],
            [-73, 28],
            [-60, -26],
            [-31, -11],
            [-24, 11],
            [-31, -11],
            [-50, -22]
        ], self.pos, math.pi * random.random())

        rand = (random.random() - 0.5)
        self.speed = [rand * 2, rand * 2]
        self.ang_speed = random.random() * 0.03

    def update(self):
        super().update()
        self.collisionLaser()
        self.cycle()

    def collisionLaser(self):
        global game
        for laser in game.ship.lasers:
            tmpResult = pointInPolygon(laser.pos, self.pos, rotate_points((self.pos[0], self.pos[1]), self.points,
                                                                       self.angle))

            if tmpResult[0]:
                laser.dead = True
                self.points[tmpResult[1]] = [self.points[tmpResult[1]][0]*0.8, self.points[tmpResult[1]][1]*0.8]
                self.points[tmpResult[2]] = [self.points[tmpResult[2]][0] * 0.8, self.points[tmpResult[2]][1] * 0.8]


class Laser(PointsObject):
    def __init__(self, pos, angle):
        super().__init__([
            [0, 0],
            [10, 0]
        ], pos, angle)
        self.speed = [5 * math.cos(self.angle), 5 * math.sin(self.angle)]

        # self.particles = ParticleGen(pos, angle + math.pi, math.pi, 2, 0.5, 5)

        self.dead = False

    def update(self):
        if not self.dead:
            super().update()

            # self.particles.pos = [self.pos[0], self.pos[1]]
            #
            # self.particles.generate(fade=False)
            # self.particles.update()

            if not 0 <= self.pos[0] <= width or not 0 <= self.pos[1] <= height:
                self.dead = True

    def draw(self, surf, **kwargs):
        super().draw(surf)

        # self.particles.draw(surf)


class Ship(PointsObject, CyclePos):
    color = (255, 255, 255)
    rate = 0.0175

    def __init__(self, pos):
        CyclePos.__init__(self, pos)

        PointsObject.__init__(self, [
            [15, 0],
            [-15, -15],
            [-10, 0],
            [-15, 15]
        ], pos, -math.pi / 2)

        self.for_speed = 0

        self.particles = ParticleGen(rotate_point(self.pos, [-10, 0], self.angle),
                                     self.angle + math.pi, math.pi / 2, 5, 2, 60)
        self.lasers = []
        self.laser_timer = 0

    def update(self):
        self.speed[0] = self.speed[0] * (1 - Ship.rate) + self.for_speed * math.cos(self.angle) * Ship.rate
        self.speed[1] = self.speed[1] * (1 - Ship.rate) + self.for_speed * math.sin(self.angle) * Ship.rate

        super().update()

        self.particles.pos = rotate_point(self.pos, [-10, 0], self.angle)
        self.particles.direction = self.angle + math.pi
        self.particles.update()
        if self.for_speed != 0:
            self.particles.generate(fade=True)

        self.for_speed = 0
        self.ang_speed = 0
        self.cycle()

        if self.laser_timer > 0:
            self.laser_timer -= 1

        for l in self.lasers:
            l.update()
            if l.dead:
                self.lasers.remove(l)

    def shoot(self):
        if self.laser_timer == 0:
            self.lasers.append(Laser(rotate_point(self.pos, [15, 0], self.angle), self.angle))
            self.laser_timer = 50

    def draw(self, surf, **kwargs):
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                super().draw(surf, (width * i, height * j))

        self.particles.draw(surf)

        for l in self.lasers:
            l.draw(surf)


class Game:
    background = (0, 0, 1)

    print(pointInTriangle([1, 1], [0, 0], [1, 0], [0, 1]))
    print(pointInTriangle([0.5, 0.5], [0, 0], [1, 0], [0, 1]))

    print(pointInPolygon([-1, -1], [1, 1], [[0, 0], [2, 0], [2, 2], [0, 2]]))
    print(pointInPolygon([1, 0.5], [1, 1], [[0, 0], [2, 0], [2, 2], [0, 2]]))
    print(pointInPolygon([1, 0.5], [1, 1], [[0, 0], [2, 0], [2, 2], [0, 2]]))

    def __init__(self):
        global width, height

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
