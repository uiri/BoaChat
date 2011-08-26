#!/usr/bin/python

import sys, os, threading, re, time
from datetime import datetime

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
        
        #This prevents the raw_input() call
        #used to wait for uses to authenticate
        while(1):
            if int(client.users.hasAppPermission('xmpp_login')):
                time.sleep(2) #Sleep for 2 seconds
            else:
                break
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

from pyxmpp.all import JID, Presence, Message, Iq
from pyxmpp.client import Client

class FacebookChatClient(Client):
    def __init__(self, chatbuff=None, **kwargs):
        Client.__init__(self, **kwargs)

    def session_started(self):
        self.get_stream().set_message_handler('chat', self.got_message)
        self.request_roster()
        p = Presence()
        self.get_stream().send(p)
    
    def roster_handler(self):
        roster = str(self.roster)
        roster = roster.replace("<query>","")
        roster = roster.replace("</query>","")
        roster = roster.replace("<item jid=\"-","")
        roster = roster.replace("@chat.facebook.com\" name=\"",":")
        roster = roster.replace("\" subscription=\"both\"/>",",")
        roster_array = roster.split(",")
        i = 0
        while(i < len(roster_array)):
            roster_array[i] = roster_array[i].split(":")
            i += 1
        return roster_array
    
    def idle(self):
        Client.idle(self)
        self.roster_handler()

    #HANDLER FOR A RECEIVED MESSAGE
    def got_message(self, stanza):
        #buffr = self.buffer.get_text()
        stanza_body = stanza.get_body()
        stanza_node = str(stanza.get_from().node).replace("-","")
        if(stanza_body == None):
            print str(stanza.get_from().node) + " is typing...\n"
        else:
            #self.buffer.set_text(buffr + stanza.get_from().node, ':', stanza_body + "\n")
            print  stanza_node+ "[" + str(datetime.now()) + "]" + stanza_body
            self.write_log(stanza_node  ,datetime.now(),stanza_body)
		#stanza.get_from().node is their UID

    def send_message(self,uid,msg):
        target = JID('-' +  uid, self.jid.domain)
        self.get_stream().send(Message(to_jid=target, body=unicode(msg)))

    def write_log(self,uid,time,msg):
#
#        **********************
#        THIS NEEDS TO BE FIXED
#        **********************
#
#        if(not str(os.curdir).endswith("logs")):
#            if(os.path.exists("logs")):
#                os.chdir("logs")
#            else:
#                os.mkdir("logs")
#                os.chdir("logs")
        _file = open(uid+"_log.txt","w")
        _file.write(uid+" ["+str(time)+"]"+str(msg))
        _file.close()
    

    def connect_and_loop(self):
        print 'Connecting...'
        self.connect()
        print 'Processing...'
        try:
            self.loop(1)
        finally:
            self.disconnect()

def setup_chat(fb_client, buffr, uidarg=None, messarg=None):
    global global_fb_client
    global_fb_client = fb_client
    import pyxmpp.sasl
    pyxmpp.sasl.all_mechanisms_dict['X-FACEBOOK-PLATFORM'] = (XFacebookPlatformClientAuthenticator, None)

    my_uid = str(global_fb_client.uid)
    my_jid = '-' + my_uid + '@chat.facebook.com/TestClient'

    print 'Creating stream...'
    xmpp_client = FacebookChatClient(
            chatbuff = buffr,
            jid = JID(my_jid),
            password = u'ignored',
            auth_methods = ['sasl:X-FACEBOOK-PLATFORM'],
            #server = 'localhost'
    )

    return xmpp_client

if __name__ == "__main__":
    print 'Preparing Facebook client...'
    global_fb_client = get_facebook_client()
    asd = setup_chat(global_fb_client, None)
    asd.connect_and_loop()
