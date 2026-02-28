from time import time
from random import choice
from random import randint
from other import Vec
from other import animation
import pygame
import math
from vars import varsclass as all
from textures import textures

class cell():
    def __init__(self, x=0, y=0):
        self.type = 'empty'
        self.pos = True
        self.destr = False
        self.x = x
        self.y = y
        self.txturetop = all.eror
        self.txturefront = all.eror
        self.sdvg = (0, 0)
    def destroy(self):
        pass

class wall(cell):
    def __init__(self, x=0, y=0):
        super().__init__(x=x, y=y)
        self.type = 'wall'
        self.pos = True
        self.txturetop = all.game.wall
        self.txturefront = all.game.wallfront
        self.destr = False

class box(cell):
    def __init__(self, x=0, y=0):
        super().__init__(x=x, y=y)
        self.type = 'box'
        self.pos = True
        self.destr = True
        self.txturetop = all.game.boxtexture
        self.txturefront = all.game.boxtexturefront

    def destroy(self):
        all.game.setcell(self.x, self.y, flor(self.x, self.y))

class flor(cell):
    def __init__(self, x=0, y=0):
        super().__init__(x=x, y=y)
        self.type = 'flor'
        self.pos = False
        self.txturetop = all.game.flor

class luck(cell):
    def __init__(self, x=0, y=0):
        super().__init__(x=x, y=y)
        self.type = 'luck'
        self.pos = False
        self.txturetop = all.game.luck
        self.sdvg = (0, -all.game.cellsizy)
        


lastid = 0

class superbox(cell):
    def __init__(self, x=0, y=0):
        super().__init__(x=x, y=y)
        self.type = 'spbox'
        self.pos = True
        self.destr = True
        self.txturetop = all.game.superboxtexture
        self.txturefront = all.game.superboxtexturefront

        if randint(0, 1) == 0:
            self.item = hert()
        else:
            self.item = all.game.randomweapon(1)

    def destroy(self):
        all.game.add_object(item, self.x * all.game.cellsizx, self.y * all.game.cellsizy, gun=self.item)
        all.game.setcell(self.x, self.y, flor(self.x, self.y))

class colisioncell():
    def __init__(self):
        self.mas = set()
        self.x = 0
        self.y = 0

