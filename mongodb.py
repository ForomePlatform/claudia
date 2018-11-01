import os
import sys
import json
from lxml import etree
from cards import CardHandler
from pymongo import MongoClient
from pymongo import errors

taxes = [
            'Cardio-Loc', 
            'CHF-Words', 
            'DECLINE', 
            'dementia', 
            'MentalStatus', 
            'MI-Words', 
            'PVD-Words', 
            'FAMILY', 
            'DOSAGE', 
            'FREQUENCY', 
            'METHOD'
            ]

# Connect to MongoDB
def connect():
    mongo = MongoClient(host="localhost",  port  = 27017, connect=False)
    try: 
        mongo.admin.command("ismaster") 
    except errors.ServerSelectionTimeoutError: 
        print("DataBase not available: could not connect to MongoDB")
        sys.exit(1)
#    else:
#        print('Database connection successfully')
    return mongo

def load_doc(dataset,  id,  mongo):
    print('Update document #' + id + ' from "' + dataset + '".')
    dbh = mongo[dataset]
    doc = {}
    # initial
    doc['id'] = id
    card = CardHandler(dataset, id)
    doc['patient'] = 'patient_' + id
    doc['html'] = []
    # Find the longest sentence
    max_nd = 0
    max_len = 0
    for nd in card.nodes:
        s = etree.tostring(nd)
        doc['html'].append(s)
        if len(s) > max_len and doc['html'][0] !=s:
            max_len = len(s)
            max_nd = doc['html'].index(s)
    if max_len != 0:
        sentence = etree.fromstring(doc['html'][max_nd])
        text = ''
        for nd in sentence.xpath('/p/span/span/span/span'):
            text += ' ' + nd.text
    else:
        text = 'No information'
    doc['abstract'] = text[0:100]
    doc['size'] = len(doc['html'])
    q = {"$set":  {key: doc[key] for key in doc}}
    dbh.initial_docs.update({'id': id,  'patient': doc['patient']},  q, upsert=True)
    
    # claculated
#    if dataset != 'cci':
#        return
    doc = {}
    doc['id'] = id
    doc['patient'] = 'patient_' + id
    
    file = card.dict
    doc['json'] = json.dumps(file)
    doc['key_words'] = [] #card.key_words.split(', ')
    
    q = {"$set":  {key: doc[key] for key in doc}}
    dbh.calculated_docs.update({'id': doc['id'],  'patient': doc['patient']},  q, upsert=True)

def update(mongo):
    # Add documents to the base
    datasets = [
                'cci', 
                'nets', 
                'medications'
                ]
    for ds in datasets:
        dbh = mongo[ds]
        
#    indexes_file_name = 'cci/documents/dir.list'
#    try:
#        indexes_file = open(indexes_file_name,  'r')
#    except IOError:
#        print('No such file or directory: ' + indexes_file_name)
#        return -1
#    else:
#        for line in indexes_file:
#            id = line.strip()
        indexes = get('all_indexes',  dataset=ds,  from_file=True)
        print('indexes: ' + str(len(indexes)))
        for id in indexes:
            load_doc(ds,  id,  mongo)
            
            # patients
            patient = {}
            patient['name'] = 'patient_' + id
            
            q = {"$set":  {key: patient[key] for key in patient}}
            dbh.patients.update({'name': patient['name']},  q,  upsert=True)

    dbh.dir.insert({})
    
    # Add taxonomies to the base
    for tax in taxes:
        taxonomy = {}
        taxonomy['taxonomy'] = tax

        q = {"$set": {key: taxonomy[key] for key in taxonomy}}
        dbh.indexes.update({'taxonomy': tax},  q,  upsert=True)
        print('Update taxonomy "' + tax + '".')

    dbh = mongo["claudia"]
    for tax in taxes:
        taxonomy = {}
        taxonomy['taxonomy'] = tax
        taxonomy['tset'] = get("tax.tset",  taxonomy=tax,  from_file=True)
        
        q = {"$set": {key: taxonomy[key] for key in taxonomy}}
        dbh.taxonomies.update({'taxonomy': tax},  q,  upsert=True)
        print('Update taxonomy "' + tax + '".')
    
    formula ={}
    formula['formula'] = 'CHF'
    formula['version'] = 0
    formula['hsir'] = get("code.hsir",  from_file=True)
    formula['json'] = json.dumps(get("code.json",  from_file=True))
    q = {"$set": {key: formula[key] for key in formula}}
    dbh.formulas.update({"formula": "CHF"},  formula, upsert=True)
    

