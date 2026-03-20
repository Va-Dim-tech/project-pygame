from vars import varsclass as all
import threading
import socket
import main
from net import *
from game import *

from time import time

    

blitlock = threading.Lock()


class client():
    def __init__(self):
        self.id = 0
        self.netdat = None
        self.state = 0
        self.instantsend = True
        self.addres = '127.0.0.1:55555'
        self.port = 55555
        self.mainsock = None
        self.prefered_buffer_len = 2000
        self.game = None
        self.keep_alive_time = 2
        self.keep_alive_time_t = time()
        self.ping_time= 2
        self.ping_time_t = 0
        self.ping = 10
        self.dead_time = 5
        self.dead_time_t = time()
        self.last_not_recived = 0
        self.objects = {} #id:obj
        self.ldtextures= {}
        self.snctextures = {}
        self.surfacecinprocess = {}

        functions[0] = to_disconnect
        functions[3] = prefer_buffer_len
        functions[4] = set_buffer_len
        functions[5] = ping_retransmission
        functions[6] = ping_get
        functions[7] = set_grid
        functions[8] = change_state
        functions[9] = set_new_obj
        functions[10] = del_obj
        functions[11] = move_object
        functions[12] = sync_obj
        functions[13] = get_surface
        functions[14] = set_player
        functions[20] = rst_level

    def start(self):
        connect(self.addres)

        


        if not all.gametexturesload:
            self.game = game()
            all.game = self.game
            self.game.init_textures()
        self.game.initialazing_game()
        self.game.entitys = []
        self.game.lazyenemy = []
        self.game.state = 0
        self.game.end_game = respawn
        self.ping_time_t = time()
        self.dead_time_t = time()
        self.keep_alive_time_t = time()
        self.ldtexttures= {}
        self.objects = {}
        self.ldtextures= {}
        self.snctextures = {}
        self.surfacecinprocess = {}
        self.need_send = True
        self.instantsend = True

    def eventer(self, event):
        self.game.eventer(event)

    def drawer(self, dt, screen):
        blitlock.acquire()
        self.game.drawer(dt, screen)
        blitlock.release()

    def toscene(self):
        shutdown()


    def ubdate(self, dt):
        if abs(time() - self.dead_time_t) > self.dead_time:
            pass
            disconnect('timeout')
        if abs(time() - self.keep_alive_time_t) > self.keep_alive_time:
            self.keep_alive_time_t = time()
            send_data()
        if abs(time() - self.ping_time_t) > self.ping_time:
            self.ping_time_t = time()
            self.netdat.send_data_funcs(5, str(time()))
            send_data()
            print('ping sendet')
             


        if self.game.state == 0:
            if self.game.playerclass != None:
                buttons = pygame.key.get_pressed()
                self.game.movevec.update(0, 0)
                if buttons[settings['right']]:
                    self.game.movevec.update(self.game.movevec.x + 1, 0)
                if buttons[settings['left']]:
                    self.game.movevec.update(self.game.movevec.x - 1, 0)
                if buttons[settings['up']]:
                    self.game.movevec.update(self.game.movevec.x, self.game.movevec.y - 1)
                if buttons[settings['down']]:
                    self.game.movevec.update(self.game.movevec.x, self.game.movevec.y + 1)
                self.game.playerclass.wiewin = cam.pos + all.curpos
                self.game.playerclass.move(self.game.movevec)
                #self.game.playerclass.client_update(dt)
                if abs(self.game.playerclass.prx - self.game.playerclass.pos.x) > 10 or abs(self.game.playerclass.pry - self.game.playerclass.pos.y) > 10:
                    self.game.playerclass.prx = self.game.playerclass.pos.x
                    self.game.playerclass.pry = self.game.playerclass.pos.y
                    all.client.netdat.send_data_funcs(11, str(self.game.playerclass.uuid) + ' ' + str(self.game.playerclass.prx) + ' ' + str(self.game.playerclass.pry))
                    
                    self.need_send = True
                if self.game.playerclass != None and self.game.playerclass.clicked:
                    if abs(self.game.playerclass.pwiewin.x - self.game.playerclass.wiewin.x) > 5 or abs(self.game.playerclass.pwiewin.y - self.game.playerclass.wiewin.y) > 5:
                        self.game.playerclass.pwiewin.x = self.game.playerclass.wiewin.x
                        self.game.playerclass.pwiewin.y = self.game.playerclass.wiewin.y
                        send_sync_data(self.netdat, self.game.playerclass.uuid)
                        self.need_send = True

                else:
                    if abs(self.game.playerclass.pwiewin.x - self.game.playerclass.wiewin.x) > 50 or abs(self.game.playerclass.pwiewin.y - self.game.playerclass.wiewin.y) > 50:
                        self.game.playerclass.pwiewin.x = self.game.playerclass.wiewin.x
                        self.game.playerclass.pwiewin.y = self.game.playerclass.wiewin.y
                        send_sync_data(self.netdat, self.game.playerclass.uuid)
                        self.need_send = True
                cam.move(dt, self.game.playerclass.pos + self.game.playerclass.center + (all.curpos - self.game.curvec) / 2)

        for i in self.game.entitys:
            if i.net_params[0][1]:
                i.client_update(dt)

        if self.need_send:
            self.need_send = False
            send_data()
            while self.netdat.tecMess > 0:
                send_data()





    def doneload(self):
        pass

