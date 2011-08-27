import gtk, fbchatlib, threading, time, gobject

gobject.threads_init()

def delete_event(something, els):
    return False

def destroy_window(lol):
    gtk.main_quit()

def send_message_gui(first, second, third, fourth):
    xmpp_client.send_message(third, fourth)

def print_roster(client):
    while(1):
        time.sleep(7)
        print client.roster_handler()

mainwindow = gtk.Window()
mainwindow.set_default_size(500,500)
mainwindow.connect("delete_event", delete_event)
mainwindow.connect("destroy", destroy_window)
chatbox = gtk.VBox(False, 0)
mainscroll = gtk.ScrolledWindow()
mainbuffer = gtk.TextBuffer()
mainview = gtk.TextView(mainbuffer)
chathbox = gtk.HBox(False, 0)
mainmessage = gtk.Entry()
mainbutton = gtk.Button('Send')

client = fbchatlib.get_facebook_client()
xmpp_client = fbchatlib.setup_chat(client, mainbuffer)

mainbutton.connect("clicked", send_message_gui, xmpp_client, None, mainmessage.get_text())
mainmessage.connect("activate", send_message_gui, xmpp_client, None, mainmessage.get_text())

mainview.set_editable(False)
chathbox.pack_start(mainmessage, True, True, 0)
chathbox.pack_start(mainbutton, False, True, 0)
mainscroll.add(mainview)
mainscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
chatbox.pack_start(mainscroll, True, True, 0)
chatbox.pack_start(chathbox, False, False, 0)
mainwindow.add(chatbox)
mainwindow.show_all()
loopthread = threading.Thread(target=xmpp_client.connect_and_loop)
loopthread.daemon = True
loopthread.start()
rosterthread = threading.Thread(target=print_roster, kwargs={'client' : xmpp_client})
rosterthread.daemon = True
rosterthread.start()
gtk.main()
