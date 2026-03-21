import pygame
from vars import varsclass
from textures import *
from main import loadscene, updaterecord


class menu():
    def start(self):
        print('start menu')
        self.back = pygame.transform.scale(textures['menu_back'][1],
                                          (varsclass.xsiz, varsclass.ysiz))
        self.startbtn = textures['menu_start_btn'][1]
        self.multstartbtn = textures['menu_multiplayer_btn'][1]
        self.pers = pygame.transform.scale(textures['pers'][1], (varsclass.xsiz / 3, varsclass.ysiz / 3))
        self.multstartbutton = self.multstartbtn[0][0].get_rect()
        self.multstartbutton.x = varsclass.xsiz / 3
        self.multstartbutton.y = varsclass.ysiz / 3
        self.multstartbuttonsel = False
        self.startbtnrect = self.startbtn[0][0].get_rect()
        self.startbtnrect.x = varsclass.xsiz / 3
        self.startbtnrect.y = varsclass.ysiz / 4
        self.startbtnsel = False
        self.addr_text = varsclass.client.addres + ':' + str(varsclass.client.port)

        updaterecord()

    def eventer(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.startbtnrect.collidepoint(event.pos):
                self.startbtnsel = True
            else:
                self.startbtnsel = False
            if self.multstartbutton.collidepoint(event.pos):
                self.multstartbuttonsel = True
            else:
                self.multstartbuttonsel = False
        

        if event.type == pygame.MOUSEBUTTONUP:
            
            if self.startbtnsel:
                loadscene('game')
                #loadscene('client')
            if self.multstartbuttonsel:
                varsclass.client.addres = self.addr_text
                loadscene('client')
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.addr_text = self.addr_text[:-1]
            else:
                self.addr_text += event.unicode 
            

    def drawer(self, dt, screen):
        screen.blit(self.back, (0, 0))
        if self.startbtnsel:
            screen.blit(self.startbtn[0][1], (varsclass.xsiz / 3, varsclass.ysiz / 4))
        else:
            screen.blit(self.startbtn[0][0], (varsclass.xsiz / 3, varsclass.ysiz / 4))
        if self.multstartbuttonsel:
            screen.blit(self.multstartbtn[0][1], (varsclass.xsiz / 3, varsclass.ysiz / 3))
        else:
            screen.blit(self.multstartbtn[0][0], (varsclass.xsiz / 3, varsclass.ysiz / 3))

        screen.blit(varsclass.font.render(self.addr_text, 1, (0, 0, 0)), (varsclass.xsiz / 3, varsclass.ysiz / 3))

        if varsclass.record != 0:
            screen.blit(varsclass.font.render('рекорд: ' + str(varsclass.record), 1, (255, 255, 255)), (varsclass.ysiz / 3, varsclass.ysiz / 2))

    def toscene(self):
        pass


    def ubdate(self, dt):
        pass

    def doneload(self):
        pass
