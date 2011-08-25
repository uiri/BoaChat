import fbchatlib, sys


print "Put in the UID of who you want to talk to:"
uid = sys.stdin.readline()
client = fbchatlib.get_facebook_client()
xmpp_client = fbchatlib.setup_chat(client, uid.strip(), 'lol')
xmpp_client.connect_and_loop()