def respawn():
    all.client.netdat.send_request(19, '3')


stop = False
def message_reciever():
    cli = all.client
    while True:
        try:
            st, adr = cli.mainsock.recvfrom(cli.netdat.Mlen)
        except:
            print('except in recvfrom')
            continue
        if stop:
            print('thread stopped')
            return
        if st == None:
            continue

        st = st.decode()
        if len(st) < 11:
            continue

        if cli.state == 0:
            rid = st[:3]
            if cli.netdat.id == 0:
                cli.netdat.id = rid
                print('get id', cli.netdat.id)
        #print('recived', st)
        st = cli.netdat.message_parser(st)
        
        if st != None:
            #print('sucsesffuly recieved', len(st[0]), 'answer_funcs', len(st[1]), 'functions', len(st[2]), 'data_funcs')
            ints = cli.instantsend
            cli.netdat.exec_all_functions(cli.netdat, st[1])
            cli.netdat.exec_to_answer_funcs(cli.netdat, st[0])
            cli.netdat.exec_data_funcs(cli.netdat, st[2])
            cli.dead_time_t = time()
            cli.last_not_recived = st[3]
            if cli.last_not_recived != 0:
                if abs(time() - cli.last_not_recived) > (cli.netdat.ping * 4):
                    cli.netdat.add_fix_func(cli.netdat.ping)
                    cli.need_send = True
            if ints:
                send_data()



def send_data():
    st = all.client.netdat.message_generator()
    if st != None:
        #print('sendet', st)
        all.client.mainsock.sendto(bytes(st, encoding='utf-8'), (all.client.addres, all.client.port))

    

def connect(fulladdr):
    global netdat 
    global addres 
    global port
    global mainsock
    global stop
    global recievingthread
    s = fulladdr.split(':')
    if len(s) < 2:
        print('addres syntax error: not found ":"')
        return False
    addr = s[0]
    all.client.port = s[1]
    s = addr.split('.')
    if len(s) < 4:
        print('addres syntax error: not enough octet')
        return False
    for i in s:
        if not i.isdigit():
            print('addres syntax error: uncorrect letter in', i)
            return False
        if not (0 <= int(i) < 256):
            print('addres syntax error: uncorrect integer in', i)
            return False
    print('trying to connect to:', fulladdr)
    all.client.addres = addr
    all.client.port = int(all.client.port)
    all.client.mainsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
   
    all.client.netdat = netdata()
    send_data()
    stop = False
    if recievingthread != None:
        del recievingthread
    recievingthread = threading.Thread(target=message_reciever, daemon=True)
    recievingthread.start()



def ping_retransmission(arg, client=None):

    client.send_data_funcs(6, arg)
    send_data()

def ping_get(arg, client=None):
    try:
        client.ping = abs(time() - float(arg)) / 2
        print('gettet ping', client.ping)
    except:
        return


def shutdown():
    global stop
    stop = True
    all.client.mainsock.sendto(bytes('asd', encoding='utf-8'), ('127.0.0.1', all.client.mainsock.getsockname()[1]))
    all.client.objects = {}
   



def disconnect(reason):
    print('disconnection by reason:', reason)
    all.client.netdat.send_request(0, reason)

    shutdown()
    main.changescene('menu')

def prefer_buffer_len(arg, client=None):
    return all.client.prefered_buffer_len

def set_buffer_len(arg, client=None):
    arg = arg.strip()
    if arg.isdigit():
        arg = int(arg)
        client.Mlen = arg
        return ''
    else:
        disconnect()

