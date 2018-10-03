import re
from lxml import etree
from lxml import objectify
from mongodb import get,  put
from main_interpretator import next_step

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
            
# This class generates a HTML-page for a card  
class showCard:
    def __init__(self,  args,  mongo=None):
        number_of_card = args['id']
        if 'flags' in args:
            flags = args['flags'].split('*')
        else:
            flags = ['false' for c in range(len(taxes)+len(anns))]
        if 'new_step' in args:
            new_step = int(args['new_step'])
        else:
            new_step = 0;
        if new_step < 0:
            new_step = 0
        step = new_step - 1
        if 'tab' in args:
            number_of_tab = int(args['tab'])
        else:
            number_of_tab = 1
        if 'panel_align' in args:
            panel_align = args['panel_align']
        else:
            panel_align = 'apply_anns_left'
        if 'ds' in args:
            dataset = args['ds']
        else:
            dataset = 'cci'

        # Head  
        root = objectify.Element('html')
        head = objectify.SubElement(root, 'head')
        head.title = "Medical cards"
        head.script = ""
        head.script.set('src',  'cards.js')
        head.style = '@import url(cards.css)'
        head.style.set('type',  'text/css')
        # Body  
        body = objectify.SubElement(root,  'body')
        
        # Tabs  
        tabs = objectify.SubElement(body, 'div')
        tabs.set('id',  'tabs')
        tabs.set('class',  'notebook2')
        
        input = objectify.SubElement(tabs, 'input')
        input.set('type',  'radio')
        input.set('name',  'notebook2a')
        input.set('id',  'notebook2a_1')
        input.set('onclick',  'tab(1);')
        if number_of_tab == 1:
            input.set('checked',  'checked')
        input = objectify.SubElement(tabs, 'input')
        input.set('type',  'radio')
        input.set('name',  'notebook2a')
        input.set('id',  'notebook2a_2')
        input.set('onclick',  'tab(2);')
        if number_of_tab == 2:
            input.set('checked',  'checked')
        input = objectify.SubElement(tabs, 'input')
        input.set('type',  'radio')
        input.set('name',  'notebook2a')
        input.set('id',  'notebook2a_3')
        input.set('onclick',  'tab(3);')
        if number_of_tab == 3:
            input.set('checked',  'checked')
        input = objectify.SubElement(tabs, 'input')
        input.set('type',  'radio')
        input.set('name',  'notebook2a')
        input.set('id',  'notebook2a_4')
        input.set('onclick',  'tab(4);')
        if number_of_tab == 4:
            input.set('checked',  'checked')
        input = objectify.SubElement(tabs, 'input')
        input.set('type',  'radio')
        input.set('name',  'notebook2a')
        input.set('id',  'notebook2a_5')
        input.set('onclick',  'tab(5);')
        if number_of_tab == 5:
            input.set('checked',  'checked')
        
        
        # Tab 1: Code
        tab = objectify.SubElement(tabs, 'div')
        tab.label = 'Code'
        tab.label.set('for',  'notebook2a_1')
        tab.label.set('id',  'code_label')
        
        tab.set('id',  'code_tab')
        apply_anns = objectify.SubElement(tab, 'div')
        apply_anns.set('class',  panel_align)
        apply_anns.set('id',  'code_panel')
        move = objectify.SubElement(apply_anns,  'div')
        move.set('class',  'move')
        move.set('onmousedown',  'move_panel("code_panel");')
        move.set('onmouseup',  'drop_panel("code_panel");')
        move.b = ' '
        
        
        div3 = objectify.SubElement(apply_anns ,  'div')
        div3.set('id',  'code_button')
        div = objectify.SubElement(div3 ,  'div')
        div.set('class',  'start')
        div.b = 'Step #' + str(new_step);
        div.b.set('id',  'step')
        button1 = etree.fromstring('<button>Prev</button>')
        button1.set('class',  'button')
        button1.set('value',  str(new_step))
        button1.set('id',  'start3')
        button1.set('onclick',  'prev_step();')
        div3.append(button1)
        button2 = etree.fromstring('<button>Next</button>')
        button2.set('class',  'button')
        button2.set('value',  str(new_step))
        button2.set('id',  'start4')
        button2.set('onclick',  'next_step();')
        div3.append(button2)
        
        div2 = objectify.SubElement(apply_anns ,  'div')
        div2.set('class',  'code')
        div2.set('id',  'code_steps')
        
        code = get("code.json",  formula="CHF",  mongo=mongo)
        filtre = re.compile("\s+", re.M + re.I + re.U)
        n=1
        if new_step > len(code['sourceStatements']):
            new_step = len(code['sourceStatements'])
            step = new_step - 1
        for line in code['sourceStatements']:
            s = filtre.sub(' ',  line['text'])
            s = re.sub('<',  '&lt;',  s)
            s = re.sub('>',  '&gt;',  s)
            if s == '' or s == ' ' or s[0] == '/':
                continue
            p = etree.fromstring('<p><b>' + str(n) + '. </b>'+ s + '</p>')
            if n == new_step:
                p.set('class',  'step_selected')
            else:
                if n % 2 == 0:
                    p.set('class',  'step_not_selected')
                else:
                    p.set('class',  'step_zebra')
            p.set('id',  'step' + str(n))
            p.set('onclick',  'change_step('+str(n)+');')
            div2.append(p)
            n += 1
        
        
        
        label = objectify.SubElement(tab, 'div')
        label.set('class',  'label_left')
        label.set('id',  'advice')
        
        steps = {}
        if new_step == 0:
            steps['card'] = number_of_card
            steps['steps'] = []
        else:
            steps = get("steps.json", dataset=dataset,  mongo=mongo)
        if new_step < len(steps['steps']):
            new_chunks = steps['steps'][new_step]
        else:
            i = len(steps['steps'])
            while i <= new_step:
                next_step(code, dataset,  number_of_card,  i,  mongo)
                snap = get("snap.json", dataset=dataset,  number_of_card=number_of_card,  mongo=mongo)
                new_chunks = snap
                steps['steps'].append(new_chunks)
                i += 1
            put("steps.json",  steps, dataset=dataset, mongo=mongo)
        if step != -1:
            previous_chunks = steps['steps'][step]
        else:
            previous_chunks = new_chunks

        all_chunks = objectify.SubElement(tab, 'div')
        if len(new_chunks['data']) == len (previous_chunks['data']):
            all_cl = 'all_chunks'
        else:
            all_cl = 'all_chunks_selected'
        if 'reject' in new_chunks['data']:
            all_cl = 'all_chunks_rejected'
        all_chunks.set('class',  all_cl)
        s = 'Document attributes: '
        if len(new_chunks['data']) == 0:
            s += 'None'
        else:
            for key in new_chunks['data']:
                s += key + ': ' + new_chunks['data'][key] + '; '
        all_chunks.set('title',  s)
        all_chunks.set('id',  'code_chunks')
        changed_chunks = 0
        for m in range(len(new_chunks['sentences'])):
            p = objectify.SubElement(all_chunks,  'p')
            if len(new_chunks['sentences'][m]['data']) != len(previous_chunks['sentences'][m]['data']):
                p_cl = 'cell_selected'
            else:
                p_cl = 'cell_not_selected'
            if 'reject' in new_chunks['sentences'][m]['data']:
                    p_cl = 'cell_rejected'
            p.set('class',  p_cl)
            s = 'Sentence attributes: '
            if len(new_chunks['sentences'][m]['data']) == 0:
                s += 'None'
            else:
                for key in new_chunks['sentences'][m]['data']:
                    s += key + ': ' + new_chunks['sentences'][m]['data'][key] + '; '
            p.set('title',  s)
            for k in range(len(new_chunks['sentences'][m]['chunks'])):
                len1 = len(new_chunks['sentences'][m]['chunks'][k]['data'])
                len2 = len(previous_chunks['sentences'][m]['chunks'][k]['data'])
                if len1 == len2:
                    cl = 'cell_not_selected'
                else:
                    if new_step == 0:
                        cl = 'cell_not_selected'
                    else:
                        cl = 'cell_selected'
                        changed_chunks += 1
                if 'reject' in new_chunks['sentences'][m]['chunks'][k]['data']:
                    cl = 'cell_rejected'
                span = objectify.SubElement(p,  'span')
                span.set('class',  cl)
                s = 'Chunk attributes: '
                if len(new_chunks['sentences'][m]['chunks'][k]['data']) == 0:
                    s += 'None'
                else:
                    for key in new_chunks['sentences'][m]['chunks'][k]['data']:
                        s += key + ': ' + new_chunks['sentences'][m]['chunks'][k]['data'][key] + '; '
                span.set('title',  s)
                span.span = new_chunks['sentences'][m]['chunks'][k]['text']
                p.append(span)
                n += 1
            all_chunks.append(p)
            
        if new_step == 0:
            label_text = 'In order to run the programm click to any step of the code.'
        else:
            label_text = 'After this step annotations of ' + str(changed_chunks) + ' chunks were changed. They are selected.'
        label.b = label_text
        
        # Tab 2: Print Key words  (Annotations)
        tab = objectify.SubElement(tabs, 'div')
        tab.label = 'Annotations'
        tab.label.set('for',  'notebook2a_2')
        
        apply_anns = objectify.SubElement(tab, 'div')
        apply_anns.set('class',  'apply_anns')
        div = objectify.SubElement(apply_anns ,  'div')
        div.set('class',  'start')
        div.b = 'Step #' + str(new_step);
        div.b.set('id',  'ann_step')
        div2 = objectify.SubElement(apply_anns ,  'div')
        div2.set('class',  'code')
        
        code = get("code.json",  formula="CHF",  mongo=mongo)
        filtre = re.compile("\s+", re.M + re.I + re.U)
        n=1
        if new_step > len(code['sourceStatements']):
            new_step = len(code['sourceStatements'])
            step = new_step - 1
        for line in code['sourceStatements']:
            s = filtre.sub(' ',  line['text'])
            s = re.sub('<',  '&lt;',  s)
            s = re.sub('>',  '&gt;',  s)
            if s == '' or s == ' ' or s[0] == '/':
                continue
            p = etree.fromstring('<p><b>' + str(n) + '. </b>' + s + '</p>')
            if n == new_step:
                p.set('class',  'step_selected')
            else:
                if n % 2 == 0:
                    p.set('class',  'step_not_selected')
                else:
                    p.set('class',  'step_zebra')
            # p.set('onclick',  'change_step(' + str(n) + ');')
            p.set('id',  'ann_step' + str(n))
            p.set('onclick',  'change_ann_step('+str(n)+');')
            div2.append(p)
            n += 1
        
        div3 = objectify.SubElement(apply_anns ,  'div')
        button1 = etree.fromstring('<button>Prev</button>')
        button1.set('class',  'button')
        button1.set('value',  str(new_step))
        button1.set('id',  'start1')
        button1.set('onclick',  'prev_ann_step();')
        div3.append(button1)
        button2 = etree.fromstring('<button>Next</button>')
        button2.set('class',  'button')
        button2.set('value',  str(new_step))
        button2.set('id',  'start2')
        button2.set('onclick',  'next_ann_step();')
        div3.append(button2)
        
        div = objectify.SubElement(tab,  'div')
        p1 = etree.fromstring('<p><b>Key words:</b></p>')
        div.append(p1)
        key_words = get("key_words",  dataset=dataset,  number_of_card=number_of_card,  mongo=mongo)
        p2 = etree.fromstring('<p>' + ', '.join(key_words) + '</p>')
        div.append(p2)
        hr3 = objectify.SubElement(tab,  'hr')
        hr3.set('class',  'hr')
        br2 = objectify.SubElement(tab,  'br')
        
        div_by_step = objectify.SubElement(tab,  'div')
