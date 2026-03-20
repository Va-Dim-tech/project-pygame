print('starting server')

import threading
import socket
from game import *
from vars import varsclass as all
from random import randint
from time import time
from net import *


config_file_name = 'server_config.txt'
config_file_separator = ' '






mainconfig = {'port': 55555,
              'max_players': 10,
              'max_time': 1,
              'kep_alive_time':1,
              'levels_count':3,
              'max_message_len':2000,
              'pinging_time':1,
              'dead_time':5,
              'gun_file':'guns.txt'}

nextid = 1





class client:
    def __init__(self, addr= ('0.0.0.0', 0)):
        global nextid
        self.state = 0
        self.lasttime = time()
        self.id = nextid
        nextid = nextid + 1
        self.addres = addr
        self.key = randint(1, 100000)
        self.netdat = None
        self.instantsend = True
        self.level = -1
        self.playerclass = None
        self.older_tim_fix = 0
        self.timr = None 
        self.kp = None 
        self.pinger = None 
        self.dead_timer = None
        self.need_send = False
        


    def gen_timers(self):
        self.kp = add_timer(timing(tim=time() + mainconfig['kep_alive_time'], lamb=keep_alive, params=self))
        self.pinger = add_timer(timing(tim=time(), lamb=pinging, params=self))
        #self.dead_timer = add_timer(timing(tim=time() + mainconfig['dead_time'], lamb=reaction_to_client_disconct, params='timeout', kparams={'client':self}))

    def delete_timrs(self):
        if self.timr != None:
            del_timer(self.timr)
        if self.kp != None:
            del_timer(self.kp)
        if self.pinger != None:
            del_timer(self.pinger)

    def to_send(self):
        if self.netdat.tecMess > 0:
            self.need_send = True
        else:
            self.need_send = False
        send_data(self)
    
    def to_state(self, state):
        if state == self.state:
            return
        if state == 0:
            self.instantsend = False
        elif state == 1:
            pass
        elif state == 2:
            pass
        elif state == 3:
            self.instantsend = True


        self.state = state


def gamover(client):
    clients_lock.acquire()
    client.to_state(1)
    client.netdat.send_request(8, '1')
    client.playerclass = None
    clients_lock.release()

def detach_player(client):
    clients_lock.acquire()
    client.netdat.send_request(14, '-1')
    client.to_state(0)
    clients_lock.release()

def detach_client_from_level(client):
    clients_lock.acquire()
    levels[client.level].clients.remove(client)
    client.netdat.send_request(20, '')
    client.need_send = True
    clients_lock.release()
    client.to_state(1)
    

def client_disconnect(client, reason):
    if reason != 'timeout':
        client.netdat.send_request(0, reason)
        send_data(client)
    clients_lock.acquire()
    levels[client.level].clients.remove(client)
    
    del clients[client.id]
    clients_lock.release()
    detach_player(client)


print('creating socket')

mainsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    mainsock.bind(('', mainconfig['port']))
except:
    print('fail to bind socket')
    exit()




def chek_client_version(ver):
    if ver != version:
        return False
    return True


def send_data(client):
    
    st = client.netdat.message_generator()
    if st != None:
        #print('sendet', st)
        mainsock.sendto(bytes(st, encoding='utf-8'), client.addres)


def keep_alive(client):
    send_data(client)
    client.kp = add_timer(timing(tim=time() + mainconfig['kep_alive_time'], lamb=keep_alive, params=client))

def pinging(client):
    client.netdat.send_data_funcs(5, str(time()))
    send_data(client)
    client.pinger = add_timer(timing(tim=time() + mainconfig['pinging_time'], lamb=pinging, params=client))


def resend_data(client):

    client.netdat.add_fix_func(client.netdat.ping)
    client.timr = None

    return
    print('loop start')
    while client.netdat.tecMess > 0:
        send_data(client)
    print('loop end')

