




class claudiaRedactor:
    def __init__(self,  args,  mongo=None):
        # debugger
        s = "Line 5: Bugs... bugs... bugs..."
        bugs = '<div id="bugs">' + s + '</div>'
        
        #results
        s = "Here results of the formula will be..."
        results = '<div id="f_results">' + s + '</div>'
        
        template_file = open('cci/viewer/redactor.html',  'r')
        template = template_file.read()
        template_file.close()
        template = template.replace('<document_results/>',  results)
        template = template.replace('<debugger/>',  bugs)
        self.site = template
