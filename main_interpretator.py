import re
import json
import sys
from lxml import etree
from mongodb import get
from mongodb import put
from mongodb import connect

#  Here there is an interpretator of JSON-code applying for decoding CHF.json  

#  Almost every function in this file has two arguments 'data' and 'dict'. 
#  Variable 'data' contains a part (a node) of JSON-code which is nessecent for the function.
#  Variable 'dict' contains a dictionary with results of annotating which is attached at every chunk.
#  All logic gunctions return 'True' or 'False'.
#  Functions annotating chuncks return new 'dict'.
#  The data about all chunks of a document is saved in variable 'doc_data'.


#  **************************************************************************
#  Functions which apply the interpretator or annotators for all documents, sentences, chunks
#  and steps of JSON-code
#  **************************************************************************


#def get_doc_data(snap_file_name):
#    try:
#        snap_file = open(snap_file_name,  'r')
#    except IOError:
#        print('No such file or directory: ' + snap_file_name)
#    else:
#        doc_data = json.loads(snap_file.read())
#        snap_file.close()
#        return doc_data

#  Apply the interpretator for a step 'step_id' of JSON-code in 'code_file_name'
#  for a document 'doc_file_name'. 'snap_file_name' is a snaphot file.
#  It's independent with 'def all_files'.
def next_step(code,  number_of_card,  step_id,  mongo):
#def next_step(doc_file_name,  code_file_name, snap_file_name, step_id):
    if step_id == 0:
        doc_data = create_dict(number_of_card,  mongo)
        doc_data = INA(doc_data)
        snapshot(number_of_card,  doc_data,  mongo)
    #doc_data = get_doc_data(snap_file_name)
    doc_data = get("snap.json",  number_of_card=number_of_card,  mongo=mongo)
    if doc_data is None:
        doc_data = create_dict(number_of_card,  mongo)
#    try:
#        code_file = open(code_file_name,  'r')
#    except IOError:
#        print('No such file or directory: ' + code_file_name)
#    else:
#        #level = 'entity'
#        code = json.loads(code_file.read())
#        code_file.close()
    for step in code['statements']:
        if 'statementId' in step and step['statementId'] == step_id:
            doc_data = json_interpretator(doc_data, number_of_card,  step,  mongo)
            break
    snapshot(number_of_card,  doc_data,  mongo)

#  Apply JSON-code for all documents in 'dir.list' and all steps of JSON-code.  
#  It's independent with 'def all_steps'.
def all_files(mongo):
    chf = []
    #chf_file = open('cci/indexes/ICHF.idx',  'w')
#    try:
#        id_file = open('cci/documents/dir.list', 'r')
#    except IOError:
#        print('No such file or directory: cci/documents/dir.list')
#    else:
#        for line in id_file:
#            number_of_card = line.strip()
    indexes = get("all_indexes",  mongo=mongo)
    for number_of_card in indexes:
        print('Card #' + number_of_card)
        doc_data = create_dict(number_of_card,  mongo)
        code = get("code.json", formula="CHF", mongo=mongo)
        all_steps(code, json_interpretator, doc_data, number_of_card,  mongo)
        if 'ICHF' in doc_data['data']:
            chf.append(number_of_card)
    #    id_file.close()
    put("calculated_indexes",  chf,  formula='CHF',  mongo=mongo)
    print(str(len(chf)) + ' documents were annotated by ICHF.')

#  Apply function 'annotator' for all sentence of a document. 'Par' is a tiple of parameters.  
def all_sentences(annotator,  doc_data,  *parp):
    for sentence in doc_data['sentences']:
        if 'reject' in sentence['data']:
            continue
        par = (parp[0],  sentence)
        annotator(par)

#  Apply function 'annotator' for all chunks of a document. 'Parp' is a tiple of parameters.  
def all_chunks(annotator,  doc_data, *parp):
    #  Annotate  
    if parp[0] == 'pipelink':
        for sentence  in doc_data['sentences']:
            for chunk in sentence['chunks']:
                par = parp[1:]
                res = annotator(chunk['text'],  par)
                chunk['data'].update(res)
    #  Find an annotation  
    else:
        for sentence  in doc_data['sentences']:
            for chunk in sentence['chunks']:
                dict = chunk['data']
                par = (parp[0],  dict)
                if 'reject' in dict:
                    continue
                new_dict = annotator(par)
                if new_dict is not None:
                    chunk = new_dict
    return doc_data

