# Script for decoding of CSV-file with medical cards of patients and recording them to json files

import json
import sys
from mongodb import put

csv_file_name = 'cci/data/TrainingCases2016-11-16.txt' # CSV-file  
json_directory = 'cci/documents' # Directory for JSON-files and file dir.list with id of cards
print('Decoding of csv file "' + csv_file_name + '".')
try:
    f = open(csv_file_name,  'r')
except FileNotFoundError:
    print('File "' + csv_file_name + '" not found.')
    sys.exit()
else:
    ids = [] # List of id of cards
    #chf_file = open('cci/indexes/CHF-diagnosed.idx',  'w')
    chf_ids = []
    for line in f:
        card = line.split('\t')
        try:
            number_of_card = card[0]
            ids.append(int(number_of_card))
        except ValueError:
            # print('This is not a card of a patient.')
            continue
        else:
            print('Card #' + number_of_card)
            # Read every card and record to a dictionary  
            dict = {}
            key = ''
            for field in card[2:]:
                if field.isspace():  continue
                if key == '':
                    key = field
                else:
                    dict[key] = field
                    if key == "CHF - diagnosed":
                        chf_ids.append(number_of_card)
                    key = ''
            # Record dictionary to JSON-file
            json_file = open(json_directory + '/' + 'Doc' + number_of_card + '.json',  'w')
            json_file.write(json.dumps({'id' : int(number_of_card),  'data' : dict},  indent=4))
            json_file.close()
    # Record of id of cards
    f.close()
    ids.sort()
    id_file = open(json_directory + '/' + 'dir.list',  'w')
    for id in ids:
        id_file.write(str(id) + '\n')
    id_file.close()
    print(str(len(chf_ids))+ ' documents apriory have diagnosis CHF.')
    put('results_apriory',  chf_ids,  formula = 'CHF')
#    for id in chf_ids:
#        chf_file.write(str(id) + '\n')
#    chf_file.close()
print('OK.')
