import random
import pygame
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
            self.particles.append(Particle([self.pos[0], self.pos[1]], angle, speed, time, fade, size))

    def update(self):
        if self.counter < self.delay:
            self.counter += 1

        for p in self.particles:
            p.update()
            if p.dead:
                self.particles.remove(p)

        self.cycle()

    def draw(self, surf):
        for particle in self.particles:
            particle.draw(surf, )


class Asteroid(PointsObject, CyclePos):
    color = (255, 255, 255)

    def __init__(self, game, wave, size, pos=None, angle=None):
        if pos is None:
            if random.random() > 0.5:
                self.pos = [random.random() * width, -100]
            else:
                self.pos = [-100, random.random() * height]
        else:
            self.pos = pos

        if angle is None:
            self.angle = random.random() * math.pi * 2
        else:
            self.angle = angle

        size_sq = size * size * 10
        offset = 2 * (0.2 * (size_sq + 5) + size_sq)
        CyclePos.__init__(self, self.pos, (offset, offset))

        PointsObject.__init__(self, self.gen(size), self.pos, self.angle)

        self.particles = ParticleGen([self.pos[0],self.pos[1]], self.angle + math.pi, math.pi * 2, 0, 2,40)

        self.speed = [0.5 * math.cos(self.angle)*2/size, 0.5 * math.sin(self.angle)*2/size]
        self.ang_speed = random.random() * 0.015

        self.size = size
        self.health = size * size
        self.split = size

        self.game = game
        self.wave = wave

    def update(self):
        super().update()
        self.collision_laser()
        self.cycle()
        self.particles.update()

        if (self.is_in(self.game.ship)[0] or self.game.ship.is_in(self)[0]) and not self.game.ship.dead:
            self.game.end_time = 180
            self.game.ship.dead = True

            pygame.mixer.Sound("sfx/ship_death.wav").play()

    def draw(self, surf, **kwargs):
        super().draw(surf, **kwargs)
        self.particles.draw(surf)

    @staticmethod
    def gen(size):
        size = size * 10 * size
        tmp = []
        nb_points = math.floor(size / 5) + 5
        for i in range(0, nb_points):
            dist = (random.random() - 0.5) * 0.4 * (size + 5) + size
            tmp.append(rotate_point([0, 0], [dist, 0], (2 * math.pi / nb_points) * i))
        return tmp

    def collision_laser(self):
        for laser in self.game.ship.lasers:
            tmp_result = self.is_in(laser)

            if tmp_result[0]:
                laser.dead = True
                self.hit(tmp_result[1], tmp_result[2], laser)

    def hit(self, point1, point2, laser):
        self.points[point1] = [self.points[point1][0] * 0.9, self.points[point1][1] * 0.9]
        self.points[point2] = [self.points[point2][0] * 0.9, self.points[point2][1] * 0.9]
        self.health = self.health - 1
        self.particles.pos = [laser.pos[0], laser.pos[1]]

        pygame.mixer.Sound("sfx/asteroid_hit.wav").play()
        
        for i in range(10):
            self.particles.generate(time_var=0.5, speed_var=0.5)

        if self.health > 0:
            self.game.score += 100

        if self.health <= 0:
            self.wave.tab.remove(self)
            self.game.score += self.size * 500

            if self.size > 1:
                for i in range(self.size):
                    angle = laser.angle + (random.random()-0.5)*2
                    self.wave.tab.append(Asteroid(self.game, self.wave, self.size - 1, [self.pos[0], self.pos[1]],
                                                  angle))


class Laser(PointsObject):
    def __init__(self, pos, angle):
        super().__init__([
            [0, 0],
            [10, 0]
        ], pos, angle)
        self.speed = [5 * math.cos(self.angle), 5 * math.sin(self.angle)]

    def update(self):
        if not self.dead:
            super().update()

            if not 0 <= self.pos[0] <= width or not 0 <= self.pos[1] <= height:
                self.dead = True

    def draw(self, surf, **kwargs):
        super().draw(surf)


class Wave:
    def __init__(self, game, asteroids, text=""):
        self.text = text
        self.tab = []

        for char in asteroids:
            for i in range(char[0]):
                self.tab.append(Asteroid(game, self, char[1]))

    def update(self):
        for asteroid in self.tab:
            asteroid.update()

    def draw(self, surf):
        for asteroid in self.tab:
            asteroid.draw(surf, )


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
            self.laser_timer = 30

            pygame.mixer.Sound("sfx/ship_laser.wav").play()

    def draw(self, surf, **kwargs):
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                super().draw(surf, (width * i, height * j))

        self.particles.draw(surf)

        for l in self.lasers:
            l.draw(surf, )


class Stars:
    def __init__(self, game, pos):
        self.pos = pos 
        self.stars = []
        off = 50
        rand = 40
        for i in range(math.floor(width/off)):
            for j in range(math.floor(height/off)):
                self.stars.append([i * off + math.floor(random.random() * rand),
                                   j * off + math.floor(random.random() * rand),
                                   ])

        self.game = game

    def draw(self, surf):
        for star in self.stars:
            c = 50+75*random.random()
            pygame.draw.rect(surf, (c, c, c),
                             pygame.rect.Rect(
                                 ((self.pos[0] + star[0]) % width, (self.pos[1] + star[1]) % height), (2, 2))
                             )

    def update(self):
        self.pos[0] += self.game.ship.speed[0] / 5
        self.pos[1] += self.game.ship.speed[1] / 5