#  Apply 'interpretator' for all steps of JSON-code in 'json_file_name' for a document.
#  'snap_file' is a snapshot file.  
def all_steps(code,  interpretator,  doc_data,  number_of_card,  mongo):
#    try:
#        file = open(json_file_name,  'r')
#    except IOError:
#        print('No such file or directory: ' + json_file_name)
#    else:
#        #level = 'entity'
#        code = json.loads(file.read())
#        file.close()
        for step in code['statements']:
            interpretator(doc_data,  number_of_card, step,  mongo)


#  *****************************************************************
#  The interpretator and main steps of interpretating.  
#  *****************************************************************

#  The interpretator of step 'step' of JSON-code appying for a document ('doc-data').  
#  Snapshots are in 'snap-file'.  
def json_interpretator(doc_data,  number_of_card,  step,  mongo):
    if step['type'] == 'pipelink':
        new_doc_data = pipelink(step,  doc_data,  number_of_card,  mongo)
        if new_doc_data is not None:
            doc_data = new_doc_data
    elif step['type'] == 'statement':
        if step['level'] == 'entity':
            doc_data = all_chunks(statement,  doc_data,  step)
        elif step['level'] == 'sentence':
            all_sentences(statement,  doc_data,  step)
        else:
            par = (step,  doc_data)
            statement(par)
    elif step['type'] == 'aggregation':
        aggregation(step)
    elif step['type'] == 'entity_filter':
        entity_filter()
    else:
        print('Unknown type: ' + step['type'])
        sys.exit()
    return doc_data

#  All statements with type "pipelink" i.e. all shapsots and annotators  
def pipelink(step,  doc_data,  number_of_card,  mongo):
    if step['name'] == 'restrict entities':
        restrict_entities(step['arguments'])
    elif step['name'] == 'apply_sememes':
        return apply_sememes(step['arguments'][0],  doc_data,  mongo)
    elif step['name'] == 'IsNumericAnnotator':
        return INA(doc_data)
    elif step['name'] == 'RegExpAnnotator':
        return REA(step['data'],  doc_data)
    elif step['name'] == 'snapshot':
        snapshot(number_of_card,  doc_data,  mongo)
    elif step['name'] == 'watchpoint':
        watchpoint()
    elif step['name'] == 'IKAllEntitiesPlugin':
        IKA()
    else:
        print('Unknown command: ' + step['name'])
        sys.exit()

#  Conditional operator: if ... then ... .
def statement(par):
    cond = condition(par[0]['condition'], par[1])
    if cond:
        return action(par[0]['action'],  par[1])

#  Conditional operator 'if'. See 'def statement'.  
def condition(data,  dict):
    if data['type'] == 'operator':
        return operator(data,  dict)
    elif data['type'] == 'collectionOperator':
        return collection_operator(data,  dict)
    elif data['type'] == 'annotationData':
        return annotation_data(data, dict)
    elif data['type'] == 'const':
        return data['value']
    else:
        print('Condition: unknown type: ' + data['type'])
        sys.exit()

#  Action executed after conditional operator. See 'def statement'.
def action(data,  dict):
    if data['name'] == 'reject':
        d = {}
        d['reject'] = 'rejected'
        if 'data' in dict:
            return dict['data'].update(d)
        else:
            return dict.update(d)
    print(data['key'] )
    if 'chunks' in dict or 'sentences' in dict:
        d = {}
        d[data['key']] = data['key']
        for nd in data['annotationData']:
            d[nd] = data['annotationData'][nd]['value']
        dict['data'].update(d)
        return dict
    if data['name'] == 'annotate':
        d = {}
        d[data['key']] = data['key']
        for nd in data['annotationData']:
            d[nd] = data['annotationData'][nd]['value']
        dict.update(d)
        return dict

#  ******************************************************************
#  Logic operators
#  ******************************************************************

#  Distribute all logic operators.
def operator(data,  dict):
    if data['name'] == 'and':
        return conjunction(data['operands'],  dict)
    elif data['name'] == 'or':
        return disjunction(data['operands'],  dict)
    elif data['name'] == 'equals':
        return equals(data['operands'],  dict)
    elif data['name'] == 'less':
        return less(data['operands'],  dict)
    elif data['name'] == 'notless':
        return notless(data['operands'],  dict)
    elif data['name'] == 'greater':
        return greater(data['orpeands'],  dict)
    elif data['name'] == 'notgreater':
        return notgreater(data['operands'],  dict)
    else:
        print('Unknown operator: ' + data['name'])
        print(data)
        sys.exit()
        return None

