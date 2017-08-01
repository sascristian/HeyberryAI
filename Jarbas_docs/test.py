
import requests
import fbchat
from fbchat.utils import *

def strip_to_json(text):
    try:
        return text[text.index('{'):]
    except ValueError as e:
        return None

def checkRequest(r, do_json_check=True):
    if not r.ok:
        raise Exception('Error when sending request: Got {} response'.format(r.status_code))

    content = get_decoded(r)
    c = strip_to_json(content)
    #print "content: ", content
    #print "stripped: ", c
    if content is None or len(content) == 0:
        raise Exception('Error when sending request: Got empty response')

    if do_json_check:
        try:
            j = json.loads(c)
        except Exception as e:
            raise Exception('Error while parsing JSON: {}'.format(repr(content)))
        check_json(j)
        return j
    else:
        return content

class FaceChat(fbchat.Client):
    def initialize(self, emitter=None, active=False):
        global log
        self.log = log

    def onMessage(self, author_id, message, thread_id, thread_type, **kwargs):
        print "\n"
        # for privacy we may want this off
        self.markAsDelivered(author_id, thread_id)  # mark delivered
        self.markAsRead(author_id)  # mark read

        print author_id, message
        print "\n"

    # bug fixes of original lib
    def _parseMessage(self, content):
        """Get message and author name from content. May contain multiple messages in the content."""

        if 'ms' not in content: return

        for m in content["ms"]:
            mtype = m.get("type")
            try:
                # Things that directly change chat
                if mtype == "delta":

                    def getThreadIdAndThreadType(msg_metadata):
                        """Returns a tuple consisting of thread ID and thread type"""
                        id_thread = None
                        type_thread = None
                        if 'threadFbId' in msg_metadata['threadKey']:
                            id_thread = str(msg_metadata['threadKey']['threadFbId'])
                            type_thread = ThreadType.GROUP
                        elif 'otherUserFbId' in msg_metadata['threadKey']:
                            id_thread = str(msg_metadata['threadKey']['otherUserFbId'])
                            type_thread = ThreadType.USER
                        return id_thread, type_thread

                    delta = m["delta"]
                    delta_type = delta.get("type")
                    metadata = delta.get("messageMetadata")

                    if metadata is not None:
                        mid = metadata["messageId"]
                        author_id = str(metadata['actorFbId'])
                        ts = int(metadata.get("timestamp"))

                    # New message
                    if delta.get("class") == "NewMessage":
                        message = delta.get('body', '')
                        thread_id, thread_type = getThreadIdAndThreadType(metadata)
                        self.onMessage(mid=mid, author_id=author_id, message=message,
                                       thread_id=thread_id, thread_type=thread_type, ts=ts, metadata=m, msg=m)
                        continue

                # Unknown message type
                else:
                    self.onUnknownMesssageType(msg=m)

            except Exception as e:
                self.onMessageError(exception=e, msg=m)

    def fetchAllUsers(self):
        """
        Gets all users the client is currently chatting with

        :return: :class:`models.User` objects
        :rtype: list
        :raises: Exception if request failed
        """

        data = {
            'viewer': self.uid,
        }
        j = checkRequest(self._post(ReqUrl.ALL_USERS, query=data))
        if not j['payload']:
            raise Exception('Missing payload')

        users = []

        for key in j['payload']:
            try:
                k = j['payload'][key]
                users.append(User(k['id'], first_name=k['firstName'], url=k['uri'], photo=k['thumbSrc'], name=k['name'], is_friend=k['is_friend'], gender=GENDERS[k['gender']]))
            except Exception as e:
                #self.log.error(e)
                pass

        return users

    def _pullMessage(self, sticky, pool):
        """Call pull api with seq value to get message data."""

        data = {
            "msgs_recv": 0,
            "sticky_token": sticky,
            "sticky_pool": pool,
            "clientid": self.client_id,
        }
        x = self._get(ReqUrl.STICKY, data)
       # print "get: ", x
        j = checkRequest(x)
        #print "j: ", x
        self.seq = j.get('seq', '0')
        #print "seq: ", self.seq
        #print " "
        return j

    def doOneListen(self, markAlive=True):
        """
        Does one cycle of the listening loop.
        This method is useful if you want to control fbchat from an external event loop

        .. note::
            markAlive is currently broken, and is ignored

        :param markAlive: Whether this should ping the Facebook server before running
        :type markAlive: bool
        :return: Whether the loop should keep running
        :rtype: bool
        """
        try:
            if markAlive: self._ping(self.sticky, self.pool)
            try:
                content = self._pullMessage(self.sticky, self.pool)
                if content:
                   # print "loop content: " + content
                    self._parseMessage(content)
            except requests.exceptions.RequestException:
                pass
            except Exception as e:
                return self.onListenError(exception=e)
        except KeyboardInterrupt:
            return False
        except requests.exceptions.Timeout:
            pass

        return True

chat = FaceChat("somom@30wave.com", "artificialjarbas6")
chat.listen()