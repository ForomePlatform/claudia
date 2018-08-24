import sys
import json
from lxml import etree
from cards import CardHandler
from pymongo import MongoClient

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

# Connect to MongoDB
def connect():
    try:
        #c = Connection(host="localhost",  port  = 27017)
        mongo = MongoClient(host="localhost",  port  = 27017)
        print('Connection successfully')
    except Exception:
        print("Could not connect to MongoDB")
        sys.exit(1)
    return mongo

def update(mongo):
    # Add documents to the base
    dbh = mongo["DataSet_test"]
    indexes_file_name = 'cci/documents/dir.list'
    try:
        indexes_file = open(indexes_file_name,  'r')
    except IOError:
        print('No such file or directory: ' + indexes_file_name)
        return -1
    else:
        for line in indexes_file:
            doc = {}
            doc['id'] = line.strip()
            doc['patient'] = 'patient_' + doc['id']
            doc['html'] = get("doc.html",  number_of_card=doc['id'],  from_file=True)

            q = {"$set":  {key: doc[key] for key in doc}}
            dbh.initial_docs.update({'id':doc['id'],  'patient': doc['patient']},  q)
            
            # claculated
            doc = {}
            doc['id'] = line.strip()
            doc['patient'] = 'patient_' + doc['id']
            
            file = get("doc.json",  number_of_card=doc['id'],  from_file=True)
            doc['json'] = json.dumps(file,  indent=4)
            doc['chunks'] = get("ch.json",  number_of_card=doc['id'],  from_file=True)
            doc['snapshot'] = get("snap.json",  number_of_card=doc['id'],  from_file=True)
            doc['key_words'] = get("key_words",  number_of_card=doc['id'],  from_file=True)
            
            q = {"$set":  {key: doc[key] for key in doc}}
            dbh.calculated_docs.update({'id': doc['id'],  'patient': doc['patient']},  q)
            print('Update document #' + doc['id'] + '.')
            
            # patients
            patient = {}
            patient['name'] = 'patient_' + line.strip()
            
            q = {"$set":  {key: patient[key] for key in patient}}
            dbh.patients.update({'name': patient['name']},  q,  upsert=True)
        indexes_file.close()
    dbh.dir.insert({})
    
    # Add taxonomies to the base
    for tax in taxes:
        taxonomy = {}
        taxonomy['taxonomy'] = tax
        #taxonomy['tset'] = get("tax.tset",  taxonomy=tax,  from_file=True)
        taxonomy['idx'] = get("tax.idx",  taxonomy=tax,  from_file=True)

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
    formula['json'] = json.dumps(get("code.json",  from_file=True),  indent=4)
    q = {"$set": {key: formula[key] for key in formula}}
    dbh.formulas.update({"formula": "CHF"},  formula, upsert=True)

