import sys, os, traceback, logging, codecs, json
from StringIO import StringIO
from urlparse import parse_qs
import logging.config

from mongodb import connect
from wsgi_mk_request import ClaudiaService

#========================================
class HServResponse:
    #========================================
    sContentTypes = {
        "html":   "text/html",
        "xml":    "text/xml",
        "css":    "text/css",
        "js":     "application/javascript",
        "png":    "image/png",
        "json":   "application/json", 
        "ico":   "image/ico"}

    sErrorCodes = {
        202: "202 Accepted",
        204: "204 No Content",
        303: "303 See Other",
        400: "400 Bad Request",
        408: "408 Request Timeout",
        404: "404 Not Found",
        422: "422 Unprocessable Entity",
        423: "423 Locked",
        500: "500 Internal Error"}

    def __init__(self, start_response):
        self.mStartResponse = start_response

    def makeResponse(self, mode = "html", content = None, error = None,
            add_headers = None, without_decoding = False):
        response_status = "200 OK"
        if error is not None:
            response_status = self.sErrorCodes[error]
        if content is not None:
            if without_decoding:
                response_body = bytes(content)
            else:
                response_body = content#.encode("utf-8")
            response_headers = [("Content-Type", self.sContentTypes[mode]),
                                ("Content-Length", str(len(response_body)))]
        else:
            response_body = response_status
            response_headers = []
        if add_headers is not None:
            response_headers += add_headers
        self.mStartResponse(response_status, response_headers)
        return [response_body]

#========================================
class HServHandler:
    sInstance = None

    @classmethod
    def init(cls, config, in_container):
        cls.sInstance = cls(config, in_container)

    @classmethod
    def request(cls, environ, start_response):
        return cls.sInstance.processRq(environ, start_response)

    def __init__(self, config, in_container):
        #self.mFileDir = config["files"]
        self.mDirFiles = config["dir-files"]
        self.mHtmlBase = (config["html-base"]
            if in_container else None)
        if self.mHtmlBase and self.mHtmlBase.endswith('/'):
            self.mHtmlBase = self.mHtmlBase[:-1]
    
    def checkFilePath(self, path):
        for path_from, path_to in self.mDirFiles:
            #print('path: ' + path)
            #print('path_from: ' + path_from)
            #print('path_to: ' + path_to)
            if path.startswith(path_from):
                return path_to + path[len(path_from):]
        return None

    #===============================================
    def parseRequest(self, environ):
        #print('environ:')
        #for key in environ:
            #print(key + ': ' + str(environ[key]))
        path = environ["PATH_INFO"]
        #print('before = "' + path + '"')
        if self.mHtmlBase and path.startswith(self.mHtmlBase):
            path = path[len(self.mHtmlBase):]
        if not path:
            path = "/"
        #print('path = "' + path + '"')
        

        if environ["REQUEST_METHOD"] == "POST":
            try:
                rq_body_size = int(environ.get('CONTENT_LENGTH', 0))
                rq_body = environ['wsgi.input'].read(rq_body_size)
                #print('body: ' + rq_body)
                if environ['CONTENT_TYPE'][:19] == 'multipart/form-data':
                    query_args = self.parse_POST(rq_body)
                else:
                    query_args_pairs = {}
                    for a, v in parse_qs(rq_body).items():
                        query_args_pairs[a] = v[0]#.decode("utf-8")
                        query_args = {}
                    query_args['method'] = 'POST'
                    query_args['data'] = query_args_pairs
            except Exception:
                rep = StringIO()
                traceback.print_exc(file = rep)
                log_record = rep.getvalue()
                logging.error(
                    "Exception on read request body:\n " + log_record)
        else:
            query_string = environ["QUERY_STRING"]
            query_args_pairs = dict()
            if query_string:
                for a, v in parse_qs(query_string).items():
                    query_args_pairs[a] = v[0]
            query_args = {}
            query_args['method'] = 'GET'
            query_args['data'] = query_args_pairs

        return path, query_args

    def parse_POST(self,  rq_body):
        lines = rq_body.split('\n')
        requests = []
        flag = True
        key = "Content-Disposition: form-data; "
        args = {}
        data = ''
        for line in lines:
            if line.find('------') != -1:
                if args != {}:
                    args['data'] = data.strip('\n\r')
                    requests.append(args)
                flag = True
                args = {}
                data = ''
            else:
                if line == '\r':
                    flag = False
                if flag:
                    if line[:len(key)] == key:
                        lin = line[len(key):]
                        parts = lin.split('; ')
                        for part in parts:
                            words = part.split('=')
                            args[words[0]] = words[1]
                else:
                    data += line + '\n'
        res = {}
        res['method'] = 'POST'
        res['data'] = requests
        return res
    

    #===============================================
    def fileResponse(self, resp_h, fpath,  without_decoding):
        #fpath = self.mFileDir + fname
        if not os.path.exists(fpath):
            return False
        if without_decoding:
            inp = open(fpath, "r")
            content = inp.read()
        else:
            with codecs.open(fpath, "r", encoding = "utf-8") as inp:
                content = inp.read()
        inp.close()
        return resp_h.makeResponse(mode = fpath.rpartition('.')[2],
            content = content,  without_decoding = without_decoding)

    #===============================================
    def processRq(self, environ, start_response):
        mongo = connect()
        resp_h = HServResponse(start_response)
        try:
            path, query_args = self.parseRequest(environ)
            file_path = self.checkFilePath(path)
            #print('path="' + path)
            #print(query_args)
            if path.find('.') != -1:
                ret = self.fileResponse(resp_h, file_path, True)
                if ret is not False:
                    return ret
            return ClaudiaService.request(resp_h, path, query_args,  mongo, thread, httpd)
        except Exception:
            rep = StringIO()
            traceback.print_exc(file = rep)
            log_record = rep.getvalue()
            logging.error(
                "Exception on GET request:\n " + log_record)
            return resp_h.makeResponse(error = 500)

