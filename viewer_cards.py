import json
import urllib
import socket
import copy
from mongodb import get
from claudia_interpretator import next_step

taxes = [
            'Cardio-Loc', 
            'CHF-Words', 
            'DECLINE', 
            'dementia', 
            'MentalStatus', 
            'MI-Words', 
            'PVD-Words', 
            'FAMILY'
            ]
anns = [
            'number', 
            'contains_number', 
            'text'
            ]

snap_file_name = "tmp/snapshot.json"

# This class generates a HTML-page for a card  
class showCard:
    def __init__(self,  args,  mongo,  httpd):
        computer = socket.gethostname()
        if computer == 'noX540LJ':
            html_file = 'cci/viewer/cards.html'
        else:
            html_file = '/home/andrey/work/Claudia/claudia/cci/viewer/cards.html'
        lock = httpd.mLock
        lock.acquire()
        html_file = open(html_file,  'r')
        html = html_file.read()
        html_file.close()
        lock.release()
        
        html = anticache(html)
        html = html.replace('<ID/>',  args['id'])
        html = html.replace('<DS/>',  args['ds'])
        html = html.replace('<FORMULA/>',  args['formula'])
        html = html.replace('TAB_SELECTED',  str(args['tab']))
        self.site = html
    


class getInfo:
    def __init__(self,  args,  mongo,  httpd):
        state = urllib.unquote(args['args'])
        state = json.loads(state)
        print(json.dumps(state,  indent=4))
        
#        lock.acquire()
#        snap_file = open(snap_file_name,  'w')
#        snap_file.write(json.dumps([]))
#        snap_file.close()
#        lock.release()
        
        # Code
        lock = httpd.mLock
        lock.acquire()
        code = get("code.cla.json",  formula=state['formula'],  
                                                                mongo=mongo)
        print('getInfo version: ' + code['version'])
        lock.release()
        state['code'] = []
        for step in code['source']:
            command = {}
            command['text'] = step['text']
            command['id'] = step['source_id']
            command['changes'] = -1
            command['visible'] = False
            state['code'].append(command)
        
        # Key words
        lock.acquire()
        state['key_words'] = get('key_words',  number_of_card=state['id'], 
                            dataset=state['ds'],  mongo=mongo)
        lock.release()
        
        # Initilal document
        lock.acquire()
        doc = get('doc.html',  number_of_card=state['id'], 
                                            dataset=state['ds'],  mongo=mongo)
        lock.release()
        state['initial_doc'] = doc
        
        # Annotations
        lock.acquire()
        doc = get('ch.json',  number_of_card=state['id'], 
                                            dataset=state['ds'],  mongo=mongo)
        lock.release()
        state['anns'] = doc
        
        # Info
        lock.acquire()
        info = get('doc.json',  number_of_card=state['id'], 
                                            dataset=state['ds'],  mongo=mongo)
        lock.release()
        if info is None:
            info = {}
        state['info'] = info
        
        # Ticket
        lock.acquire()
        cch = httpd.cch
        if state['ticket'] != 'admin':
            state['ticket'] = cch.getFreeTicket()
            if state['ticket'] is None:
                state['ticket'] = 'admin'
        lock.release()
        print('ticket: ' + state['ticket'])
        
        #print(json.dumps(state,  indent=4))
        
        self.site = urllib.quote(json.dumps(state))


class runCode:
    def __init__(self,  args,  mongo,  httpd):
        req = urllib.unquote(args['args'])
        req = json.loads(req)
        print('req' + str(req))
        lock = httpd.mLock
        lock.acquire()
        code = get("code.cla.json",  formula=req['formula'],  
                                                                mongo=mongo)
        print('runCode version: ' + code['version'])
        lock.release()
        doc = []
        doc_data = {}
        n = 0
        while True:
            print('Step: ' + str(n))
            doc_data = next_step(doc_data,  code, req['ds'],  req['id'],  
                                                            n,  mongo)
            if doc_data is None:
                break
            doc.append(doc_data)
            # Save to file
            snap_file = open(snap_file_name,  'w')
            snap_file.write(json.dumps(doc,  indent=4))
            snap_file.close()
            n += 1
        answer = 'ready'
        self.site = urllib.quote(json.dumps(answer,  indent=4))


class getCode:
    def __init__(self,  args,  mongo,  httpd):
        req = urllib.unquote(args['args'])
        req = json.loads(req)
        print('req: '+ str(req))
        
        lock = httpd.mLock
        lock.acquire()
        if req['ticket'] == 'admin':
            snap_file = open(snap_file_name,  'r')
            doc = json.loads(snap_file.read())
            snap_file.close()
        else:
            cch = httpd.cch
            #print('Locks: ' + str(cch.mch.mLocks))
            doc = cch.getValue(req['ticket'])
            #print('doc: ' + str(doc))
            if doc is None:
                doc= []
        lock.release()
        
        if doc == []:
            doc_data = {}
        else:
            doc_data = doc[-1]
        lock.acquire()
        code = get("code.cla.json",  formula=req['formula'],  
                                                                mongo=mongo)
        print('GetCode version: ' + code['version'])
        lock.release()
        for n in range(len(doc),  req['new_step'] + 1):
            print('Step: '  + str(n))
            doc_data = next_step(doc_data,  code, req['ds'],  req['id'],  
                                                            n,  mongo)
            doc_copy = copy.deepcopy(doc_data)
            doc.append(doc_copy)
        new_cadres = doc[req['step']+1:]
        
        lock.acquire()
        if req['ticket'] == 'admin':
            snap_file = open(snap_file_name,  'w')
            snap_file.write(json.dumps(doc,  indent=4))
            snap_file.close()
        else:
            cch.putValue(req['ticket'], doc)
        lock.release()
        self.site = urllib.quote(json.dumps(new_cadres))

import datetime
def anticache(html):
    now = datetime.datetime.now()
    s = str(now.second)
    html = html.replace('.js"',  '.js?v=' + s + '"')
    html = html.replace(".js'",  ".js?v=" + s + "'")
    html = html.replace('.css)',  '.css?v=' + s + ')')
    return html

class clearCache:
    def __init__(self,  args,  mongo,  httpd):
        req = urllib.unquote(args['args'])
        req = json.loads(req)
        print('req: ' + str(req))
        lock = httpd.mLock
        lock.acquire()
        cch = httpd.cch
        cch.removeTicket(req['ticket'])
        lock.release()
        self.site = 'Ok.'
