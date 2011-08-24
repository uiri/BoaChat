import fbchatlib, sys
import pyxmpp.sasl
from pyxmpp.all import JID

print "Put in the UID of who you want to talk to:"
uid = sys.stdin.readline()
print "First message:"
mess = sys.stdin.readline()
client = fbchatlib.get_facebook_client()
fbchatlib.setupChat(client, uid.strip(), mess.strip())
