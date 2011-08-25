#!/usr/bin/python

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

<<<<<<< HEAD
    #HANDLER FOR A RECEIVED MESSAGE
=======
>>>>>>> b28b0b54055e537ecb92842d28e4fa299ee7c3eb
    def got_message(self, stanza):
        stanza_body = stanza.get_body()
        if(stanza_body == None):
            print str(stanza.get_from().node) + " is typing..."
        else:
            print stanza.get_from().node, ':', stanza_body
<<<<<<< HEAD

		#stanza.get_from().node is their UID

=======
            
            #stanza.get_from().node is their UUID
            
>>>>>>> b28b0b54055e537ecb92842d28e4fa299ee7c3eb
    def send_message(self,uid,msg):
        target = JID('-' +  to_uid, self.jid.domain)
        self.get_stream().send(Message(to_jid=target, body=unicode(msg)))

    def connect_and_loop(self):
        print 'Connecting...'
        self.connect()
                
        print 'Processing...'
<<<<<<< HEAD
=======
        writethread = threading.Thread(target=self.sendpoll)
        writethread.daemon = True
        writethread.start()
>>>>>>> b28b0b54055e537ecb92842d28e4fa299ee7c3eb
        try:
            self.loop(1)
        finally:
            self.disconnect()
<<<<<<< HEAD
=======

    def sendpoll(self):
        while 1:
            msg = sys.stdin.readline()
            if msg.strip() != '/quit':
                self.send_message(self.to_uid, msg)
            else:
                self.disconnect()
>>>>>>> b28b0b54055e537ecb92842d28e4fa299ee7c3eb

def setup_chat(fb_client, uidarg=None, messarg=None):
    global global_fb_client
    global_fb_client = fb_client
<<<<<<< HEAD
    try:
        import pyxmpp.sasl
        pyxmpp.sasl.all_mechanisms_dict['X-FACEBOOK-PLATFORM'] = (XFacebookPlatformClientAuthenticator, None)
    except:
        import pyxmpp2.sasl
        pyxmpp2.sasl.all_mechanisms_dict['X-FACEBOOK-PLATFORM'] = (XFacebookPlatformClientAuthenticator, None)

    my_uid = str(global_fb_client.uid)
    my_jid = '-' + my_uid + '@chat.facebook.com/TestClient'

    print 'Creating stream...'
    xmpp_client = FacebookChatClient(
            to_uid = None,
            message = None,
            jid = JID(my_jid),
            password = u'ignored',
            auth_methods = ['sasl:X-FACEBOOK-PLATFORM'],
            #server = 'localhost'
    )
=======
    import pyxmpp.sasl
    pyxmpp.sasl.all_mechanisms_dict['X-FACEBOOK-PLATFORM'] = (XFacebookPlatformClientAuthenticator, None)
    my_uid = str(global_fb_client.uid)
    if uidarg == None:
        to_uid = sys.argv[1]
    else:
        to_uid = uidarg
        my_jid = '-' + my_uid + '@chat.facebook.com/TestClient'

    print 'Creating stream...'
    xmpp_client = FacebookChatClient(
        to_uid = to_uid,
        message = None,
        jid = JID(my_jid),
        password = u'ignored',
        auth_methods = ['sasl:X-FACEBOOK-PLATFORM'],
        #server = 'localhost'
        )
>>>>>>> b28b0b54055e537ecb92842d28e4fa299ee7c3eb
    return xmpp_client

if __name__ == "__main__":
    print 'Preparing Facebook client...'
    global_fb_client = get_facebook_client()
    asd = setup_chat(global_fb_client)
    asd.connect_and_loop()
