import fbchatlib, sys
import pyxmpp.sasl
from pyxmpp.all import JID

print "Put in the UID of who you want to talk to:"
uid = sys.stdin.readline()
print "First message:"
mess = sys.stdin.readline()
client = fbchatlib.get_facebook_client()
xmpp_client = fbchatlib.setup_chat(client, uid.strip(), mess.strip())
xmpp_client.connect_and_loop()