# Get arbitrary file from the database or form a file (if 'from_file' is True)
def get(type, number_of_card="0",  taxonomy ="None",  from_file=False, formula="None",   mongo=None):
    if from_file:
        if type == "doc.html":
            card = CardHandler(number_of_card)
            nodes = []
            for nd in card.nodes:
                nodes.append(etree.tostring(nd))
            return nodes
        elif type == "doc.json":
            card = CardHandler(number_of_card)
            return card.dict
        elif type == "key_words":
            card = CardHandler(number_of_card)
            return card.key_words.split(', ')
        elif type == "ch.json":
            file_name = 'cci/chunks/ch' + number_of_card + '.json'
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
            try:
                snap_file  = open(snap_file_name,  'r')
            except IOError:
                print('No such file or directory: ' + snap_file_name)
                return
            else:
                return snap_file.read()
        elif type == "tax.tset":
            tax_file_name = 'cci/taxonomies/' + taxonomy + '.tset'
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
            tax_file_name = 'cci/indexes/' + taxonomy + '.idx'
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
            code_file_name = 'cci/rules/CHF.hsir'
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
            code_file_name = 'cci/rules/CHF.json'
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
            try:
                id_file = open('cci/documents/dir.list', 'r')
            except IOError:
                print('No such file or directory: cci/documents/dir.list')
            else:
                indexes = []
                for line in id_file:
                    number_of_card = line.strip()
                    indexes.append(number_of_card)
                return indexes

    else:
        if mongo is None:
            return
        if type == "doc.html":
            dbh = mongo["DataSet_test"]
            doc = dbh.initial_docs.find_one({"id": number_of_card})
            return doc['html']
        elif type == "doc.json":
            dbh = mongo["DataSet_test"]
            doc = dbh.calculated_docs.find_one({"id": number_of_card})
            return json.loads(doc['json'])
        elif type == "key_words":
            dbh = mongo["DataSet_test"]
            doc = dbh.calculated_docs.find_one({"id": number_of_card})
            return doc["key_words"]
        elif type == "ch.json":
            dbh = mongo["DataSet_test"]
            doc = dbh.calculated_docs.find_one({"id": number_of_card})
            return json.loads(doc["chunks"])
        elif type == "snap.json":
            dbh = mongo["DataSet_test"]
            doc = dbh.calculated_docs.find_one({"id": number_of_card})
            return doc["snapshot"]
        elif type == "tax.tset":
            dbh = mongo["claudia"]
            tax = dbh.taxonomies.find_one({"taxonomy": taxonomy})
            return tax['tset']
        elif type == "tax.idx":
            dbh = mongo["DataSet_test"]
            tax = dbh.indexes.find_one({"taxonomy": taxonomy})
            return tax['idx']
        elif type == "code.hsir":
            dbh = mongo["claudia"]
            form = dbh.formulas.find_one({"formula": formula})
            return form["hsir"]
        elif type == "code.json":
            dbh = mongo["claudia"]
            form = dbh.formulas.find_one({"formula": formula})
            return json.loads(form["json"])
        elif type == "all_indexes":
            dbh = mongo["DataSet_test"]
            indexes = dbh.initial_docs.distinct('id')
            return indexes
        elif type == "calculated_indexes":
            dbh = mongo["DataSet_test"]
            indexes = dbh.formula_results.find_one({"formula": formula})
            return indexes["indexes"]

# Put any file to the database
def put(type, file,  number_of_card="0",  taxonomy="None", formula="None",  mongo=None):
    if type == "doc.html":
        key = 'html'
        dbh = mongo["DataSet_test"]
        q = {"$set":  {key: file}}
        dbh.initial_docs.update({'id': number_of_card},  q,  upsert=True)
    elif type == "doc.json":
        key = 'json'
        dbh = mongo["DataSet_test"]
        q = {"$set":  {key: file}}
        dbh.calculated_docs.update({'id': number_of_card},  q,  upsert=True)
    elif type == "ch.json":
        key = 'chunks'
        dbh = mongo["DataSet_test"]
        q = {"$set":  {key: json.dumps(file,  indent=4)}}
        dbh.calculated_docs.update({'id': number_of_card},  q,  upsert=True)
    elif type == "snap.json":
        key = 'snapshot'
        dbh = mongo["DataSet_test"]
        q = {"$set":  {key: file}}
        dbh.calculated_docs.update({'id': number_of_card},  q,  upsert=True)
    if type == "tax.tset":
        key = 'tset'
        dbh = mongo["claudia"]
        q = {"$set":  {key: file}}
        dbh.taxonomies.update({'taxonomy': taxonomy},  q,  upsert=True)
    elif type == "tax.idx":
        key = 'idx'
        dbh = mongo["DataSet_test"]
        q = {"$set":  {key: file}}
        dbh.initial_docs.update({'taxonomy': taxonomy},  q,  upsert=True)
    elif type == "code.hsir":
        key = 'hsir'
        dbh = mongo["claudia"]
        q = {"$set":  {key: file}}
        dbh.initial_docs.update({'formula': formula},  q,  upsert=True)
    elif type == "code.json":
        key = 'json'
        dbh = mongo["claudia"]
        q = {"$set":  {key: file}}
        dbh.initial_docs.update({'formula': formula},  q,  upsert=True)
    elif type == "calculated_indexes":
        key = 'indexes'
        dbh = mongo["DataSet_test"]
        q = {"$set":  {key: file}}
        dbh.formula_results.update({'formula': formula},  q,  upsert=True)

if __name__ == '__main__':
    c = connect()
    update(c)
    print('Ok')
