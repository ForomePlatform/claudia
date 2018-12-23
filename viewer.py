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
apostriory = [
            'ICHF', 
            'Other'
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
    def __init__(self,  args,  mongo,  lock):
        computer = socket.gethostname()
        if computer == 'noX540LJ':
            html_file = 'cci/viewer/viewer.html'
        else:
            html_file = '/home/andrey/work/Claudia/claudia/cci/viewer/viewer.html'
        html_file = open(html_file,  'r')
        html = html_file.read()
        html_file.close()
        self.site = html
#        now = datetime.datetime.now()
#        version = '?v=' + str(now.second)
#        config_file = open('claudia.json',  'r')
#        config = json.loads(config_file.read())
#        config_file.close()
#        if 'tax' in args:
#            tax_selected = args['tax']
#        else:
#            tax_selected = 'None'
#        if 'flag1' in args:
#            flag1 = args['flag1']
#        else:
#            flag1 = 'false'
#        if 'selected' in args:
#            selected = args['selected'].split('*')[1:]
#        else:
#            selected = ['0_0']
#        if 'ds' in args:
#            ds_selected = args['ds']
#        else:
#            ds_selected = 'cci'
#        cards_in_one_portion = 100
#        if 'portion' in args:
#            portion = int(int(args['portion'].split(' - ')[0])/cards_in_one_portion)
#        else:
#            portion = 0
#        # Head  
#        root = objectify.Element('html')
#        head = objectify.SubElement(root, 'head')
#        head.title = "Medical cards"
#        head.script = ""
#        head.script.set('src',  config['addr'] + config['html-base'] + 'viewer.js' + version)
#        url =  config['addr'] + config['html-base'] + 'viewer.css' + version
#        head.style = '@import url(' + url + ')'
#        # Body  
#        body = objectify.SubElement(root,  'body')
#        url = config['addr'] + config['html-base'] +'aquamarine-cubes.png' + version
#        body.set('style', 'background-image: url(' + url + ')')
#        body.set('id',  'main')
#        # Left part of page  
#        td1 = objectify.SubElement(body,  'div')
#        td1.set('class',  'left_column')
#        menu = objectify.SubElement(td1,  'div')
#        menu.set('class',  'menu')
#        # Emblem
#        emblem = objectify.SubElement(menu,  'div')
#        emblem.set('class',  'emblem')
#        claudia = objectify.SubElement(emblem,  'div')
#        claudia.set('class',  'claudia')
#        img = objectify.SubElement(claudia,  'img')
#        img.set('src',  config['addr'] + config['html-base'] + 'emblem_shadow.png')
#        ws = objectify.SubElement(emblem,  'div')
#        ws.set('class',  'workspace')
#        ws_div = objectify.SubElement(ws,  'div')
#        ws_div.b = 'Workspace:'
#        ws.span = 'Cardio'
#        # Pivot table
#        pivot_div = objectify.SubElement(menu,  'div')
#        pivot = objectify.SubElement(pivot_div,  'table')
#        pivot.set('class',  'pivote_table')
#        tr = objectify.SubElement(pivot,  'tr')
#        td = objectify.SubElement(tr,  'td')
#        td.set('class',  'key_cell')
#        ids = get('all_indexes',  dataset=ds_selected,  mongo=mongo)
#        need_list = []
#        for column in apostriory:
#            td= objectify.SubElement(tr,  'td')
#            td.set('class',  'key_cell')
#            td.b = column
#        if ds_selected == 'cci':
#            rows = apriory
#        else:
#            rows = ['all documents']
#        for row in rows:
#            tr = objectify.SubElement(pivot,  'tr')
#            td = objectify.SubElement(tr,  'td')
#            td.set('class',  'key_cell')
#            td.b = row
#            for column in apostriory:
#                i = rows.index(row)
#                j = apostriory.index(column)
#                couple = str(i) + '_' + str(j)
#                td = objectify.SubElement(tr,  'td')
#                td.set('onclick',  'renew_list("cell' + couple +'");')
#                td.set('id',  'cell' + couple)
#                list_apostriory = get('calculated_indexes',  dataset=ds_selected,
#                                        formula='CHF',  mongo=mongo)
#                if column == 'Other':
#                    ids2 = difference(ids,  list_apostriory)
#                else:
#                    ids2 = list_apostriory
#                ids3 = get('results_apriory.' + row, dataset=ds_selected, 
#                                        formula='CHF',  mongo=mongo)
#                if ds_selected != 'cci':
#                    ids3 = ids
#                list = intersection(ids2,  ids3)
#                td.i = len(list)
#                if couple in selected:
#                    td.set('class',  'cell_selected')
#                    need_list = union(need_list,  list)
#                else:
#                    td.set('class',  'ordinary_cell')
#        number_list = []
#        for id in need_list:
#            number_list.append(int(id))
#        number_list.sort()
#        need_list = []
#        for number in number_list:
#            need_list.append(str(number))
#        
#        reset = objectify.SubElement(menu,  'div')
#        reset.button = 'Reset all filters'
#        reset.button.set('class',  'button')
#        reset.set('id',  'reset')
#        reset.button.set('onclick',  'reset();')
#        
#
#        # Open the file with id of documents  
#        #ids = self.get_ids(tax_selected,  filter2_selected,  filter3_selected,  flag1,  flag2,  flag3,  mongo)
#        if tax_selected == 'None':
#            ids1 = ids
#        else:
#            ids1 = get("tax.idx", dataset=ds_selected,  
#                            taxonomy=tax_selected,  mongo=mongo)
#        if flag1 == 'false':
#            need_list = intersection(need_list,  ids1)
#        else:
#            need_list = difference(need_list,  ids1)
#        count = objectify.SubElement(menu,  'p')
#        count.b = str(len(need_list)) + ' cards were found.'
#        if len(need_list) == 0:
#            count.span = '''Choose several cells in the table in order to see a list of cards.'''
#        else:
#            count.span = '''Every card in following list has chosen annotations.'''
#        
#        # List of numbers  
#        scroll = objectify.SubElement(td1,  'div')
#        scroll.set('class',  'scroll')
#        ul = objectify.SubElement(scroll,  'ul')
#        ul.set('class',  'pink')
#        ul.set('id',  'card_list')
#        chf = {}
#        if portion*cards_in_one_portion > len(need_list):
#            portion = 0
#        cut_need_list = need_list[portion*cards_in_one_portion:(portion+1)*cards_in_one_portion]
#        for stat in apriory:
#            chf[stat] = get("results_apriory." + stat,  dataset = ds_selected,  
#                                        formula='CHF',  mongo=mongo)
#        for id in cut_need_list:
#            # Generate left list of id  
#            size = str(get("size_of_doc", dataset=ds_selected,  
#                                        number_of_card=id,  mongo=mongo))
#            diag = ''
#            for stat in apriory:
#                if id in chf[stat]:
#                    diag = ': CHF-' + stat
#            abs = get('abstract',  dataset=ds_selected,  
#                                    number_of_card=id,  mongo=mongo)
#            abs = abs.replace('>',  '&gt;')
#            abs = abs.replace('<',  '&lt;')
#            abs = abs.replace('&',  '&amp;')
#            abstract = etree.fromstring('<div>' + abs + '...</div>')
#            abstract.set('id',  'abs' + str(id))
#            abstract.set('class',  'hide_abstract')
#            s = '<li>#' + str(id)+' (' + size + ' sentences)' + diag +'</li>'
#            li= objectify.fromstring(s)
#            li.set('onclick',  'show_card('+str(id)+');')
#            li.set('onmouseover',  'show_abstract(' + id + ');')
#            li.set('onmouseout',  'hide_abstract(' + id + ');')
#            li.set('id',  'number'+str(id))
#            li.set('class',  'pinkli')
#            ul.append(li)
#            li.append(abstract)
#            
#        # Right part of page  
#        td2 = objectify.SubElement(body,  'div')
#        td2.set('class',  'right_column')
#        td2.set('valign',  'top')
#        td2.set('align',  'center')
#        # This paragraph will be a frame with data of cards  
#        card = objectify.SubElement(td2,  'div')
#        card.set('id',  'card')
#        card.set('class',  'click')
#        card.em = 'Click an element in left list in order to open a medical card.'
#        
#        # Panel of filters
#        filters_panel = objectify.SubElement(card,  'div')
#        filters_panel.set('class',  'filters_panel')
#        keys = objectify.SubElement(filters_panel,  'div')
#        keys.b = 'Choose filters:'
#        # row-data
#        row_data = objectify.SubElement(filters_panel,  'div')
#        row_data.set('class',  'filters')
#        row_data.div = 'Row-data:'
#        row_data.div.set('class',  'filter_name')
#        check = objectify.SubElement(row_data,  'div')
#        check.input = 'NOT'
#        check.input.set('type',  'checkbox')
#        check.input.set('id',  'filter_check1')
#        check.input.set('onchange',  'filter();')
#        if flag1 == 'true':
#            check.input.set('checked',  'checked')
#        check.set('class',  'tax_check')
#        select = objectify.SubElement(row_data,  'select')
#        select.set('class',  'select')
#        select.set('id',  'select1')
#        select.set('onchange',  'filter();')
#        option = etree.fromstring('<option>' + tax_selected + '</option>')
#        option.set('value',  tax_selected)
#        select.append(option)
#        for tax in taxes:
#            if tax == tax_selected:
#                continue
#            option = etree.fromstring('<option>'+tax+'</option>')
#            option.set('value',  tax)
#            select.append(option)
#        # DataSets
#        formulas = objectify.SubElement(filters_panel,  'div')
#        formulas.set('class',  'filters')
#        formulas.div = 'Data Set:'
#        formulas.div.set('class',  'filter_name')
#        select = objectify.SubElement(formulas,  'select')
#        select.set('class',  'select')
#        select.set('onchange',  'filter();')
#        select.set('id',  'dataset')
#        for ds in datasets:
#            option = etree.fromstring('<option>' + ds + '</option>')
#            if ds == ds_selected:
#                option.set('selected',  'selected')
#            select.append(option)
#        # Formulas
#        formulas = objectify.SubElement(filters_panel,  'div')
#        formulas.set('class',  'filters')
#        formulas.div = 'Formula:'
#        formulas.div.set('class',  'filter_name')
#        select = objectify.SubElement(formulas,  'select')
#        select.set('class',  'select')
#        select.set('onchange',  'filter();')
#        select.set('id',  'select_formulas')
#        option = etree.fromstring('<option>CHF</option>')
#        select.append(option)
#        
#        # Portions of cards
#        if len(need_list) > cards_in_one_portion:
#            portions = objectify.SubElement(filters_panel,  'div')
#            portions.set('class',  'filters')
#            portions.div = 'Show cards from the interval:'
#            portions.div.set('class',  'filter_name')
#            select = objectify.SubElement(portions,  'select')
#            select.set('class',  'select')
#            select.set('onchange',  'filter();')
#            select.set('id',  'portions')
#            for n in range(int((len(need_list)-1)/cards_in_one_portion)+1):
#                if n != int(len(need_list)/cards_in_one_portion):
#                    portion_size = str(n*cards_in_one_portion + 1) + ' - ' + str((n+1)*cards_in_one_portion)
#                else:
#                    portion_size = str(n*cards_in_one_portion +1) + ' - ' + str(len(need_list))
#                option = etree.fromstring('<option>' + portion_size + '</option>')
#                if portion == n:
#                    option.set('selected',  'selected')
#                select.append(option)
#        
#        # Print to file  
#        objectify.deannotate(root)
#        etree.cleanup_namespaces(root)
#        self.site = etree.tostring(root,  pretty_print = True,  xml_declaration = True)


class cardList:
    def __init__(self,  args,  mongo,  lock):
        state = urllib.unquote(args['args'])
        state = json.loads(state)
        # Find all cards selected in pivot table
        lock.acquire()
        ids = get('all_indexes',  dataset=state['ds'],  mongo=mongo)
        list_apostriory = get('calculated_indexes',  dataset=state['ds'],
                                            formula='CHF',  mongo=mongo)
        need_list = []
        for i in range(len(state['selected_cells'])):
            ids3 = get('results_apriory.' + apriory[i], dataset=state['ds'], 
                                            formula='CHF',  mongo=mongo)
            for j in range(len(state['selected_cells'][i])):
                if apostriory[j] == 'Other':
                    ids2 = difference(ids,  list_apostriory)
                else:
                    ids2 = list_apostriory
                if state['ds'] != 'cci':
                    ids3 = ids
                list = intersection(ids2,  ids3)
                if state['selected_cells'][i][j]['selected']:
                    need_list = union(need_list,  list)
                state['selected_cells'][i][j]['count'] = len(list)
        
        # Find cards with the taxonomy only
        tax = state['tax']
        if tax['tax'] == 'None':
            ids1 = ids
        else:
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
        lock.acquire()
        for stat in apriory:
            chf[stat] = get("results_apriory." + stat,  dataset = state['ds'],  
                                        formula='CHF',  mongo=mongo)
        for id in cut_need_list:
            card = {}
            card['id'] = id
            card['size'] = str(get("size_of_doc", dataset=state['ds'],  
                                        number_of_card=id,  mongo=mongo))
            card['diagnosis'] = []
            for stat in apriory:
                if id in chf[stat]:
                    card['diagnosis'].append('CHF-' + stat)
            abs = get('abstract',  dataset=state['ds'],  
                                    number_of_card=id,  mongo=mongo)
            abs = abs.replace('>',  '&gt;')
            abs = abs.replace('<',  '&lt;')
            abs = abs.replace('&',  '&amp;')
            card['abstract'] = abs
            state['list'].append(card)
        lock.release()
        self.site = urllib.quote(json.dumps(state))
        