def to_disconnect(arg, **keys):
    print('disconnection by reason:', arg)
    shutdown()

def rst_level(arg, client=None):
    for y in range(all.game.gridsizy):
        for x in range(all.game.gridsizx):
            all.game.setcell(x, y, flor(x, y))
    all.game.playerclass = None
    all.game.entitys = []
    all.client.objects = {}



def change_state(arg, client=None):
    try:
        arg = int(arg)
    except:
        print('except in change state')
        return ''
    all.client.game.tostate(arg)
    print('tec state', all.client.game.state)
    if arg == 0:
        all.client.instantsend = False
    return ''

def set_grid(arg, **keys):
    arg = arg.split()
    if len(arg) < 3 or (not arg[0].strip().isdigit()) or (not arg[1].strip().isdigit()) or (not arg[2].strip().isdigit()):
        return None
    i = int(arg[0])
    x = int(arg[1])
    y = int(arg[2])
    if x < 0 or x > all.game.gridsizx or y < 0 or y > all.game.gridsizy:
        return None
    all.game.setcell(x, y, grid_cells[i](x, y))


def parser_for_set_new_obj(i, arg):
    if i >= len(arg):
        print('parser_for_set_new_obj: error: str is too small')
        return 
    if arg[i] == 'S':
        i += 1
        pi = i
        i = arg.find(' ', i)
        st = arg[pi:i]
        if not st.isdigit():
            print('parser_for_set_new_obj: error: surface index not is digit in', arg)
            return (i, generateeror())
        id = int(st)
        if id not in all.client.ldtextures:
            all.client.netdat.send_request(13, str(c), addition=get_surface)
            all.client.ldtextures[id] = None
            print('parser_for_set_new_obj: creting response for new surface')
            
        if all.client.ldtextures[id] == None:
            print('parser_for_set_new_obj: alert: recived not loadet texture')
            return (i, generateeror())
        return (i, all.client.ldtextures[id])
    elif arg[i] == 'V': 
        i += 1 
        pi = i 
        i = arg.find(' ', i)
        x = arg[pi:i]
        i += 1 
        pi = i
        i = arg.find(' ', i)
        y = arg[pi:i]
        if i == -1:
            i = len(arg)

        try:
            x = float(x)
            y = float(y)
        except:
            print('parser_for_set_new_obj: error: vector index not is digit in', arg)
            return (i, pygame.Vector2(0, 0))
        
        return (i, pygame.Vector2(x, y))
    elif arg[i] == '<':
        i += 1
        pi = i
        i = arg.find(' ', i)
        id = arg[pi:i]
        if not id.isdigit():
            print('parser_for_set_new_obj: error: new obj not is digit', arg)
            return
        id = int(id)
        if id >= len(other_objects):
            print('parser_for_set_new_obj: error: id not in other objects', arg)
            return 
        i += 1 
        params = []
        while i < len(arg) and arg[i] != '>':
            if arg[i] != ' ':
                pi = i
                while i < len(arg) and arg[i] != ':' and arg[i] != ' ':
                    i += 1
                st = arg[pi:i]
                if st == 'params':
                    i += 1
                    ob = parser_for_set_new_obj(i, arg)
                    if ob == None:
                        print('parser_for_set_new_obj: error: parser_for_set_new_obj returned None')
                        return
                    i, ob = ob
                    params.append(ob)
                else:
                    print('parser_for_set_new_obj: error: not resolvet', st, 'in', arg)
            i += 1
        i += 1
        return (i, other_objects[id](*params))
    else:
        pi = i
        i = arg.find(' ', i)
        if i == -1:
            i = len(arg) - 1
        return (i, arg[pi:i])



