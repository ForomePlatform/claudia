import sys
import json
import copy
from lxml import etree
from mongodb import get
from mongodb import put
from mongodb import connect
from annotators import IsNumericAnnotator,  taxonomy,  RegExpAnnotator


formulas = [
            'CHF', 
            'MI'
            ]

def all_formulas(mongo):
    for formula in formulas:
        print('Formula: ' + formula)
        all_datasets(formula,  mongo)

# Apply code to all datasets
def all_datasets(formula,  mongo):
    datasets=[
                'cci', 
                'nets', 
                'medications'
                ]
    for ds in datasets:
        print('DataSet: ' + ds)
        all_files(ds, formula, mongo)

#  Apply JSON-code for all documents in 'dir.list' and all steps of JSON-code.  
#  It's independent with 'def all_steps'.
def all_files(dataset, formula, mongo):
    chf = []
    #formula = 'CHF'
    indexes = get("all_indexes", dataset=dataset,  mongo=mongo)
    code = get("code.cla.json", formula=formula, mongo=mongo)
    for number_of_card in indexes:
        print('Card #' + number_of_card)
        doc_data = create_dict(dataset,  number_of_card,  mongo)
        all_steps(code, doc_data, dataset,  number_of_card,  mongo,  False)
        put("annotations",  doc_data['data'],  
                dataset=dataset,  number_of_card=number_of_card, 
                formula = formula,  mongo=mongo)
        if doc_data['data']['Formula diagnose'] != 'No':
            chf.append(number_of_card)
            print(doc_data['data']['Formula diagnose'])
    put("calculated_indexes",  chf,  formula=formula,  
                dataset=dataset,  mongo=mongo)

# Apply function 'annotator' for all document of a patient
#def all_documents(annotator,  doc_data,  old_step,  mongo,  step_id):
#    for document in doc_data['documents']:
#        step = copy.deepcopy(old_step)
#        annotator(document,  step,  mongo,  step_id)

#  Apply function 'annotator' for all sentence of a document.  
def all_sentences(annotator,  doc_data,  old_step,  mongo,  step_id):
    for sentence in doc_data['sentences']:
        step = copy.deepcopy(old_step)
        annotator(sentence,  step,  mongo,  step_id)

#  Apply function 'annotator' for all chunks of a document. 
def all_chunks(annotator, doc_data, old_step,  mongo,  step_id):
    for sentence  in doc_data['sentences']:
        for chunk in sentence['chunks']:
            step = copy.deepcopy(old_step)
            annotator(chunk,  step,  mongo,  step_id)


#  Apply 'interpretator' for all steps of JSON-code in 'json_file_name' for a document.
#  'snap_file' is a snapshot file.  
def all_steps(code,  doc_data, dataset,  number_of_card,  mongo,  with_snap):
    for step in code['statements']:
        claudia_interpretator(doc_data,  dataset,  
                                        number_of_card, step,  mongo, with_snap,  -1)


#  Represent a document to a list 'doc_data' of sentences. Every sentence is a list of chunks.
#  Every chunk is a dictionary:
#
#  text: 'chunk'
#  data: '{key: value, ... }
#
#  Attribute 'data' is empty.  
def create_dict(dataset,  patient,  mongo):
    #sHTML_Parser = etree.HTMLParser(remove_comments = True)
    doc = get("doc.html",  dataset=dataset,  
                                number_of_card=patient,  mongo=mongo)
    return create_dict_by_doc(doc)