#========================================
def loadJSonConfig(config_file):
    with codecs.open(config_file, "r", encoding = "utf-8") as inp:
        content = inp.read()
    dir_name = os.path.abspath(__file__)
    #print('dir_name: ' + dir_name)
    for idx in range(1):
        dir_name = os.path.dirname(dir_name)
        #print('loop ' + str(idx) + ': ' + dir_name)
    content = content.replace('${HOME}', dir_name)
    pre_config = json.loads(content)

    file_path_def = pre_config.get("file-path-def")
    if file_path_def:
        for key, value in file_path_def.items():
            assert key != "HOME"
            content = content.replace('${%s}' % key, value)
    return json.loads(content)


def setupHServer(config_file, in_container):
    if not os.path.exists(config_file):
        logging.critical("No config file provided (%s)" % config_file)
        sys.exit(2)
#    config = None
#    with codecs.open(config_file, "r", encoding = "utf-8") as inp:
#        content = inp.read()
#    config = json.loads(content)
    config = loadJSonConfig(config_file)
    logging_config = config.get("logging")
    if logging_config:
        logging.config.dictConfig(logging_config)
        logging.basicConfig(level = 0)
    ClaudiaService.start(config, in_container)
    print('Start server.')
    HServHandler.init(config, in_container)
    if not in_container:
        return (config["host"], int(config["port"]))
    return None


#========================================
def application(environ, start_response):
    return HServHandler.request(environ, start_response)

#========================================

#from threads_for_server import MyThreadPool
import threading
from wsgiref.simple_server import make_server, WSGIRequestHandler

class _LoggingWSGIRequestHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        logging.info(("%s - - [%s] %s\n" %
            (self.client_address[0], self.log_date_time_string(),
            format % args)).rstrip())

class MyThreadPool:
    def __init__(self,  num_threads,  host,  port):
        self.num_threads = num_threads
        self.daemon_threads = False
        self.threads = {}
        self.httpd = make_server(host, port, application, 
                        handler_class = _LoggingWSGIRequestHandler)
        
    def run(self):
        for n in range(self.num_threads):
            #t = threading.Thread(target = self.httpd.serve_forever)
            t = threading.Thread(target = self.thread_init)
            t.daemon = self.daemon_threads
            t.start()
            self.threads[t.getName()] = t
            logging.info('Thread ' + str(n) + ': ' + t.getName())
    
    def thread_init(self):
        lock = threading.Lock()
        lock.acquire()
        for i in range(self.num_threads):
            name = 'Thread-' + str(i)
            if name not in httpd.mLocks:
                httpd.mLocks[name] = lock
                global thread
                thread = name
                print('Start: ' + thread)
        self.httpd.serve_forever()

class ThreadServer:
    def __init__(self,  host,  port,  count_of_threads):
        self.countOfThreads = count_of_threads
        self.pool = MyThreadPool(self.countOfThreads,  host,  port)
        self.results = []
        self.mLocks = {}
        for thread in self.pool.threads:
            self.mLocks[thread.getName()] = threading.Lock()
    
    def start(self):
        self.pool.run()
    
    def stop(self):
        logging.info('Interrupting of all threads...')
        for n in range(self.num_threads):
            self.threads[n].join()

    def except_hook(self, exctype, value, traceback):
        if exctype == KeyboardInterrupt:
            print('Interrupt...')
            self.stop()
        sys.__excepthook__(exctype, value, traceback)

#========================================
if __name__ == '__main__':
    logging.basicConfig(level = 0)
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "claudia.json"

    #from threads_for_server import MyThreadWSGI
    #from wsgiref.simple_server import make_server, WSGIRequestHandler
    #log_file_name = config["logging"]['handlers']['default']['filename']
    #os.remove(log_file_name)
    
    

    #========================================
#    class _LoggingWSGIRequestHandler(WSGIRequestHandler):
#        def log_message(self, format, *args):
#            logging.info(("%s - - [%s] %s\n" %
#                (self.client_address[0], self.log_date_time_string(),
#                format % args)).rstrip())

    #========================================
    host, port = setupHServer(config_file, False)
    #httpd = make_server(host, port, application, server_class=MyThreadWSGI, 
    #    handler_class = _LoggingWSGIRequestHandler)
    logging.info("HServer listening %s:%d" % (host, port))
    mongo = connect()
    #httpd.serve_forever()
    config = loadJSonConfig(config_file)
    print('Count of threads: ' + str(config['count_of_threads']))
    global httpd
    httpd = ThreadServer(host,  port,  config['count_of_threads'])
    #import signal
    #signal(signal.SIGQUIT,  httpd.stop)
    sys.excepthook = httpd.except_hook
    httpd.start()
    
else:
    mongo = connect()
    logging.basicConfig(level = 10)
    setupHServer("claudia/claudia.json", True)
