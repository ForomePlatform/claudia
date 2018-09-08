import re
import json
from lxml import etree
from mongodb import get
from mongodb import put

from mongodb import connect
from main_interpretator import create_dict
from annotators import IsNumericAnnotator

#  There are certain annotators and a 'baby version' of JSON-interpretator.  

#  Apply regular expression 'pattern' for 'text'.  
def RegExpAnnotator(text,  pattern):
    dict = {}
    result = re.search(pattern,  text)
    if result is not None:
        dict['pattern'] = pattern
        return dict


#  If 'text' is a text, a number or a fragment with a number,  
#  returns a dictionary 'dict' with lebels..
#def IsNumericAnnotator(text):
#    dict = {}
#    # There exists a number  
#    result = re.search(r'\d',   text)
#    if result is None:
#        # There are text only  
#        result = re.search(r'[A-z]+',  text)
#        if result is not None and result.group(0) == text:
#            dict['class'] = 'numeric'
#            dict['type'] = 'text'
#            dict['value'] = text
#        return dict
#    dict['class'] = 'numeric'
#    if re.search(r'[A-z]',  text) is None:
#        dict['type'] = 'number'
#        dict['value'] = text
#        return dict
#    else:
#        dict['type'] = 'contains_number'
#        dict['value'] = re.search(r'\d',   text)
#        return dict

# Find 'term' in 'text' and check that 'term' is a word, not a part of a word
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

# Apply taxonomy 'tax' for 'text'  
def taxonomy(text,  tax,  mongo):
    dict = {}
    filtre = re.compile("\s+", re.M + re.I + re.U)
#    file_name = 'cci/taxonomies/' + tax + '.tset'
#    try:
#        tax_file = open(file_name,  'r')
#    except IOError:
#        print('No such file: ' + file_name)
#        return {}
#    else:
    tax_file = get("tax.tset",  taxonomy=tax,  mongo=mongo)
    lines = tax_file.split('\n')
    for line in lines:
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
#        tax_file.close()
    return dict

#  'Baby version' of the interpretator. It was realised for SimpleRule1.json.  
def json_interpretator(json_file_name):
    try:
        file = open(json_file_name,  'r')
    except IOError:
        print('No such file or directory: ' + json_file_name)
    else:
        code = json.loads(file.read())
        file.close()
        try:
            id_file = open('cci/documents/dir.list', 'r')
        except IOError:
            print('No such file or directory: cci/documents/dir.list')
        else:
            for line in id_file:
                number_of_card = line.strip()
                file_name = "cci/documents/Doc" + number_of_card + ".html"
                print('File: ' + file_name)
                # file_name = code['context']['domainID']
                sHTML_Parser = etree.HTMLParser(remove_comments = True)
                try:
                    inp = open(file_name,  'rb')
                except IOError:
                    print('No such file or directory: ' + file_name)
                    return
                else:
                    doc = etree.parse(inp, sHTML_Parser)
                    top = 0
                    nchunk = 0
                    chunks = []
                    for sample in doc.xpath('/html/body/p'):
                        sentence = []
                        s = etree.tostring(sample)
                        ss = etree.fromstring(s)
                        for nd in ss.xpath('/p/span/span/span/span'):
                            if nchunk > top:
                                break
                            nchunk += 1
                            chunk = {}
                            chunk['text'] = nd.text
                            dict = {}
                            for step in code['statements']:
                                if 'name' in step:
                                    if step['name'] == 'restrict entities':
                                        top = step['arguments'][0]['value']['value']
                                    elif step['name'] == 'apply_sememes':
                                        # for tax in step['arguments'][0]['value']:
                                        for tax in taxes:
                                            dict.update(taxonomy(nd.text, tax))
                                    elif step['name'] == 'IsNumericAnnotator':
                                        dict.update(IsNumericAnnotator(nd.text))
                                    elif step['name'] == 'RegExpAnnotator':
                                        for arg in step['arguments']:
                                            if arg['name'] == 'Pattern':
                                                pattern = arg['value']['value']
                                                if RegExpAnnotator(nd.text,  pattern) is not None:
                                                    dict.update(RegExpAnnotator(nd.text,  pattern))
                            chunk['data'] = dict
                            sentence.append(chunk)
                        chunks.append(sentence)
                    inp.close()
                    
                    file_name = 'cci/chunks/ch' + number_of_card + '.json'
                    try:
                        file = open(file_name,  'w')
                    except IOError:
                        print('No such directory: ' + file_name)
                        return
                    else:
                        file.write(json.dumps(chunks,  indent = 4))
                    file.close()


if __name__ == '__main__':
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
    



    mongo = connect()
    indexes = get("all_indexes",  mongo=mongo)
    for number_of_card in indexes:
        print("Card: " + number_of_card)
        doc_data = create_dict(number_of_card,  mongo)
        for sentence in doc_data["sentences"]:
            for chunk in sentence["chunks"]:
                par = (mongo, )
                for tax in taxes:
                    chunk["data"].update(taxonomy(chunk["text"],  tax,  mongo))
                chunk["data"].update(IsNumericAnnotator(chunk["text"],  par))
        put("ch.json",  doc_data,  number_of_card=number_of_card,  mongo=mongo)
    print('Ok.')