# Generate the dictionary by raw HTML-document. "doc" is a list of sentences.
def create_dict_by_doc(nodes):
    doc_data = {}
    doc_data['data'] = {}
    doc_data['sentences'] = []
    for node in nodes:
        try:
            sample = etree.fromstring(node)
            sentence = {}
            sentence['data'] = {}
            sentence['chunks'] = []
            s = etree.tostring(sample)
            ss = etree.fromstring(s)
            for nd_alevel in ss.xpath('/p/span/span'):
                alevel = nd_alevel.attrib
                s = etree.tostring(nd_alevel)
                sss = etree.fromstring(s)
                for nd in sss.xpath('/span/span/span'):
                    chunk = {}
                    chunk['text'] = nd.text
                    chunk['data'] = {}
                    chunk['data']['__negation'] = alevel['class'][6:]
                    sentence['chunks'].append(chunk)
            doc_data['sentences'].append(sentence)
        except etree.XMLSyntaxError:
            print('XMLSyntaxError: ' + node)
            return 'XMLSyntaxError'
    return doc_data

def apply_tax(chunk,  step,  mongo,  step_id):
#    if step_id != step['source_id'] and step_id != -1:
#        return
    if step['options']['name'] == 'RegExp':
        new_dict = RegExpAnnotator(chunk['text'], step['options']['pattern'])
        key = step['options']['var']
        new_dict[key] = key
        chunk['data'].update(new_dict)
        return
    for tax in step['options']['values']:
        if tax == 'NUMERIC':
            dict = IsNumericAnnotator(chunk['text'],  mongo)
        else:
            dict = taxonomy(chunk['text'],  tax,  mongo)
        chunk['data'].update(dict)

def loop(doc_data, dataset, number_of_card,  step,  mongo,  with_snap,  step_id):
    for new_step in step['options']['action']:
        if step_id not in new_step['steps'] and step_id != -1:
            continue
        if step['set'] == 'entities':
            all_chunks(one_step,  doc_data,  new_step,  mongo,  step_id)
        elif step['set'] == 'sentences':
            all_sentences(one_step,  doc_data,  new_step,  mongo,  step_id)
        elif step['set'] == 'documents':
            dstep = copy.deepcopy(new_step)
            one_step(doc_data,  dstep,  mongo,  step_id)
        else:
            print('Unknoun loop set: ' + str(step['set']))
            sys.exit(0)
        if with_snap:
            snapshot(dataset,  number_of_card, doc_data, mongo)

def one_step(data,  step,  mongo,  step_id):
    if step['action'] == 'detect':
        if step['name'] == 'if':
            return statement(data,  step['options'],  mongo,  step_id)
        elif step['name'] == 'annotate':
            annotate(data,  step,  step_id)
        else:
            print('Unknown name: ' + step['name'])
            sys.exit(1)
    elif step['action'] == 'reject':
        reject(data,  step,  step_id)
    else:
        print('Unknown action: ' + step['action'])
        sys.exit(2)
    return data


def reject(data,  step,  step_id):
    if step_id not in step['steps'] and step_id != -1:
        return
    data['data']['reject'] = 'reject'


#  Conditional operator: if ... then ... .
def statement(data,  step,  mongo,  step_id):
    cond = condition(data, step['condition'],  step['args'])
    if cond:
        if step_id in step['steps_if'] or step_id == -1:
            for new_step in step['action_if']:
                return one_step(data,  new_step,  mongo,  step_id)
    else:
        if 'action_else' in step:
            if step_id in step['steps_else'] or step_id == -1:
                for new_step in step['action_else']:
                    return one_step(data,  new_step,  mongo,  step_id)

#  Conditional operator 'if'. See 'def statement'.  
def condition(data,  cond,  args):
    #print('f: ' + cond['f'] + ' args: ' + str(args))
    #print('cond: ' + json.dumps(cond,  indent=4))
    if cond['f'] == 'annotated':
        return annotated(data,  cond,  args)
    elif cond['f'] == 'and':
        return conjunction(data,  cond['a'],  args)
    elif cond['f'] == 'or':
        return disjunction(data,  cond['a'],  args)
    elif cond['f'] == 'not':
        return negative(data,  cond['a'],  args)
    elif cond['f'] == 'equals':
        return equals(data,  cond['a'],  args)
#    elif cond['f'] == 'annotationData':
#        return annotationData(data,  cond['a'],  args)
    elif cond['f'] == 'x':
        return variable(data,  args)
