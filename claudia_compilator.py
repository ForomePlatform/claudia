import sys
import json
from mongodb import get,  put,  connect

# Split a line into a list of words.
def split_to_words(line):
    special_simbols = [ ' ',  '\t',  '\n',  '(',  ')',  ':',  '.',  '=',  '{',  '}',  ',']
    bad_simbols = [' ',  '\t',  '\n']
    words = []
    place = 0
    comons = False
    com_start = 0
    for i in range(len(line)):
        #print('cadre: s="' + line[i] + '", words=' + ''.join(words))
        if line[i] == '"':
            comons = not comons
            if comons:
                com_start = i
            else:
                words.append(line[com_start:i+1])
                place = i+1
                continue
        if comons:
            continue
        if line[i] in special_simbols:
            #print('spec: "' + line[i] + '" i=' + str(i))
            words.append(line[place:i])
            if line[i] not in bad_simbols:
                words.append(line[i])
            place = i+1
    words.append(line[place:])
    while '' in words:
        words.remove('')
    #print(words)
    return words
    
def line_constructor(text):
    lines = text.split('\n')
    stack = ''
    new_lines = []
    current_line = ''
    for n in range(len(lines)):
        current_line += lines[n]
        for w in lines[n]:
            if stack!= '' and stack[-1] == '"':
                if w != '"':
                    continue
                else:
                    stack = stack[:-1]
            if w == '(' or w == '{':
                stack += w
            if w == ')' or w == '}':
                if stack == '':
                    error = {}
                    error['action'] = 'error'
                    error['line'] = len(new_lines)
                    error['message'] = 'Breket is absent.'
                    return error
                else:
                    if w == ')' and stack[-1] == '(' or w == '}' and stack[-1] == '{':
                        stack = stack[:-1]
        if stack == '':
            new_lines.append(current_line)
            current_line = ''
        else:
            if stack[-1] == '"':
                error = {}
                error['action'] = 'error'
                error['line'] = len(new_lines)
                error['message'] = 'End of string constant is not found.'
                return error
    if stack != '':
        error = {}
        error['action'] = 'error'
        error['line'] = len(new_lines)
        error['message'] = 'Breket is absent.'
        return error
    return new_lines

# Delete all comments in Claudia-code
def delete_comments(code):
    new_code = []
    for line in code:
        place = line.find('#')
        if place != -1:
            new_code.append(line[:place])
        else:
            new_code.append(line)
    return new_code

# Definite a set of values of an annotation
def annotation_values(words):
    words = ''.join(words)
    #print('Annotation values: ' + str(words))
    part = words.split('=')
    if words == '':
        return {}
    if len(part) != 2:
        error = {}
        error['action'] = 'error'
        error['message'] = 'Wrong statement "' + words + '". Model: "key"={"value1", "value2"}.'
        return error
    else:
        annotation = {}
        annotation['key'] = part[0]
        set = split_to_words(part[1])
        if set[0] != '{' or set[-1] != '}':
            error = {}
            error['action'] = 'error'
            error['message'] = 'Wrong set of values for annotation "' + part[0] + '".'
            return error
        set = ''.join(set[1:-1]).split(',')
        set_of_values = []
        for el in set:
            if el == []:
                continue
            if el[0] == '"' and el[-1] == '"':
                value = el[1:-1]
            else:
                value = int(el)
            set_of_values.append(value)
        annotation['values'] = set_of_values
        return annotation

def defineAnnotation(words):
    #print('define: ' + str(words))
    definition = {}
    if words == []:
        return definition
    if words[0][0] != '"' or words[0][-1] != '"':
        error = {}
        error['action'] = 'error'
        error['message'] = 'Type of the annotation is not string.'
        return error
    definition['key'] = words[0][1:-1]
    definition['annotations'] = []
    words = words[1:]
    brekets = 0
    place = 0
    for m in range(len(words)):
        if words[m] == '{':
            brekets += 1
        if words[m] == '}':
            brekets -= 1
        if words[m] == ',' and brekets == 0:
            if m == place:
                place = m+1
                continue
            annotation = annotation_values(words[place:m])
            if 'message' in annotation:
                return annotation
            place = m + 1
            definition['annotations'].append(annotation)
    annotation = annotation_values(words[place:])
    if 'message' in annotation:
        return annotation
    definition['annotations'].append(annotation)
    definition['annotations'].append({'key': 'context',  'values': ['ambiguous', 
                                            'negative',  'affirmative']})
    words = ''.join(words).split(',')[1:]
    return definition

