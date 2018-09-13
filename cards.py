import os
import json
from lxml import etree

# This class finds all informaition about a card  
class CardHandler:
    dict = {}
    nodes = []
    key_words = ''
    def __init__(self, number_of_card):
        # Load JSON-file  
        json_file_name = 'cci/documents/Doc' + number_of_card + '.json'
        try:
            json_file = open(json_file_name,  'r')
        except IOError:
            print('No such file or directory: ' + json_file_name)
            return
        else:
            self.dict = json.loads(json_file.read())
            json_file.close()
        
        # Load DocNNN.html
        doc_name = 'cci/documents/Doc' + number_of_card + '.html'
        sHTML_Parser = etree.HTMLParser(remove_comments = True)
        try:
            with open(doc_name,  'rb') as inp:
                tree = etree.parse(inp, sHTML_Parser)
                self.nodes = tree.xpath('/html/body/p')
                self.size = os.path.getsize(doc_name)
        except IOError:
            print('No such file or directory: ' + doc_name)
            return None
        
        # Make a list of key words  
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
        keys = []
        for tax in taxes:
            try:
                taxes[tax] = open('cci/indexes/' + tax + '.idx')
            except IOError:
                print('No such file or directory: cci/indexes/' + tax + '.idx')
                continue
            else:
                for line in taxes[tax]:
                    if number_of_card == line.strip() != -1:
                            keys.append(tax)
                            break
                taxes[tax].close()
        self.key_words = ', '.join(keys)
