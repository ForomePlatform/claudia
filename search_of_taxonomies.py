import re
import json
from lxml import etree

# Find medical terms in documents  

# A dictionary written like {taxonomy : id of file with result of search} 
taxes = {
            'Cardio-Loc': None, 
            'CHF-Words': None, 
            'DECLINE': None, 
            'dementia': None, 
            'MentalStatus': None, 
            'MI-Words': None, 
            'PVD-Words': None, 
            'FAMILY': None
            }

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
    



# Main dictionary used in order to find taxonomies in documents  
dict = {}
filtre = re.compile("\s+", re.M + re.I + re.U)
sHTML_Parser = etree.HTMLParser(remove_comments = True)
for tax in taxes:
    # Make dictionary 'dict'  
    print('tax: ',  tax)
    try:
        inp = open('cci/taxonomies/' + tax + '.tset',  'r')
    except IOError:
        print('No such file or directory: ' + tax + '.tset')
        continue
    else:
        for line in inp:
            if line[0] != '"':
                continue
            words = line.split('"')
            word = filtre.sub(' ', words[1])
            dict[word] = tax
        inp.close()
    # Open files where we will save the results of search
    try:
        taxes[tax] = open('cci/indexes/' + tax + '.idx',  'w')
    except IOError:
        print('No such directory: cci/indexes')
        continue

# Save the dictionary like JSON-file  
try:
    json_file = open('cci/taxonomies/dict.json',  'w')
except IOError:
    print('No such directory: cci/taxonomies')
else:
    json_file.write(json.dumps(dict,  indent = 4))
    json_file.close()

# Research of documents  
try:
    id_file = open('cci/documents/dir.list', 'r')
except IOError:
    print('No such file or directory: cci/documents/dir.list')
else:
    for line in id_file:
        number_of_card = int(line.strip())
        
        #if number_of_card != 9:
        #   continue
        
        print('Finding in file "Doc' + str(number_of_card) + '.html"')
        doc_name = "cci/documents/Doc" + str(number_of_card) + ".html"
        try:
            inp = open(doc_name,  'rb') 
        except IOError:
            print('No such file or directory: cci/documents/dir.list')
        else:
            doc = etree.parse(inp, sHTML_Parser)
            last = set()
            for term in dict:
                if dict[term] in last:
                    continue
                for nd in doc.xpath('/html/body/p/span/span/span/span'):
                    s = filtre.sub(' ',  nd.text)
                    #if s.find(term) != -1:
                    if term == 'family' and number_of_card == 239:
                        print(s,  is_word(term,  s))
                    if is_word(term,  s):
                        # Save a result  
                        if number_of_card == 239:
                            print('Card #239: term=' + term + ', s=' + s)
#                        if term == 'chf' or term == 'heart failure' or term == 'heartfailure':
#                            print('Stop, CHF!')
#                        if term == "ejection fraction":
#                            print('Stop, EF!')
                        taxes[dict[term]].write(str(number_of_card) + '\n')
                        last.add(dict[term])
                        break
            inp.close()
    id_file.close()

for tax in taxes:
    taxes[tax].close()
print('OK.')