def message_reciever():
    bufferlen = mainconfig['max_message_len']

    while True:
        st = None
        try:
            st, adr = mainsock.recvfrom(bufferlen)
        except BaseException as e:
            print('except in recvfrom', e)
        if st == None:
            continue

        st = st.decode()
        if len(st) < 11 or not st[:3].strip().isdigit():
            continue

        id = int(st[:3])
        if id == 0:
            clients_lock.acquire()
            
            id = nextid
            clients[id] = client(addr=adr)
            clients[id].netdat = netdata()
            clients[id].netdat.id = id
            clients[id].netdat.send_request(1, str(id), addition=on_version_get)
            send_data(clients[id])
            clients_lock.release()
            print('new user!')
            continue

        if id not in clients:
            print('uncnovn client')
        else:
            if clients[id].addres[0] != adr[0] or clients[id].addres[1] != adr[1]:
                print('client change addr')
                clients[id].addres = adr

            #print('get', st)
            st = clients[id].netdat.message_parser(st)
            if st != None:

                try:
                    clients[id].netdat.exec_all_functions(clients[id], st[1])
                except BaseException as e:
                    print('except in exec_all_functions', e)
                try:
                    clients[id].netdat.exec_to_answer_funcs(clients[id], st[0])
                except BaseException as e:
                    print('except in exec_to_answer_funcs', e)
                try:
                    clients[id].netdat.exec_data_funcs(clients[id], st[2])
                except BaseException as e:
                    print('except in exec_data_funcs', e)
                
                #if clients[id].timr == None:
                #    if st[3] != 0:
                if st[3] != clients[id].older_tim_fix:
                    print(st[3], clients[id].older_tim_fix)
                    clients[id].older_tim_fix = st[3]
                    
                    if clients[id].timr != None:
                        del_timer(clients[id].timr)
                        clients[id].timr= None 
                    if st[3] != 0:
                        print('wit for resend', time() -  clients[id].older_tim_fix + clients[id].netdat.ping * 4)

                        clients[id].timr = timing(tim=clients[id].older_tim_fix + mainconfig['pinging_time'] * 2, lamb=resend_data, params=clients[id])
                        add_timer(clients[id].timr)

                if clients[id].dead_timer != None:
                    del_timer(clients[id].dead_timer)
                clients[id].dead_timer = timing(tim=time() + mainconfig['dead_time'], lamb=reaction_to_client_disconct, params='timeout', kparams={'client':clients[id]})
                add_timer(clients[id].dead_timer)

                if clients[id].instantsend:
                    send_data(clients[id])

def on_version_get(param, client=None):
    try:
        a = float(param)
    except:
        client_disconnect(client, 'version')
        return
    if chek_client_version(a):
        client.netdat.send_request(3, '', addition=on_buffer_len_get)
    else:
        client_disconnect(client, 'version')
        return 

def on_buffer_len_get(arg, client=None):
    arg = arg.strip()
    if arg.isdigit():
        arg = int(arg)
        if arg > mainconfig['max_message_len']:
            arg = mainconfig['max_message_len']
    else:
        arg = client.netdat.Mlen
    client.netdat.send_request(4, str(arg), addition=to_start_game)
    client.gen_timers()
    print('setting buffer size to', arg)
        

def reaction_to_client_disconct(arg, client=None):
    print('client say disconnect in reason', arg)
    clients[client.netdat.id].delete_timrs()
    if client.playerclass != None:
        levels[client.level].del_player(client.playerclass)
        levels[client.level].delete_object(client.playerclass)
        
    clients_lock.acquire()
    del clients[client.netdat.id]
    clients_lock.release() 

    detach_player(client)

def to_start_game(arg, client=None):
    client.netdat.send_request(8, '0', addition=start_game)

def attach_client_to_level(client):
    clients_lock.acquire()
    levels[client.level].clients.append(client)
    send_level(client)
    client.to_state(1)
    clients_lock.release()

def attach_player_to_client(player, client):
    clients_lock.acquire()
    client.netdat.send_request(14, str(player.uuid))
    client.playerclass = player
    send_sync_data(client, player, param=['inventar'])
    add_timer(timing(tim=time() + 1, lamb=sync_weapon, params=client))
    clients_lock.release()

def start_game(arg, client=None):
    print('user start game')
    client.level= 0
    pl = add_player(client.level)
    attach_client_to_level(client)
    
    #send_level(client)
    attach_player_to_client(pl, client)
    client.to_state(2)
    client.need_send = True