# Logic expression in a condition operator
def is_condition(words,  vars,  annotations):
    #print('annotations: ' + json.dumps(annotations,  indent=4))
    #print('condition words: ' + str(words))
    if words == []:
        error = {}
        error['action'] = 'error'
        error['message'] = 'Condition is missed.'
        return error
    brekets = 0
    # Operator 'and' or 'or'
    for m in range(len(words)):
        if words[m] == '(':
            brekets += 1
        if words[m] == ')':
            brekets -= 1
        if (words[m] == 'and' or words[m] == 'or') and brekets == 0:
            exp1 = words[0:m]
            exp2 = words[m+1:]
            cond1 = is_condition(exp1,  vars,  annotations)
            if cond1['action'] == 'error':
                return cond1
            cond2 = is_condition(exp2,  vars,  annotations)
            if cond2['action'] == 'error':
                return cond2
            operator = {}
            operator['action'] = {}
            operator['action']['f'] = words[m]
            operator['action']['a'] = [cond1['action'],  cond2['action']]
            operator['args'] = []
            operator['args'].extend(cond1['args'])
            operator['args'].extend(cond2['args'])
            return operator
    if brekets != 0:
        error = {}
        error['action'] = 'error'
        error['message'] = '")" is absent'
        return error
    if words[0] == '(' and words[-1] == ')':
        cond = is_condition(words[1: -1],  vars)
        return cond
    # Negative of a logic expression
    if words[0] == 'not':
        operator = {}
        operator['action'] = {}
        operator['action']['f'] = 'not'
        cond = is_condition(words[1:],  vars,  annotations)
        if cond['action'] == 'error':
            return cond
        operator['action']['a'] = cond['action']
        operator['args'] = cond['args']
        return operator
    # Check an annotation
    if words[1:4] == ['.',  'annotated',  '('] and words[-1] == ')':
        if words[0] in vars:
            words = words[4:]
            words = words[:-1]
            operator = {}
            operator['action'] = {}
            operator['action']['f'] = 'annotated'
            operator['action']['a'] = []
            operator['args'] = []
            if words == []:
                return operator
            key_word = {}
            key_word['type'] = 'key'
            key_word['value'] = words[0]
            operator['args'].append(key_word)
            line = ''.join(words)
            words = line.split(',')
            current_ann = {}
            for annotation in annotations:
                if annotation['key'] == words[0]:
                    current_ann = annotation
            if current_ann == {}:
                error = {}
                error['action'] = 'error'
                error['message'] = 'Undefined annotations ' + words[0] + '.'
                return error
            for word in words[1:]:
                part = word.split('=')
                #print('part: ' + str(part))
                if len(part) != 2:
                    error = {}
                    error['action'] = 'error'
                    error['message'] = 'Wrong statement "' + word + '". Model: "key"="value".'
                    return error
                else:
                    curr_key = {}
                    for field in current_ann['annotations']:
                        if field['key'] == part[0]:
                            curr_key = field
                    #print('value: ' + part[0] + ', current value: ' + str(curr_key))
                    if curr_key == {} and part[0] != 'context' and part[0] != 'diagnosis':
                        if part[0] not in ['equals',  'great_than',  'less_than']:
                            error = {}
                            error['action'] = 'error'
                            error['message'] = 'Undefined key of annotations: ' + str(part[0])
                            return error
                    value = {}
                    value['type'] = 'const'
                    if part[1][0] == '"' and part[1][-1] == '"':
                        value['value'] = part[1][1:-1]
                    else:
                        value['value'] = int(part[1])
                    #print('value: ' + part[0] + ', current value: ' + str(curr_key))
