import gtk, fbchatlib, threading

def delete_event(something, els):
    return False

def destroy_window(lol):
    gtk.main_quit()

mainwindow = gtk.Window()
mainwindow.set_default_size(500,500)
mainwindow.connect("delete_event", delete_event)
mainwindow.connect("destroy", destroy_window)
mainbox = gtk.VBox(False, 0)
mainscroll = gtk.ScrolledWindow()
mainbuffer = gtk.TextBuffer()
mainview = gtk.TextView(mainbuffer)
mainhbox = gtk.HBox(False, 0)
mainmessage = gtk.Entry()
mainbutton = gtk.Button('Send')

client = fbchatlib.get_facebook_client()
xmpp_client = fbchatlib.setup_chat(client, mainbuffer)

def send_message_gui(first, second, third, fourth):
    xmpp_client.send_message(third, fourth)

mainbutton.connect("clicked", send_message_gui, xmpp_client, None, mainmessage.get_text())
mainmessage.connect("activate", send_message_gui, xmpp_client, None, mainmessage.get_text())

mainview.set_editable(False)
mainhbox.pack_start(mainmessage, True, True, 0)
mainhbox.pack_start(mainbutton, False, True, 0)
mainscroll.add(mainview)
mainscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
mainbox.pack_start(mainscroll, True, True, 0)
mainbox.pack_start(mainhbox, False, False, 0)
mainwindow.add(mainbox)
mainwindow.show_all()
loopthread = threading.Thread(target=xmpp_client.connect_and_loop)
loopthread.daemon = True
loopthread.start()
gtk.main()
