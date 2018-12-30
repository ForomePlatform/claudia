import threading
from viewer import showIndex
from viewer import cardList
from viewer_cards import showCard
from viewer_cards import getInfo
from viewer_cards import runCode
from viewer_cards import getCode
from viewer_cards import clearCache
from redactor import claudiaRedactor
from redactor import runClaudia
from redactor import redactorTicket
from redactor import redactorProgress

#===============================================
class ClaudiaService:
    sMain = None

    @classmethod
    def start(cls, config, in_container):
        assert cls.sMain is None
        cls.sMain = cls(config, in_container)

    @classmethod
    def request(cls, serv_h, rq_path, rq_args,  mongo, httpd,  cch):
        thread = threading.currentThread().getName()
        if thread not in httpd.mLocks:
            lock = threading.Lock()
            lock.acquire()
            httpd.mLocks[thread] = lock
            lock.release()
        else:
            lock = httpd.mLocks[thread]
        if rq_path == "/":
            return serv_h.makeResponse(
                content = showIndex(rq_args['data'],  mongo,  lock).site)
        elif (rq_path == "/card") and ("id" in rq_args['data']):
            return serv_h.makeResponse(
                content = showCard(rq_args['data'],  mongo,  lock).site)
        elif rq_path == "/redactor":
            return serv_h.makeResponse(
                content = claudiaRedactor(rq_args,  mongo,  lock,  httpd).site)
        elif rq_path == "/redactor/run":
            return serv_h.makeResponse(
                content = runClaudia(rq_args['data'],  mongo, httpd,  cch).site)
        elif rq_path == "/list":
            return serv_h.makeResponse(
                content = cardList(rq_args['data'],  mongo,  lock).site)
        elif rq_path == "/card/info":
            return serv_h.makeResponse(
                content = getInfo(rq_args['data'],  mongo,  lock).site)
        elif rq_path == "/card/run":
            return serv_h.makeResponse(
                content = runCode(rq_args['data'],  mongo,  lock).site)
        elif rq_path == "/card/code":
            return serv_h.makeResponse(
                content = getCode(rq_args['data'],  mongo,  lock).site)
        elif rq_path == "/card/clear":
            return serv_h.makeResponse(
                content = clearCache(rq_args['data'],  mongo,  lock).site)
        elif rq_path == "/redactor/ticket":
            return serv_h.makeResponse(
                content = redactorTicket(rq_args['data'],  mongo, httpd,  cch).site)
        elif rq_path == "/redactor/progress":
            return serv_h.makeResponse(
                content = redactorProgress(rq_args['data'],  mongo,  httpd,  cch).site)


        return serv_h.makeResponse(error = 404)

    #===============================================
    def __init__(self, config, in_container):
        self.mConfig = config
        self.mInContainer = in_container
        # AnfisaData.setup(config)
        self.mHtmlTitle = self.mConfig["html-title"]
        self.mHtmlBase = (self.mConfig["html-base"]
            if self.mInContainer else None)
        if self.mHtmlBase and not self.mHtmlBase.endswith('/'):
            self.mHtmlBase += '/'

 
