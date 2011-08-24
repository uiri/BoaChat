import fb, sys
import pyxmpp.sasl
from pyxmpp.all import JID

client = fb.get_facebook_client()
my_uid = str(client.uid)
print "Put in the UID of who you want to talk to:"
to_uid = sys.stdin.readline()
print "First message:"
message = sys.stdin.readline()
my_jid = "-" + my_uid + '@chat.facebook.com/netcat'
pw = pyxmpp.sasl.core.PasswordManager()
pw.get_password(my_uid)
pyxmpp.sasl.all_mechanisms_dict['X-FACEBOOK-PLATFORM'] = \
            (fb.XFacebookPlatformClientAuthenticator(pw, fb_client=client), None)
xmpp_client = fb.FacebookChatClient( to_uid       = to_uid,
                                     message      = message,
                                     jid          = JID(my_jid),
                                     password     = u'ignored',
                                     auth_methods =['sasl:X-FACEBOOK-PLATFORM'],
                                   )
xmpp_client.connect()
try:
    xmpp_client.loop(1)
finally:
    xmpp_client.disconnect()