# Get arbitrary file from the database or form a file (if 'from_file' is True)
def get(type, number_of_card="0",  taxonomy ="None",  
            from_file=False, formula="None", base="",  
            dataset='cci',  mongo=None):
    if from_file:
        if type == "doc.html":
            card = CardHandler(dataset,  number_of_card)
            nodes = []
            for nd in card.nodes:
                nodes.append(etree.tostring(nd))
            return nodes
        elif type == "doc.json":
            card = CardHandler(dataset,  number_of_card)
            return card.dict
        elif type == "key_words":
            card = CardHandler(dataset,  number_of_card)
            return card.key_words.split(', ')
        elif type == "ch.json":
            file_name = 'cci/chunks/ch' + number_of_card + '.json'
            file_name = base + file_name
            try:
                file = open(file_name,  'r')
            except IOError:
                print('No such directory: ' + file_name)
                return
            else:
                chunks = file.read()
                file.close()
                return chunks
        elif type == "snap.json":
            snap_file_name = 'cci/snapshots/snap' + number_of_card + '.json'
            snap_file_name = base + snap_file_name
            try:
                snap_file  = open(snap_file_name,  'r')
            except IOError:
                print('No such file or directory: ' + snap_file_name)
                return
            else:
                return snap_file.read()
        elif type == "tax.tset":
            tax_file_name = dataset + '/taxonomies/' + taxonomy + '.tset'
            tax_file_name = base + tax_file_name
            try:
                tax_file  = open(tax_file_name,  'r')
            except IOError:
                print('No such file or directory: ' + tax_file_name)
                return
            else:
                res = tax_file.read()
                tax_file.close()
                return res
        elif type == "tax.idx":
            tax_file_name = dataset + '/indexes/' + taxonomy + '.idx'
            tax_file_name = base + tax_file_name
            try:
                tax_file  = open(tax_file_name,  'r')
            except IOError:
                print('No such file or directory: ' + tax_file_name)
                return
            else:
                dict = []
                for line in tax_file:
                    dict.append(line.strip())
                tax_file.close()
                return dict
        elif type == "code.hsir":
            code_file_name = dataset + '/rules/CHF.hsir'
            code_file_name = base + code_file_name
            try:
                code_file  = open(code_file_name,  'r')
            except IOError:
                print('No such file or directory: ' + code_file_name)
                return
            else:
                code = code_file.read()
                code_file.close()
                return code
        elif type == "code.cla":
            code_file_name = dataset + '/claudia_rules/' + formula + '.cla'
            code_file_name = base + code_file_name
            try:
                code_file  = open(code_file_name,  'r')
            except IOError:
                print('No such file or directory: ' + code_file_name)
                return
            else:
                code = code_file.read()
                code_file.close()
                return code
        elif type == "code.json":
            code_file_name = dataset + '/rules/CHF.json'
            code_file_name = base + code_file_name
            try:
                code_file  = open(code_file_name,  'r')
            except IOError:
                print('No such file or directory: ' + code_file_name)
                return
            else:
                code = json.loads(code_file.read())
                code_file.close()
                return code
        elif type == "all_indexes":
            path = base + dataset + '/documents'
            files = os.listdir(path)
            indexes = []
            for file in files:
                if file[-5:] != '.html':
                    continue
                id = file[3:-5]
                indexes.append(int(id))
            indexes.sort()
            ids = [str(n) for n in indexes]
            return ids
#            try:
#                id_file = open(base + 'cci/documents/dir.list', 'r')
#            except IOError:
#                print('No such file or directory: cci/documents/dir.list')
#            else:
#                indexes = []
#                for line in id_file:
#                    number_of_card = line.strip()
#                    indexes.append(number_of_card)
#                return indexes
        elif type == "results_apriory":
            try:
                id_file = open(base + dataset + '/indexes/' + formula + '-diagnosed.idx' , 'r')
            except IOError:
                print('No such file or directory: ' + base + dataset + '/indexes/' + formula + '-diagnosed.idx')
            else:
                indexes = []
                for line in id_file:
                    number_of_card = line.strip()
                    indexes.append(number_of_card)
                return indexes
        elif type == "steps.json":
            try:
                steps_file = open(base + dataset + '/viewer/steps.json' , 'r')
            except IOError:
                print('No such file or directory: ' +base + dataset + '/viewer/steps.json')
            else:
                steps = json.loads(steps_file)
                return steps
        elif type == "size_of_doc":
            card = CardHandler(dataset,  number_of_card)
            return card.size

    else:
        if mongo is None:
            return
        if type == "doc.html":
            dbh = mongo[dataset]
            doc = dbh.initial_docs.find_one({"id": number_of_card})
            return doc['html']
        elif type == "doc.json":
            dbh = mongo[dataset]
            doc = dbh.calculated_docs.find_one({"id": number_of_card})
            return json.loads(doc['json'])
        elif type == "key_words":
            dbh = mongo[dataset]
            doc = dbh.calculated_docs.find_one({"id": number_of_card})
            return doc["key_words"]
        elif type == "ch.json":
            dbh = mongo[dataset]
            doc = dbh.calculated_docs.find_one({"id": number_of_card})
            return json.loads(doc["chunks"])
        elif type == "snap.json":
            dbh = mongo[dataset]
            doc = dbh.calculated_docs.find_one({"id": number_of_card})
            return doc["snapshot"]
        elif type == "tax.tset":
            dbh = mongo["claudia"]
            tax = dbh.taxonomies.find_one({"taxonomy": taxonomy})
            return tax['tset']
        elif type == "tax.idx":
            dbh = mongo[dataset]
            tax = dbh.indexes.find_one({"taxonomy": taxonomy})
            return tax['idx']
        elif type == "code.hsir":
            dbh = mongo["claudia"]
            form = dbh.formulas.find_one({"formula": formula})
            return form["hsir"]
        elif type == "code.cla.json":
            dbh = mongo["claudia"]
            form = dbh.formulas.find_one({"formula": formula})
            return json.loads(form["cla_json"])
        elif type == "code.json":
            dbh = mongo["claudia"]
            form = dbh.formulas.find_one({"formula": formula})
            return json.loads(form["json"])
        elif type == "all_indexes":
            dbh = mongo[dataset]
            indexes = dbh.initial_docs.distinct('id')
            return indexes
        elif type == "calculated_indexes":
            dbh = mongo[dataset]
            indexes = dbh.formula_results.find_one({"formula": formula})
            return indexes["indexes"]
        elif type.split('.')[0] == "results_apriory":
            key = type.split('.')[1]
            dbh = mongo[dataset]
            results = dbh.results_apriory.find_one({"formula": formula},  {key: True})
            if results is None:
                return []
            else:
                return results[key]
        elif type == "steps.json":
            dbh = mongo[dataset]
            results = dbh.steps.find_one({"formula": formula})
            return results["indexes"]
        elif type == "annotations":
            dbh = mongo[dataset]
            annotations = dbh.calculated_docs.find_one({'id': number_of_card})
            return annotations["annotations"]
        elif type == "size_of_doc":
            dbh = mongo[dataset]
            size = dbh.initial_docs.find_one({'id': number_of_card},  {'size': True})
            return size['size']
        elif type == "abstract":
            dbh = mongo[dataset]
            abstract = dbh.initial_docs.find_one({'id': number_of_card}, {'abstract': True})
            return abstract['abstract']