#    elif cond['f'] == 'annotationData':
#        return annotation_data(data, dict)
#    elif cond['f'] == 'const':
#        return data['value']
    else:
        print('Unknown function: ' + cond['f'])
        sys.exit(7)

def annotated(data,  cond,  args):
    #print('data: ' + str(data))
    #print('cond: ' + str(cond))
    #print('args: ' + str(args))
    if 'sentences' in data:
        set = 'sentences'
    elif 'chunks'in data:
        set = 'chunks'
    else:
        set = 'text'
    if set == 'text':
        arg = args[0]
        args.pop(0)
        if arg['type'] == 'key':
            if arg['value'] in data['data']:
                res = True
            else:
                res = False
            for ann in cond['a']:
                res = condition(data,  ann,  args) and res
            return res
        else:
            print('Unknown type: ' + arg['type'])
            sys.exit(8)
    else:
        #print('chunk cond: ' + str(cond))
        for chunk in data[set]:
            new_args = copy.deepcopy(args)
            new_cond = copy.deepcopy(cond)
            #print('args before: ' + str(new_args))
            arg = new_args[0]
            new_args.pop(0)
            if arg['type'] == 'key':
                if arg['value'] in chunk['data']:
                    res = True
                else:
                    res = False
                for ann in new_cond['a']:
                    #print('ann: ' + json.dumps(ann,  indent=4))
                    #print('new_args: ' + json.dumps(new_args,  indent=4))
                    res = condition(chunk,  ann,  new_args) and res
                if res:
                    args.pop(0)
                    for ann in new_cond['a']:
                        args.pop(0)
                        args.pop(0)
                    return True
            else:
                print('Unknown type: ' + arg['type'])
                sys.exit(11)
#            if annotated(chunk,  new_cond,  new_args):
#                args.pop(0)
#                for ann in new_cond['a']:
#                    args.pop(0)
#                    args.pop(0)
#                return True
        args.pop(0)
        for ann in cond['a']:
            args.pop(0)
            args.pop(0)
        return False
#        sys.exit()
#        n = 0
#        for chunk in data[set]:
#            new_args = copy.deepcopy(args)
#            arg = new_args[0]
#            new_args.pop(0)
#            if arg['type'] == 'key':
#                if arg['value'] in data['data']:
#                    res = True
#                else:
#                    res = False
#                for ann in cond['a']:
#                    if new_args[0] == 'count':
#                    res = condition(data,  ann,  args) and res
#                return res
#            else:
#                print('Unknown type: ' + arg['type'])
#                sys.exit(8)


#  'And'
def conjunction(data,  cond,  args):
    cond1 = condition(data, cond[0],  args)
    cond2 = condition(data,  cond[1],  args)
    return cond1 and cond2


#  'Or'
def disjunction(data,  cond,  args):
    cond1 = condition(data, cond[0],  args)
    cond2 = condition(data,  cond[1],  args)
    return cond1 or cond2


#  'Not'
def negative(data,  cond,  args):
    return not condition(data,  cond,  args)


#  '='
def equals(data,  cond,  args):
    if args[0]['value'] == 'context':
        context = args[1]['value']
        args.pop(0)
        args.pop(0)
        #print('chunk: ' + data['text'] + ', negation: ' + str(data['data']['__negation']))
        neg = int(data['data']['__negation'])
        res = (neg >= negation[context]['min'] and neg <= negation[context]['max'])
        return res
    a = condition(data,  cond[0],  args)
    b = condition(data,  cond[1],  args)
    if a is None or b is None:
        return False
    return a == b
#    if a == b:
#        return True
#    else:
#        return False


def variable(data,  args):
    arg = args[0]
    args.pop(0)
    if arg['type'] == 'annotationData':
        if arg['value'] in data['data']:
            res = data['data'][arg['value']]
            return res
    elif arg['type'] == 'const':
        res = arg['value']
        return res
    else:
        print('Unknown type: ' + arg['type'])
        print(args)
        #print(data)
        sys.exit(9)