def collision(pos, cornpos, to):
    x = int(pos.x // all.game.cellsizx)
    y = int(pos.y // all.game.cellsizy)
    x1 = int((pos.x + cornpos.x) // all.game.cellsizx)
    y1 = int((pos.y + cornpos.y) // all.game.cellsizy)
    res = pygame.Vector2(to.x, to.y)
    for i in range(2):
        for ii in range(2):
            c = all.game.getcell(int((pos.x + cornpos.x * i + to.x) // all.game.cellsizx), int(( pos.y + cornpos.y * ii) // all.game.cellsizy))
            if c == None or c.pos:
                res.x = 0
            c = all.game.getcell(int((pos.x + cornpos.x * i) // all.game.cellsizx), int(( pos.y + cornpos.y * ii + to.y) // all.game.cellsizy))
            if c == None or c.pos:
                res.y = 0
    if res.y == 0 and res.x == 0:
        return res
    for dy in range(y + 1, y1):
        for dx in range(x + 1, x1):
            c = all.game.getcell(int((dx * all.game.cellsizx + to.x) // all.game.cellsizx), dy)
            if c == None or c.pos:
                res.x = res.x
            c = all.game.getcell(dx, int((dy * all.game.cellsizy + to.y) // all.game.cellsizy))
            if c == None or c.pos:
                res.y = 0
    return res



def tocolision(mas, pos, cornpos, entity):

    rem = True
    while rem:
        rem = False
        for i in mas:
            if not (i.y * all.game.cellsizy - cornpos.y <= pos.y <= all.game.cellsizy * (i.y + all.game.colisizy) and (i.x * all.game.cellsizx - cornpos.x <= pos.x <= all.game.cellsizx * (i.x + all.game.colisizx))):
                i.mas.remove(entity)
                mas.remove(i)
                rem = True
                break
    for i in range(2):
        for ii in range(2):
            c = all.game.getcolcell(int((pos.x + cornpos.x * ii) // all.game.coliscelsizx), int((pos.y + cornpos.y * i) // all.game.coliscelsizy))
            if c != None and c not in mas:
                mas.add(c)
                c.mas.add(entity)
                

def poscolide(pos, ignor=None, typign=[], white=''):
    c = all.game.getcolcell(int((pos.x) // all.game.coliscelsizx), int((pos.y) // all.game.coliscelsizy))
    if white == '':
        for i in c.mas:
            if i == ignor or i.type in typign:
                #print(i.type)
                continue
            if i.pos.x < pos.x < (i.pos.x + i.cornpos.x) and i.pos.y < pos.y < (i.pos.y + i.cornpos.y):
                return i
    else:
        for i in c.mas:
            if i == ignor or i.type in typign or i.type != white: 
                #print(i.type)
                continue
            if i.pos.x < pos.x < (i.pos.x + i.cornpos.x) and i.pos.y < pos.y < (i.pos.y + i.cornpos.y):
                return i

def getpos(pos):
    return (int(pos[0] // all.game.cellsizx), int(pos[1] // all.game.cellsizy))

def raycast(pos, vec, ignor=None, typign=[], white=''):

    pos = pygame.Vector2(pos)
    if type(vec) is tuple:
        vec = pygame.Vector2(vec)
    if vec.length() == 0:
        return None, False
    vec = pygame.math.Vector2.normalize(vec) * 10
    while True:
        
        c = all.game.getcell(int(pos.x // all.game.cellsizx), int(pos.y // all.game.cellsizy))
        if c == None or c.pos:
            return c, False
        c = poscolide(pos, ignor=ignor, typign=typign, white=white)
        if c != None:
            return c, True
        pos += vec

class entity():
    def __init__(self, x=0, y=0):
        global lastid
        self.live = True
        self.type = 'eror'
        self.pos = pygame.Vector2(x, y)
        self.uuid = lastid
        lastid += 1

        self.sync = False
        self.net_params = ((False, False), (), (), (False, True), ()) #has (server update, client update), (sync params) (creating params) (has sync var(0=no, 1=sync without sync pos, 2=sync with pos), need update, (client sync params))

    def client_init(self):
        pass
    def server_init(self):
        pass
    def drawer(self, screen, pos):
        pass
    def ubdate(self, delta):
        pass
    def move(self, mov):
        pass
    def hit(self, dmg):
        pass
    def remover(self):
        pass
    def server_update(self, delta):
        pass
    def client_update(self, delta):
        pass
    def set_pos(self, x, y):
        self.x = x
        self.y = y 
    def on_sync_get(self):
        pass


class bullet(entity):
    def __init__(self, vec, x=0, y=0, angle=0, ign=None, damage=0, igntype=''):
        super().__init__(x=x, y=y)
        self.type = 'bullet'
        self.live = True
        self.pos = pygame.Vector2(x, y)
        self.vec = vec
        self.clc = pygame.time.Clock()
        self.rendered = pygame.transform.rotate(all.game.bul, vec.angle_to((1,0)))
        self.ignored = ign
        self.damage = damage
        self.ignoredtype = igntype
        self.net_params = ((False, True), (), ['vec'], (False, True))

    def drawer(self, screen, pos):
        if not self.live:
            return # add deelte 

        screen.blit(self.rendered, pos)

    def ubdate(self, delta):
        self.pos += self.vec * delta
        c = all.game.getcell(int(self.pos.x // all.game.cellsizx), int(self.pos.y // all.game.cellsizy))
        if c == None or c.pos:
            if (not c == None) and c.destr:
                c.destroy()
            all.game.delete_object(self)
            return
        c = poscolide(self.pos, ignor=self.ignored, typign=[self.ignoredtype, 'item'])
        if c != None and c != self.ignored:
            c.hit(self.damage)
            all.game.delete_object(self)
            return
    def client_update(self, delta):
        self.pos += self.vec * delta


class minibul(entity):
    def __init__(self, vec, x=0, y=0, angle=0, ign=None, damage=0, igntype='', tim=10):
        super().__init__(x=x, y=y)
        self.type = 'bullet'
        self.live = True
        self.pos = pygame.Vector2(x, y)
        self.vec = vec
        self.clc = pygame.time.Clock()
        self.rendered = pygame.transform.rotate(textures['minibul'][1], vec.angle_to((1,0)))
        self.ignored = ign
        self.damage = damage
        self.ignoredtype = igntype
        self.timr = time()
        self.tim = tim
        self.net_params = ((False, True), (), ['vec'], (False, True))

    def drawer(self, screen, pos):

        if not self.live:
            return # add deelte 

        screen.blit(self.rendered, pos)

    def ubdate(self, delta):
        if time() - self.timr > self.tim:
            all.game.delete_object(self)
            return
        self.pos += self.vec * delta
        c = all.game.getcell(int(self.pos.x // all.game.cellsizx), int(self.pos.y // all.game.cellsizy))
        if c == None or c.pos:
            if (not c == None) and c.destr:
                c.destroy()
                
            all.game.delete_object(self)
            return
        c = poscolide(self.pos, ignor=self.ignored, typign=[self.ignoredtype, 'item'])
        if c != None and c != self.ignored:
            c.hit(self.damage)
            all.game.delete_object(self)
            return
    def client_update(self, delta):
        if time() - self.timr > self.tim:    
            return
        self.pos += self.vec * delta

class plasmabul(entity):
    def __init__(self, vec, x=0, y=0, angle=0, ign=None, damage=0, igntype=''):
        super().__init__(x=x, y=y)
        self.type = 'bullet'
        self.live = True
        self.pos = pygame.Vector2(x, y)
        self.vec = vec
        self.clc = pygame.time.Clock()
        self.rendered = pygame.transform.rotate(textures['plasmabul'][1], vec.angle_to((1,0)))
        self.ignored = ign
        self.damage = damage
        self.ignoredtype = igntype
        self.net_params = ((False, True), (), ['vec'], (False, True))

    def drawer(self, screen, pos):
        if not self.live:
            return # add deelte 
        
        screen.blit(self.rendered, pos)

    def ubdate(self, delta):
        self.pos += self.vec * delta
        c = all.game.getcell(int(self.pos.x // all.game.cellsizx), int(self.pos.y // all.game.cellsizy))
        if c == None or c.pos:
            if (not c == None) and c.destr:
                c.destroy()
                
            all.game.delete_object(self)
            return
        c = poscolide(self.pos, ignor=self.ignored, typign=[self.ignoredtype, 'item'])
        if c != None and c != self.ignored:
            c.hit(self.damage)
            all.game.delete_object(self)
            return
    def client_update(self, delta):
        self.pos += self.vec * delta
arrowid = [0]
lastarrowid = [0]

class arrow(entity):
    def __init__(self, vec, x=0, y=0, angle=0, ign=None, damage=0, igntype=''):
        super().__init__(x=x, y=y)
        self.type = 'bullet'
        self.live = True
        self.pos = pygame.Vector2(x, y)
        self.vec = vec
        self.clc = pygame.time.Clock()
        self.rendered = pygame.transform.rotate(textures['arrow'][1], vec.angle_to((1,0)))
        self.ignored = ign
        self.damage = damage
        self.ignoredtype = igntype
        self.state = 0
        self.id = arrowid[0]
        arrowid[0] += 1
        self.net_params = ((False, True), (), ['vec'], (False, True))

    def drawer(self, screen, pos):
        if not self.live:
            return # add deelte 

        screen.blit(self.rendered, pos)

    def ubdate(self, delta):
        if self.state == 0:
            self.pos += self.vec * delta
            c = all.game.getcell(int(self.pos.x // all.game.cellsizx), int(self.pos.y // all.game.cellsizy))
            if c == None or c.pos:
                if (not c == None) and c.destr:
                    c.destroy()
                self.state = 1
                if lastarrowid[0] < self.id:
                    lastarrowid[0] = self.id
                return
            c = poscolide(self.pos, ignor=self.ignored, typign=[self.ignoredtype, 'item'])
            if c != None and c != self.ignored:
                c.hit(self.damage)
                all.game.delete_object(self)
                return
        elif self.state == 1:
            if lastarrowid[0] - self.id > 5:
                all.game.delete_object(self)

    def client_update(self, delta):
        self.pos += self.vec * delta

class player(entity):
    def __init__(self, x=0, y=0):
        super().__init__(x=x, y=y)
        self.type = 'player'
        self.live = True
        self.pos = pygame.Vector2(x, y)
        self.speed = 0.3
        self.mv = pygame.Vector2(0, 0)
        self.player = all.game.playerhead
        self.eye = all.game.playereye
        self.month = all.game.playerm
        self.arm = all.game.playerarm
        self.armdraw = self.arm
        self.armvec = pygame.Vector2(1, 0)
        self.armdist = 20
        self.armforvard = pygame.Vector2(7, 0)
        self.armsdvg = pygame.Vector2(9, 0)
        self.gunsdvg = pygame.Vector2(20, 0)
        self.gunpos = pygame.Vector2(0, 0)
        self.guncorect = pygame.Vector2(0, 0)
        self.cornpos = pygame.Vector2(all.game.cellsizx, all.game.cellsizy)
        self.feetanim = animation(all.game.playerfeet, 0.2, [0, 2])
        self.moving = False
        self.drawsdwg = pygame.Vector2(0, 0)
        self.drawfeetsdwg = pygame.Vector2(0, all.game.cellsizy + 4)
        self.center = pygame.Vector2((all.game.cellsizy + 4) / 2, (all.game.cellsizy + 4) / 2)
        self.lefteye = pygame.Vector2(-7 - (all.game.cellsizx - 20) / 2, -10)
        self.righteye = pygame.Vector2(7 - (all.game.cellsizx - 20) / 2, -10)
        self.monthsdvg = pygame.Vector2((all.game.cellsizx) / 2 - (self.month.get_rect().width) - 7, 0)
        self.eyeposdvg = pygame.Vector2(0, 0)
        self.itemsdvg = pygame.Vector2(0, -20)
        self.inventar = [None, None]
        self.selected = 0
        self.coliscells = set()
        self.clicked = False
        self.lastf = time()
        self.health = 15
        self.itemselected = None
        self.level = 0
        self.wiewin = pygame.Vector2(self.pos.x, self.pos.y)
        self.pwiewin = pygame.Vector2(self.wiewin.x, self.wiewin.y)
        self.net_params = ((True, True), ['wiewin', 'inventar', 'health'], (), (True, False), ['wiewin', 'selected'])
        self.pref_selected = 0
        self.eraese_time = 10 / self.speed
        
        self.timer_cap = 0
        self.prx = self.pos.x
        self.pry = self.pos.y
        self.tx = self.pos.x
        self.ty = self.pos.y


    def drawer(self, screen, pos):
        screen.blit(self.player, pos + self.drawsdwg)
        self.feetanim.draw(screen, pos + self.drawsdwg + self.drawfeetsdwg)
        if self.feetanim:
            self.feetanim.update()
        screen.blit(self.eye, pos + self.center + self.lefteye + (self.wiewin - (self.pos + self.center)) / 90)
        screen.blit(self.eye, pos + self.center + self.righteye + (self.wiewin - (self.pos + self.center)) / 90)
        screen.blit(self.month, pos + self.center + self.monthsdvg + (self.wiewin - (self.pos + self.center)) / 130)
        screen.blit(self.armdraw, pos + self.center + self.armvec + self.armsdvg)

        if self.inventar[self.selected] != None:
            self.inventar[self.selected].draw(screen, pos + self.center + self.armsdvg + self.guncorect)
        if self.itemselected != None:
            
            screen.blit(textures['gui'][1][1][0], pos + (self.itemselected.pos - self.pos) + self.itemsdvg)

    def cursorubdate(self, vec):
        
        angle = vec.angle_to((1,0))

        self.armvec = self.armforvard.rotate(angle)
        self.gunpos = self.gunsdvg.rotate(angle)
        self.gunpos.y = -self.gunpos.y
        self.armvec.y = -self.armvec.y
        self.armdraw = pygame.transform.rotate(self.arm, angle)

        if self.inventar[self.selected] != None:
            
            if abs(angle) > 90:
                if self.inventar[self.selected] != None:
                    self.inventar[self.selected].miror(True)
                    self.inventar[self.selected].rotate(angle)
                
                self.guncorect.update(0, 0)
                

                if angle > 90:
                    angle2 = 180 - angle
                    self.guncorect.x = -self.inventar[self.selected].size[0] * math.cos(math.radians(angle2)) - self.inventar[self.selected].size[1] * math.cos(math.radians(90 - angle2))
                    self.guncorect.y = -self.inventar[self.selected].size[0] * math.sin(math.radians(angle2))

                elif angle < -90:
                    angle2 = abs(angle) - 90
                    self.guncorect.x = - self.inventar[self.selected].size[0] * math.cos(math.radians(90 - angle2))
                    self.guncorect.y = 0


            else:
                self.inventar[self.selected].miror(False)
                self.inventar[self.selected].rotate(angle)
                
                if angle > 0:

                    self.guncorect.x = 0
                    self.guncorect.y = -self.inventar[self.selected].size[0] * math.sin(math.radians(angle))
                    
                elif angle < 0:
                    self.guncorect.x = -self.inventar[self.selected].size[1] * math.cos(math.radians(90 + angle))
                    self.guncorect.y = 0
        if self.inventar[self.selected] != None:
            self.guncorect = self.guncorect + self.inventar[self.selected].sdvig.rotate(180 - angle)


    def fire(self):
        print('need')
        if self.inventar[self.selected] != None:
            self.inventar[self.selected].fire(self.pos + self.center + self.armsdvg + self.guncorect, self.gunpos, self)

    def onclick(self):
        self.clicked = True

    def offclick(self):
        self.clicked = False

    def net_onclick(self):
        if not self.clicked:
            self.clicked = True
            all.client.netdat.send_request(16, '1')
            all.client.need_send = True

    def net_offclick(self):
        if self.clicked:
            self.clicked = False
            all.client.netdat.send_request(16, '0')
            all.client.need_send = True

    def equip(self):
        self.inventar[self.selected], self.itemselected.gun = self.itemselected.gun, self.inventar[self.selected]

    def net_equip(self):
        print(self.itemselected.uuid)
        all.client.netdat.send_request(17, str(self.itemselected.uuid))
        all.client.need_send = True

    def take_heal(self, c):
        all.game.delete_object(c)
        self.health += 3


    def ubdate(self, delta):
        #self.pos = self.pos + self.mv * self.speed * delta
        if self.mv.length():
            if not self.moving:
                self.moving = True
                self.feetanim.playing = True
                self.feetanim.frame = 1
            self.pos = self.pos + collision(self.pos, self.cornpos, self.mv * self.speed * delta)
            tocolision(self.coliscells, self.pos, self.cornpos, self)
              
            c = all.game.getcell(int((self.pos.x + self.center.x) // all.game.cellsizx), int((self.pos.y + self.center.y) // all.game.cellsizy))
            if c != None and c.type == 'luck':
                all.game.nextlevel()
            c = poscolide(self.pos + self.center, ignor=self, white='item')
            if c != None and type(c.gun) is hert:
                self.take_heal(c)
            else:
                self.itemselected = c

        else:
            if self.moving:
                self.moving = False
                self.feetanim.playing = False
                self.feetanim.frame = 1

        if self.inventar[self.selected] != None:
            if abs(time() - self.lastf) > self.inventar[self.selected].worker.timr:
                self.lastf = time()
                self.inventar[self.selected].worker.update()
            if self.clicked:
                self.inventar[self.selected].worker.fire(self.pos + self.center + self.armsdvg + self.guncorect, self.gunpos, self)

    def set_pos(self, x, y):
        if self != all.client.game.playerclass:
            self.tx = x
            self.ty = y
            self.prx = self.pos.x
            self.pry = self.pos.y
            self.timer_cap = 0
        else:
            self.pos.x = x
            self.pos.y = y

    def client_update(self, delta):
        if self != all.client.game.playerclass:
            
            if self.pos.x != self.tx or self.pos.y != self.ty:
                if not self.moving:
                    self.moving = True
                    self.feetanim.playing = True
                    self.feetanim.frame = 1
                self.timer_cap += delta
                
                if self.timer_cap >= self.eraese_time:
                    self.timer_cap = self.eraese_time
                
                if self.pos.x != self.tx:
                    self.pos.x = self.prx + (self.tx - self.prx) * (self.timer_cap / self.eraese_time)
                if self.pos.y != self.ty:
                    self.pos.y = self.pry + (self.ty - self.pry) * (self.timer_cap / self.eraese_time)
            else:
                if self.moving:
                    self.timer_cap = 0
                    self.moving = False
                    self.feetanim.playing = False
        else:
            if self.mv.length():
                if not self.moving:
                    self.moving = True
                    self.feetanim.playing = True
                    self.feetanim.frame = 1
                self.pos = self.pos + collision(self.pos, self.cornpos, self.mv * self.speed * delta)
                tocolision(self.coliscells, self.pos, self.cornpos, self)
                c = poscolide(self.pos + self.center, ignor=self, white='item')
                if c != None and type(c.gun) is hert:
                    all.client.netdat.send_request(17, str(c.uuid))
                    all.client.need_send = True
                else:
                    self.itemselected = c
            else:
                if self.moving:
                    self.moving = False
                    self.feetanim.playing = False
                    self.feetanim.frame = 1
            if self.selected != self.pref_selected:
                self.pref_selected = self.selected
                all.client.netdat.send_request(18, str(self.selected))
                all.client.need_send = True


    def server_update(self, delta):
        if abs(self.pwiewin.x - self.wiewin.x) > 50 or abs(self.pwiewin.y - self.wiewin.y) > 50:
            self.sync = True
            self.pwiewin.x = self.wiewin.x
            self.pwiewin.y = self.wiewin.y

        if abs(self.prx - self.pos.x) > 10 or abs(self.pry - self.pos.y) > 10:
            self.sync = True
            self.prx = self.pos.x
            self.pry = self.pos.y
            tocolision(self.coliscells, self.pos, self.cornpos, self)
        if self.inventar[self.selected] != None:
            angle = (self.wiewin - self.pos).angle_to((1,0))
            self.gunpos = self.gunsdvg.rotate(angle)
            self.gunpos.y = -self.gunpos.y
            if abs(time() - self.lastf) > self.inventar[self.selected].worker.timr:
                self.lastf = time()
                self.inventar[self.selected].worker.update()
            if self.clicked:
                self.inventar[self.selected].worker.fire(self.pos + self.center + self.armsdvg + self.guncorect, self.gunpos, self)


    def move(self, mov):
        if mov.length() == 0:
            self.mv.update(0, 0)
            return
        self.mv = mov
        self.mv = pygame.math.Vector2.normalize(self.mv)

    def hit(self, dmg):
        self.health -= dmg
        if self.health <= 0:
            self.health = 0
            all.game.gamower()



circlepos = [(1, 0), (1, 1), (0, 1),(1, -1), (-1, 0), (-1, -1), (0, -1), (-1, 1)]
sizpos = [(0, 0),(0, 1), (1, 0), (1, 1)]

def pathfind(fromx, fromy, tox, toy, endrule=lambda w, tx, ty: (w[1][0] == tx and w[1][1] == ty), rules=[lambda w, tx, ty: ((tx - w[1][0]) ** 2 + (ty - w[1][1]) ** 2)], debug=False):
    toupdate = set()
    toupdate.add((0, (fromx, fromy), 0))
    mas = [[None] * all.game.gridsizx for i in range(all.game.gridsizy)]
    mas[fromy][fromx] = [0, (fromx, fromy)]
    while len(toupdate) > 0:
        worker = min(toupdate, key= lambda x: (x[0]))
        toupdate.remove(worker)
        if endrule(worker, tox, toy):
            break
        for pos in circlepos:
            if mas[worker[1][1] + pos[1]][worker[1][0] + pos[0]] != None:
                continue
            ok = True
            for i in sizpos:
                c = all.game.getcell(pos[0] + i[0] + worker[1][0], pos[1] + i[1] + worker[1][1])
                if c == None or c.pos:
                    ok = False
                    break
            if not ok:
                continue
            mas[worker[1][1] + pos[1]][worker[1][0] + pos[0]] = [mas[worker[1][1]][worker[1][0]][0] + 1, (worker[1][0], worker[1][1])]
            coast = 0
            for i in rules:
                coast += i(worker, tox, toy)
            toupdate.add((mas[worker[1][1] + pos[1]][worker[1][0] + pos[0]][0] + coast, (worker[1][0] + pos[0], worker[1][1] + pos[1]), mas[worker[1][1] + pos[1]][worker[1][0] + pos[0]][0]))
    if debug:
        print(mas)
        print('-' * 100)
        print(toupdate)
    if not endrule(worker, tox, toy):
        return
    worker = (worker[1][0], worker[1][1])
    path = []
    while worker[0] != fromx or worker[1] != fromy:
        path.append((worker[0] * all.game.cellsizx, worker[1] * all.game.cellsizy))
        worker = (mas[worker[1]][worker[0]][1])
    return path




class enemy(player):

    def __init__(self, x=0, y=0):
        entity.__init__(self, x=x, y=y)
        self.type = 'enemy'
        self.live = True
        self.pos = pygame.Vector2(x, y)
        self.speed = 0.2
        self.mv = pygame.Vector2(0, 0)
        self.player = all.game.enemyhead
        self.eye = all.game.enemyeye
        self.month = all.game.enemym
        self.arm = all.game.enemyarm
        self.armdraw = self.arm
        self.armvec = pygame.Vector2(1, 0)
        self.armdist = 20
        self.armforvard = pygame.Vector2(7, 0)
        self.armsdvg = pygame.Vector2(9, 0)
        self.gunsdvg = pygame.Vector2(20, 0)
        self.gunpos = pygame.Vector2(0, 0)
        self.guncorect = pygame.Vector2(0, 0)
        self.cornpos = pygame.Vector2(all.game.cellsizx, all.game.cellsizy)

        self.feetanim = animation(all.game.enemyfeet, 0.2, [0, 2])
        self.moving = False
        self.drawsdwg = pygame.Vector2(0, 0)
        self.drawfeetsdwg = pygame.Vector2(0, all.game.cellsizy + 4)
        self.center = pygame.Vector2((all.game.cellsizy + 4) / 2, (all.game.cellsizy + 4) / 2)
        self.lefteye = pygame.Vector2(-7 - (all.game.cellsizx - 20) / 2, -10)
        self.righteye = pygame.Vector2(7 - (all.game.cellsizx - 20) / 2, -10)
        self.monthsdvg = pygame.Vector2((all.game.cellsizx) / 2 - (self.month.get_rect().width) - 7, 0)
        self.eyeposdvg = pygame.Vector2(0, 0)
        self.wiewin = pygame.Vector2(self.pos.x, self.pos.y)

        self.inventar = [all.game.randomweapon(0)]
        self.coliscells = set()
        tocolision(self.coliscells, self.pos, self.cornpos, self)
        self.lastsee = pygame.Vector2(0, 0)
        self.state = 0
        all.game.lazyenemy.append(self)
        self.walkingtime = 5
        self.lastmove = time() - randint(0, self.walkingtime)
        self.path = []
        self.pathid = 0
        self.selected = 0

        self.haspath = False
        self.see = False
        self.prfstate = self.state
        if self.inventar[0] != None:
            self.dist = self.inventar[0].enemdist
        else:
            self.dist = 6
        self.lasangle = 0
        self.lastf = time()
        self.health = 6

        self.lazyplid = 0
        self.net_params = ((False, True), ('inventar', 'wiewin', 'mv', 'pos'), (), (True, True))

    def tostate(self, stat):
        if self.state == stat:
            return
        #print(stat)
        self.state = stat
        if self.state == 0:
            self.haspath = False
        elif self.state == 1:
            pass
        elif self.state == 2:
            
            self.path = pathfind(int(self.pos.x // all.game.cellsizx), int(self.pos.y // all.game.cellsizy), 
                                 int(self.lastsee.x // all.game.cellsizx), int(self.lastsee.y // all.game.cellsizy))
            if self.path != None:
                self.pathid = len(self.path) - 1
                self.haspath = True
            else:
                self.haspath = False
        elif self.state == 3:
            self.path = pathfind(int(self.pos.x // all.game.cellsizx), int(self.pos.y // all.game.cellsizy),
                                        int(self.lastsee.x // all.game.cellsizx), int(self.lastsee.y // all.game.cellsizy),
                                            endrule=lambda w, tx, ty: ((self.dist ** 2 < ((w[1][0] - tx) ** 2 + (w[1][1] - ty) ** 2)) < (self.dist + 10) ** 2) and w[2] > 3,
                                           rules=[lambda w, tx, ty: abs(((w[1][0] - tx) ** 2 + (w[1][1] - ty) ** 2) - self.dist ** 2),
                                                  lambda w, tx, ty: raycast(((w[1][0]) * all.game.cellsizx + all.game.cellsizx / 2, w[1][1] * all.game.cellsizy + all.game.cellsizy / 2), (tx * all.game.cellsizx + all.game.cellsizx / 2, ty * all.game.cellsizy + all.game.cellsizy / 2))[1] * 50])
            #print(self.path)
            if self.path != None:
                self.pathid = len(self.path) - 1
                self.haspath = True
            else:
                self.haspath = False

    def remover(self):
        if self in all.game.lazyenemy:
            all.game.lazyenemy.remove(self)
        for i in self.coliscells:
            i.mas.remove(self)


    def lazy(self):
        self.lazyplid += 1
        pl = all.game.getplayers()
        
        if len(pl) <= self.lazyplid:
            self.lazyplid = 0
        if len(pl) == 0:
            pl = self
        else:
            pl = pl[self.lazyplid]
        c, t = raycast(self.pos + self.center, (pl.pos + pl.center) - (self.pos + self.center), ignor=self, typign=[self.type, 'item'], white='player')
        
        if t and c == pl:
            
            self.lastsee = pl.pos
            if not self.see:
                self.see = True
                self.tostate(3)
                    
            self.agrow = True

        else:
            
            if self.see:
                self.tostate(2)
                self.see = False

        if self.state == 2 or self.state == 3:
            
            self.wiewin = pl.pos + pl.center
        else:
            self.wiewin = self.mv + self.pos
        if self.state == 0:
            if (time() - self.lastmove) > self.walkingtime:
                self.lastmove = time()
                self.path = pathfind(int(self.pos.x // all.game.cellsizx), int(self.pos.y // all.game.cellsizy), 0, 0,
                                     endrule=lambda w, t1, t2: w[0] > 5, rules=[lambda w, tx, ty: 0])
                if self.path != None:
                    self.pathid = len(self.path) - 1
                    self.haspath = True
                else:
                    self.haspath = False

    def drawer(self, screen, pos):
        
        screen.blit(self.player, pos + self.drawsdwg)
        self.feetanim.draw(screen, pos + self.drawsdwg + self.drawfeetsdwg)
        screen.blit(self.eye, pos + self.center + self.lefteye + (self.wiewin - self.pos) / 90)
        screen.blit(self.eye, pos + self.center + self.righteye + (self.wiewin - self.pos) / 90)
        screen.blit(self.month, pos + self.center + self.monthsdvg + (self.wiewin - self.pos) / 130)
        screen.blit(self.armdraw, pos + self.center + self.armvec + self.armsdvg)
        if self.lasangle != self.wiewin.angle_to((1,0)):
            #print(self.guncorect, self.gunpos)
            self.lasangle = self.wiewin.angle_to((1,0))
            self.cursorubdate(self.wiewin - self.pos)

        if self.moving:
            self.feetanim.update()

        if self.inventar[self.selected] != None:
            self.inventar[self.selected].draw(screen, pos + self.center + self.armsdvg + self.guncorect)


        
    def fire(self):
        if self.inventar[self.selected] != None:
            self.inventar[self.selected].fire(self.pos + self.center + self.armsdvg + self.guncorect, self.gunpos, self)

    def ubdate(self, delta):
        if not self.live:
            return
        #self.pos = self.pos + self.mv * self.speed * delta
        if self.mv.length():
            if not self.moving:
                self.moving = True
                self.feetanim.playing = True
                self.feetanim.frame = 1
            self.pos = self.pos + self.mv * self.speed * delta #collision(self.pos, self.cornpos, self.mv * self.speed * delta)
            tocolision(self.coliscells, self.pos, self.cornpos, self)
        else:
            if self.moving:
                self.moving = False
                self.feetanim.playing = False
                self.feetanim.frame = 1

        if self.inventar[self.selected] != None:
            if abs(time() - self.lastf) > self.inventar[self.selected].worker.timr:
                self.lastf = time()
                self.inventar[self.selected].worker.update()
            if self.see:
                self.inventar[self.selected].worker.fire(self.pos + self.center + self.armsdvg + self.guncorect, self.wiewin - self.pos, self)

        if self.haspath:
            if ((self.pos.x - self.path[self.pathid][0]) ** 2 + (self.pos.y - self.path[self.pathid][1]) ** 2) < 0.5:
                self.pathid -= 1
                if self.pathid < 0:
                    self.haspath = False
                    if self.mv.length() != 0:
                        self.sync = True
                    self.mv.update(0, 0)
                    if self.state == 3:
                         self.path = pathfind(int(self.pos.x // all.game.cellsizx),
                                             int(self.pos.y // all.game.cellsizy), int(self.lastsee.x // all.game.cellsizx), 
                                             int(self.lastsee.y // all.game.cellsizy), 
                                             endrule=lambda w, tx, ty: ((self.dist ** 2 < ((w[1][0] - tx) ** 2 + (w[1][1] - ty) ** 2)) < (self.dist + 10) ** 2) and w[2] > 3, 
                                             rules=[lambda w, tx, ty: abs(((w[1][0] - tx) ** 2 + (w[1][1] - ty) ** 2) - self.dist ** 2),
                                                    lambda w, tx, ty: raycast(((w[1][0]) * all.game.cellsizx + all.game.cellsizx / 2, w[1][1] * all.game.cellsizy + all.game.cellsizy / 2), (tx * all.game.cellsizx + all.game.cellsizx / 2, ty * all.game.cellsizy + all.game.cellsizy / 2))[1] * 50])
                         if self.path != None:
                             self.pathid = len(self.path) - 1
                             self.haspath = True
                         else:
                             self.haspath = False
                    elif self.state == 2:
                        self.tostate(0)
                    return
            self.move(self.path[self.pathid] - self.pos)
        else:
            if self.mv.length() != 0:
                self.sync = True
            self.mv.update(0, 0)

    def client_update(self, delta):
        self.pos = self.pos = self.pos + self.mv * self.speed * delta
        

    def move(self, mov):
        if mov.length() == 0:
            self.mv.update(0, 0)
            return
        pr = pygame.math.Vector2.normalize(mov)
        if pr != self.mv:
            self.sync = True
        self.mv = pr

    def hit(self, dmg):
        self.health -= dmg
        if self.health <= 0:
            self.health = 0
            all.game.delete_object(self)
            return

class item(entity):
    def __init__(self, x=0, y=0, gun=None):
        super().__init__(x=x, y=y)
        self.type = 'item'
        self.gun = gun
        self.cornpos = pygame.Vector2(30, 30)
        self.mas = set()
        tocolision(self.mas, self.pos, self.cornpos, self)
        self.net_params = ((True, False), ['gun'], (), (False, True))
         
    def server_update(self, delta):
        if self.gun == None:
            all.game.delete_object(self)
            return

    def drawer(self, screen, pos):
        if self.gun == None:
            
            all.game.delete_object(self)
            
            return

        self.gun.draw(screen, pos)

    def remover(self):
        for i in self.mas:
            i.mas.remove(self)
    def on_sync_get(self):
        if 'gun' in str(type(self.gun)):
            self.gun.updateimage()

class hert:
    def __init__(self, *args, **kwargs):
        self.net_params = ((False, False), (), (), (False, True))

    def draw(self, screen, pos):
        screen.blit(textures['heart'][1], pos)


grid_cells = [wall, box, flor, luck, superbox]
objects = [bullet, minibul, plasmabul, arrow, player, enemy, item]