def set_new_obj(arg, **karg):
    print('new obj', arg)
    if len(arg) < 6:
        print('set new object: error is too small in', srg)
        return
    i = 0
    pi = 0
    try:
        pi = i
        i = arg.find(' ', i)
        id =  int(arg[pi:i])
        i += 1
        pi = i 
        i = arg.find(' ', i)
        uuid = int(arg[pi:i])
        i += 1
        pi = i
        i = arg.find(' ', i)
        x = float(arg[pi:i])
        i += 1
        pi = i
        i = arg.find(' ', i)
        y = float(arg[pi:i])
    except:
        print('set new object: exeption in', arg)
        return 
    if not (0 <= id < len(objects)):
        print('set new object: id not in objects')
        return
    params = []
    kparams = {}
    if i != -1:
        while i < len(arg):
            if arg[i] != ' ':
                pi = i
                while i < len(arg) and arg[i] != ' ' and arg[i] != ':':
                    i += 1
                st = arg[pi:i]
                if st == 'params':
                    i += 1
                    ob = parser_for_set_new_obj(i, arg)
                    if ob == None:
                        print('set new object: error: parser_for_set_new_obj returned None')
                        return
                    i, ob = ob
                    params.append(ob)
                
                else:

                    kparam = st
                    i += 1
                    ob = parser_for_set_new_obj(i, arg)
                    if ob == None:
                        print('set new object: error: parser_for_set_new_obj returned None')
                        return
                    i, ob = ob
                    kparams[kparam] = ob
                    print('set new object: error: not resolved', st, 'in', arg)
            i += 1
    obj = objects[id](x=x, y=y, *params, **kparams)
    obj.uuid = uuid
    all.client.objects[uuid] = obj
    all.client.game.add_gnerated_object(obj)
    obj.client_init()

def move_object(arg, **keys):
    argt = arg.split()
    if len(argt) < 3:
        print('error 1 in move object', arg)
        return 
    try:
        argt[0] = int(argt[0])
        argt[1] = float(argt[1])
        argt[2] = float(argt[2])
    except:
        print('error 2 in move object', arg)
        return
    if argt[0] not in all.client.objects:
        print('error 3 in move object', arg)
        return
    if all.client.game.playerclass != None and all.client.objects[argt[0]] == all.client.game.playerclass:
        if abs(all.client.objects[argt[0]].pos.x - argt[1]) < 1000 and abs(all.client.objects[argt[0]].pos.y - argt[2]) < 1000:
            return

    all.client.objects[argt[0]].set_pos(argt[1], argt[2])
    


   


def generator_for_sync_obj(i, arg, obj, param, aobj):
    if i >= len(arg):
        return i
    if arg[i] == 'S':
        i += 1
        pi = i
        i = arg.find(' ', i)
        if i == -1:
            i = len(arg) - 1
        id = arg[pi:i]
        if not id.isdigit():
            print('generator_for_sync_obj: error: surface id not is int', id, 'in', arg)
            return i
        id = int(id)
        if id not in all.client.ldtextures:
            
            all.client.netdat.send_request(13, str(id), addition=get_surface)
            all.client.ldtextures[id] = None

        if all.client.ldtextures[id] == None:
            if id not in all.client.snctextures:
                all.client.snctextures[id] = []
            all.client.snctextures[id].append((aobj, param))
            print('generator_for_sync_obj: alert: not loadet texture', id)
            return (i, generateeror())
        return (i, all.client.ldtextures[id])
    elif arg[i] == 'V':
        i += 1
        pi = i 
        i = arg.find(' ', i)
        if i == -1:
            print('generator_for_sync_obj: error: vector has not y', arg)
            return i
        x = arg[pi:i]
        i += 1
        pi = i
        i = arg.find(' ', i)
        if i == -1:
            i = len(arg) - 1
        y = arg[pi:i]
        x = float(x)
        y = float(y)
        c = obj
        c.x = x 
        c.y = y
        return i
    elif arg[i] == '[':
        i += 1
        if arg[i] != ' ':
            pi = i 
            i = arg.find(']', i)
            
            id = arg[pi:i]
            i += 2
            if not id.isdigit():
                print('generator_for_sync_obj: error: mas index not is digit in', arg)
                return i 
            id = int(id)
            ob = generator_for_sync_obj(i, arg, obj[id], param, obj)
            if ob == None:
                print('generator_for_sync_obj: error: generator_for_sync_obj returnet None')
                return 
            if type(ob) != tuple:
                i = ob
                return i
            
            i, ob = ob
            obj[id] = ob
            return i
        id = 0
        while i < len(arg) and arg[i] != ']':
            if arg[i] != ' ':

                ob = obj[id]
                ob = generator_for_sync_obj(i, arg, ob, param, obj)
                if ob == None:
                    print('generator_for_sync_obj: error: generator_for_sync_obj returnet None')
                    return
                if type(ob) != tuple:
                    i = ob
                    #i = arg.find(']', i)
                    i += 1
                    id += 1
                    continue
                    #return i
                i, ob = ob
                if type(ob) == int:
                    if ob == -10:
                        print('generator_for_sync_obj: alert: generator_for_sync_obj say that the obj is None, response for what is that')
                        all.client.netdat.send_data_funcs(15, str(aobj.uuid) + ' ' + param + ':[' + str(id) + ']')
                    else:
                        obj[id] = ob
                else:
                    obj[id] = ob
                id += 1
            
            i+= 1 
        i+= 1
        
        return i 
    elif arg[i] == '{':
        if obj == None:
            print('error 2 in parser_for_sync_objects response for what is it')
            while i < len(arg) and arg[i] != '}':
                i += 1
            return (i, -10)
        i += 1
        while i < len(arg) and arg[i] != '}':
            if arg[i] != ' ':
                pi = i
                i = arg.find(':', i)
                kparam = arg[pi:i]
                i += 1
                
                ob = generator_for_sync_obj(i, arg,getattr(obj, kparam), kparam, obj)
                if ob == None:
                    print('generator_for_sync_obj: error: generator_for_sync_obj returned None in sync exited obj in', arg)
                    return 
                if type(ob) != tuple:
                    i = ob
                else:
                    i, ob = ob
                    setattr(obj, kparam, ob)
                if hasattr(obj, 'on_sync_get'):
                    blitlock.acquire()
                    obj.on_sync_get()
                    blitlock.release()
            i += 1
        return i
    elif arg[i] == '<':
        ob = parser_for_set_new_obj(i, arg)
        i, ob = ob
        return (i, ob)
    elif arg[i] == 'T':
        i += 1
        return (i, True)
    elif arg[i] == 'F':
        i += 1
        return (i, False)
    elif arg[i] == 'D':
        i += 1
        pi = i 
        i = arg.find(' ', i)
        if i == -1:
            i = len(arg)
        
        st = arg[pi:i]
        if '.' in st:
            return(i, float(st))
        else:
            return(i, int(st))
    elif arg[i] == 'N':
        i += 1
        return (i, None)
    else:
        pi = i
        while i < len(arg) and arg[i] != ' ':
            i += 1
        st = arg[pi:i]
        return (i, st)
           