#        if new_step == 0:
#            p = etree.fromstring('''<b>Press any step of the programm 
#                    in order to see document annotations.</b>''')
#        else:
#            p = etree.fromstring('''<b>After this step the 
#                    document has next annotations:</b>''')
        p = etree.fromstring('<b>The document has following annotations:</b>')
        div_by_step.append(p)
        annotations = get('annotations',  dataset=dataset,  
                            number_of_card=number_of_card,  formula='CHF',  mongo=mongo)
        if len(annotations) == 0 and new_step != 0:
            div_by_step.p = 'None'
        else:
            for el in annotations:
                s = str(el)  + ': ' + str(annotations[el])
                p = etree.fromstring('<p>' + s + '</p>')
                div_by_step.append(p)
        
        # Tab 3: Print DocNNN.html (Document)
        tab = objectify.SubElement(tabs, 'div')
        tab.label = 'Document'
        tab.label.set('for',  'notebook2a_3')
        doc = objectify.SubElement(tab, 'div')
        doc.set('class',  'all_chunks')
        center = etree.fromstring('<h1>Document #' + number_of_card +'</h1>')
        doc.append(center)
        nodes = get("doc.html",  dataset=dataset,  
                                number_of_card=number_of_card,  mongo=mongo)
        for node in nodes:
            doc.append(etree.fromstring(node))
        hr2 = objectify.SubElement(doc,  'hr')
        hr2.set('class',  'hr')
        br = objectify.SubElement(doc,  'br')
        
        
        
        # Tab 4: Show chunks  (Chunks)
        tab = objectify.SubElement(tabs, 'div')
        tab.label = 'Chunks'
        tab.label.set('for',  'notebook2a_4')
        
        apply_anns = objectify.SubElement(tab, 'div')
        apply_anns.set('class',  'apply_anns')
        file = get("ch.json", dataset=dataset,  number_of_card=number_of_card,  mongo=mongo)
        if file is not None:
            doc_data = file

            #  Tab 4: Annotators  
            div = objectify.SubElement(apply_anns,  'div')
            
            label = objectify.SubElement(tab, 'div')
            label.set('class',  'label')
            
            # Tab 4: Chunks
            all_chunks = objectify.SubElement(tab, 'div')
            all_chunks.set('class',  'all_chunks')
            n=1