def annotate(data,  step,  step_id):
#    elements = ['chunks',  'sentences',  'documents']
#    for el in elements:
#        if el in data:
#            n = 0
#            for chunk in data[el]:
#                if step['key'] in chunk:
#                    n += 1
#            data['data'][step['key']] = n
#    if step['key'] not in data['data']:
    if step_id not in step['steps'] and step_id != -1:
        return
    data['data'][step['key']] = step['key']
    data['data'].update(step['options'])


#  Save all results about a document in file 'file_name'. 
def snapshot(dataset,  number_of_card,  doc_data,  mongo):
    put("snap.json",  doc_data,  dataset=dataset,  
                                number_of_card=number_of_card,  mongo=mongo)


def setFinalAnnotation(doc_data,  step):
    key = step['key']
    if key in doc_data['data']:
        doc_data['data']['Formula diagnose'] = key + '-diagnosed'
    else:
        doc_data['data']['Formula diagnose'] = 'No'


#  The interpretator of step 'step' of JSON-code appying for a document ('doc-data').  
#  Snapshots are in 'snap-file'.  
def claudia_interpretator(doc_data, dataset, 
                    number_of_card,  step,  mongo, with_snap,  step_id):
    if step_id not in step['steps'] and step_id != -1:
        return doc_data
    if step['action'] == 'for':
        loop(doc_data, dataset,  number_of_card,  
                                        step,  mongo, with_snap,  step_id)
    elif step['action'] == 'detect':
        if step['name'] == 'lookup':
            all_chunks(apply_tax,  doc_data,  step,  mongo,  step_id)
        elif step['name'] == 'setFinalAnnotations':
            setFinalAnnotation(doc_data,  step['options'])
        else:
            print('Unknown operator: ' + step['name'])
            sys.exit(3)
    else:
        print('Unknown action: ' + step['action'])
        sys.exit(4)
    return doc_data


#  Apply the interpretator for a step 'step_id' of JSON-code in 'code_file_name'
#  for a document 'doc_file_name'. 'snap_file_name' is a snaphot file.
#  It's independent with 'def all_files'.
def next_step(doc_data,  code, dataset, number_of_card,  step_id,  mongo):
#def next_step(doc_file_name,  code_file_name, snap_file_name, step_id):
    if step_id == 0 and number_of_card is not None:
        doc_data = create_dict(dataset, number_of_card,  mongo)
    if step_id > code['count_of_steps']:
        return
    if doc_data is None:
        doc_data = create_dict(dataset,  number_of_card,  mongo)
    for step in code['statements']:
        claudia_interpretator(doc_data, dataset, 
                                                    number_of_card,  step,  mongo,  False,  step_id)
    #snapshot(dataset,  number_of_card,  doc_data,  mongo)
    return doc_data


def for_one_doc(doc,  code,  mongo,  cch,  ticket,  lock):
    doc_data = create_dict_by_doc(doc)
    state = {}
    state['count_of_steps'] = code['count_of_steps']
    for step in code['statements']:
        lock.acquire()
        state['step'] = step
        print('Step: ' + str(step))
        cch.putValue(ticket,  state)
        lock.release()
        claudia_interpretator(doc_data, None, 
                            None,  step,  mongo,  False,  -1)
    #print("Results of the formula: " + json.dumps(doc_data,  indent=4))
    return doc_data
    

negation = {
            "positive": {
                    "max": 0, 
                    "min": 0
            }, 
            "possibly negative": {
                    "max": 100, 
                    "min": 10
            }, 
            "negative": {
                    "max": 100, 
                    "min": 50
            }, 
            "ambiguous": {
                    "max": 40, 
                    "min": 10
            }, 
            "affirmative": {
                    "max": 0, 
                    "min": 0
            }
}


if __name__ == '__main__':
    mongo = connect()
    #all_files(mongo)
    all_formulas(mongo)
    print('Ok.')