def sync_obj(arg, **karg):
    #print('sync_obj', arg)
    if len(arg) < 5:
        print('sync_obj: error: str is too small', arg)
        return
    '''
    if 'wiewin' in arg and False:
        l = 0 
        pi = l
        l = arg.find(' ', l)
        uuid = arg[pi:l]
        if not uuid.isdigit():
            print('sync_obj: error: uuid not is digit in', arg)
            return 
        uuid = int(uuid)
        if uuid not in all.client.objects:
            print('sync_obj: error: uuid not in objects', uuid, 'in', arg)
            return
    
        obj = all.client.objects[uuid]

        l += 1

        while l < len(arg):
            if arg[l] != ' ':
                pi = l
                l = arg.find(':', l)
                if l == -1:
                    print('sync_obj: error: : not found in', arg, 'at', l)
                    return
                kparam = arg[pi:l]
                l += 1
                if 'wiewin' in kparam and kparam != 'wiewin':
                    print('fail') ## сопипаст код для дебага, плавающая ошибка
            l += 1
    '''
    i = 0 
    pi = i 
    i = arg.find(' ', i)
    uuid = arg[pi:i]
    if not uuid.isdigit():
        print('sync_obj: error: uuid not is digit in', arg)
        return 
    uuid = int(uuid)
    if uuid not in all.client.objects:
        print('sync_obj: error: uuid not in objects', uuid, 'in', arg)
        return
    
    obj = all.client.objects[uuid]

    i += 1
    while i < len(arg):
        if arg[i] != ' ':
           

            pi = i
            i = arg.find(':', i)
            if i == -1:
                print('sync_obj: error: : not found in', arg, 'at', i)
                return
            kparam = arg[pi:i]
            i += 1

                
            ob = generator_for_sync_obj(i, arg, getattr(obj, kparam), kparam, obj)
            if ob == None:
                print('sync_obj: error: generator_for_sync_obj returned None')
                return
            if type(ob) != tuple:
                i = ob
            else: 
                i, ob = ob
                if type(ob) == int:
                    if ob == -10:
                        print('sync_obj: alert: generator_for_sync_obj say that the obj is None, response for what is that')
                        
                        all.client.netdat.send_data_funcs(15, str(obj.uuid) + ' ' + kparam)
                    else:
                        setattr(obj, kparam, ob)
                else:
                    setattr(obj, kparam, ob)
        i += 1
    obj.on_sync_get()