def respawn(arg, client=None):
    if client.state == 2:
        return
    newlvl = 0
    if client.level != newlvl:
        detach_client_from_level(client)
        client.level = newlvl
        attach_client_to_level(client)
    client.level = newlvl
    pl = add_player(client.level)
    
    attach_player_to_client(pl, client)

    client.to_state(2)
    client.netdat.send_request(8, '0')
    client.need_send = True
    return None

def ping_retransmission(arg, client=None):
    client.netdat.send_data_funcs(6, arg)
    send_data(client)

def ping_get(arg, client=None):
    try:
        client.netdat.ping = abs(time() - float(arg)) / 2
        print('ping get', client.netdat.ping)
    except BaseException as e:
        print('ping except', e)
        return



Surfaces = []


def generator_for_sunc_data(obj):
    if type(obj) == int or type(obj) == float:
        return 'D' + str(obj)
    elif type(obj) == pygame.Surface:
        if obj not in Surfaces:
            Surfaces.append(obj)
            print('append surface')
        return 'S' + str(Surfaces.index(obj))
    elif type(obj) == pygame.Vector2:
        st = 'V' + str(obj.x) + ' ' + str(obj.y)
        return st
    elif type(obj) == bool:
        if obj:
            return 'T'
        else:
            return 'F'
    elif obj is None:
        return 'N'
    elif type(obj) in other_objects:
        st = '{'
        for i in obj.net_params[1]:
            t = getattr(obj, i)
            if t != None:
                st += ' ' + i + ':' + generator_for_sunc_data(t)
        st += ' }'
        return st
    else:
        print('error in generator_for_sunc_data for', obj)
        return 


def send_sync_data(client, obj, param=None):
    if param ==None:
        param = obj.net_params[1]
    st = str(obj.uuid)
    for i in param:
        t = getattr(obj, i)
        if type(t) == int or type(t) == float:
            st += ' ' + i + ':'+ 'D' + str(t)
        elif type(t) == list:
            st += ' ' + i + ':[ '
            for i in t:
                if i != None:
                    st += generator_for_sunc_data(i) + ' '
            st += ']'
        else:
            st += ' ' + i + ':' + generator_for_sunc_data(t)
    if len(st) > 5:
        client.netdat.send_data_funcs(12, st)


def generator_for_send_new_object(obj):
    if type(obj) == int or type(obj) == float:
        return ('params:i' +str(obj), None)
    elif type(obj) == pygame.Surface:
        if obj not in Surfaces:
            Surfaces.append(obj)
        st = 'params:S'
        st += str(Surfaces.index(obj))
        return (st, None)
    elif type(obj) == pygame.Vector2:
        st = 'params:V' + str(obj.x) + ' ' + str(obj.y)
        return (st, None)
    elif type(obj) in other_objects:
        st = 'params:<' + str(other_objects.index(type(obj))) + ' '
        se = set()
        se.add(obj)
        for i in obj.net_params[2]:
            a, b = generator_for_send_new_object(getattr(obj, i))
            st += ' ' + a
            if b != None:
                se = se.union(b)
            
        st += ' >'
        return (st, se)
    elif type(obj) == str:
        return ('params:' + obj, None)
    else:
        print('global error in generator_for_send_new_object', type(obj))


def send_new_object(client, obj):
    if type(obj) not in objects:
        print('trying to send not existed object')
        return
    se = set()
    st = str(objects.index(type(obj))) + ' ' + str(obj.uuid) + ' ' + str(obj.pos.x) + ' ' + str(obj.pos.y)
    for i in obj.net_params[2]:
        t = getattr(obj, i)
        if type(t) == int or type(t) == float:
            st += ' params:' + str(t)
        elif type(t) == list:
            st += ' params:['
            for i in t:
                a, b = generator_for_send_new_object(i)
                st += ' ' + a
                if b != None:
                    se = se.union(b)
            st += ']'
        else:
            a, b = generator_for_send_new_object(t)
            st += ' ' + a
            if b != None:
                se = se.union(b)
        
    client.netdat.send_request(9, st)
    for i in se:
        send_sync_data(client, i)


