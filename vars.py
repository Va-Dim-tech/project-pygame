from pygame import Vector2
from other import generateeror
gridfolder = 'grid textures'
unitfolder = 'unit textures'


eror = generateeror()

class variables():
    def __init__(self, *args, **kwargs):
        self.loadscreen = None
        self.ubdatelist = None
        self.font = None
        self.hasload = False
        self.lastload = ''
        self.lastLoadId = 0
        self.toloadids = []
        self.toscndonload = None
        self.loading_scene = ''
        self.scene = None
        self.xsiz = 600
        self.ysiz = 600
        self.game = None
        self.eror = None
        self.threading = False
        self.threads = []
        self.threadcount = 0
        self.curpos = Vector2(0, 0)
        self.gametexturesload = False
        self.recordfilame = 'record'
        self.record = 0

varsclass = variables()


settings = {'up': 0,
            'down': 0,
            'left': 0,
            'right': 0,
            'equip': 0,
            'change': 0}