# Put any file to the database
def put(type, file,  number_of_card="0",  taxonomy="None", 
                formula="None",  dataset = 'cci',  mongo=None):
    if type == "doc.html":
        key = 'html'
        dbh = mongo[dataset]
        q = {"$set":  {key: file}}
        dbh.initial_docs.update({'id': number_of_card},  q,  upsert=True)
    elif type == "doc.json":
        key = 'json'
        dbh = mongo[dataset]
        q = {"$set":  {key: json.dumps(file)}}
        dbh.calculated_docs.update({'id': number_of_card},  q,  upsert=True)
    elif type == "ch.json":
        key = 'chunks'
        dbh = mongo[dataset]
        q = {"$set":  {key: json.dumps(file)}}
        dbh.calculated_docs.update({'id': number_of_card},  q,  upsert=True)
    elif type == "snap.json":
        key = 'snapshot'
        dbh = mongo[dataset]
        q = {"$set":  {key: file}}
        dbh.calculated_docs.update({'id': number_of_card},  q,  upsert=True)
    elif type == "tax.tset":
        key = 'tset'
        dbh = mongo["claudia"]
        q = {"$set":  {key: file}}
        dbh.taxonomies.update({'taxonomy': taxonomy},  q,  upsert=True)
    elif type == "tax.idx":
        key = 'idx'
        dbh = mongo[dataset]
        q = {"$set":  {key: file}}
        dbh.indexes.update({'taxonomy': taxonomy},  q,  upsert=True)
    elif type == "code.hsir":
        key = 'hsir'
        dbh = mongo["claudia"]
        q = {"$set":  {key: file}}
        dbh.formulas.update({'formula': formula},  q,  upsert=True)
    elif type == "code.json":
        key = 'json'
        dbh = mongo["claudia"]
        q = {"$set":  {key: file}}
        dbh.formulas.update({'formula': formula},  q,  upsert=True)
    elif type == "code.cla.json":
        key = 'cla_json'
        dbh = mongo["claudia"]
        q = {"$set":  {key: json.dumps(file)}}
        dbh.formulas.update({'formula': formula},  q,  upsert=True)
    elif type == "calculated_indexes":
        key = 'indexes'
        dbh = mongo[dataset]
        q = {"$set":  {key: file}}
        dbh.formula_results.update({'formula': formula},  q,  upsert=True)
    elif type == "results_apriory":
        dbh = mongo[dataset]
        for key in file:
            q = {"$set":  {key: file[key]}}
            dbh.results_apriory.update({'formula': formula},  q,  upsert=True)
    elif type == "steps.json":
        key = 'indexes'
        dbh = mongo[dataset]
        q = {"$set":  {key: file}}
        dbh.steps.update({'formula': formula},  q,  upsert=True)
    elif type == "annotations":
        key = 'annotations'
        dbh = mongo[dataset]
        q = {"$set":  {key: file}}
        dbh.calculated_docs.update({'id': number_of_card},  q,  upsert=True)
    elif type == "key_words":
        key = 'key_words'
        dbh = mongo[dataset]
        q = {"$set":  {key: file}}
        dbh.calculated_docs.update({'id': number_of_card},  q,  upsert=True)

