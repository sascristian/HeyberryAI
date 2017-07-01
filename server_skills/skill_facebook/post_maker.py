from mycroft.messagebus.message import Message


class FbPost():
    # template, use this inside any skill to make posts if face book skill is available
    def __init__(self, emitter):
        self.emitter = emitter

    def post_text(self, text, id="me", speech= "Making a post on face book", link= None):
        self.emitter.emit(Message("fb_post_request", {"type":"text", "id":id, "link":link, "text":text, "speech":speech}))

    def post_link(self, link,  text="", id="me", speech= "Sharing a link on face book"):
        self.emitter.emit(Message("fb_post_request", {"type":"link", "id":id, "link":link, "text":text, "speech":speech}))

