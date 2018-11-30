from viewer import showIndex
from viewer import cardList
from viewer_cards import showCard
from viewer_cards import getCode
from redactor import claudiaRedactor
from redactor import runClaudia

#===============================================
class ClaudiaService:
    sMain = None

    @classmethod
    def start(cls, config, in_container):
        assert cls.sMain is None
        cls.sMain = cls(config, in_container)

    @classmethod
    def request(cls, serv_h, rq_path, rq_args,  mongo):
        if rq_path == "/":
            return serv_h.makeResponse(
                content = showIndex(rq_args['data'],  mongo).site)
        elif (rq_path == "/card") and ("id" in rq_args['data']):
            return serv_h.makeResponse(
                content = showCard(rq_args['data'],  mongo=mongo).site)
        elif rq_path == "/redactor":
            return serv_h.makeResponse(
                content = claudiaRedactor(rq_args,  mongo=mongo).site)
        elif rq_path == "/run":
            return serv_h.makeResponse(
                content = runClaudia(rq_args['data'],  mongo).site)
        elif rq_path == "/list":
            return serv_h.makeResponse(
                content = cardList(rq_args['data'],  mongo).site)
        elif rq_path == "/card/code":
            return serv_h.makeResponse(
                content = getCode(rq_args['data'],  mongo).site)


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

 