#                needed_anns = []
#                for i in range(len(taxes) + len(anns)):
#                    needed_anns.append(0)
            needed_anns = [0 for j in range(len(taxes) + len(anns))]
            selected_chunks = 0
            for sentence in doc_data["sentences"]:
                p = objectify.SubElement(all_chunks,  'p')
                for chunk in sentence["chunks"]:
#                        if n>count_of_chunks:
#                            break
                    for tax in taxes:
                        if tax in chunk['data']:
                            id = taxes.index(tax)
                            needed_anns[taxes.index(tax)] += 1
                            if flags[id] == 'true':
                                cl = 'cell_selected'
                                break
                        cl = 'cell_not_selected'
                    for ann in anns:
                        if 'type' in chunk['data'] and chunk['data']['type'] == ann:
                            id = anns.index(ann) + len(taxes)
                            if flags[id] == 'true':
                                cl = 'cell_selected'
                                break
                    if cl == 'cell_selected':
                        selected_chunks += 1
                    span = objectify.SubElement(p,  'span')
                    span.set('class',  cl)
                    s = 'Attributes: '
                    if len(chunk['data']) == 0:
                        s += 'None'
                    else:
                        for key in chunk['data']:
                            s += key + ': ' + chunk['data'][key] + '; '
                    span.set('title',  s)
                    span.span = chunk['text']
                    p.append(span)
                    n += 1
                all_chunks.append(p)
            
