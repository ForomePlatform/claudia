#import json
import urllib
import socket
import subprocess
from lxml import etree
from mongodb import get
from claudia_interpretator import for_one_doc
from claudia_compilator import start_compilator



class claudiaRedactor:
    def __init__(self,  args,  mongo=None):
        #print('args: ' + json.dumps(args,  indent=4))
        computer = socket.gethostname()
        
        document = ""
        formula = "<p>Upload a formula from a file.</p>"
        formula_text = urllib.quote(formula)
        for arg in args['data']:
            data = arg['data']
            if arg['name'] == '"formula"':
                formula_text = urllib.quote(data)
            elif arg['name'] == '"formula_reserve"\r':
                formula_text = data
            elif arg['name'] == '"document_text"\r': 
                document = data
            elif arg['name'] == '"document"':
                document = urllib.quote(data)
            else:
                print('Unknown name: ' + arg['name'])
        
        # debugger
        s = "Formula: No errors."
        bugs = '<div id="bugs">' + s + '</div>'
        
        #results
        s = "Here results of the formula will be..."
        results = '<div id="f_results">' + s + '</div>'
        
        if computer == 'noX540LJ':
            template_name = 'cci/viewer/redactor.html'
        else:
            template_name = '/home/andrey/work/Claudia/claudia/cci/viewer/redactor.html'
        template_file = open(template_name,  'r')
        template = template_file.read()
        template_file.close()
        template = template.replace('<document_results/>',  results)
        template = template.replace('<debugger/>',  bugs)
        template = template.replace('<document/>',  document)
        template = template.replace('<formula_text/>',  formula_text)
        self.site = template
        

class runClaudia():
    def __init__(self,  args, mongo=None):
        #print(json.dumps(args,  indent=4))
        formula = args['formula']
        text = args['doc']
        doc = self.generator_of_chunks(text,  mongo)
        if doc is None:
            self.site = 'File ' + text[5:] + ' is not found.'
            return
        formula_name = "Formula was generated by ClaudiaRedactor. " + "Date: Today."
        code = start_compilator(formula,  formula_name)
        doc_data = for_one_doc(doc,  code,  mongo)
        
        results = '<p class="res_paragraph">Diagnose:</p>'
        results += '<p>' + doc_data['data']['Formula diagnose'] + '</p>'
        if text[:5] == 'Doc #':
            js = get('doc.json',  number_of_card = text[5:],  dataset='cci',  mongo = mongo)
            print('js: ' + str(js))
            for key in js:
                #print(key)
                if key.find('CHF') != -1:
                    results += '<p class="res_paragraph">Apriory:</p>'
                    results += '<p>' + str(key) + '</p>'
        results += '<p class="res_paragraph">Sentences with untrivial annotations:</p>'
        for sentence in doc_data['sentences']:
            if len(sentence['data']) < 2:
                continue
            attr = ''
            for key in sentence['data']:
                if key == 'reject':
                    continue
                attr += key + ': ' + sentence['data'][key] + '; '
            p = '<p class="sentence_attr"><b>Sentence attributes: </b>' + attr + '</p>'
            results += p
            sent = ''
            for chunk in sentence['chunks']:
                sent += chunk['text'] + ' '
            p = '<p class="res_sentence">' + sent + '</p>'
            results += p
        results += '<p> </p>'
        
        results += '<p class="res_paragraph">Document:</p>'
        for node in doc:
            results += node
        self.site = results


    def split_to_chunks(self,  text):
        computer = socket.gethostname()
        if computer == 'noX540LJ':
            return text
        else:
            file_name = '/home/andrey/work/Claudia/claudia/tmp/text.txt'
            file = open(file_name,  'w')
            file.write(text)
            file.close()
            q = "java -jar /data/projects/Claudia/lib/hsconnector.jar < "
            out,  err = subprocess.Popen(q + file_name, stdout=subprocess.PIPE, shell=True).communicate()
            out = out.replace('\r',  '')
            print('generator of chunks: ' + out)
            return out

    def generator_of_chunks(self,  text, mongo):
        if text[:5] == 'Doc #':
            number_of_card = text[5:]
            nodes = get("doc.html",  number_of_card=number_of_card,  
                                            dataset='cci',  mongo=mongo)
            if nodes is None:
                return
            doc = '\n'.join(nodes)
        else:
            doc = self.split_to_chunks(text)
            #doc = text
        
        computer = socket.gethostname()
        if computer == 'noX540LJ':
            tmp_file = 'tmp/formula.cla'
        else:
            tmp_file = '/home/andrey/work/Claudia/claudia/tmp/formula.cla'
        file = open(tmp_file,  'w')
        file.write(doc)
        file.close()
        try:
            with open(tmp_file,  'rb') as inp:
                sHTML_Parser = etree.HTMLParser(remove_comments = True)
                tree = etree.parse(inp, sHTML_Parser)
                nodes = tree.xpath('/html/body/p')
        except IOError:
            print('No such file or directory: ' + tmp_file)
            return
        s_nodes = []
        for node in nodes:
            s_nodes.append(etree.tostring(node))
        return s_nodes