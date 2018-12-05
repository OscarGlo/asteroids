import math
import pygame

from config import width, height


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
    return ((point1[0] - point3[0]) * (point2[1] - point3[1]) - (point2[0] - point3[0]) * (point1[1] - point3[1]))/2

def aire_triangle(point1, point2, point3):
    return abs(sign(point1, point2, point3))

def dist_points(point1, point2):
    return math.sqrt(math.pow(point1[0]-point2[0], 2) + math.pow(point1[1]-point2[1], 2))

def point_in_triangle(point, tri):
    d1 = aire_triangle(point, tri[0], tri[1])
    d2 = aire_triangle(point, tri[1], tri[2])
    d3 = aire_triangle(point, tri[2], tri[0])

    return not (d1+d2+d3 > aire_triangle(tri[0], tri[1], tri[2]))

def point_in_polygon(point, center, polygon):
    i = 0

    while i < len(polygon) - 1:
        if point_in_triangle(point, (center, polygon[i], polygon[i + 1])):
            return [True, i, i + 1]
        i += 1
    if point_in_triangle(point, (center, polygon[i], polygon[0])):
        return [True, i, 0]

    return [False, [0, 0], [0, 0]]


class CyclePos:
    def __init__(self, pos, off=(0, 0)):
        self.pos = pos
        self.off = off

    def cycle(self):
        if self.pos[0] >= width + self.off[0]:
            self.pos[0] = -self.off[0]
        elif self.pos[0] <= -self.off[0]:
            self.pos[0] = width + self.off[0]

        if self.pos[1] >= height + self.off[1]:
            self.pos[1] = -self.off[1]
        elif self.pos[1] <= -self.off[1]:
            self.pos[1] = height + self.off[1]

class PointsObject:
    def __init__(self, points, pos, angle):
        self.points = points
        self.pos = pos
        self.angle = angle
        self.speed = [0.0, 0.0]
        self.ang_speed = 0
        self.dead = False

    def update(self):
        if not self.dead:
            self.pos[0] += self.speed[0]
            self.pos[1] += self.speed[1]

            self.angle += self.ang_speed

    def draw(self, surf, off=(0, 0), thick=2, color=(255, 255, 255)):
        pygame.draw.lines(surf, color, True, rotate_points((self.pos[0] + off[0], self.pos[1] + off[1]),
                                                           self.points, self.angle), thick)

    def is_in(self, point_obj):
        rot_point = rotate_points(self.pos, self.points, self.angle)

        for point in rotate_points(point_obj.pos, point_obj.points, point_obj.angle):
            tmp_result = point_in_polygon(point, self.pos, rot_point)
            if tmp_result[0]:
                return tmp_result

        return [False, 0, 0]