#  'And'
def conjunction(data,  dict):
    res = True
    for operand in data:
        cond = condition(operand,  dict)
        if cond is None:
            return False
        res = res and cond
    return res

#  'Or'
def disjunction(data,  dict):
    res = False
    for operand in data:
        cond = condition(operand,  dict)
        if cond is None:
            return False
        res = res or cond

#  '='
def equals(data,  dict):
    a = condition(data[0],  dict)
    b = condition(data[1],  dict)
    if a is None or b is None:
        return False
    if a == b:
        return True
    else:
        return False

#  '<'
def less(data,  dict):
    a = condition(data[0],  dict)
    b = condition(data[1],  dict)
    if a is None or b is None:
        return False
    try:
        if int(a) < int(b):
            return True
        else:
            return False
    except TypeError:
        print('TypeError: ' + str(a) + ' < ' + str(b))
        sys.exit()

#  '>='
def notless(data,  dict):
    a = condition(data[0],  dict)
    b = condition(data[1],  dict)
    if a is None or b is None:
        return False
    try:
        if int(a) >= int(b):
            return True
        else:
            return False
    except TypeError:
        print('TypeError: ' + str(a) + ' >= ' + str(b))

#  '>'
def greater(data,  dict):
    return not notless(data,  dict)

#  '<='
def notgreater(data,  dict):
    return not less(data,  dict)

#  ****************************************************************
#  Other functions.
#  ****************************************************************

#  Boundary of used chunks in one file. Not finished.
#  It's absent in CHF.json.
def restrict_entities(data):
    print('Annotator: restrict entities.')

#  Start annotator of taxonomies for all chunks in a document.  
def apply_sememes(data,  doc_data,  mongo):
    for tax in data['value']:
        doc_data = all_chunks(taxonomy,  doc_data,  'pipelink',  tax,  mongo)
    return doc_data

#  Start numeric annotator for all chunks in a document.  
def INA(doc_data):
    return all_chunks(IsNumericAnnotator,  doc_data,  'pipelink')
    
#  Start regular expression annotator for all chunks in a document.  Not finished.
#  It's absent in CHF.json.
def REA(data,  dict):
    return RegExpAnnotator(dict['text'],  dict['data']['pattern'])

#  New level.  
def aggregation(data):
    return data['level']

#  A filter...  Not finished.
def entity_filter():
    pass

#  IKAllEntitiesPlugin... What is it? Not finished.  
def IKA():
    pass

#   Find an information about a chunk or sentence
def collection_operator(data,  dict):
    #  For all chunks which has a key.  
    if data['name'] == 'forSome':
        if data['key'] in dict:
            return operator(data['condition'],  dict)
        else:
            return False
    #  For all chunks which has not a key.  
    elif data['name'] == 'forNone':
        if data['key'] in dict:
            if 'condition' in data:
                return not operator(data['condition'],  dict)
            else:
                return False
        else:
            return True
    #  For all sentences. Returns count of chunks with a key.
    elif data['name'] == 'count':
        n = 0;
        if 'chunks' in dict:
            for chunk in dict['chunks']:
                if 'condition' in data:
                    if data['key'] in chunk['data'] and condition(data['condition'],  chunk['data']):
                        n += 1
                else:
                    if data['key'] in chunk['data']:
                        n += 1
            return n
        else:
            for sentence in dict['sentences']:
                if 'condition' in data:
                    if data['key'] in sentence['data'] and condition(data['condition'],  sentence['data']):
                        n += 1
                else:
                    if data['key'] in sentence['data']:
                        n += 1
            return n
    else:
        print('Unknown name: ' + data['name'])
        sys.exit()
        return None

#  Returns an annotation of a chunk.
def annotation_data(data,  dict):
#    if data['name'] in dict:
#        return dict[data['name']]
#    low = data['name'].lower()
#    print('low:' + low)
#    if low in dict:
#        return dict[low]
#    print('No')
    for key in dict:
        if data['name'].lower() == key.lower():
            return dict[key]

#  **************************************************************
#  Snapshots etc.
#  **************************************************************

#  Save all results about a document in file 'file_name'. 
def snapshot(number_of_card,  doc_data,  mongo):
    #file = json.dumps(doc_data,  indent = 4)
    put("snap.json",  doc_data,  number_of_card=number_of_card,  mongo=mongo)
#    try:
#        file = open(file_name,  'w')
#    except IOError:
#        print('No such file or directory: ' + file_name)
#    else:
#        file.write(json.dumps(doc_data,  indent = 4))
#        file.close()

