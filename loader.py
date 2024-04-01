import main

from vars import varsclass



class loader():
    def start(self):
        pass

    def eventer(self, event):
        pass

    def drawer(self, dt, screen):
        screen.blit(varsclass.loadscreen, (0, 0))
        screen.blit(varsclass.font.render(varsclass.lastload, 1, (0, 0, 0)), (10, varsclass.xsiz - 30))

    def toscene(self):
        pass


    def ubdate(self, dt):
        if varsclass.hasload:
            main.backLoad(0)
        if varsclass.sumarLoad >= len(varsclass.toloadids):
            self.doneload()

    def doneload(self):
        main.changescene(varsclass.loading_scene)
