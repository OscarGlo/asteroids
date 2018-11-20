import random, pygame
from util import *


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

    def __init__(self, game, size):
        if random.random() > 0.5:
            self.pos = [random.random() * width, -100]
        else:
            self.pos = [-100, random.random() * height]

        CyclePos.__init__(self, self.pos, (100, 100))

        # PointsObject.__init__(self, [
        #     [-45, -52],
        #     [-31, -47],
        #     [43, -61],
        #     [42, -29],
        #     [19, -13],
        #     [42, -29],
        #     [43, -61],
        #     [64, -40],
        #     [58, -22],
        #     [62, 15],
        #     [41, 7],
        #     [48, 0],
        #     [41, 7],
        #     [68, 30],
        #     [17, 68],
        #     [-13, 60],
        #     [-22, 45],
        #     [-13, 60],
        #     [-22, 73],
        #     [-51, 75],
        #     [-73, 28],
        #     [-60, -26],
        #     [-31, -11],
        #     [-24, 11],
        #     [-31, -11],
        #     [-50, -22]
        # ], self.pos, math.pi * random.random())
        PointsObject.__init__(self, self.gen(size*10*size), self.pos, math.pi * random.random())

        angle = random.random() * math.pi * 2
        self.speed = [0.5 * math.sin(angle), 0.5 * math.cos(angle)]
        self.ang_speed = random.random() * 0.015

        self.health = size*size
        self.split = size

        self.game = game

    def update(self):
        if self.health <= 0:
            self.dead = True

        if not self.dead:
            super().update()
            self.collision_laser()
            self.cycle()

    @staticmethod
    def gen(size):

        tmp = []
        nb_points = math.floor(size/5)+5
        for i in range(0, nb_points):
            dist = (random.random()-0.5)*0.4*(size+5) + size
            tmp.append(rotate_point([0, 0], [dist, 0], (2*math.pi/nb_points)*i))
        return tmp

    def collision_laser(self):
        for laser in self.game.ship.lasers:
            tmp_result = self.is_in(laser)

            if tmp_result[0]:
                laser.dead = True
                self.hit(tmp_result[1], tmp_result[2])

    def hit(self, point1, point2):
        self.points[point1] = [self.points[point1][0] * 0.9, self.points[point1][1] * 0.9]
        self.points[point2] = [self.points[point2][0] * 0.9, self.points[point2][1] * 0.9]
        self.health = self.health -1




class Laser(PointsObject):
    def __init__(self, pos, angle):
        super().__init__([
            [0, 0],
            [10, 0]
        ], pos, angle)
        self.speed = [5 * math.cos(self.angle), 5 * math.sin(self.angle)]

        # self.particles = ParticleGen(pos, angle + math.pi, math.pi, 2, 0.5, 5)

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


class Wave:

    def __init__(self, game, text, asteroids):
        self.text = text
        self.tab = []

        for caracteristic in asteroids:
            for i in range(caracteristic[0]):
                self.tab.append(Asteroid(game, caracteristic[1]))

    def update(self):
        for asteroid in self.tab:
            asteroid.update()

    def draw(self, surf):
        for asteroid in self.tab:
            asteroid.draw(surf)



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