#  It's like a snapshot. But I don't know the difference. Not finished.
def watchpoint():
    pass

#  **************************************************************
#  Annotators.
#  **************************************************************

def is_word(term,  text):
    text_low = text.lower()
    term_low = term.lower()
    if text_low.find(term_low) == -1:
        return False
    w_text = re.findall(r'\w+',  text_low)
    w_term = re.findall(r'\w+',  term_low)
    for word in w_term:
        if word not in w_text:
            return False
    return True

#  Apply a taxonomy 'tax' for chunk 'text'. 'Par' is a tiple of parameters.  
def taxonomy(text,  par):
    tax = par[0]
    mongo = par[1]
    dict = {}
    filtre = re.compile("\s+", re.M + re.I + re.U)
    tax_file = get("tax.tset",  taxonomy=tax,  mongo=mongo).split('\n')
#    file = 'cci/taxonomies/' + tax + '.tset'
#    try:
#        tax_file = open(file,  'r')
#    except IOError:
#        print('No such file: ' + file)
#        return {}
#    else:
    for line in tax_file:
        if line == "" or line[0] != '"':
            continue
        words = line.split('"')
        triped_text = filtre.sub(' ',  text)
        triped_word = filtre.sub(' ',  words[1])
        if is_word(triped_word,  triped_text):
            dict[tax] = text
            flag = True
            key = ''
            for word in words[2:]:
                if flag:
                    flag = False
                    continue
                flag = True
                if key == '':
                    key = filtre.sub(' ',  word)
                else:
                    dict[key] = filtre.sub(' ',  word)
                    key = ''
    return dict

#  Apply numeric annotator for chunk 'text'. 'Par' is a tiple of parameters.  
def IsNumericAnnotator(text,  par):
    dict = {}
    # In 'text' there is a number  
    result = re.search(r'\d',   text)
    if result is None:
        # There are text only  
        res = re.search(r'[A-z]+',  text)
        if res is not None and res.group(0) == text:
            dict['class'] = 'numeric'
            dict['type'] = 'text'
            dict['value'] = text
        return dict
    dict['class'] = 'numeric'
    # It is a number
    if re.search(r'[A-z]',  text) is None:
        dict['type'] = 'number'
        dict['value'] = text
        return dict
    #  It's not a number but contains a number  
    else:
        dict['type'] = 'contains_number'
        dict['value'] = result.group(0)
        # Find a measure
        try:
            tax_file_name = 'cci/taxonomies/DOSAGE.tset'
            tax_file = open(tax_file_name,  'r')
        except IOError:
            print('No such file: ' + tax_file)
            return
        else:
            filtre = re.compile("\s+", re.M + re.I + re.U)
            for line in tax_file:
                if line[0] != '"':
                    continue
                words = line.split('"')
                end = result.end()
                triped_text = filtre.sub(' ',  text[end:])
                triped_word = filtre.sub(' ',  words[1])
                #if  triped_text.find(triped_word) != -1:
                if is_word(triped_word,  triped_text):
                    dict['measure'] = triped_word
        return dict

#  Apply regular expression 'pattern' for 'text'.  
def RegExpAnnotator(text,  pattern):
    dict = {}
    result = re.search(pattern,  text)
    if result is not None:
        dict['pattern'] = pattern
        return dict

#  *******************************************************************
#  Other.
#  *******************************************************************

#  Represent a document to a list 'doc_data' of sentences. Every sentence is a list of chunks.
#  Every chunk is a dictionary:
#
#  text: 'chunk'
#  data: '{key: value, ... }
#
#  Attribute 'data' is empty.  
def create_dict(number_of_card,  mongo):
    doc_data = {}
    doc_data['data'] = {}
    doc_data['sentences'] = []
    sHTML_Parser = etree.HTMLParser(remove_comments = True)
#    try:
#        inp = open(file_name,  'rb')
#    except IOError:
#        print('No such file or directory: ' + file_name)
#        return None
#    else:
#        doc = etree.parse(inp, sHTML_Parser)
    samples = get("doc.html",  number_of_card=number_of_card,  mongo=mongo)
        #for sample in doc.xpath('/html/body/p'):
    for node in samples:
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
    return doc_data


#  *************************************************

if __name__ == '__main__':
    mongo = connect()
    # json_file_name = 'cci/rules/CHF.json'
    all_files(mongo)
    print('Ok.')
