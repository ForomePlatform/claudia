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
    #mongo=par[0]
    dict = {}
    # In 'text' there is a number  
    result = re.search(r'\d',   text)
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
    if re.search(r'[A-z]',  text) is None:
        dict['type'] = 'number'
        dict['value'] = text
        return dict
    #  It's not a number but contains a number  
    else:
        dict['type'] = 'contains_number'
        dict['value'] = result.group(0)
        # Find a measure
        tax_file = get("tax.tset", taxonomy="DOSAGE", mongo=mongo).split('\n')
        filtre = re.compile("\s+", re.M + re.I + re.U)
        for line in tax_file:
            if line == "" or line[0] != '"':
                continue
            words = line.split('"')
            end = result.end()
            triped_text = filtre.sub(' ',  text[end:])
            triped_word = filtre.sub(' ',  words[1])
            if is_word(triped_word,  triped_text):
                dict['measure'] = triped_word
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
