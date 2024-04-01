import pygame
from vars import varsclass as all
from vars import eror as Nonfile
from other import *
from textures import *
import sys

if __name__ == '__main__':

    pygame.init()  #fast show
    size = all.xsiz, all.ysiz = 600, 600
    all.screen = pygame.display.set_mode(size)
    pygame.display.flip()

    if not os.path.isdir('data'):
        try:
            os.chdir(sys._MEIPASS)
            print('work in', sys._MEIPASS)
        except:
            print('eror to change dir')
    else:
        print('work in start folder')
    all.loadscreen = load_image('load_screen.png')
    all.loadscreen = pygame.transform.scale(all.loadscreen, (600, 600))
    all.screen.blit(all.loadscreen, (0, 0))
    pygame.display.flip()

import random
import threading
import os
from time import time
from vars import settings


#globals
lasttask = 0
ubdatefreq = 1 / 60
drawfreq = 0
all.hasload = False
all.lastLoadId = 0
all.sumarLoad = 0
all.lastload = ''
all.gametexturesload = False
tsklock = threading.Lock()


def gettask():
    tsklock.acquire()
    if lasttask < len(ubdatelist):
        
        res = lasttask
        lasttask += 1
        tsklock.release()
        return lasttask
    tsklock.release()
    return



def getLoad():
    tsklock.acquire()
    if all.hasload and all.lastLoadId < len(all.toloadids):
        id = all.lastLoadId
        all.lastLoadId += 1
        tsklock.release()
        if all.lastLoadId >= len(all.toloadids):
            all.hasload = False
        return all.toloadids[id]
    tsklock.release()
    return

def backLoad(nom):
    ldid = getLoad()
    if ldid != None:
        if textures[ldid][1] is not None and textures[ldid][1] is not Nonfile:
            return
        if len(textures[ldid]) > 3:
            textures[ldid][1] = load_multi_image(textures[ldid][0], textures[ldid][3], sizemod=textures[ldid][2])
        else:
            if len(textures[ldid]) == 3:
                textures[ldid][1] = load_image(textures[ldid][0], sizemod=textures[ldid][2])
            else:
                textures[ldid][1] = load_image(textures[ldid][0])
        all.lastload = str(nom) + ': ' + textures[ldid][0]
        print(all.lastload)
        all.sumarLoad += 1


def threadcore(nom):
    print('start thread', nom)
    task = 0
    lzi = 0
    lastubd = time.process_time()
    while True:
        if time.process_time() - lastubd > ubdatefreq:
            if lasttask < len(all.ubdatelist):
                task = gettask()
                if task != None and ubdatelist[task] != None: 
                    ubdatelist[task]()
        # lazy ubdate
        if lzi >= 10:
            lzi = 0
        lzi += 1
        if all.hasload:
            backLoad(nom)


def doneload():
    all.scene.doneload()

def changescene(scn):
    print('chenging scene to', scn)
    if scn == None or scn == 'menu':
        all.scene = all.menu
        all.menu.start()

        
    elif scn == 'loader':
        all.scene = all.loader
        all.scene.start()
    elif scn == 'game':
        all.scene = all.game
        all.game.start()
    all.scene.drawer(0, all.screen)


def loadscene(scn):
    if scn == None or scn == 'menu':
            all.loading_scene = 'menu'
            changescene('loader')
    if scn == 'game':
        if not all.gametexturesload:
            all.lastLoadId = 0
            all.sumarLoad = 0
            all.toloadids = ['wals', 'player', 'player parts', 'bullet',
                            'enemy parts', 'boxes', 'heart', 'luck', 'test', 'gui',
                            'minibul', 'plasmabul', 'gamover', 'hint', 'arrow']
            all.hasload = True
        all.loading_scene = 'game'
        changescene('loader')

def updaterecord():
    if not os.path.isfile(all.recordfilame):
        if all.record == 0:
            return
        print('record file not found, creating file')
        f = open(all.recordfilame, 'w')
        f.write(str(all.record))
        f.close()
        return
    else:
        f = open(all.recordfilame)
        try:
            a = int(f.readline())
        except:
            print('record file reading eror, recreating file')
            a = 0
            f.close()
            f = open(all.recordfilame, 'w')
            f.write(str(all.record))
            f.close()
        if a < all.record:
            f.close()
            f = open(all.recordfilame, 'w')
            f.write(str(all.record))
            f.close()
        else:
            all.record = a
            f.close()


if __name__ == '__main__':
#if True:

    all.font = pygame.font.Font(None, 30)
    # importing scenes
    from loader import loader
    from menu import menu
    from game import game
    all.loader = loader()
    all.menu = menu()
    all.game = game()
    all.eror = generateeror()
    print('imported')

    pygame.display.set_caption('смертельный лабиринт')

    all.hasload = True
    all.ubdatelist = []
    all.toloadids = ['menu_back', 'menu_start_btn']

    loadscene('menu')

    settings['up'] = pygame.key.key_code('w')
    settings['down'] = pygame.key.key_code('s')
    settings['left'] = pygame.key.key_code('a')
    settings['right'] = pygame.key.key_code('d')
    settings['equip'] = pygame.key.key_code('e')
    settings['change'] = pygame.key.key_code('q')

    clock = pygame.time.Clock()
    drawclock = pygame.time.Clock()
    lastdraw = time()
    running = True
    all.showfps = True
    frames = 0
    framesout = 0
    lastfps = time()

    all.threading = False
    if all.threading:
        print('starting paralels')
        # lol thread in python is not normal threading (hello GIL)
        all.threadcount = os.cpu_count()
        all.threads = []
        for i in range(all.threadcount):
            all.threads.append(threading.Thread(target=threadcore, args=(i + 1,), daemon=True))
            all.threads[i].start()
    all.scene = all.loader
    updaterecord()
    print('start while')
    while running:
        delta = clock.tick()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
                all.curpos.update(event.pos[0], event.pos[1])
            all.scene.eventer(event)
        if time() - lastdraw > drawfreq:
            #print(1 / (time() - lastdraw))
            lastdraw = time()
            all.screen.fill((0, 0, 0))
            drawdelta = drawclock.tick()
            all.scene.drawer(drawdelta, all.screen)
            frames += 1
            if all.showfps:
                all.screen.blit(all.font.render('fps: ' + str(framesout), 1, (255, 255, 255)), (10, all.xsiz - 30))
                if time() - lastfps > 1:
                    lastfps = time()
                    framesout = frames
                    frames = 0
        
        pygame.display.flip()
        all.scene.ubdate(delta)

        


    pygame.quit()