def parser_for_sync_objects(obj, argt, c):
    if c[1][0] == 'S':
        id = int(c[1][1:])
        setattr(obj, c[0], Surfaces[id])
        
    elif c[1][0] == '{':
        ob = getattr(obj, c[0])
        if ob == None:
            print('error 1 parser_for_sync_objects')
            return
        i = argt.pop(0)
        while len(argt) > 0 and i[-1] != '}':
            i = i.split(':')
            parser_for_sync_objects(ob, argt, i)
            i = argt.pop(0)
            

    elif c[1][0] == '[':

        i = 0
        t = argt.pop(0)
        while len(argt) > 0 and t[-1] != ']':
            if t[0] == '{':
                ob = getattr(obj, c[0])[i]
                if ob == None:
                    print('error 2 in parser_for_sync_objects')
                    return
                k = argt.pop(0)
                while len(argt) > 0 and k[-1] != '}':
                    k = k.split(':')
                    parser_for_sync_objects(ob, argt, k)
                    k = argt.pop(0)
            elif t[0] == '<':
                print('client trying to create obj')
                return
    elif c[1][0] == '<':
        print('client trying to create obj')
        return
    elif c[1][0] == 'V':
        x = float(c[1][1:])
        y = float(argt.pop(0))
        c = getattr(obj, c[0])
        c.x = x
        c.y = y
        #print('seting ', obj, c[0])
    else:
        if '.' in c[1]:
            setattr(obj, c[0], float(c[1]))
        else:
            setattr(obj, c[0], int(c[1]))

    

def sync_object(arg, client=None):
    #print('sync_object:', arg)
    argt = arg.split()
    if len(argt) < 1:
        print('error 1 in sync_object', arg)
        return 
    id = int(argt.pop(0))
    if client.playerclass == None:
        return
    if id != client.playerclass.uuid:
        print('error 2 in sync obj', arg)
        return

    obj = client.playerclass
    #print('get str', arg)
    while len(argt) > 0:
        i = argt.pop(0)
        i = i.split(':')
        parser_for_sync_objects(obj, argt, i)


def send_level(client):
    for y in range(all.game.gridsizy):
        for x in range(all.game.gridsizx):
            client.netdat.send_request(7, str(grid_cells.index(type(levels[client.level].getcell(x, y)))) + ' ' + str(x) + ' ' + str(y))
    for i in levels[client.level].entitys:
        send_new_object(client, i)
        send_sync_data(client, i)
    client.need_send = True

def send_new_pos(client, obj):
    client.netdat.send_data_funcs(11, str(obj.uuid) + ' ' + str(obj.pos.x) + ' ' + str(obj.pos.y))

def get_move_obj(arg, client=None):
    if client.playerclass == None:
        return
    arg = arg.split()
    if len(arg) < 3:
        print('error 1 in get move obj')
        return
    x = arg[1]
    y = arg[2]
    try:
        x = float(x)
        y = float(y)
    except:
        print('error 2 in get move obj')
    client.playerclass.pos.x = x
    client.playerclass.pos.y = y
    
def send_del_obj(client, obj):
    client.netdat.send_request(10, str(obj.uuid))

def parse_what_obj(arg, client=None):
    argt = arg.split()
    id = int(argt[0])
    flag = False
    for i in levels[client.level].entitys:
        if i.uuid == id:
            flag = True
            obj = i
            break
    if not flag:
        print('obbj not found in parse_what_obj', arg)
        return
    res = str(id) + ' '
    argl = argt[1].split(':')
    i = argl.pop(0)
    tk = obj
    while True:
        if i[0] == '[':
            res += '['
            id = int(i[1])
            res += str(id) + ']:'
            tk = tk[id]
        else:
            tk = getattr(tk, i)
            res += i + ':'
        if len(argl) == 0:
            break
        i = argl.pop(0)
    r = generator_for_send_new_object(tk)
    st = r[0][r[0].find(':')+1:]
    res += st
    
    client.netdat.send_request(12, res)
    send_sync_data(client, obj)