#                    if  type(value['value']) != int and value['value'] not in curr_key['values']:
#                        error = {}
#                        error['action'] = 'error'
#                        error['message'] = 'Undefined value of the annotation: ' + str(part[1])
#                        return error
                    key = {}
                    key['type'] = 'annotationData'
                    key['value'] = part[0]
                    equals = {}
                    equals['f'] = 'equals'
                    equals['a'] = [{'f':'x'},  {'f':'x'}]
                    operator['action']['a'].append(equals)
                    operator['args'].append(key)
                    operator['args'].append(value)
            return operator
        else:
            error = {}
            error['action'] = 'error'
            error['message'] = 'Unknown variable "' + words[0] + '"'
            return error
        
    error = {}
    error['action'] = 'error'
    error['message'] = 'Wrong logic expression.'
    return error
    
# Add an annotation
def annotate(ann,  source_id):
    annotation = {}
    annotation['action'] = 'detect'
    annotation['name'] = 'annotate'
    source_id['id'] += 1
    annotation['source_id'] = source_id['id']
    if ann == []:
        return annotation
    annotation['key'] = ann[0]
    pars = {}
    words = ''.join(ann).split(',')
    if len(words) == 1:
        annotation['options'] = pars
        return annotation
    for word in words[1:]:
        part = word.split('=')
        if len(part) != 2:
            error = {}
            error['action'] = 'error'
            error['message'] = 'Wrong statement "' + word + '". Model: "key"="value".'
            return error
        else:
            if part[1][0] == '"' and part[1][-1] == '"':
                value = part[1][1:-1]
            else:
                value = int(part[1])
            pars[part[0]] = value
    annotation['options'] = pars
    return annotation

def is_str(s):
    if len(s)>1 and s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return

# Find all phrase such that "collection...."
def collection(words,  source_id,  annotations):
    #print('collection: ' + str(words[1:4]))
    if words[1:4] == ['.',  'lookup',  '('] and words[-1] == ')':
        source_id['id'] += 1
        lookup = {}
        lookup['action'] = 'detect'
        lookup['options'] = {}
        lookup['source_id'] = source_id['id']
        lookup['steps'] = [source_id['id']]
        lookup['name'] = 'lookup'
        if words[4] == 'RegExp':
            if len(words) != 11 or words[5] != '(' or words[7] != ',' or words[9:11] != [')',  ')']:
                error = {}
                error['action'] = 'error'
                error['message'] = 'Wrong definition of Regular Expression operator.'
                return error
            if is_str(words[6]) is None or is_str(words[8]) is None:
                error = {}
                error['action'] = 'error'
                error['message'] = 'Wrong definition of Regular Expression operator.'
                return error
            lookup['options']['name'] = 'RegExp'
            lookup['options']['var'] = is_str(words[6])
            lookup['options']['pattern'] = is_str(words[8])
            annotations.append({'key': is_str(words[6]),  'annotations': []})
            return lookup
        lookup['options']['name'] = 'lookup'
        ann = words[4:-1]
        sememes = ''.join(ann).split(',')
        lookup['options']['values'] = sememes
        return lookup
    elif words[1:4] == ['.',  'setFinalAnnotation',  '('] and words[-1] == ')':
        action = {}
        action['action'] = 'detect'
        action['name'] = 'setFinalAnnotations'
        source_id['id'] += 1
        action['source_id'] = source_id['id']
        action['steps'] = [source_id['id']]
        action['options'] = {}
        action['options']['key'] = words[4]
        return action
    else:
        error = {}
        error['action'] = 'error'
        error['message'] = 'Unknown method of "collection".'
        return error

def cycle(words,  vars):
    vars.append(words[1])
    loop = {}
    loop['action'] = 'for'
    loop['set'] = words[3:-1]
    if loop['set'][:2] != ['collection',  '.'] or loop['set'][3:] != ['(',  ')']:
        error = {}
        error['action'] = 'error'
        error['message'] = 'Unknown set of loop elements.'
        return error
    loop['set'] = loop['set'][2]
    if loop['set'] not in ['entities',  'sentences',  'documents']:
        error = {}
        error['action'] = 'error'
        error['message'] = 'Unknown set of loop elements.'
        return error
    return loop

# If line starts from a variable
def variable(words,  source_id):
    if words[1:4] == ['.',  'annotate',  '(']:
        ann = words[4:-1]
        #print('ann: ' + str(ann))
        ann = annotate(ann,  source_id)
        return ann
    elif words[1:5] == ['.',  'reject',  '(',  ')']:
        reject = {}
        reject['action'] = 'reject'
        source_id['id'] += 1
        reject['source_id'] = source_id['id']
        reject['options'] = {}
        reject['options']['variable'] = words[0]
        return reject
    else:
        error = {}
        error['action'] = 'error'
        error['message'] = 'Unknown method.'
        return error


