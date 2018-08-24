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
class showIndex:
    def __init__(self,  args,  mongo):
        if 'tax' in args:
            tax_selected = args['tax']
        else:
            tax_selected = 'None'
        if 'filter2_selected' in args:
            filter2_selected = args['filter2_selected']
        else:
            filter2_selected = 'None'
        if 'filter3_selected' in args:
            filter3_selected = args['filter3_selected']
        else:
            filter3_selected = 'None'
        if 'flag1' in args:
            flag1 = args['flag1']
        else:
            flag1 = 'false'
        if 'flag2' in args:
            flag2 = args['flag2']
        else:
            flag2 = 'false'
        if 'flag3' in args:
            flag3 = args['flag3']
        else:
            flag3 = 'false'
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
        # Filter  
        menu = objectify.SubElement(td1,  'div')
        menu.set('class',  'menu')
        keys = objectify.SubElement(menu,  'div')
        keys.b = 'Choose a filter:'
        # row-data
        row_data = objectify.SubElement(menu,  'div')
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
        # calculated
        calculated= objectify.SubElement(menu,  'div')
        calculated.set('class',  'filters')
        calculated.div = 'Calculated:'
        calculated.div.set('class',  'filter_name')
        check = objectify.SubElement(calculated,  'div')
        check.input = 'NOT'
        check.input.set('type',  'checkbox')
        check.input.set('id',  'filter_check2')
        check.input.set('onchange',  'filter();')
        check.set('class',  'tax_check')
        if flag2 == 'true':
            check.input.set('checked',  'checked')
        select = objectify.SubElement(calculated,  'select')
        select.set('class',  'select')
        select.set('id',  'select2')
        select.set('onchange',  'filter();')
        option = etree.fromstring('<option>' + filter2_selected + '</option>')
        option.set('value',  filter2_selected)
        select.append(option)
        for opt in filter2:
            if opt == filter2_selected:
                continue
            option = etree.fromstring('<option>'+opt+'</option>')
            option.set('value',  opt)
            select.append(option)
        # known
        known = objectify.SubElement(menu,  'div')
        known.set('class',  'filters')
        known.div = 'Known:'
        known.div.set('class',  'filter_name')
        check = objectify.SubElement(known,  'div')
        check.input = 'NOT'
        check.input.set('type',  'checkbox')
        check.input.set('id',  'filter_check3')
        check.input.set('onchange',  'filter();')
        check.set('class',  'tax_check')
        if flag3 == 'true':
            check.input.set('checked',  'checked')
        select = objectify.SubElement(known,  'select')
        select.set('class',  'select')
        select.set('id',  'select3')
        select.set('onchange',  'filter();')
        option = etree.fromstring('<option>' + filter3_selected + '</option>')
        option.set('value',  filter3_selected)
        select.append(option)
        for opt in filter3:
            if opt == filter3_selected:
                continue
            option = etree.fromstring('<option>'+opt+'</option>')
            option.set('value',  opt)
            select.append(option)
        # Open the file with id of documents  
        ids = self.get_ids(tax_selected,  filter2_selected,  filter3_selected,  flag1,  flag2,  flag3,  mongo)
        count = objectify.SubElement(menu,  'p')
        count.b = str(len(ids)) + ' cards were found.'
        count.span = '''Every card in following list has chosen annotations 
                        or has not them if option "NOT" was indicated.'''
        # List of numbers  
        scroll = objectify.SubElement(td1,  'div')
        scroll.set('class',  'scroll')
        ul = objectify.SubElement(scroll,  'ul')
        ul.set('class',  'pink')
        for id in ids:
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
        card = objectify.SubElement(td2,  'p')
        card.set('id',  'card')
        card.set('class',  'click')
        card.em = 'Click an element in left list in order to open a medical card.'
        # Print to file  
        objectify.deannotate(root)
        etree.cleanup_namespaces(root)
        self.site = etree.tostring(root,  pretty_print = True,  xml_declaration = True)
    
    def get_ids(self,  filter1,  filter2,  filter3,  flag1,  flag2,  flag3,  mongo):
        print('Start get')
#        id_file_name = 'cci/documents/dir.list'
#        try:
#            id_file = open(id_file_name,  'r')
#        except IOError:
#            print('No such file or directory: ' + id_file_name)
#            return None
#        else:
#            ids = []
#            for line in id_file:
#                ids.append(int(line))
#            id_file.close()
        ids = get("all_indexes",  mongo=mongo)
        
        if filter1 == 'None':
            ids1 = ids
        else:
            ids1 = get("tax.idx",  taxonomy=filter1,  mongo=mongo)
#            filter1_file_name = 'cci/indexes/' + filter1 + '.idx'
#        try:
#            filter1_file = open(filter1_file_name,  'r')
#        except IOError:
#            print('No such file or directory: ' + filter1_file_name)
#            return None
#        else:
#            ids1 = []
#            for line in filter1_file:
#                ids1.append(int(line))
#            filter1_file.close()
            
        if filter2 == 'None':
            ids2 = ids
        else:
            ids2 = get("calculated_indexes",  formula="CHF",  mongo=mongo)
#            filter2_file_name = 'cci/indexes/' + filter2 + '.idx'
#        try:
#            filter2_file = open(filter2_file_name,  'r')
#        except IOError:
#            print('No such file or directory: ' + filter2_file_name)
#            return None
#        else:
#            ids2 = []
#            for line in filter2_file:
#                ids2.append(int(line))
#            filter2_file.close()
        
        if filter3 == 'None':
            ids3 = ids
        else:
            filter3_file_name = 'cci/indexes/' + filter3 + '.idx'
            try:
                filter3_file = open(filter3_file_name,  'r')
            except IOError:
                print('No such file or directory: ' + filter3_file_name)
                return None
            else:
                ids3 = []
                for line in filter3_file:
                    ids3.append(line.strip())
                filter3_file.close()
        
        need_list = []
        for id in ids:
            if (id in ids1) == (flag1 == 'true'):
                continue
            if (id in ids2) == (flag2 == 'true'):
                continue
            if (id in ids3) == (flag3 == 'true'):
                continue
            need_list.append(id)
        return need_list
