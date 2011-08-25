#!/sw/bin/python2.7

# This is a demonstration script for Facebook Chat
# using the X-FACEBOOK-PLATFORM SASL mechanism.
# It requires pyfacebook and pyxmpp to be installed.

# This client only works for desktop applications (configured in the
# developer app), and uses the old-style auth.getSession mechanism to get a
# Facebook session.  For newer-style or web apps, only the
# `get_facebook_client` function should have to change.

import sys, os, threading


def get_facebook_client():
        import facebook
        # Replace these with your app's credentials
        api_key = '147201912033054'
        secret_key = '61ef5734be20d29715ef1133e9456834'

        client = facebook.Facebook(api_key, secret_key)

        try:
                # Try to read cached credentials from the session-key file.
                # If authorization fails, you should delete this file and start of.
                handle = open('session-key', 'r')
                client.uid, client.session_key, client.secret = [ line.strip() for line in handle ]
                handle.close()
        except IOError:
                client.auth.createToken()
                client.login()
                print 'Log in to the app in your browser, then press enter.'
                raw_input()
                client.auth.getSession()
                handle = open('session-key', 'w')
                print >> handle, client.uid
                print >> handle, client.session_key
                print >> handle, client.secret
                handle.close()

        if not int(client.users.hasAppPermission('xmpp_login')):
                import webbrowser
                webbrowser.open(client.get_url('authorize',
                                               ext_perm = 'xmpp_login',
                                               api_key = client.api_key,
                                               v = '1.0'))
                print 'Grant the extended permission to the app in your browser, then press enter.'
                raw_input()

        return client

from pyxmpp.sasl.core import ClientAuthenticator
from pyxmpp.sasl.core import Response, Failure, Success

class XFacebookPlatformClientAuthenticator(ClientAuthenticator):
        def __init__(self, password_manager, fb_client=None):
                ClientAuthenticator.__init__(self, password_manager)
                if fb_client is None:
                        global global_fb_client
                        fb_client = global_fb_client
                self._fb_client = fb_client

        def start(self, ignored_username, ignored_authzid):
                return Response()

        def challenge(self, challenge):
                in_params = dict([part.split('=') for part in challenge.split('&')])
                out_params = {'nonce': in_params['nonce']}
                out_params = self._fb_client._add_session_args(out_params)
                out_params = self._fb_client._build_post_args(in_params['method'], out_params)
                import urllib
                return Response(urllib.urlencode(out_params))

        def finish(self,data):
                return Success(None)

from pyxmpp.all import JID, Presence, Message
from pyxmpp.client import Client

class FacebookChatClient(Client):
        def __init__(self, to_uid, message, **kwargs):
                Client.__init__(self, **kwargs)
                self.to_uid = to_uid
                self.message = message
                self.sent = False

        def session_started(self):
                self.get_stream().set_message_handler('chat', self.got_message)
                self.get_stream().send(Presence())

        def idle(self):
                Client.idle(self)
                if self.session_established and not self.sent:
                        self.sent = True
                        target = JID('-' + self.to_uid, self.jid.domain)
                        self.get_stream().send(Message(to_jid=target, body=unicode(self.message)))

        def got_message(self, stanza):
                stanza_body = stanza.get_body()
                if(stanza_body == None):
                        print str(stanza.get_from().node) + " is typing..."
                else:
                        print stanza.get_from().node, ':', stanza_body
		#stanza.get_from().node is their UUID
	
        def send_message(self,uid,msg):
                target = JID('-' + self.to_uid, self.jid.domain)
                self.get_stream().send(Message(to_jid=target, body=unicode(msg)))

        def connect_and_loop(self):
                print 'Connecting...'
                self.connect()
                
                print 'Processing...'
                writethread = threading.Thread(target=self.sendpoll)
                writethread.daemon = True
                writethread.start()
                try:
                        self.loop(1)
                finally:
                        self.disconnect()

        def sendpoll(self):
                while 1:
                        msg = sys.stdin.readline()
                        if msg.strip() != '/quit':
                                self.send_message(self.to_uid, msg)
                        else:
                                self.disconnect()

def setup_chat(fb_client, uidarg=None, messarg=None):
        global global_fb_client
        global_fb_client = fb_client
        import pyxmpp.sasl
        pyxmpp.sasl.all_mechanisms_dict['X-FACEBOOK-PLATFORM'] = (XFacebookPlatformClientAuthenticator, None)

        try:
                my_uid = str(global_fb_client.uid)
                if uidarg == None:
                        to_uid = sys.argv[1]
                else:
                        to_uid = uidarg
                my_jid = '-' + my_uid + '@chat.facebook.com/TestClient'
        except IndexError:
                sys.exit('usage: %s {to_uid} {message}' % sys.argv[0])

        print 'Creating stream...'
        xmpp_client = FacebookChatClient(
                to_uid = to_uid,
                message = None,
                jid = JID(my_jid),
                password = u'ignored',
                auth_methods = ['sasl:X-FACEBOOK-PLATFORM'],
                #server = 'localhost'
                )
        return xmpp_client

if __name__ == "__main__":
        print 'Preparing Facebook client...'
        global_fb_client = get_facebook_client()
        setupChat()