# Count of spaces at the begining of a line
def get_level(line):
    for i in range(len(line)):
        if line[i] != ' ':
            return i
    return len(line)

# Compilator
def compilator(lines,  old_vars,  source_id,  old_source,  annotations):
    n = 0
    source = []
    if len(lines) == 0:
        return
    level = -1
    statements = []
    steps = []
    vars = old_vars
    
    while n < len(lines):
        #print('line ' + str(n) + ': ' + lines[n])
        words = split_to_words(lines[n])
        while '' in words:
            words.remove('')
        if words == []:
            n += 1
            continue
        if level == -1:
            level = get_level(lines[n])
        # Go out to higher level
        if get_level(lines[n]) < level:
            response = {}
            response['action'] = statements
            response['line'] = n
            response['source'] = source
            response['steps'] = steps
            return response
        # Import taxonomies
        if words[0] == 'import':
            s = ''.join(words[1:])
            anns = s.split(',')
            for ann in anns:
                annotation = {}
                annotation['key'] = ann
                if ann == 'NUMERIC':
                    annotation['annotations'] = [{'key':'equals'},  
                                                    {'key':'great_than'},  {'key': 'less_than'}, 
                                                    {'key': 'measure',  'values': ['%']}]
                else:
                    annotation['annotations'] = []
                annotations.append(annotation)
            n += 1
        elif words[0] == 'from' and words[2] == 'import':
            s = ''.join(words[3:])
            anns = s.split(',')
            for ann in anns:
                annotation = {}
                annotation['key'] = ann
                annotation['annotations'] = [
                                            {'key':'diagnosis',  'values': ['CHF']}, 
                                            {'key': 'protocol',  'values': ['true',  'false']}, 
                                            {'key': 'context',  'values': ['ambiguous', 
                                            'negative',  'affirmative']}, 
                                            {'key': '_negation_literal',  'values': 'rule_out'}, 
                                            {'key': 'condition', 'values': ['HF',  'CD']}, 
                                            {'key': 'qualifier',  'values': ['congestive']}, 
                                            {'key': 'symptom',  'values': ['EF',  'low_EF',  'PED', 
                                            'SHORTNESS',  'BREATH']}, 
                                            {'key': 'procedure',  'values': ['CXR']}]
                annotations.append(annotation)
            n += 1
        # Apply taxonomies (lookup), seFinalAnnotations
        elif words[0] == 'collection':
            res = collection(words,  source_id,  annotations)
            if res['action'] == 'error':
                res['line'] = n
                return res
            steps.extend(res['steps'])
            statements.append(res)
            source_line = {}
            source_line['source_id'] = source_id['id']
            source_line['line'] = n
            source_line['column'] = level
            source_line['text'] = old_source + '\n' + lines[n]
            source.append(source_line)
            n += 1
        # Definition of an annotation
        elif words[1:6] == ['=',  'collection',  '.',  'defineAnnotation',  '(']:
            ann = words[6:-1]
            definition = defineAnnotation(ann)
            if 'message' in definition:
                definition['line'] = n
                return definition
            annotations.append(definition)
            n += 1
        # Loop
        elif words[0] == 'for' and words[2] == 'in' and words[-1] == ':':
            loop = cycle(words,  vars)
            if loop['action'] == 'error':
                return loop
            n += 1
            res = compilator(lines[n:],  vars,  source_id,  old_source,  annotations)
            if res['action'] == 'error':
                res['line'] += n
                return res
            n += res['line']
            source.extend(res['source'])
            res.pop('source')
            steps.extend(res['steps'])
            loop['steps'] = res['steps']
            res.pop('steps')
            loop['options'] = res
            statements.append(loop)
            vars.remove(words[1])
        # Condition operator
        elif words[0] == 'if':
            operator_if = {}
            operator_if['name'] = 'if'
            operator_if['action'] = 'detect'
            operator_if['steps'] = []
            operator_if['options'] = {}
            
            text = lines[n]
            condition = []
            words = words[1:]
            while words != [] and words[-1] != ':':
                condition.extend(words)
                n += 1
                if n >= len(lines):
                    error = {}
                    error['action'] = 'error'
                    error['message'] = 'Operator "if" is defined but ":" is not found.'
                    error['line'] = n
                    return error
                words = split_to_words(lines[n])
                text += lines[n]
            condition.extend(words[:-1])
            cond = is_condition(condition,  vars,  annotations)
            if cond['action'] == 'error':
                cond['line'] = n
                return cond
            operator_if['options']['condition'] = cond['action']
            operator_if['options']['args'] = cond['args']
            
            # action "if"
            n += 1
            action_if = compilator(lines[n:],  vars,  source_id,  
                                            old_source + '\n' + text,  annotations)
            if action_if['action'] == 'error':
                action_if['line'] = n
                return action_if
            source.extend(action_if['source'])
            operator_if['options']['steps_if'] = action_if['steps']
            operator_if['options']['action_if'] = action_if['action']
            operator_if['steps'].extend(action_if['steps'])
            n += action_if['line']
            words = split_to_words(lines[n])
            
            # action "else"
            if words == ['else',  ':']:
                n += 1
                text = text.replace('if ',  'if not (')
                text = text.replace(':',  '):')
                action_else = compilator(lines[n:],  vars,  
                                        source_id, old_source + '\n' + text,  annotations)
                if action_else['action'] == 'error':
                    action_else['line'] = n
                    return action_else
                source.extend(action_else['source'])
                operator_if['options']['steps_else'] = action_else['steps']
                operator_if['options']['action_else'] = action_else['action']
                operator_if['steps'].extend(action_else['steps'])
                n += action_else['line']
                
            steps.extend(operator_if['steps'])
            statements.append(operator_if)
        # Reject and add an annotation
        elif words[0] in vars:
            res = variable(words,  source_id)
            res['line'] = n
            if res['action'] == 'error':
                return res
            source_line = {}
            source_line['source_id'] = source_id['id']
            source_line['line'] = n
            source_line['column'] = level
            source_line['text'] = old_source + '\n' + lines[n]
            source.append(source_line)
            steps.append(source_id['id'])
            res['steps'] = [source_id['id']]
            statements.append(res)
            n += 1
        else:
            error = {}
            error['action'] = 'error'
            error['message'] = 'Unknown operator.'
            error['line'] = n
            return error
    response = {}
    response['action'] = statements
    response['line'] = n
    response['source'] = source
    response['steps'] = steps
    response['annotations'] = annotations
    return response

