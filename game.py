import os
import pygame
import math
import main
from time import time
from vars import varsclass as all
from vars import settings
from textures import *
from other import Vec
from other import animation
from random import choice
from random import randint
from other import load_image
from other import load_multi_image
from other import generateeror
from objects import *

class camera():
    def __init__(self):
        self.pos = pygame.Vector2(0, 0)
        self.cpos = pygame.Vector2(all.xsiz / 2, all.ysiz / 2)
        self.startdrwx = 0
        self.startdrwy = 0
        self.sizedrawx = 100
        self.sizedrawy = 100
        self.facingdelta = 10
        self.mod = 150

    def start(self):
        self.pos.update(0, 0)
        
        self.startdrwx = int(self.pos.x // all.game.cellsizx)
        self.startdrwy = int(self.pos.y // all.game.cellsizy)
        self.sizedrawx = int((self.pos.x + all.xsiz) // all.game.cellsizx - self.pos.x) + 3
        self.sizedrawy = int((self.pos.y + all.ysiz) // all.game.cellsizy - self.pos.y) + 3

    def render(self, delta, screen):
        self.startdrwx = int(self.pos.x // all.game.cellsizx)
        self.startdrwy = int(self.pos.y // all.game.cellsizy)
        if self.startdrwy < 0:
            self.startdrwy = 0
        if self.startdrwx < 0:
            self.startdrwx = 0
        for y in range(self.startdrwy, self.startdrwy + self.sizedrawy):
            if y >= all.game.gridsizy:
                break
            for x in range(self.startdrwx, self.startdrwx + self.sizedrawx):
                if x >= all.game.gridsizx:
                    break
                ii = all.game.grid[y][x]
                if ii is None:
                    continue
                if not ii.pos:
                    screen.blit(ii.txturetop, (ii.x * all.game.cellsizx - self.pos.x + ii.sdvg[0], ii.y * all.game.cellsizy - self.pos.y + ii.sdvg[1]))
                elif ii.y == all.game.gridsizy - 1 or not all.game.grid[ii.y + 1][ii.x].pos:
                    screen.blit(ii.txturefront, (ii.x * all.game.cellsizx - self.pos.x, ii.y * all.game.cellsizy - self.pos.y + all.game.cellsdvigy))


    def renderafterentity(self, delta, screen):
        self.startdrwx = int(self.pos.x // all.game.cellsizx)
        self.startdrwy = int(self.pos.y // all.game.cellsizy)
        if self.startdrwy < 0:
            self.startdrwy = 0
        if self.startdrwx < 0:
            self.startdrwx = 0
        for y in range(self.startdrwy, self.startdrwy + self.sizedrawy):
            if y >= all.game.gridsizy:
                break
            for x in range(self.startdrwx, self.startdrwx + self.sizedrawx):
                if x >= all.game.gridsizx:
                    break
                ii = all.game.grid[y][x]
                if ii is None:
                    continue
                if ii.pos:
                    screen.blit(ii.txturetop, (ii.x * all.game.cellsizx - self.pos.x, ii.y * all.game.cellsizy - self.pos.y - all.game.cellsdvigy))
                    
    def renderentytis(self, delta, screen):

        for i in all.game.entitys:
            self.renderentity(i, screen, delta)



    def renderentity(self, entity, screen, delta):
        entity.drawer(screen, entity.pos - self.pos)

    def move(self, delta, pos):
        res = pygame.Vector2(0, 0)
        if abs(self.cpos.x + self.pos.x - pos.x) > self.facingdelta:
            res.update(((pos.x - (self.cpos.x + self.pos.x)) / self.mod), 0)
        if abs(self.cpos.y + self.pos.y - pos.y) > self.facingdelta:
            res.update(res.x, ((pos.y - (self.cpos.y + self.pos.y)) / self.mod))
        self.pos += res * delta

cam = camera()


def generator(grid, gridsizx, gridsizy, labirintxcells, labirintycells):
    labirintx = gridsizx // labirintxcells
    labirinty = gridsizy // labirintycells
    labirint = [[[False, True, True] for i in range(labirintx)] for i in range(labirinty)]
    # ubdated xright+ ydown+ 
    x = 0
    y = 0
    path = [(0, 0)]
    labirint[0][0][0] = True
    while len(path) > 0:
        vec = Vec(1, 0)
        sides = set()
        for i in range(4):
            vec.rotate(90)
            if 0 <= x + vec.x < labirintx and 0 <= y + vec.y < labirinty:
                if not labirint[y + vec.y][x + vec.x][0]:
                    sides.add((vec.x, vec.y))
        if len(sides) < 1:
            path.pop(len(path) - 1)
            if len(path) == 0:
                break
            x = path[-1][0]
            y = path[-1][1]
            continue
        side = choice(list(sides))
        if side[1] > 0:
            labirint[y][x][2] = False
            path.append((x, y + 1))
        if side[1] < 0:
            labirint[y - 1][x][2] = False
            path.append((x, y - 1))
        if side[0] > 0:
            labirint[y][x][1] = False
            path.append((x + 1, y))
        if side[0] < 0:
            labirint[y][x - 1][1] = False
            path.append((x - 1, y))
        x = path[-1][0]
        y = path[-1][1]
        labirint[y][x][0] = True

    for yl in range(len(labirint)):
        for xl in range(len(labirint[yl])):
            if labirint[yl][xl][1]:
                for i in range(labirintxcells):
                    y, x = (yl * labirintycells + i), (xl * labirintxcells + labirintxcells - 1)
                    grid[y][x] = wall(x, y)
                    
            if labirint[yl][xl][2]:
                for i in range(labirintxcells):
                    y, x = (yl * labirintycells + labirintycells - 1), (xl * labirintxcells + i)
                    grid[y][x] = wall(x, y)

    for i in range(gridsizx):
        grid[0][i] = wall(i, 0)
    for i in range(gridsizx):
        grid[gridsizy - 1][i] = wall(i, gridsizy - 1)
    for i in range(gridsizy):
        grid[i][0] = wall(0, i)
    for i in range(gridsizy):
        grid[i][gridsizx - 1] = wall(gridsizx - 1, i)
    
    
    while True:
        startpos = (randint(0, all.game.gridsizx), randint(0, all.game.gridsizy))
        flag = True
        for i in sizpos:
            c = all.game.getcell(startpos[0] + i[0], startpos[1] + i[1])
            if c == None or c.pos:
                flag = False
                break
        if not flag:
            continue
        path = pathfind(startpos[0], startpos[1], 0, 0, endrule=lambda w, tx, ty: (w[0] > all.game.gridsizx), rules=[])
        if path == None:
            continue
        break


    for i in range(50):
        a = (randint(0, all.game.gridsizx), randint(0, all.game.gridsizy))
        if (startpos[0] - a[0])**2 + (startpos[1] - a[1]) ** 2 < 100:
            continue
        c = all.game.getcell(a[0], a[1])
        if c != None and (not c.pos):
            if randint(0, 3) == 0:
                grid[a[1]][a[0]] = superbox(a[0], a[1])
            else:
                grid[a[1]][a[0]] = box(a[0], a[1])
            for i in range(3):
                b = (randint(0, 2) - 1, randint(0, 2) - 1)
                b = randint(0, 3)
                if b == 0:
                    b = (1, 0)
                elif b == 1:
                    b = (-1, 0)
                elif b == 2:
                    b = (0, 1)
                elif b == 3:
                    b = (0, -1)
                c = all.game.getcell(a[0] + b[0], a[1] + b[1])
                if c == None or c.pos:
                    continue
                grid[a[1] + b[1]][a[0] + b[0]] = box(a[0] + b[0], a[1] + b[1])
                if randint(0, 1):
                    a = (a[0] + b[0], a[1] + b[1])
    
    for i in range(len(path) - 20, 0, -5):
        flag = True
        for j in sizpos:
            c  = all.game.getcell(path[i][0] + j[0], path[i][1] + j[1])
            if c == None or c.pos:
                flag = False
                break
        if not flag:
            continue
        all.game.entitys.append(enemy(path[i][0] * all.game.cellsizx, path[i][1] * all.game.cellsizy))
    for i in range(30):
        a = (randint(0, all.game.gridsizx), randint(0, all.game.gridsizy))
        if (startpos[0] - a[0])**2 + (startpos[1] - a[1]) ** 2 < 100:
            continue
        flag = True
        for j in sizpos:
            c  = all.game.getcell(a[0] + j[0], a[1] + j[1])
            if c == None or c.pos:
                flag = False
                break
        if not flag:
            continue
        all.game.entitys.append(enemy(a[0] * all.game.cellsizx, a[1] * all.game.cellsizy))
    all.game.grid[int(path[0][1] / all.game.cellsizy)][int(path[0][0] / all.game.cellsizx)] = luck(int(path[0][0] / all.game.cellsizx), int(path[0][1] / all.game.cellsizy))
    return startpos
    for yl in range(len(labirint)):
        for xl in range(len(labirint[yl])):
            l = 0
            l += labirint[yl][xl][1]
            l += labirint[yl][xl][2]
            if  0 <= xl - 1:
                l += labirint[yl][xl - 1][1]
            if 0 <= yl - 1:
                l += labirint[yl][xl - 1][1]





class game():
    def __init__(self):
        self.gridsizx = 50
        self.gridsizy = 50
        self.cellsizx = 32
        self.cellsizy = 32
        self.cellsdvigy = 16
        self.labirintcellx = 5
        self.labirintcelly = 5
        self.colisizx = 5
        self.colisizy = 5
        self.coliscelsizx = self.colisizx * self.cellsizx
        self.coliscelsizy = self.colisizy * self.cellsizy
        self.colisgrdsizx = self.gridsizx // self.colisizx + 1
        self.colisgrdsizy = self.gridsizy // self.colisizy + 1
        self.grid = [[]]
        self.cgrid = []
        self.entitys = []
        self.dodelete = False
        self.lazyenemy = []
        self.lazyenid = 0
        self.forenemyitems = []
        self.forenemychances = []
        self.boxchances =[]
        self.boxitems = []
        self.playerweapon  =None
        self.playerhealpos = pygame.Vector2(0, 0)
        self.playerhealsdvg = pygame.Vector2(20, 20)
        self.state = 0
        

    def gamower(self):
        print('gamover')
        if self.playerclass.level > all.record:
            self.newrecord = True
            all.record = self.playerclass.level
            main.updaterecord()
        self.tostate(2)

    def tostate(self, nom):
        if self.state == nom:
            return
        self.state = nom
        if self.state == 0:
            pass
        elif self.state == 2:
            self.hinttimr = time()
            for i in self.playerclass.coliscells:
                i.mas.remove(self.playerclass)


    def start(self):
        if not all.gametexturesload:
            self.playerhead = pygame.transform.scale(textures['player parts'][1][0][0], (self.cellsizx + 4, self.cellsizy + 4))

            self.playerfeet = [pygame.transform.scale(textures['player parts'][1][1][i], (self.cellsizx + 4, self.cellsizy - 21)) for i in range(3)]
            self.playereye = pygame.transform.scale(textures['player parts'][1][2][0], (self.cellsizx - 20, self.cellsizy - 20))
            self.playerarm = pygame.transform.scale(textures['player parts'][1][3][0], (self.cellsizx - 20, self.cellsizy - 20))
            self.playerm = pygame.transform.scale(textures['player parts'][1][4][0], (self.cellsizx - 15, self.cellsizy - 21))
        
            self.enemyhead = pygame.transform.scale(textures['enemy parts'][1][0][0], (self.cellsizx + 4, self.cellsizy + 4))
            self.enemyfeet = [pygame.transform.scale(textures['enemy parts'][1][1][i], (self.cellsizx + 4, self.cellsizy - 21)) for i in range(3)]
            self.enemyeye = pygame.transform.scale(textures['enemy parts'][1][2][0], (self.cellsizx - 20, self.cellsizy - 20))
            self.enemyarm = pygame.transform.scale(textures['enemy parts'][1][3][0], (self.cellsizx - 20, self.cellsizy - 20))
            self.enemym = pygame.transform.scale(textures['enemy parts'][1][4][0], (self.cellsizx - 15, self.cellsizy - 21))
        
            self.player = pygame.transform.scale(textures['player'][1], (self.cellsizx + 10, self.cellsizy + 10))
            self.healheart = pygame.transform.scale(textures['heart'][1], (20, 20))
        
            self.boxtexture = pygame.transform.scale(textures['boxes'][1][0][0], (self.cellsizx, self.cellsizy)) 
            self.boxtexturefront = pygame.transform.scale(textures['boxes'][1][0][1], (self.cellsizx, self.cellsdvigy)) 
            self.superboxtexture = pygame.transform.scale(textures['boxes'][1][0][2], (self.cellsizx, self.cellsizy)) 
            self.superboxtexturefront = pygame.transform.scale(textures['boxes'][1][0][3], (self.cellsizx, self.cellsdvigy)) 
            self.wall = pygame.transform.scale(textures['wals'][1][0][1], (self.cellsizx, self.cellsizy))
            self.wallfront = pygame.transform.scale(textures['wals'][1][0][2], (self.cellsizx, self.cellsdvigy))
            self.flor = pygame.transform.scale(textures['wals'][1][0][0], (self.cellsizx, self.cellsizy))
            self.luck = pygame.transform.scale(textures['luck'][1], (self.cellsizx, self.cellsizy * 2))
            self.test = pygame.transform.scale(textures['test'][1], (self.cellsizx / 2, self.cellsizy / 2))
            self.gameoverscreen1 = pygame.transform.scale(textures['gamover'][1], (all.xsiz, all.ysiz))
            self.gameoverscreen2 = pygame.transform.scale(textures['hint'][1], (all.xsiz, all.ysiz))

            siz = textures['bullet'][1].get_size()
            siz = siz[0] * 1.7, siz[1] * 1.7
            self.bul = pygame.transform.scale(textures['bullet'][1], siz)

            self.movevec = pygame.Vector2(0, 0)
            self.curvec = pygame.Vector2(all.xsiz / 2, all.ysiz / 2)
            
            loader('guns.txt')
            all.gametexturesload = True
        self.state = 0
        self.newrecord = False
        self.updatechances()
        self.updatechancesbox()
        print('start game')
        self.grid = []
        for y in range(self.gridsizy):
            ou = [None] * self.gridsizx
            for x in range(self.gridsizx):
                ou[x] = flor(x, y)
            self.grid.append(ou)
        
        for y in range(self.colisgrdsizy):
            ou = [None] * self.colisgrdsizx
            for x in range(self.colisgrdsizx):
                ou[x] = colisioncell()
                ou[x].x = x * self.colisizx
                ou[x].y = y * self.colisizy
            self.cgrid.append(ou)

        while len(self.entitys) > 0:
            a = self.entitys.pop()
            a.remover()
        self.lazyenemy = []
        self.lazyenid = 0

        cam.start()
        a = generator(self.grid, self.gridsizx, self.gridsizy, self.labirintcellx, self.labirintcelly)
        self.playerclass = player(x=a[0] * self.cellsizx + 10, y=a[1] * self.cellsizy + 10)
        self.playerclass.cornpos.update(self.cellsizx, self.cellsizy)
        if self.playerweapon != None:
            self.playerclass.inventar[0] = self.playerweapon.construct()

        #self.entitys.append(enemy(50,50))



    def eventer(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.playerclass.cursorubdate(all.curpos - self.curvec)

        if event.type == pygame.MOUSEBUTTONUP:
            self.playerclass.offclick()


        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == 0:
                self.playerclass.onclick()
            elif self.state == 1:
                main.changescene('menu')
        if event.type == pygame.KEYDOWN:
            if self.state == 0:
                if event.key == settings['change']:
                    self.playerclass.selected += 1
                    if self.playerclass.selected >= 2:
                        self.playerclass.selected = 0
                elif event.key == settings['equip']:
                    if self.playerclass.itemselected != None:
                        self.playerclass.inventar[self.playerclass.selected], self.playerclass.itemselected.gun = self.playerclass.itemselected.gun, self.playerclass.inventar[self.playerclass.selected]
            elif self.state == 1:
                main.changescene('menu')

    def nextlevel(self):

        self.playerclass.level += 1
        while len(self.entitys) > 0:
            a = self.entitys.pop()
            a.remover()
        for y in range(self.gridsizy):
            for x in range(self.gridsizx):
                self.grid[y][x] = flor(x, y)
        print('next level')
        a = generator(self.grid, self.gridsizx, self.gridsizy, self.labirintcellx, self.labirintcelly)
        self.playerclass.pos.x = a[0] * self.cellsizx + 10
        self.playerclass.pos.y = a[1] * self.cellsizy + 10
        cam.pos = self.playerclass.pos


    def getcell(self, x, y):
        if 0 <= x < self.gridsizx:
            if 0 <= y < self.gridsizy:
                return self.grid[y][x]
        return None

    def getcolcell(self, x, y):
        if 0 <= x < self.colisgrdsizx:
            if 0 <= y < self.colisgrdsizy:
                return self.cgrid[y][x]
        return None

    def drawer(self, dt, screen):
        cam.render(dt, screen)
        cam.renderentytis(dt, screen)
        if self.state == 0:
            cam.renderentity(self.playerclass, screen, dt)
        cam.renderafterentity(dt, screen)
        #ui drawing
        if self.state == 0:
            for i in range(self.playerclass.health):
                screen.blit(self.healheart, self.playerhealpos + (self.playerhealsdvg.x * (i % 15), self.playerhealsdvg.y * (i // 15)))
            screen.blit(textures['gui'][1][0][0], (10, 50))
            if self.playerclass.selected == 0:
                screen.blit(textures['gui'][1][1][1], (15, 90))
            screen.blit(textures['gui'][1][0][0], (60, 50))
            if self.playerclass.selected == 1:
                screen.blit(textures['gui'][1][1][1], (65, 90))
            if self.playerclass.inventar[0] != None:
                screen.blit(self.playerclass.inventar[0].image1, (20, 60))
            
            if self.playerclass.inventar[1] != None:
                screen.blit(self.playerclass.inventar[1].image1, (70, 60))
        elif self.state == 1:
            screen.blit(self.gameoverscreen1, (0, 0))
            screen.blit(self.gameoverscreen2, (0, 0))
          
        elif self.state == 2:
            screen.blit(self.gameoverscreen1, (0, 0))
            if time() - self.hinttimr > 2:
                self.tostate(1)
                screen.blit(self.gameoverscreen2, (0, 0))
        if self.state == 1 or self.state == 2:
            screen.blit(all.font.render('уровней пройдено: ' + str(self.playerclass.level), 1, (255, 255, 255)), (50, all.ysiz / 3))
            if self.newrecord:
                screen.blit(all.font.render('Новый рекорд', 1, (255, 255, 255)), (50, all.ysiz / 3 + 50))

    def toscene(self):
        pass

    def updatechances(self):

        self.forenemychances = [[1 - self.forenemyitems[i].enemychance, self.forenemyitems[i]] for i in range(len(self.forenemyitems))]
        #self.forenemychances.sort(key=lambda x: x[0])
        if len(self.forenemychances) <= 1:
            return
        return
        su = self.forenemychances[0][0]
        for i in range(1, len(self.forenemychances)):
            a = self.forenemychances[i][0]
            self.forenemychances[i][0] = (min(a, su) / max(su, a))
            su = su * a


    def updatechancesbox(self):
        self.boxchances = [[1 - self.boxitems[i].boxchanse, self.boxitems[i]] for i in range(len(self.boxitems))]
        #self.boxchances.sort(key=lambda x: x[0])
        if len(self.boxchances) <= 1:
            return
        return
        su = self.boxchances[0][0]
        for i in range(1, len(self.boxchances)):
            a = self.boxchances[i][0]
            self.boxchances[i][0] = (min(a, su) / max(su, a))
            su = su * a

    def randomweapon(self, typ):
        if typ == 0:
            if len(self.forenemychances) < 1:
                return None
            for i in range(len(self.forenemychances)):
                a = randint(0, 100) / 100
                if a < self.forenemychances[i][0]:
                    return self.forenemychances[i][1].construct()
            return self.forenemychances[-1][1].construct()
        elif typ == 1:
            if len(self.boxchances) < 1:
                return None
            for i in range(len(self.boxchances)):
                a = randint(0, 100) / 100
                if a < self.boxchances[i][0]:
                    return self.boxchances[i][1].construct()
            return self.boxchances[-1][1].construct()

    def ubdate(self, dt):
        if self.state == 0:
            buttons = pygame.key.get_pressed()
            self.movevec.update(0, 0)
            if buttons[settings['right']]:
                self.movevec.update(self.movevec.x + 1, 0)
            if buttons[settings['left']]:
                self.movevec.update(self.movevec.x - 1, 0)
            if buttons[settings['up']]:
                self.movevec.update(self.movevec.x, self.movevec.y - 1)
            if buttons[settings['down']]:
                self.movevec.update(self.movevec.x, self.movevec.y + 1)
            self.playerclass.move(self.movevec)
            self.playerclass.ubdate(dt)
        
            cam.move(dt, self.playerclass.pos + self.playerclass.center + (all.curpos - self.curvec) / 2)

        for i in self.entitys:
            i.ubdate(dt)
        if self.dodelete:
            self.dodelete = False
            i = 0 
            while i < len(self.entitys):
                if not self.entitys[i].live:
                    self.entitys[i].remover()
                    del self.entitys[i]
                i += 1
        self.lazyenid += 1
        if self.lazyenid >= len(self.lazyenemy):
            self.lazyenid = -1
        else:
            self.lazyenemy[self.lazyenid].lazy()

    def doneload(self):
        pass






class gunsettings():
    def __init__(self, name):
        self.worker = None
        self.image1 = None
        self.image2 = None
        self.bullet = bullet
        self.name = name
        self.sdvig = pygame.Vector2(0, 0)
        self.params = None
        self.enemdist = 25

    def construct(self):
        res = gun(self.name)
        res.worker = self.worker(self.params)
        res.worker.main = res
        if self.image1 != None:
            res.image1 = self.image1
        else:
            res.image1 = generateeror()
        if self.image2 != None:
            res.image2 = self.image2
        else:
            res.image2 = generateeror()
        res.bullet = self.bullet
        res.sdvig = pygame.Vector2(self.sdvig.x, self.sdvig.y)
        res.drawedim = self.image1
        res.usedim = res.drawedim
        res.size = self.image1.get_size()
        res.enemdist = self.enemdist
        return res

class gun():
    def __init__(self, name):
        self.worker = None
        self.image1 = None
        self.image2 = None
        self.usedim = None
        self.bullet = bullet
        self.name = name
        self.sdvig = pygame.Vector2(0, 0)
        self.size = (0, 0)
        self.mirored = False
        self.fired = False
        self.drawedim = None
        self.angle = 0
        self.enemdist = 6

    def rotate(self, angle):
        self.drawedim = pygame.transform.rotate(self.usedim, angle)
        self.angle = angle
    

    def draw(self, screen, pos):
        screen.blit(self.drawedim, self.sdvig + pos)

    def updateimage(self):
        if self.mirored:

            if not self.fired:
                siz = self.image1.get_size()
                self.usedim = pygame.transform.flip(self.image1, False, True)
            else:
                siz = self.image2.get_size()
                self.usedim = pygame.transform.flip(self.image2, False, True)
        else:
            if not self.fired:
                siz = self.image1.get_size()
                self.usedim = self.image1
            else:
                siz = self.image2.get_size()
                self.usedim = self.image2
        self.rotate(self.angle)


    def miror(self, bool):
        if bool:
            if not self.mirored:
                self.mirored = True

                if not self.fired:
                    siz = self.image1.get_size()
                    self.usedim = pygame.transform.flip(self.image1, False, True)
                else:
                    siz = self.image2.get_size()
                    self.usedim = pygame.transform.flip(self.image2, False, True)
        else:
            if self.mirored:

                self.mirored = False
                if not self.fired:
                    self.usedim = self.image1
                else:
                    self.usedim = self.image2

    def fire(self, pos, vec, ovner, dmg, dopparams={}, dopangle=0):
        vec = pygame.math.Vector2.normalize(vec)
        if dopangle != 0:
            vec = vec.rotate(dopangle)
        all.game.entitys.append(self.bullet(vec, x=pos.x, y=pos.y, angle=self.angle + dopangle, ign=ovner, damage=dmg, igntype=ovner.type, **dopparams))



class logic():
    def __init__(self, params):
        self.timr = 0

    def update(self):
        pass

    def fire(self, pos, vec, ovner):
        pass



class refile(logic):
    def __init__(self, params):
        self.timr = 0 
        self.reloadtime = params[0]
        self.bulletspeed = params[1]
        self.damage = int(params[2])
        if self.bulletspeed == 0:
            self.bulletspeed = 0.1
        self.reloding = False
        self.frmaetim = 0.15
        self.octtim = 0
        self.state = 0
        self.main = None
        
        if self.frmaetim > self.reloadtime:
            self.speedmode = True
        else:
            self.speedmode = False

    def update(self):
        if self.state == 0:
            self.reloding = False
            self.timr = 100

        if self.state == 1:
            self.timr = self.octtim
            self.state = 0
            self.main.fired = False
            self.main.updateimage()
        if self.state == 2:
            self.timr = self.octtim
            self.state = 1
            self.reloding = False

    def fire(self, pos, vec, ovner):
        if not self.reloding:
            self.state = 1
            self.reloding = True
            if self.speedmode:
                self.state = 2
                self.timr = self.reloadtime
                self.octtim = self.reloadtime - self.frmaetim
            else:
                self.state = 1
                self.timr = self.frmaetim
                self.octtim = self.reloadtime - self.frmaetim
            self.main.fired = True
            self.main.updateimage()
            
            self.main.fire(pos, vec * self.bulletspeed, ovner, self.damage)
            

class uzi(logic):
    def __init__(self, params):
        self.timr = 0 
        self.reloadtime = params[0]
        self.bulletspeed = params[1]
        self.damage = int(params[2])
        self.livetim = params[3]
        self.spread = params[4]
        if self.bulletspeed == 0:
            self.bulletspeed = 0.1
        self.reloding = False
        self.frmaetim = 0.15
        self.octtim = 0
        self.state = 0
        self.main = None
        
        if self.frmaetim > self.reloadtime:
            self.speedmode = True
        else:
            self.speedmode = False

    def update(self):
        if self.state == 0:
            self.reloding = False
            self.timr = 100

        if self.state == 1:
            self.timr = self.octtim
            self.state = 0
            self.main.fired = False
            self.main.updateimage()
        if self.state == 2:
            self.timr = self.octtim
            self.state = 1
            self.reloding = False

    def fire(self, pos, vec, ovner):
        if not self.reloding:
            self.state = 1
            self.reloding = True
            if self.speedmode:
                self.state = 2
                self.timr = self.reloadtime
                self.octtim = self.reloadtime - self.frmaetim
            else:
                self.state = 1
                self.timr = self.frmaetim
                self.octtim = self.reloadtime - self.frmaetim
            self.main.fired = True
            self.main.updateimage()
            self.main.fire(pos, vec * self.bulletspeed, ovner, self.damage, dopparams={'tim': self.livetim}, dopangle=(self.spread * (randint(-100, 100) / 100)))

class shotgun(logic):
    def __init__(self, params):
        self.timr = 0 
        self.reloadtime = params[0]
        self.bulletspeed = params[1]
        self.damage = int(params[2])
        self.glbspread = params[3]
        self.spread = params[4]
        self.count = int(params[5])
        self.vects = []

        for i in range(self.count):
            self.vects.append(self.glbspread - ((self.glbspread * 2) / (self.count - 1)) * i)
        if self.bulletspeed == 0:
            self.bulletspeed = 0.1
        self.reloding = False
        self.frmaetim = 0.15
        self.octtim = 0
        self.state = 0
        self.main = None
        
        if self.frmaetim > self.reloadtime:
            self.speedmode = True
        else:
            self.speedmode = False

    def update(self):
        if self.state == 0:
            self.reloding = False
            self.timr = 100

        if self.state == 1:
            self.timr = self.octtim
            self.state = 0
            self.main.fired = False
            self.main.updateimage()
        if self.state == 2:
            self.timr = self.octtim
            self.state = 1
            self.reloding = False

    def fire(self, pos, vec, ovner):
        if not self.reloding:
            self.state = 1
            self.reloding = True
            if self.speedmode:
                self.state = 2
                self.timr = self.reloadtime
                self.octtim = self.reloadtime - self.frmaetim
            else:
                self.state = 1
                self.timr = self.frmaetim
                self.octtim = self.reloadtime - self.frmaetim
            self.main.fired = True
            self.main.updateimage()
            for i in self.vects:
                self.main.fire(pos, vec * self.bulletspeed, ovner, self.damage, dopangle=i + (self.spread * (randint(-100, 100) / 100)))
            


gunconstructors = []

def loader(name):
    fullname = os.path.join("data", name)
    if not os.path.isfile(fullname):
        print('неудалось найти файл', fullname)
        return
    strlen = 6
    paramlen = 8
    file = open(fullname)
    lines = file.readlines()
    ln = len(lines)
    file.close()
    contructor = None
    scale = 1
    pics = []
    params = [0] * paramlen
    i = -1
    for line in lines:
        if len(line) > 0 and line[0] == '/':
            continue
        st = line.split()
        if len(st) < 1:
            continue
        for i in range(strlen - len(st)):
            st.append(None)
        if st[0] == 'end':
            if contructor != None:
                contructor.params = params
                gunconstructors.append(contructor)
                if forenemy:
                    all.game.forenemyitems.append(contructor)
                if forplayer:
                    all.game.playerweapon = contructor
                if forbox:
                    all.game.boxitems.append(contructor)
                contructor = None

        if st[0] == 'name':
            if contructor != None:
                contructor.params = params
                gunconstructors.append(contructor)
                if forenemy:
                    all.game.forenemyitems.append(contructor)
                if forplayer:
                    all.game.playerweapon = contructor
                if forbox:
                    all.game.boxitems.append(contructor)
                contructor = None
            if st[1] == None:
                continue
            contructor = gunsettings(st[1])
            pics = []
            params = [0] * paramlen
            scale = 1
            forenemy = False
            forplayer = False
            forbox = False
        if contructor == None:
            continue
        if st[0] == 'type':
            if st[1] == None:
                continue
            if st[1] == 'rifle':
                contructor.worker = refile
            if st[1] == 'uzi':
                contructor.worker = uzi
            if st[1] == 'shotgun':
                contructor.worker = shotgun
            continue
        if st[0] == 'pic':
            if st[1] == None or st[2] == None:
                continue
            dat = st[2].split(',')
            if len(dat) < 7:
                continue
            dat = list(map(int, dat))
            pics.append(load_multi_image(st[1], [dat], scale)[0])
            continue
        if st[0] == 'imagen':
            if st[1] == None:
                continue
            if st[1] == 'pic':
                dat = st[2].split(',')
                if len(dat) < 2:
                    continue
                dat = list(map(int, dat))
                contructor.image1 = pics[dat[0]][dat[1]]
                continue
            contructor.image1 = load_image(st[1], scale)
            continue
        if st[0] == 'imagef':
            if st[1] == None:
                continue
            if st[1] == 'pic':
                dat = st[2].split(',')
                if len(dat) < 2:
                    continue
                dat = list(map(int, dat))
                contructor.image2 = pics[dat[0]][dat[1]]
                continue
            contructor.image2 = load_image(st[1], scale)
            continue
        if st[0] == 'bullet':
            if st[1] == None or st[1] == 'default':
                contructor.bullet = bullet
            if st[1] == 'minibullet':
                contructor.bullet = minibul
            if st[1] == 'plasmabullet':
                contructor.bullet = plasmabul
            if st[1] == 'arrow':
                contructor.bullet = arrow
            continue
        if st[0] == 'sdvig':
            if st[1] == None:
                continue
            dat = st[1].split(',')
            if len(dat) < 2:
                continue
            dat = list(map(int, dat))
            contructor.sdvig.update(dat[0] * scale, dat[1] * scale)
            continue
        if st[0] == 'param':
            if st[1] == None or st[2] == None:
                continue
            params[int(st[1])] = float(st[2])
        if st[0] == 'size':
            if st[1] == None:
                continue
            scale = float(st[1])
        if st[0] == 'enemy':
            if st[1] == None:
                continue
            forenemy = True
            contructor.enemychance = 1 - int(st[1]) / 100
        if st[0] == 'box':
            if st[1] == None:
                continue
            forbox = True
            contructor.boxchanse = 1 - int(st[1]) / 100
        if st[0] == 'player':
            forplayer = True
        if st[0] == 'enemydist':
            if st[1] == None:
                continue
            contructor.enemdist = int(st[1])
    if contructor != None:
        contructor.params = params
        gunconstructors.append(contructor)
        if forenemy:
            all.game.forenemyitems.append(contructor)
        if forplayer:
            all.game.playerweapon = contructor
        if forbox:
            all.game.boxitems.append(contructor)