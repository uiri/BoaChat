#!/usr/bin/python
# Copyright 2011 Uiri Noyb and Rafael Khan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os, threading, re, gobject
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
        while(1):
            try:
                client.auth.getSession()
                break
            except:
                pass
        handle = open('session-key', 'w')
        print >> handle, client.uid
        print >> handle, client.session_key
        print >> handle, client.secret
        handle.close()

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
        if chatbuff != None:
            self.buffr = chatbuff
        self.roster_array = []
        self.nametouid = None

    def session_started(self):
        self.get_stream().set_message_handler('chat', self.got_message)
        self.request_roster()
        p = Presence()
        self.get_stream().send(p)
    
    def roster_handler(self):
        roster = str(self.roster)
        querymatch = re.compile(".query(.+)roster..<item jid=\"-")
        roster = querymatch.sub("", roster)
        roster = roster.replace("</item></query>","")
        roster = roster.replace("</query>", "")
        roster = roster.replace("<item jid=\"-",",")
        roster = roster.replace("</item>", "")
        roster = roster.replace("@chat.facebook.com\" name=\"",":")
        subscriptmatch = re.compile("\" subscription\=\"both\"/?>")
        roster = subscriptmatch.sub("", roster)
        roster = roster.replace("</group>", "")
        roster = roster.replace("<group>", ":")
        tmp_roster_array = roster.split(",")
        for i in tmp_roster_array:
            i = i.split(":")
            self.roster_array.append(i)
        dictarray = []
        for i in self.roster_array:
            if len(i) > 2:
                dictarray.append([i[0], i[1]])
            else:
                dictarray.append(i)
        self.nametouid = dict(dictarray)
        return self.roster_array

    def idle(self):
        Client.idle(self)

    #HANDLER FOR A RECEIVED MESSAGE
    def got_message(self, stanza):
        if self.buffr != None:
            buffr = self.buffr.get_text(self.buffr.get_start_iter(),self.buffr.get_end_iter())
        else:
            buffr = None
        stanza_body = stanza.get_body()
        stanza_node = str(stanza.get_from().node).replace("-","")
        try:
            name = self.nametouid[stanza_node]
        except:
            name = stanza_node
        if(stanza_body == None):
            #gui to show this as tooltip? show/hide dynamic element below buffer?
            if buffr == None:
                print name + " is typing...\n"
        else:
            msgtxt = "[" + datetime.now().strftime("%H:%M:%S") + "] <" + name + "> " + stanza_body + "\n"
            if buffr != None:
                addtext = buffr + msgtxt
                gobject.idle_add(self.buffr.set_text, addtext)
            else:
                print msgtxt
            logtext = "[" + datetime.now().strftime("%b %d %Y %H:%M:%S") + "] <" + name + "> " + stanza_body +"\n"
            self.write_log(stanza_node, logtext)
		#stanza.get_from().node is their UID

    def send_message(self,uid,msg):
        target = JID('-' +  uid, self.jid.domain)
        self.get_stream().send(Message(to_jid=target, body=unicode(msg)))

    def write_log(self,uid,logtext):
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
        _file = open(uid+"_log.txt","a+")
        _file.write(logtext)
        _file.close()
    

    def connect_and_loop(self):
        print 'Connecting...'
        self.connect()
        print 'Processing...'
        try:
            self.loop(1)
        finally:
            self.disconnect()

def setup_chat(fb_client, buffr=None, uidarg=None, messarg=None):
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