negation = {
            "positive": {
                    "max": 0, 
                    "min": 0
            }, 
            "possibly negative": {
                    "max": 100, 
                    "min": 10
            }, 
            "negative": {
                    "max": 100, 
                    "min": 50
            }, 
            "ambiguous": {
                    "max": 40, 
                    "min": 10
            }, 
            "affirmative": {
                    "max": 0, 
                    "min": 0
            }
}

def start_compilator(claudia,  claudia_file_name):
    lines = line_constructor(claudia)
    lines = delete_comments(lines)
    ret = compilator(lines,  [],  {'id': 0},  '',  [])
    if ret['action'] == 'error':
        message = 'Line ' + str(ret['line']) + ': ' + ret['message']
        print(message)
        sys.exit()
    else:
        code = {}
        code['rulename'] = claudia_file_name
        code['version'] = '0.1'
        code['declarations'] = negation
        code['statements'] = ret['action']
        code['source'] = ret['source']
        code['count_of_steps'] = len(ret['steps'])
        #code['annotations'] = ret['annotations']
        for source in code['source']:
            #print('source-id: ' + str(source['source_id']))
            while source['text'].find('  ') != -1:
                source['text'] = source['text'].replace('  ',  ' ')
        return code

if __name__ == '__main__':
    mongo = connect()
    for claudia_file_name in ['CHF', 'MI']:
        claudia = get('code.cla', formula=claudia_file_name,  from_file=True)
        code = start_compilator(claudia,  claudia_file_name)
        file = open('cci/claudia_rules/' + claudia_file_name + '.cla.json',  'w')
        file.write(json.dumps(code,  indent=4))
        file.close()
        put('code.cla.json',  code,  formula=claudia_file_name,  mongo=mongo)
    print('Ok.')
