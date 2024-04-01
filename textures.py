toloadids = []
from vars import eror
datafiledir = 'data'

# ofsetx ofsety sizex sizey count deltax deltay
textures = {'menu_back': ['background.png', eror],
            'menu_start_btn': ['startbtn.png', eror, 1,[(0, 0, 125, 36, 2, 0, 36)]],
            'pers': ['to menu.png', eror, 1],
            'wals': ['grid textures\walls.png', eror, 1, [(0, 0, 12, 12, 3, 12, 0)]],
            'player': ['unit textures\player.png', eror, 1],
            'player parts':['unit textures\plyer.png', eror, 1,[(0, 0, 11, 9, 1, 0, 0),
                                                             (11, 0, 11, 3, 3, 11, 0),
                                                            (11, 4, 3, 3, 1, 0, 0),
                                                           (15, 4, 4, 3, 1, 0, 0),
                                                           (11, 7, 5, 3, 1, 0, 0)]],
            'bullet': ['items/bullet.png', eror],
            'enemy parts': ['unit textures\enemy.png', eror,  1, [(0, 0, 11, 9, 1, 0, 0),
                                                             (11, 0, 11, 3, 3, 11, 0),
                                                            (11, 4, 3, 3, 1, 0, 0),
                                                           (15, 4, 4, 3, 1, 0, 0),
                                                           (11, 7, 5, 3, 1, 0, 0)]],
            'boxes': ['grid textures/box.png', eror, 1, [(0, 0, 12, 12, 4, 12, 0)]],
            'heart': ['health.png', eror, 3],
            'luck': ['grid textures/luck.png', eror],
            'test': ['debug.png', eror],
            'gui': ['gui.png', eror, 1, [(0, 0, 42, 42, 1, 0, 0), (50, 0, 27, 14, 2, 0, 14)]],
            'minibul': ['items/minibullet.png', eror, 4],
            'plasmabul': ['items/plasmabullet.png', eror, 4],
            'gamover': ['game over.png', eror],
            'hint':['hint.png', eror],
            'arrow': ['items/arrow.png', eror, 4]}