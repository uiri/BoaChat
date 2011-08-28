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

import gtk, fbchatlib, threading, time, gobject

gobject.threads_init()

def delete_event(something, els):
    return False

def destroy_window(lol):
    gtk.main_quit()

def send_message_gui(whatever):
    try:
        rosterrow, rosterdata = rosterview.get_selection().get_selected()
        touid = nametouid[rosterrow.get_value(rosterdata, 0)]
    except:
        raise
    xmpp_client.send_message(touid,mainmessage.get_text())
    mainmessage.set_text("")

def fill_roster(client):
    while(1):
        if client.roster != None:
            break
        else:
            pass
    roster_array = client.roster_handler()
    group_list = []
    dictarray = []
    for i in roster_array:
        if len(i) > 2:
            dictarray.append([i[1], i[0]])
        else:
            dictarray.append(i)
    global nametouid
    nametouid = dict(dictarray)
    for i in roster_array:
        if len(i) > 2:
            groups = True
    storearray = []
    if groups:
        grouplist = ['Friends']
    for i in roster_array:
        if groups:
            try:
                storearray.append([i[1], i[2]])
                try:
                    grouplist.index(i[2])
                except:
                    grouplist.append(i[2])
            except:
                storearray.append([i[1], "Friends"])
        else:
            storearray.append(i[1])
    if groups:
        groupstoredict = {}
        for g in grouplist:
            treeiter = rosterstore.append(None, [g])
            groupstoredict[g] = treeiter
    for i in storearray:
        if groups:
            rosterstore.append(groupstoredict[i[1]], [i[0]])
        else:
            rosterstore.append(None, [i])

mainwindow = gtk.Window()
mainwindow.set_default_size(500,500)
mainwindow.connect("delete_event", delete_event)
mainwindow.connect("destroy", destroy_window)
mainbox = gtk.HBox(False, 0)
chatbox = gtk.VBox(False, 0)
mainscroll = gtk.ScrolledWindow()
mainbuffer = gtk.TextBuffer()
mainview = gtk.TextView(mainbuffer)
mainview.set_wrap_mode(gtk.WRAP_WORD_CHAR)
chathbox = gtk.HBox(False, 0)
mainmessage = gtk.Entry()
mainbutton = gtk.Button('Send')

rosterstore = gtk.TreeStore(gobject.TYPE_STRING)
rosterview = gtk.TreeView(rosterstore)
rosterscroll = gtk.ScrolledWindow(None, None)
rosterscroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
rosterscroll.add(rosterview)
rostercell = gtk.CellRendererText()
rostercolumn = gtk.TreeViewColumn("Friend", rostercell, text=0)
rosterview.append_column(rostercolumn)

client = fbchatlib.get_facebook_client()
xmpp_client = fbchatlib.setup_chat(client, mainbuffer)

mainbutton.connect("clicked", send_message_gui)
mainmessage.connect("activate", send_message_gui)

mainview.set_editable(False)
chathbox.pack_start(mainmessage, True, True, 0)
chathbox.pack_start(mainbutton, False, True, 0)
mainscroll.add(mainview)
mainscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
chatbox.pack_start(mainscroll, True, True, 0)
chatbox.pack_start(chathbox, False, False, 0)
mainbox.pack_start(rosterscroll, False, False, 0)
mainbox.pack_start(chatbox, True, True, 0)
mainwindow.add(mainbox)
mainwindow.show_all()
loopthread = threading.Thread(target=xmpp_client.connect_and_loop)
loopthread.daemon = True
loopthread.start()
rosterthread = threading.Thread(target=fill_roster, kwargs={'client' : xmpp_client})
rosterthread.daemon = True
rosterthread.start()
gtk.main()