#                for j in range(len(taxes) + len(anns)):
#                    print('need: ' + str(i) + ', ' + str(needed_anns))
            div.b = 'Choose annotators:'
            for tax in taxes:
                if needed_anns[taxes.index(tax)] == 0:
                    continue
                p = objectify.SubElement(div,   'p')
                input = objectify.SubElement(p,   'input')
                input.span = tax
                input.set('type',  'checkbox')
                input.set('value',  tax)
                input.set('id',  'ch'+str(taxes.index(tax)))
                input.set('onchange',  'change_chunks('+str(len(taxes)+len(anns))+');')
                if flags[taxes.index(tax)] == 'true':
                    input.set('checked',  '')
            div = objectify.SubElement(apply_anns,  'div')
            div.b = 'Other annotators:'
            for ann in anns:
                p = objectify.SubElement(div,   'p')
                input = objectify.SubElement(p,   'input')
                input.span = ann
                input.set('type',  'checkbox')
                input.set('value',  ann)
                id = anns.index(ann)+len(taxes)
                input.set('id',  'ch'+str(id))
                input.set('onchange',  'change_chunks('+str(len(taxes)+len(anns))+');')
                if flags[id] == 'true':
                    input.set('checked',  '')
#                div = objectify.SubElement(apply_anns,  'div')
#                div.button = 'Apply'
#                div.button.set('class',  'button')
#                div.button.set('value',  number_of_card)
#                div.button.set('id',  'apply')
#                div.button.set('onclick',  'change_chunks('+str(len(taxes)+len(anns))+');')
            
            for flag in flags:
                if flag == 'true':
                    label_text = str(selected_chunks) + ' chunks are endowed this annotations. They are selected.'
                    break
                else:
                    label_text = 'Choose annotatators in order to see chunks endowed this annotations.'
            label.b = label_text
        
        # Tab 5: Info
        tab = objectify.SubElement(tabs, 'div')
        tab.label = 'Info'
        tab.label.set('for',  'notebook2a_5')
        doc = objectify.SubElement(tab, 'div')
        doc.set('class',  'all_chunks')
        title = objectify.SubElement(doc,  'center')
        title.h1 = 'Card #' + number_of_card
        title.h1.set('id',  'title')
        ds = objectify.SubElement(doc,  'div')
        ds.b = 'DataSet: ' + dataset
        ds.b.set('id',  'ds_name')
        carcas0 = objectify.SubElement(doc,  'p')
        carcas = objectify.SubElement(carcas0,  'center')
        
        # Print the table from JSON-file
        table = objectify.SubElement(carcas,  'table')
        table.set('class',  'table')
        dict = get("doc.json",  dataset=dataset,  
                        number_of_card=number_of_card,  mongo=mongo)
        for field in dict:
            tr = objectify.SubElement(table,  'tr')
            td = etree.fromstring('<td>'+str(field)+'</td>')
            tr.append(td)
            tr.td.set('class',  'cell1')
            td = etree.fromstring('<td>'+dict[field]+'</td>')
            td.set('class',  'cell2')
            tr.append(td)
        carcas.br = ''
        hr1 = objectify.SubElement(carcas,  'hr')
        carcas.hr.set('class', 'hr')
        br = objectify.SubElement(carcas,  'br')
        
        
                
                
        

        # Print HTML-code
        objectify.deannotate(root)
        etree.cleanup_namespaces(root)
        self.site = etree.tostring(root,  pretty_print = True,  xml_declaration = True)
        return