def surface_response(arg, client=None):
    if not arg.strip().isdigit():
        print('not int in surface response')
        return
    arg = int(arg)
    if arg >= len(Surfaces):
        print('tring to get not existed surface')
        return
    
    siz = Surfaces[arg].get_size()
    bt = pygame.image.tobytes(Surfaces[arg], 'RGBA')
    #print('sending surface with total len', len(bt), 'is', bt)
    parts = []
    res = ''
    for i in bt:
        res += chr(i)
        if len(res) > 800:
            parts.append(res)
            res = ''
    parts.append(res)
    print('generated surface with', len(parts), 'parts')
    for i in range(len(parts)):
        client.netdat.send_request(13, str(arg) + ' ' + str(siz[0]) + ' ' + str(siz[1]) + ' ' + str(i) + ' ' + str(len(parts)) + ' ' + parts[i])
    return

def plyer_fire(arg, client=None):
    if client.playerclass != None:
        if arg == '1':
            client.playerclass.clicked = True
        else:
            client.playerclass.clicked = False

def player_equip(arg, client=None):
    if client == None:
        return
    if client.playerclass != None:
        if not arg.isdigit():
            print('player_equip uuid not is digit', arg)
            return
        id = int(arg)
        obj = None
        for i in levels[client.level].entitys:
            if i.uuid == id:
                obj = i
                break
        if obj is None:
            print('obbj not found in parse_what_obj', arg)
            return
        if obj.type != 'item':
            print('client trying to equip not item obect', obj.type)
            return

        client.playerclass.itemselected = obj;
        if type(obj.gun) is hert:
            client.playerclass.take_heal(obj)
        else:
            client.playerclass.equip()
            for i in levels[client.level].clients:
                send_sync_data(i, obj)
                sync_weapon(i)

def player_select_weapon(arg, client=None):
    if not arg.isdigit():
        print('player_select_weapon id not is digit', arg)
        return
    arg = int(arg)
    client.playerclass.selected = arg
    for i in levels[client.level].clients:
        send_sync_data(i, client.playerclass,  param=['selected'])


functions[0] = reaction_to_client_disconct
functions[5] = ping_retransmission
functions[6] = ping_get
functions[11] = get_move_obj
functions[12] = sync_object
functions[13] = surface_response
functions[15] = parse_what_obj
functions[16] = plyer_fire
functions[17] = player_equip
functions[18] = player_select_weapon
functions[19] = respawn
print('opening config file')
if not os.path.isfile(config_file_name):
    print('config file not found. creating file')
    fd = open(config_file_name, 'w')
    for i, j in mainconfig.items():
        fd.write(i)
        fd.write(config_file_separator)
        fd.write(str(j))
        fd.write('\n')
    fd.close()

fd = open(config_file_name)
st = fd.readlines()
fd.close()
for i in st:
    j = i.split(config_file_separator)
    if len(j) < 2 or len(j[0]) < 1 or len(j[1]) < 1:
        continue
    if j[0:1] == 's_':
        mainconfig[j[0]] = j[1]
    else:
        mainconfig[j[0]] = int(j[1])


class timing():
    def __init__(self, tim=0, lamb=None, params=None, kparams=None):
        self.tim = tim
        self.lamb = lamb
        if type(params) != tuple:
            params = tuple([params])
        self.params = params
        self.kparams = kparams

timlock = threading.Lock()
def add_timer(t):
    timlock.acquire()
    k = 0 
    i = 0
    while i < len(timers):
        if timers[i].tim > t.tim:
            break
        i += 1
    timers.insert(i, t)
    timlock.release()
    return t

def del_timer(t):
    if t not in timers:
        return
    timlock.acquire()
    timers.remove(t)
    timlock.release()


timers = []

