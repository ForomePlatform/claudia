import json
import urllib
import socket
from mongodb import get

# Create main page 'index.html'  
taxes = [
            'None', 
            'Cardio-Loc', 
            'CHF-Words', 
            'DECLINE', 
            'dementia', 
            'MentalStatus', 
            'MI-Words', 
            'PVD-Words'
            ]
#apostriory = [
#            'ICHF', 
#            'Other'
#            ]
apostriory = [
            'not mentioned', 
            'ambiguous',
            'diagnosed', 
            'inconclusive', 
            'ruled out', 
            'symptoms present', 
            'other'
            ]
apriory = [
            'not mentioned', 
            'ambiguous',
            'diagnosed', 
            'inconclusive', 
            'ruled out', 
            'symptoms present', 
            'other'
            ]
datasets = [
            'cci', 
            'nets', 
            'medications'
            ]
formulas = [
            'CHF', 
            'MI'
            ]

def intersection(list1,  list2):
    res = []
    for el in list1:
        if el in list2:
            res.append(el)
    return res

def union(list1,  list2):
    res = []
    for el in list1:
        if el not in list2:
            res.append(el)
    res.extend(list2)
    return res
    
def difference(list1,  list2):
    res = []
    for el in list1:
        if el not in list2:
            res.append(el)
    return res

class showIndex:
    def __init__(self,  args,  mongo,  httpd):
        computer = socket.gethostname()
        if computer == 'noX540LJ':
            html_file = 'cci/viewer/viewer.html'
        else:
            html_file = '/home/andrey/work/Claudia/claudia/cci/viewer/viewer.html'
        lock = httpd.mLock
        lock.acquire()
        html_file = open(html_file,  'r')
        html = html_file.read()
        html_file.close()
        lock.release()
        self.site = html


class cardList:
    def __init__(self,  args,  mongo,  httpd):
        state = urllib.unquote(args['args'])
        state = json.loads(state)
        # Find all cards selected in pivot table
        lock = httpd.mLock
        lock.acquire()
        ids = get('all_indexes',  dataset=state['ds'],  mongo=mongo)
#        list_apostriory = get('calculated_indexes',  dataset=state['ds'],
#                                            formula=state['formula'],  mongo=mongo)
        lock.release()
        #print('apostriory: ' + str(list_apostriory))
        need_list = []
        for i in range(len(state['selected_cells'])):
            lock.acquire()
            ids3 = get('results_apriory.' + apriory[i], dataset=state['ds'], 
                                            formula=state['formula'],  mongo=mongo)
            print('Apriory (' + apriory[i] + '): ' + str(ids3))
            lock.release()
            for j in range(len(state['selected_cells'][i])):
                #if apostriory[j] == 'Other':
                lock.acquire()
                list_apostriory = get('results_apostriory.' + apostriory[j], dataset=state['ds'], 
                                            formula=state['formula'],  mongo=mongo)
                print('Apostriory (' + apostriory[j] + '): ' + str(list_apostriory))
                lock.release()
#                if apostriory[j] == 'Other':
#                    ids2 = difference(ids,  list_apostriory)
#                else:
#                    ids2 = list_apostriory
                if state['ds'] != 'cci':
                    ids3 = ids
                #list = intersection(ids2,  ids3)
                list = intersection(list_apostriory,  ids3)
                if state['selected_cells'][i][j]['selected']:
                    need_list = union(need_list,  list)
                state['selected_cells'][i][j]['count'] = len(list)
        
        # Find cards with the taxonomy only
        tax = state['tax']
        if tax['tax'] == 'None':
            ids1 = ids
        else:
            lock.acquire()
            ids1 = get("tax.idx", dataset=state['ds'],  
                            taxonomy=tax['tax'],  mongo=mongo)
            lock.release()
        if not tax['flag']:
            need_list = intersection(need_list,  ids1)
        else:
            need_list = difference(need_list,  ids1)
        
        # Sort list of cards
        number_list = []
        for id in need_list:
            number_list.append(int(id))
        number_list.sort()
        need_list = []
        for number in number_list:
            need_list.append(str(number))
        state['count'] = len(need_list)
        
        # Data of every card
        cards_in_one_portion = 100
        chf = {}
        if state['portion']*cards_in_one_portion > len(need_list):
            state['portion'] = 0
        cut_need_list = need_list[state['portion']*cards_in_one_portion:(state['portion']+1)*cards_in_one_portion]
        for stat in apriory:
            lock.acquire()
            chf[stat] = get("results_apriory." + stat,  dataset = state['ds'],  
                                        formula=state['formula'],  mongo=mongo)
            lock.release()
        for id in cut_need_list:
            card = {}
            card['id'] = id
            lock.acquire()
            card['size'] = str(get("size_of_doc", dataset=state['ds'],  
                                        number_of_card=id,  mongo=mongo))
            lock.release()
            card['diagnosis'] = []
            for stat in apriory:
                if id in chf[stat]:
                    card['diagnosis'].append(state['formula'] + '-' + stat)
            lock.acquire()
            abs = get('abstract',  dataset=state['ds'],  
                                    number_of_card=id,  mongo=mongo)
            lock.release()
            abs = abs.replace('>',  '&gt;')
            abs = abs.replace('<',  '&lt;')
            abs = abs.replace('&',  '&amp;')
            card['abstract'] = abs
            state['list'].append(card)
        self.site = urllib.quote(json.dumps(state))
        
