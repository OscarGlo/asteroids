import random
import pygame
from util import *


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

    def draw(self, surf, size=2, circle=False):
        if self.fade:
            c = math.floor(255 * (self.time / self.startTime))
        else:
            c = 255
        if c < 0:
            c = 0
        rect = pygame.rect.Rect([self.pos[0] - size/2, self.pos[1] - size/2], (size, size))
        if circle:
            pygame.draw.ellipse(surf, (c, c, c), rect, 2)
        else:
            pygame.draw.rect(surf, (c, c, c), rect)


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
            self.particles.append(Particle([self.pos[0], self.pos[1]], angle, speed, time, fade))

    def update(self):
        if self.counter < self.delay:
            self.counter += 1

        for p in self.particles:
            p.update()
            if p.dead:
                self.particles.remove(p)

        self.cycle()

    def draw(self, surf, size=2, circle=False):
        for particle in self.particles:
            particle.draw(surf, size, circle)


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
            self.angle = random.randint(0, 3) * math.pi/2 + (1 + random.random() * 3) * math.pi/10
        else:
            self.angle = angle

        size_sq = size * size * 10
        offset = 0.2 * (size_sq + 5) + size_sq
        CyclePos.__init__(self, self.pos, (offset, offset))

        PointsObject.__init__(self, self.gen(size), self.pos, self.angle)

        self.particles = ParticleGen([self.pos[0], self.pos[1]], self.angle + math.pi, math.pi * 2, 0, 2, 40)

        self.speed = [0.5 * math.cos(self.angle) * 2 / size, 0.5 * math.sin(self.angle) * 2 / size]
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

        for i in range(10):
            self.particles.generate(time_var=0.5, speed_var=0.5)

        if self.health > 0:
            self.game.score += 100

            pygame.mixer.Sound("sfx/asteroid_hit.wav").play()

        if self.health <= 0:
            try:
                self.wave.tab.remove(self)
            except ValueError:
                pass
            self.game.score += self.size * 500

            if self.size > 1:
                for i in range(self.size):
                    angle = laser.angle + (random.random() - 0.5) * 2
                    self.wave.tab.append(Asteroid(self.game, self.wave, self.size - 1, [self.pos[0], self.pos[1]],
                                                  angle))

            self.game.asteroid_explode.pos = [self.pos[0], self.pos[1]]
            self.game.asteroid_explode_timer = self.size * self.size + 2
            self.game.asteroid_explode_size = self.size * 2 + 4

            pygame.mixer.Sound("sfx/asteroid_death.wav").play()


class Laser(PointsObject):
    def __init__(self, pos, angle, points=None, speed=5):

        if points is None:
            points = [[0, 0], [10, 0]]

        super().__init__(points, pos, angle)
        self.speed = [speed * math.cos(self.angle), speed * math.sin(self.angle)]

    def update(self):
        if not self.dead:
            super().update()

            if not 0 <= self.pos[0] <= width or not 0 <= self.pos[1] <= height:
                self.dead = True

    def draw(self, surf, **kwargs):
        super().draw(surf, **kwargs)


class Wave:
    def __init__(self, game, asteroids, text=""):
        self.text = text
        self.tab = []

        for char in asteroids:
            if char == "Boss":
                self.tab.append(Boss(game, [width/2, -50]))
            else:
                for i in range(char[0]):
                    self.tab.append(Asteroid(game, self, char[1]))

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

    def update(self, gen_particles=True):
        self.speed[0] = self.speed[0] * (1 - Ship.rate) + self.for_speed * math.cos(self.angle) * Ship.rate
        self.speed[1] = self.speed[1] * (1 - Ship.rate) + self.for_speed * math.sin(self.angle) * Ship.rate

        super().update()

        if gen_particles:
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
            l.draw(surf)


class Boss(Ship):
    color = (255, 20, 20)

    def __init__(self, game, pos):
        super().__init__(pos)
        self.game = game

        CyclePos.__init__(self, pos, off=[50, 50])

        PointsObject.__init__(self, [
            [45, 0],
            [-45, -45],
            [-30, 0],
            [-45, 45]
        ], pos, math.pi / 2)
        self.health = 20

    def update(self):
        self.shoot()
        self.for_speed =  20/(self.health+10)
        ship = self.game.ship
        if sign([self.pos[0], self.pos[1]], rotate_point([self.pos[0], self.pos[1]], [1, 0], self.angle),
                [ship.pos[0] + ship.speed[0]*120*dist_points(self.pos, ship.pos)/300, ship.pos[1] + ship.speed[1]*120*dist_points(self.pos, ship.pos)/300]) < 0:
            self.ang_speed = -0.025
        else:
            self.ang_speed = 0.025

        super().update(False)

        if (self.game.ship.is_in(self)[0] or self.is_in(self.game.ship)[0]) and not self.game.ship.dead:
            self.game.end_time = 180
            self.game.ship.dead = True
            pygame.mixer.Sound("sfx/ship_death.wav").play()

        for laser in self.lasers:
            if self.game.ship.is_in(laser)[0] and not self.game.ship.dead:
                self.game.end_time = 180
                self.game.ship.dead = True
                pygame.mixer.Sound("sfx/ship_death.wav").play()

        for laser in self.game.ship.lasers:
            if self.is_in(laser)[0]:
                self.health -= 1
                self.game.score += 100
                self.game.ship.lasers.remove(laser)
            if self.health == 0:
                self.game.score += 10000
                self.game.wave.tab.remove(self)
                break

    def draw(self, surf, **kwargs):

        PointsObject.draw(self, surf, color=self.color)
        self.particles.draw(surf)

        self.show_health(surf, self.health, 20)

        for l in self.lasers:
            l.draw(surf, color=[255, 20, 20])

    def shoot(self):
        if self.laser_timer == 0:
            self.lasers.append(Laser(rotate_point(self.pos, [45, 0], self.angle), self.angle,
                                     points=[[0, 0], [10, 0], [20, 0], [30, 0]], speed=2))
            self.laser_timer = 150

    def show_health(self, surf, health, max_health):
        pygame.draw.rect(surf, [200, 20, 20], pygame.Rect(width * 0.05, height * 0.9,
                                                          width * 0.9*(health/max_health), height * 0.025))
        pygame.draw.rect(surf, [220, 220, 220], pygame.Rect(width*0.05, height*0.9, width*0.9, height*0.025), 2)


class Stars:
    def __init__(self, game, pos, speed):
        self.pos = pos
        self.speed = speed
        self.stars = []
        off = self.speed * 800
        rand = self.speed * 600
        for i in range(math.ceil(width / off)):
            for j in range(math.ceil(height / off)):
                self.stars.append([i * off + math.floor(random.random() * rand),
                                   j * off + math.floor(random.random() * rand)])

        self.game = game

    def draw(self, surf):
        for star in self.stars:
            c = (500 + 750 * random.random()) * self.speed
            pygame.draw.rect(surf, (c, c, c),
                             pygame.rect.Rect(
                                 ((self.pos[0] + star[0]) % width, (self.pos[1] + star[1]) % height), (2, 2))
                             )

    def update(self):
        self.pos[0] -= self.game.ship.speed[0] * self.speed
        self.pos[1] -= self.game.ship.speed[1] * self.speed
