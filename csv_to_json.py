# Script for decoding of CSV-file with medical cards of patients and recording them to json files
import sys
from mongodb import put
from mongodb import connect

apriory = [
            'not mentioned', 
            'ambiguous',
            'diagnosed', 
            'inconclusive', 
            'ruled out', 
            'symptoms present', 
            'other'
            ]

def csv_to_json(mongo):
    csv_file_name = 'cci/data/TrainingCases2016-11-16.txt' # CSV-file  
    #json_directory = 'cci/documents' # Directory for JSON-files and file dir.list with id of cards
    print('Decoding of csv file "' + csv_file_name + '".')
    try:
        f = open(csv_file_name,  'r')
    except IOError:
        print('File "' + csv_file_name + '" not found.')
        sys.exit()
    else:
        ids = [] # List of id of cards
        chf_ids = {}
        for stat in apriory:
            chf_ids[stat] = []
        for line in f:
            card = line.split('\t')
            try:
                number_of_card = card[0]
                ids.append(int(number_of_card))
            except ValueError:
                continue
            else:
                print('Card #' + number_of_card)
                # Read every card and record to a dictionary  
                dict = {}
                key = ''
                h = True
                for field in card[2:]:
                    if field.isspace():  continue
                    if key == '':
                        key = field
                    else:
                        dict[key] = field
                        if key[0:3] == "CHF":
                            h = False
                            for stat in apriory:
                                if key.find(stat) != -1:
                                    chf_ids[stat].append(number_of_card)
                                    break
                        key = ''
                if h:
                    print(number_of_card)
                # Record dictionary to JSON-file
                put("doc.json", dict, number_of_card=number_of_card,  mongo=mongo)
        # Record of id of cards
        f.close()
        ids.sort()
        #print(str(len(chf_ids))+ ' documents apriory have diagnosis CHF.')
        put('results_apriory',  chf_ids,  formula = 'CHF',  mongo=mongo)

if __name__ == '__main__':
    mongo = connect()
    csv_to_json(mongo)
    print('OK.')
