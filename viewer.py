from lxml import etree
from lxml import objectify
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
filter2 = [
            'None', 
            'ICHF'
            ]
filter3 = [
            'None', 
            'CHF-diagnosed'
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
    def __init__(self,  args,  mongo):
        if 'tax' in args:
            tax_selected = args['tax']
        else:
            tax_selected = 'None'
#        if 'filter2_selected' in args:
#            filter2_selected = args['filter2_selected']
#        else:
#            filter2_selected = 'None'
#        if 'filter3_selected' in args:
#            filter3_selected = args['filter3_selected']
#        else:
#            filter3_selected = 'None'
        if 'flag1' in args:
            flag1 = args['flag1']
        else:
            flag1 = 'false'
#        if 'flag2' in args:
#            flag2 = args['flag2']
#        else:
#            flag2 = 'false'
#        if 'flag3' in args:
#            flag3 = args['flag3']
#        else:
#            flag3 = 'false'
        if 'selected' in args:
            selected = args['selected'].split('*')[1:]
        else:
            selected = []
        # Head  
        root = objectify.Element('html')
        head = objectify.SubElement(root, 'head')
        head.title = "Medical cards"
        head.script = ""
        head.script.set('src',  'viewer.js')
        head.style = '@import url(viewer.css)'
        # Body  
        body = objectify.SubElement(root,  'body')
        body.set('style', 'background-image: url("aquamarine-cubes.png")')
        body.set('id',  'main')
        # Left part of page  
        td1 = objectify.SubElement(body,  'div')
        td1.set('class',  'left_column')
        # Filters
        menu = objectify.SubElement(td1,  'div')
        menu.set('class',  'menu')
        
        # Pivot table
        pivot = objectify.SubElement(menu,  'table')
        pivot.set('class',  'pivote_table')
        tr = objectify.SubElement(pivot,  'tr')
        td = objectify.SubElement(tr,  'td')
        td.set('class',  'key_cell')
        ids = get('all_indexes',  mongo=mongo)
        need_list = []
        for column in filter3:
            td= objectify.SubElement(tr,  'td')
            td.set('class',  'key_cell')
            td.b = column
        for row in filter2:
            tr = objectify.SubElement(pivot,  'tr')
            td = objectify.SubElement(tr,  'td')
            td.set('class',  'key_cell')
            td.b = row
            for column in filter3:
                i = filter2.index(row)
                j = filter3.index(column)
                couple = str(i) + '_' + str(j)
                td = objectify.SubElement(tr,  'td')
                td.set('onclick',  'renew_list("cell' + couple +'");')
                td.set('id',  'cell' + couple)
                if row == 'None':
                    ids2 = ids
                else:
                    ids2 = get('calculated_indexes',  formula='CHF',  mongo=mongo)
                if column == 'None':
                    ids3 = ids
                else:
                    ids3 = get('results_apriory',  formula='CHF',  mongo=mongo)
                list = intersection(ids2,  ids3)
                td.i = len(list)
                if couple in selected:
                    td.set('class',  'cell_selected')
                    need_list = union(need_list,  list)
                else:
                    td.set('class',  'ordinary_cell')
        number_list = []
        for id in need_list:
            number_list.append(int(id))
        number_list.sort()
        need_list = []
        for number in number_list:
            need_list.append(str(number))
        
        reset = objectify.SubElement(menu,  'div')
        reset.button = 'Reset all filters'
        reset.button.set('class',  'button')
        reset.set('id',  'reset')
        reset.set('onclick',  'reset();')
            
#        keys = objectify.SubElement(menu,  'div')
#        keys.b = 'Choose a filter:'
#        # row-data
#        row_data = objectify.SubElement(menu,  'div')
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
#        # calculated
#        calculated= objectify.SubElement(menu,  'div')
#        calculated.set('class',  'filters')
#        calculated.div = 'Calculated:'
#        calculated.div.set('class',  'filter_name')
#        check = objectify.SubElement(calculated,  'div')
#        check.input = 'NOT'
#        check.input.set('type',  'checkbox')
#        check.input.set('id',  'filter_check2')
#        check.input.set('onchange',  'filter();')
#        check.set('class',  'tax_check')
#        if flag2 == 'true':
#            check.input.set('checked',  'checked')
#        select = objectify.SubElement(calculated,  'select')
#        select.set('class',  'select')
#        select.set('id',  'select2')
#        select.set('onchange',  'filter();')
#        option = etree.fromstring('<option>' + filter2_selected + '</option>')
#        option.set('value',  filter2_selected)
#        select.append(option)
#        for opt in filter2:
#            if opt == filter2_selected:
#                continue
#            option = etree.fromstring('<option>'+opt+'</option>')
#            option.set('value',  opt)
#            select.append(option)
#        # known
#        known = objectify.SubElement(menu,  'div')
#        known.set('class',  'filters')
#        known.div = 'Known:'
#        known.div.set('class',  'filter_name')
#        check = objectify.SubElement(known,  'div')
#        check.input = 'NOT'
#        check.input.set('type',  'checkbox')
#        check.input.set('id',  'filter_check3')
#        check.input.set('onchange',  'filter();')
#        check.set('class',  'tax_check')
#        if flag3 == 'true':
#            check.input.set('checked',  'checked')
#        select = objectify.SubElement(known,  'select')
#        select.set('class',  'select')
#        select.set('id',  'select3')
#        select.set('onchange',  'filter();')
#        option = etree.fromstring('<option>' + filter3_selected + '</option>')
#        option.set('value',  filter3_selected)
#        select.append(option)
#        for opt in filter3:
#            if opt == filter3_selected:
#                continue
#            option = etree.fromstring('<option>'+opt+'</option>')
#            option.set('value',  opt)
#            select.append(option)
        # Open the file with id of documents  
        #ids = self.get_ids(tax_selected,  filter2_selected,  filter3_selected,  flag1,  flag2,  flag3,  mongo)
        if tax_selected == 'None':
            ids1 = ids
        else:
            ids1 = get("tax.idx",  taxonomy=tax_selected,  mongo=mongo)
        if flag1 == 'false':
            need_list = intersection(need_list,  ids1)
        else:
            need_list = difference(need_list,  ids1)
        count = objectify.SubElement(menu,  'p')
        count.b = str(len(need_list)) + ' cards were found.'
        if len(need_list) == 0:
            count.span = '''Choose several cells in the table in order to see a list of cards.'''
        else:
            count.span = '''Every card in following list has chosen annotations.'''
                            #or has not them if option "NOT" was indicated.'''
        # List of numbers  
        scroll = objectify.SubElement(td1,  'div')
        scroll.set('class',  'scroll')
        ul = objectify.SubElement(scroll,  'ul')
        ul.set('class',  'pink')
        for id in need_list:
            # Generate left list of id  
            li= objectify.fromstring('<li><center>#' + str(id)+'</center></li>')
            li.set('onclick',  'show_card('+str(id)+');')
            li.set('id',  'number'+str(id))
            li.set('class',  'pinkli')
            ul.append(li)
        # Right part of page  
        td2 = objectify.SubElement(body,  'div')
        td2.set('class',  'right_column')
        td2.set('valign',  'top')
        td2.set('align',  'center')
        # This paragraph will be a frame with data of cards  
        card = objectify.SubElement(td2,  'div')
        card.set('id',  'card')
        card.set('class',  'click')
        card.em = 'Click an element in left list in order to open a medical card.'
        
        # Panel of filters
        filters_panel = objectify.SubElement(td2,  'div')
        filters_panel.set('class',  'filters_panel')
        keys = objectify.SubElement(filters_panel,  'div')
        keys.b = 'Choose a filter:'
        # row-data
        row_data = objectify.SubElement(filters_panel,  'div')
        row_data.set('class',  'filters')
        row_data.div = 'Row-data:'
        row_data.div.set('class',  'filter_name')
        check = objectify.SubElement(row_data,  'div')
        check.input = 'NOT'
        check.input.set('type',  'checkbox')
        check.input.set('id',  'filter_check1')
        check.input.set('onchange',  'filter();')
        if flag1 == 'true':
            check.input.set('checked',  'checked')
        check.set('class',  'tax_check')
        select = objectify.SubElement(row_data,  'select')
        select.set('class',  'select')
        select.set('id',  'select1')
        select.set('onchange',  'filter();')
        option = etree.fromstring('<option>' + tax_selected + '</option>')
        option.set('value',  tax_selected)
        select.append(option)
        for tax in taxes:
            if tax == tax_selected:
                continue
            option = etree.fromstring('<option>'+tax+'</option>')
            option.set('value',  tax)
            select.append(option)
        # Print to file  
        objectify.deannotate(root)
        etree.cleanup_namespaces(root)
        self.site = etree.tostring(root,  pretty_print = True,  xml_declaration = True)
    
#    def get_ids(self,  filter1,  filter2,  filter3,  flag1,  flag2,  flag3,  mongo):
#        ids = get("all_indexes",  mongo=mongo)
#        
#        if filter1 == 'None':
#            ids1 = ids
#        else:
#            ids1 = get("tax.idx",  taxonomy=filter1,  mongo=mongo)
#            
#        if filter2 == 'None':
#            ids2 = ids
#        else:
#            ids2 = get("calculated_indexes",  formula="CHF",  mongo=mongo)
#
#        
#        if filter3 == 'None':
#            ids3 = ids
#        else:
#            ids3 = get("results_apriory",  formula="CHF",  mongo=mongo)
#                
#        need_list = []
#        for id in ids:
#            if (id in ids1) == (flag1 == 'true'):
#                continue
#            if (id in ids2) == (flag2 == 'true'):
#                continue
#            if (id in ids3) == (flag3 == 'true'):
#                continue
#            need_list.append(id)
#        return need_list
