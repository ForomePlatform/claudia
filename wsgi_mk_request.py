from viewer import showIndex
from viewer_cards import showCard

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
                content = showIndex(rq_args,  mongo).site)
        if (rq_path == "/card") and ("id" in rq_args):
            return serv_h.makeResponse(
                content = showCard(rq_args,  mongo=mongo).site)


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

 
