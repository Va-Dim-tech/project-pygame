from time import time 
version = 0.01



def get_version(arg, **keys):
    return str(version)




functions = {0:None, # disconnected 
             1:get_version, # get version
             2:None, # disconnect
             3:None,# what buffer lenght do you want?
             4:None, #set buffer size
             5:None, # ping retransmisiion
             6:None, # ping get
             7:None,  # grid set
             8:None, #change state
             9:None, #new object (id uuid x y param:<> kparam:value ...kparam:<id>)
             10:None, #delete object (uuid)
             11:None, #move object (uuid x y)
             12:None, #sync object (uuid kparam_name:value/svalue ... <>)
             13:None, #response for Surface (id siz(x y) part_nom part_count Surf)
             14:None, #set player (uuid)
             15:None, #what is obj (uuid kparam:[i]:)
             16:None, #player fire (1 or 0)
             17:None, # player equip
             18:None  #player select weapon
             } 









def to_str_len(i, l):
    k = str(i)
    return k + ' ' * (l - len(k))

class netdata:

    def __init__(self):
        self.funcs = {} # executing when ans recieved
        self.funcrecvid = 0
        self.funcerrors = [] # recieved
        self.lastfuncid = 0 # recieved
        self.lastfunsend = 0 # sended
        self.sended = {} # id: [r/a, funname/funid, params, sendtime] # sendtime=None when not sendet
        self.ping = 1000
        self.id = 0
        self.tecMess = 0
        self.in_mes_func = [[]]
        self.messages = ['']
        self.Mlen = 500 




    def message_parser(netdat, msg):
        if len(msg) < 11:
            print('parse rror 0 in mes', msg)
            return None

        if not (msg[3:8].strip().isdigit() and msg[8:11].strip().isdigit()):
            print('parse error 1 in mes:', msg)
            return None
        lirecv = int(msg[3:8])
        errors = int(msg[8:11])
        if len(msg) < 11+errors:
            print('parse error 1.5 in mes', msg)
            return None
        errs = set()
        
        for i in range(errors):
            if not msg[(11+i*5):(16+i*5)].strip().isdigit():
                print('parse error 2 in mes:', msg)
                return None
            errs.add(int(msg[(11+i*5):(16+i*5)]))
        tim = 0
        t = set()
        for i, j in netdat.sended.items():
            if i <= lirecv and i not in errs:
                t.add(i)
                continue
            if netdat.sended[i][3] == None:
                continue
            if tim == 0:
                tim = netdat.sended[i][3]
            elif tim > netdat.sended[i][3]:
                tim = netdat.sended[i][3]
        for i in t:
            del netdat.sended[i]


        datstart = 11+errors*5
        funa = {} # answer [fun id answer, params]
        funr = {} # response [fun id, params]
        data = set()
        i = datstart
    
        mx = netdat.lastfuncid
        while len(msg) > i:
            if msg[i] == '1': #functions
                if len(msg) < i+13:
                    print('parse error 2.5 in mes', msg)
                    return None
                if msg[i+6] == 'a':
                    if not (msg[i+1:i+6].strip().isdigit() and msg[i+7:i+10].strip().isdigit() and msg[i+10:i+15].strip().isdigit()):
                        print('parse error 4 in mes', msg)
                        return None
                    s = [int(msg[i+7:i+12]), '']
                    params = int(msg[i+12:i+15])
                    if len(msg) < i+15+params:
                        print('parse error 4.5 in mes', msg)
                        return None
                    s[1] = msg[i+15:i+15+params]
                    id = int(msg[i+1:i+6].strip())
                    if id < netdat.lastfuncid and id not in netdat.funcerrors:
                        continue
                    mx = max(mx, id)
                    funa[id] = s
                    i += 15 + params
                elif msg[i+6] == 'r':
                    if not (msg[i+1:i+6].strip().isdigit() and msg[i+7:i+10].strip().isdigit() and msg[i+10:i+13].strip().isdigit()):
                        print('parse error 4 in mes', msg)
                        return None
                    s = [int(msg[i+7:i+10]), '']
                    params = int(msg[i+10:i+13])
                    if len(msg) < i+13+params:
                        print('parse error 4.5 in mes', msg)
                        return None
                    s[1] = msg[i+13:i+13+params]
                    id = int(msg[i+1:i+6].strip())
                    if id < netdat.lastfuncid and id not in netdat.funcerrors:
                        continue
                    mx = max(mx, id)
                    funr[id] = s
                    i += 13 + params
                else:
                    print('parse error 3 in mes', msg)
                    return None
            elif msg[i] == '2':
                if len(msg) < i+7:
                    print('parse error 7 in mes', msg)
                    return None

                if not (msg[i+1:i+4].strip().isdigit() and msg[i+4:i+7].strip().isdigit()):
                    print('parse error 6 in mes', msg)
                    return None
                id = int(msg[i+1:i+4])
                params = int(msg[i+4:i+7])
                if len(msg) < i+7+params:
                    print('parse error 8 in mes', msg)
                    return None
                data.add((id, msg[i+7:i+7+params]))
                i += 7 + params
            else:
                print('parse error 5 in mes', msg, 'unexpected', msg[i], 'at', i)
                return None

        i = netdat.lastfuncid
    
        er = 0

        # ну нету тут условной компиляции(вроде)
        c = 0 # закоментировать все связанное с 'c' после отладки
        while i != mx:
            i += 1
            if i > 99999:
                i = 0
            if not (i in funa or i in funr):
                netdat.funcerrors.append(i)
                c += 1
                
        
            er += 1
            if er > 1000:
                print('parse error 5 in mes', msg)
                return None
        if c != 0:
            print('not recieved', c, 'functions')
        netdat.lastfuncid = mx
        return (funa, funr, data, tim)
    

    def message_generator(netdat):
        if len(netdat.messages) > 1:
            st = netdat.messages.pop(0)
            fn = netdat.in_mes_func.pop(netdat.tecMess)
            netdat.tecMess -= 1
        else:
            st = netdat.messages[0]
            netdat.messages[0] = ''
            fn = netdat.in_mes_func[netdat.tecMess]
            netdat.in_mes_func[netdat.tecMess] = []

        for i in fn:
            if i in netdat.sended:
                netdat.sended[i][3] = time()

        for i in netdat.funcerrors:
            k = str(i)
            st = k + ' ' * (5 - len(k)) + st
        st =to_str_len(netdat.id, 3) + to_str_len(netdat.lastfuncid, 5) + to_str_len(len(netdat.funcerrors), 3) + st
        return st


    def chk_msg(netdat, mes):
        if len(netdat.messages[netdat.tecMess]) + len(mes) > netdat.Mlen:
            if len(netdat.messages) < netdat.tecMess + 2:
                netdat.messages.append('')
                netdat.in_mes_func.append([])
            netdat.tecMess = netdat.tecMess + 1


    def send_request(netdat, funame, params, addition=None):
        netdat.lastfunsend += 1
        if netdat.lastfunsend > 99999:
            netdat.lastfunsend = 0
    
        s = '1' + to_str_len(netdat.lastfunsend, 5) + 'r' + to_str_len(funame, 3) + to_str_len(len(params), 3) + params
        netdat.chk_msg(s)
        netdat.messages[netdat.tecMess] += s
        netdat.in_mes_func[netdat.tecMess].append(netdat.lastfunsend)
        netdat.sended[netdat.lastfunsend] = ['r', funame, params, None]
        if addition != None:
            netdat.funcs[netdat.lastfunsend] = addition

    def send_answer(netdat, funid, params):
        netdat.lastfunsend += 1
        if netdat.lastfunsend > 99999:
            netdat.lastfunsend = 0
        s = '1' + to_str_len(netdat.lastfunsend, 5) + 'a' + to_str_len(funid, 5) + to_str_len(len(params), 3) + params
        netdat.chk_msg(s)
        netdat.messages[netdat.tecMess] += s
        netdat.in_mes_func[netdat.tecMess].append(netdat.lastfunsend)
        netdat.sended[netdat.lastfunsend] = ['a', funid, params, None]

    def send_data_funcs(netdat, funid, params):
        s = '2' + to_str_len(funid, 3) + to_str_len(len(params), 3) + params
        netdat.chk_msg(s)
        netdat.messages[netdat.tecMess] += s

    def add_fix_func(netdat, tim):
        print('fixing function')
        c = 0 # закоментировать все связанное с 'c' после отладки
        for i, j  in netdat.sended.items():
            if j[3] != None and abs(time() - j[3]) >= tim:
                c += 1
                if j[0] == 'a':
                    s = '1' + to_str_len(i, 5) + 'a' + to_str_len(funid, 5) + to_str_len(len(params), 3) + params
                    netdat.chk_msg(s)
                    netdat.messages[netdat.tecMess] += s
                    netdat.sended[i] = ['a', funid, params, None]
                elif [0] == 'r':
                    send_request(netdat, j[1], f[2])
                    s = '1' + to_str_len(i, 5) + 'r' + to_str_len(funame, 3) + to_str_len(len(params), 3) + params
                    netdat.chk_msg(s)
                    netdat.messages[netdat.tecMess] += s
                    netdat.sended[i] = ['r', funame, params, None]

        if c != 0:
            print('resend', c, 'functions')

    def exec_all_functions(netdat, client, funcs):
        for i, j in funcs.items():
            if functions[j[0]] == None:
                print('truing to exec not existet function', j)
                continue
            res = functions[j[0]](j[1], client=client)
            if res != None:
                netdat.send_answer(i, str(res))

    def exec_to_answer_funcs(netdat, client, funcs):
        for i, j in funcs.items():
            if j[0] not in netdat.funcs:
                print('nothing to ansver to', j)
                continue
            print('executing', netdat.funcs[j[0]])
            netdat.funcs[j[0]](j[1], client=client)
            del netdat.funcs[j[0]]

    def exec_data_funcs(netdat, client, data):
        for i in data:
            if functions[i[0]] == None:
                print('nothing to exec to dat', i)
                continue
            functions[i[0]](i[1], client=client)




    