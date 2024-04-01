import pygame
import os
import sys
from time import time

datadir = 'data'

class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec(self.x + other.x, self.y + other.y)

    def set(self, x, y):
        self.x = x
        self.y = y

    def rotate(self, deg):
        if deg == 90:
            self.x, self.y = self.y, -self.x
            return

        if deg == -90:
            self.x, self.y = -self.y, self.x
            return
        self(self.x * cos(deg) - self.y * sin(deg),
             self.x * sin(deg) + self.y * cos(deg))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __call__(self, x, y):
        self.x = x
        self.y = y

def generateeror():
    image = pygame.Surface((30, 30))
    image.fill((255, 255, 255))
    pygame.draw.rect(image, (172, 0, 255), (0, 0, 15, 15), 0)
    pygame.draw.rect(image, (172, 0, 255), (15, 15, 30, 30), 0)
    return image

def load_image(name, sizemod=1):
    fullname = os.path.join(datadir, name)
    if not os.path.isfile(fullname):
        print(f"Изображение '{fullname}' не найдено")
        image = generateeror()
        siz = image.get_size()
        siz = siz[0] * sizemod, siz[1] * sizemod
        image = pygame.transform.scale(image, siz)
        return generateeror()
    image = pygame.image.load(fullname)
    siz = image.get_size()
    siz = siz[0] * sizemod, siz[1] * sizemod
    image = pygame.transform.scale(image, siz)
    return image

def load_multi_image(name, mas, sizemod=1):
    fullname = os.path.join(datadir, name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        image = pygame.Surface((30, 30))
        image.fill((255, 255, 255))
        pygame.draw.rect(image, (172, 0, 255), (0, 0, 15, 15), 0)
        pygame.draw.rect(image, (172, 0, 255), (15, 15, 30, 30), 0)
        siz = image.get_size()
        siz = siz[0] * sizemod, siz[1] * sizemod
        image = pygame.transform.scale(image, siz)
        outer = []
        for i in mas:
            ou = []
            for j in range(i[4]):
                ou.append(image)
            outer.append(ou)
        return outer
    globimage = pygame.image.load(fullname)
    outer = []
    for i in mas:
        ofsetx = i[0]
        ofsety = i[1]
        sizex = i[2]
        sizey = i[3]
        count = i[4]
        deltax = i[5]
        deltay = i[6]
        ou = []
        for i in range(count):
            image = globimage.subsurface(pygame.Rect((ofsetx + deltax * i, ofsety + deltay * i), (sizex, sizey)))
            siz = image.get_size()
            siz = siz[0] * sizemod, siz[1] * sizemod
            image = pygame.transform.scale(image, siz)
            ou.append(image)
        outer.append(ou)
    return outer


class animation():
    def __init__(self, anim, delta, map):
        self.anim = anim
        self.delta = delta
        self.map = map
        self.frame = map[0]
        self.index = 0
        self.starttime = time()
        self.playing = False

    def draw(self, screen, pos):
        screen.blit(self.anim[self.frame], pos)

    def update(self):
        if self.playing:
            if abs(time() - self.starttime) > self.delta:
                self.starttime = time()
                self.index += 1
                if self.index >= len(self.map):
                    self.index = 0
                self.frame = self.map[self.index]