def set_player(arg, **keys):
    if arg == '-1':
        print('set playerclass None')
        all.client.game.playerclass = None
        return
    if not arg.strip().isdigit():
        print('error 1 in set player')
        return
    arg = int(arg)
    if arg not in all.client.objects:
        print('error 2 in set player')
        return
    print('seting', all.client.objects[arg], arg,'at playerclass')
    all.client.game.playerclass = all.client.objects[arg]
    all.client.game.playerclass.prx = 0
    all.client.game.playerclass.pry = 0
    all.client.game.playerclass.uuid = arg
    all.client.game.playerclass.onclick = all.client.game.playerclass.net_onclick
    all.client.game.playerclass.offclick = all.client.game.playerclass.net_offclick
    all.client.game.playerclass.equip = all.client.game.playerclass.net_equip


def del_obj(arg, **keys):
    arg = int(arg)
    if arg not in all.client.objects:
        print('deleting not existing entity')
        return
    print('del object')
    delete_object(arg)

    
def delete_object(uuid):
    obj = all.client.objects[uuid]
    obj.remover()
    del all.client.objects[uuid]
    all.client.game.entitys.remove(obj)


def generator_for_sunc_data(obj):
    if type(obj) == int or type(obj) == float:
        return str(obj)
    elif type(obj) == pygame.Surface:
        for i, j in all.client.ldtextures.items():
            if j == obj:
                return 'S' + str(i)
    elif type(obj) == pygame.Vector2:
        st = 'V' + str(obj.x) + ' ' + str(obj.y)
        return st

    elif type(obj) in other_objects:
        st = '{'
        for i in obj.net_params[4]:
            t = getattr(obj, i)
            if t != None:
                st += ' ' + i + ':' + generator_for_sunc_data(t)
        st += ' }'
        return st
    else:
        print('error in generator_for_sunc_data for', obj)
        return 


def send_sync_data(netdat, uuid):
    st = str(uuid)
    obj = all.client.objects[uuid]
    for i in obj.net_params[4]:
        t = getattr(obj, i)
        if type(t) == int or type(t) == float:
            st += ' ' + i + ':'+ str(t)
        elif type(t) == list:
            st += ' ' + i + ':[ '
            for i in t:
                if i != None:
                    st += generator_for_sunc_data(i) + ' '
            st += ']'
        else:
            st += ' ' + i + ':' + generator_for_sunc_data(t)
    netdat.send_data_funcs(12, st)





def get_surface(arg, **karg):

    i = 0
    pi = i
    i = arg.find(' ', i)
    id = arg[pi:i]
    id = arg[pi:i]
    i += 1
    pi = i
    i = arg.find(' ', i)
    x = arg[pi:i]
    i += 1
    pi = i
    i = arg.find(' ', i)
    y = arg[pi:i]
    i += 1
    pi = i 
    i = arg.find(' ', i)
    nom = arg[pi:i]
    i += 1
    pi = i
    i = arg.find(' ', i)
    count = arg[pi:i]
    i+= 1

    res = arg[i:]

    try: 
        id = int(id)
        x = int(x)
        y = int(y)
        nom = int(nom)
        count = int(count)
    except:
        print('get_surface: error: 1')

    if nom >= count:
        print('get_surface: error: receved part of surface with invalid nom')
        return
    print('get_surface: message: recived surface part', nom + 1, '/', count)
    if id not in all.client.surfacecinprocess:
        all.client.surfacecinprocess[id] = [None] * count
    else:
        if len(all.client.surfacecinprocess[id]) != count:
            all.client.surfacecinprocess[id] = [None] * count

    bt = bytes()
    for i in res:
        bt = bt + ord(i).to_bytes()
    
    all.client.surfacecinprocess[id][nom] = bt
    if None not in all.client.surfacecinprocess[id]:
        bt = bytes()
        for i in all.client.surfacecinprocess[id]:
            bt = bt + i
        #print('trying to generate surface of len', len(bt), 'with dat', bt)
        surf = pygame.image.frombytes(bt, (x, y), 'RGBA')
        if surf == None:
            print('get_surface: error: fail to parse surface')
            return

        all.client.ldtextures[id] = surf
        del all.client.surfacecinprocess[id]
        print('get_surface: message: recieved surface', id, all.client.ldtextures[id])
        if id not in all.client.snctextures:
            return
        
        for j in all.client.snctextures[id]:
            print('get_surface: message: setting', j[1], 'of obj', j[0])

            if type(j[0]) == gun:
                blitlock.acquire()
                j[0].updateimage()
                blitlock.release()

            setattr(j[0], j[1], all.client.ldtextures[id])


            
        del all.client.snctextures[id]



recievingthread = None


