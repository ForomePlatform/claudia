import re

from mongodb import get

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
def taxonomy(text,  tax,  mongo):
    #tax = par[0]
    #mongo = par[1]
    dict = {}
    filtre = re.compile("\s+", re.M + re.I + re.U)
    tax_file = get("tax.tset",  taxonomy=tax,  mongo=mongo).split('\n')
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
def IsNumericAnnotator(text,  mongo):
    dict = {}
    # Find a measure
    tax_file = get("tax.tset", taxonomy="DOSAGE", mongo=mongo).split('\n')
    filtre = re.compile("\s+", re.M + re.I + re.U)
    for line in tax_file:
        if line == "" or line[0] != '"':
            continue
        words = line.split('"')
        #end = result.end()
        triped_text = filtre.sub(' ',  text)
        triped_word = filtre.sub(' ',  words[1])
        #if is_word(triped_word,  triped_text):
        pos = triped_text.find(triped_word)
        neib = triped_text[pos-1:pos] + triped_text[pos + len(triped_word) : pos+1 + len(triped_word)]
        nn = re.findall(r'[A-z]',  neib)
        if pos != -1 and nn == []:
            #print('Triped_text: ' + triped_text + ', triped_word: ' + triped_word)
            dict['measure'] = triped_word
    
    # In 'text' there is a number  
    result = re.search(r"[-+]?\d*\.\d+|\d+",   text)
    if result is None:
        # There are text only  
#        res = re.search(r'[A-z]+',  text)
#        if res is not None and res.group(0) == text:
#            dict['class'] = 'numeric'
#            dict['type'] = 'text'
#            dict['value'] = text
        return dict
    dict['class'] = 'numeric'
    # It is a number
    #if re.search(r'[A-z]',  text) is None:
    if result.group(0) == text:
        dict['type'] = 'number'
        dict['value'] = float(result.group(0))
        return dict
    #  It's not a number but contains a number  
    else:
        dict['type'] = 'contains_number'
        dict['value'] = float(result.group(0))
        #print('INA: text=' + text + ', number=' + str(result.group(0)))
        return dict

#  Apply regular expression 'pattern' for 'text'.  
def RegExpAnnotator(text,  pattern):
    #print('pattern: ' + str(pattern))
    #print('text: ' + str(text))
    dict = {}
    result = re.search(pattern,  text)
    if result is not None:
        dict['pattern'] = pattern
    return dict