class level():
    def __init__(self):
        self.players = []
        self.clients = []
        self.entitys = []
        self.grid = []
        for y in range(all.game.gridsizy):
            ou = [None] * all.game.gridsizx
            for x in range(all.game.gridsizx):
                ou[x] = flor(x, y)
            self.grid.append(ou)

        self.dodelete = False
        self.reset()

    def set_params(self, gm):
        gm.grid = self.grid
        gm.players = self.players
        gm.entitys = self.entitys
        gm.cgrid = self.cgrid
        gm.setcell = self.setcell
        gm.getcell = self.getcell
        gm.getcolcell = self.getcolcell
        gm.getplayers = self.getplayers
        gm.add_gnerated_object = self.add_gnerated_object
        gm.add_object = self.add_object
        gm.delete_object = self.delete_object
        gm.player_dead = self.player_dead
        gm.nextlevel = self.nextlevel
        
    def get_params(self, gm):
        self.grid = gm.grid
        self.players = gm.players
        self.entitys = gm.entitys
        self.cgrid = gm.cgrid

    def reset(self):
        #for i in self.clients:
        #    for y in range(all.game.gridsizy):
        #        for x in range(all.game.gridsizx):
        #            self.setcell(x, y, flor(x, y))
        
        for i in self.clients:
            i.netdat.send_request(20, '')

        self.grid = []
        for y in range(all.game.gridsizy):
            ou = [None] * all.game.gridsizx
            for x in range(all.game.gridsizx):
                ou[x] = flor(x, y)
            self.grid.append(ou)
        
        #for e in self.entitys:
        #    self.delete_object(e)

        self.entitys = []
        self.cgrid = []
        self.start_pos = (0, 0)

        for y in range(all.game.colisgrdsizy):
            ou = [None] * all.game.colisgrdsizx
            for x in range(all.game.colisgrdsizx):
                ou[x] = colisioncell()
                ou[x].x = x * all.game.colisizx
                ou[x].y = y * all.game.colisizy
            self.cgrid.append(ou)


    def setcell(self, x, y, c):
        if 0 <= x < all.game.gridsizx:
            if 0 <= y < all.game.gridsizy:
                self.grid[y][x] = c
                for i in self.clients:
                    i.netdat.send_request(7, str(grid_cells.index(type(self.grid[y][x]))) + ' ' + str(x) + ' ' + str(y))

    def getcell(self, x, y):
        if 0 <= x < all.game.gridsizx:
            if 0 <= y < all.game.gridsizy:
                return self.grid[y][x]
        return None

    def getcolcell(self, x, y):
        if 0 <= x < all.game.colisgrdsizx:
            if 0 <= y < all.game.colisgrdsizy:
                return self.cgrid[y][x]
        return None

    def getplayers(self):
        return self.players

    def player_dead(self, player):
        for i in self.clients:
            if i.playerclass == player:
                gamover(i)
                detach_player(i)
                self.del_player(player)
                self.delete_object(player)
                return


    def add_player(self, player):

        self.players.append(player)

    def del_player(self, player):
        if player in self.players:
            self.players.remove(player)

    def nextlevel(self, pl):
        
        for i in self.clients:
            if i.playerclass == pl:
                newlvl = i.level + 1
                if newlvl >= len(levels):
                    newlvl = 0
                add_timer(timing(tim=time(), lamb=change_player_level, params=(newlvl, i)))
                #change_player_level(newlvl, i)
                return



    def add_gnerated_object(self, obj):
        obj.prx = obj.pos.x
        obj.pry = obj.pos.y
        if len(obj.net_params) > 5 and obj.net_params[5]:
            obj.lock = threading.Lock()
        obj.server_init()
        #print('addet obj', obj)
        self.entitys.append(obj)

        for i in self.clients:
            send_new_object(i, obj)
            send_sync_data(i, obj)




    def add_object(self, obj, *params, **kparams):
        self.add_gnerated_object(obj(*params, **kparams))
        
        
    def delete_object(self, obj):
        obj.live = False
        self.dodelete = True
        for i in self.clients:
            send_del_obj(i, obj)


def gen_level(level):
    level.reset()

    level.set_params(all.game)
    level.start_pos = generator(all.game.grid, all.game.gridsizx, all.game.gridsizy, all.game.labirintcellx, all.game.labirintcelly)
    level.get_params(all.game)
    print('gen_level')

def add_player(levelid):
    #if len(levels[levelid].players) == 0:
    #    gen_level(levels[levelid])

    pl = player(x=levels[levelid].start_pos[0] * all.game.cellsizx + 10, y=levels[levelid].start_pos[1] * all.game.cellsizy + 10)
    if all.game.playerweapon != None:
        pl.inventar[0] = all.game.playerweapon.construct()
        
    levels[levelid].add_gnerated_object(pl)
    levels[levelid].add_player(pl)
    #levels[levelid].players.append(pl)
    #levels[levelid].clients.append(client)
    #client.level = levelid
    #client.playerclass = pl

    return pl

def get_next_player_level(client):
    return (client.level + 1) % len(levels)

def change_player_level(levelid, client):
    print('change_player_level')

    pl = client.playerclass

    detach_player(client)
    detach_client_from_level(client)

    levels[client.level].del_player(pl)
    levels[client.level].delete_object(pl)
    levels[client.level].entitys.remove(pl)

    pl.live = True

    client.level = levelid

    if len(levels[levelid].clients) == 0:
        gen_level(levels[levelid])
    attach_client_to_level(client)
    #add_timer(timing(tim=time() + 3, lamb=attach_client_to_level, params=client))

    levels[levelid].add_gnerated_object(pl)
    levels[levelid].add_player(pl)
    
    attach_player_to_client(pl, client)

def sync_weapon(client):
    print('weapon send')
    send_sync_data(client, client.playerclass, param=['inventar'])


print('creating threads')

reciever = threading.Thread(target=message_reciever, daemon=True)



print('starting sockets')

reciever.start()

print('starting game')


clients_lock = threading.Lock()
    

clients = {}


clock = pygame.time.Clock()

all.game = game()

all.game.create_txtures_vars()
loader(mainconfig['gun_file'])
all.game.updatechances()
all.game.updatechancesbox()

levels = []

for i in range(mainconfig['levels_count']):
    levels.append(level())


for i in levels:
    gen_level(i)


while True:
    t = time()
    while (len(timers) > 0 and timers[0].tim < time()):
        if timers[0].kparams != None:
            timers[0].lamb(*timers[0].params, **timers[0].kparams)
        else:
            timers[0].lamb(*timers[0].params)
        del_timer(timers[0])



    clients_lock.acquire()
    for i in clients:
        if clients[i].need_send:
            clients[i].to_send()
    clients_lock.release()
    dt = clock.tick()
    for lvl in levels:
        if len(lvl.clients) != 0:
            lvl.set_params(all.game)

            for i in all.game.entitys:

                if i.net_params[3][0]:
                    i.sync = False
                    if i.net_params[3][1]:
                        if len(i.net_params) > 5 and i.net_params[5]:
                            i.lock.acquire()
                            i.ubdate(dt)
                            i.lock.release()
                        else:
                            i.ubdate(dt)
                    if i.net_params[0][0]:
                        if len(i.net_params) > 5 and i.net_params[5]:
                            i.lock.acquire()
                            i.server_update(dt)
                            i.lock.release()
                        else:
                            i.server_update(dt)
                    if i.sync:
                        clients_lock.acquire()
                        for j in lvl.clients:
                            j.need_send = True
                            send_new_pos(j, i)
                            send_sync_data(j, i)
                        clients_lock.release()
                else:
                    if i.net_params[3][1]:
                        i.ubdate(dt)
                    if i.net_params[0][0]:
                        i.server_update(dt)
                    if abs(i.prx - i.pos.x) > 10 or abs(i.pry - i.pos.y) > 10:
                        i.prx = i.pos.x
                        i.pry = i.pos.y
                        clients_lock.acquire()
                        for j in lvl.clients:
                            j.need_send = True
                            send_new_pos(j, i)
                            send_sync_data(j, i)

                        clients_lock.release()
            if lvl.dodelete:
                lvl.dodelete = False
                i = 0 
                while i < len(all.game.entitys):
                    if not all.game.entitys[i].live:
                        all.game.entitys[i].remover()
                        del all.game.entitys[i]
                    i += 1
            all.game.lazyenid += 1
            if all.game.lazyenid >= len(all.game.lazyenemy):
                all.game.lazyenid = -1
            else:
                if len(all.game.lazyenemy[all.game.lazyenid].net_params) > 5 and all.game.lazyenemy[all.game.lazyenid].net_params[5]:
                    all.game.lazyenemy[all.game.lazyenid].lock.acquire()
                    all.game.lazyenemy[all.game.lazyenid].lazy()
                    all.game.lazyenemy[all.game.lazyenid].lock.release()
                else:
                    all.game.lazyenemy[all.game.lazyenid].lazy()













