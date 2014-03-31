#/usr/bin/env python
# -*- Mode: Python; coding: utf-8;
import httplib 
import urllib 
import urllib2
import time
import gtk
import gtk.glade
from history import History
from contacts import Contacts
def isInteger(number):
    ok = True
    try:
        int(number)
    except ValueError:
        ok = False
    return ok
class History_UI:
    def __init__(self, history=History(), contacts=Contacts()):
        self.result = None
        self.history = history
        self.contacts= contacts
        self.builder = gtk.Builder()
        self.builder.add_from_file("history.glade")
        self.window = self.builder.get_object("history_dialog")
        self.window.connect("destroy", self.on_cancel_clicked)
        self.builder.get_object("tool_ok").connect("clicked", self.on_ok_clicked)
        self.builder.get_object("tool_cancel").connect("clicked", self.on_cancel_clicked)
        self.builder.get_object("clear_history").connect("clicked", self.on_clear_history_clicked)
        self.ok = self.builder.get_object("ok")
        self.ok.connect("clicked", self.on_ok_clicked)
        self.cancel = self.builder.get_object("cancel")
        self.cancel.connect("clicked", self.on_cancel_clicked)
        self.treeview = self.builder.get_object("treeview")
        self.store = gtk.TreeStore(str, str)
        self.treeview.set_model(self.store)
        self.treeview.set_model(self.update_model(self.store))
        columns = ["Číslo","Text zprávy"]
        for i in range(0,len(columns)):
          column = gtk.TreeViewColumn(columns[i])
          cell = gtk.CellRendererText()
          column.pack_start(cell, True)
          column.add_attribute(cell, 'text', i)
          self.treeview.append_column(column)
        self.treeview.set_cursor(0)
    def update_model(self, model):
        model.clear()
        try:
          for i in self.history.list_all():
              model.append(None, [i[0], i[1]])
        except TypeError:
              print "No history stored"
        return model
    def on_ok_clicked(self, widget):
        cursor = self.treeview.get_cursor()[0]
        if cursor:
            try:
                cislo = int(self.treeview.get_model()[cursor[0]][0])
            except ValueError:
                cislo = Contacts().get_num(self.treeview.get_model()[cursor[0]][0])
            text = self.treeview.get_model()[cursor[0]][1]
            self.result = [cislo, text]
        self.window.hide()

    def on_cancel_clicked(self, widget):
        self.window.hide()
    def on_clear_history_clicked(self, widget):
        dialog = gtk.MessageDialog(
            buttons = gtk.BUTTONS_YES_NO,
            message_format = "Chcete smazat veškerou historii, bez možnosti návratu?"
        )
        #+9 je tu proto, že mi dialog vrací "-8 na True" a "-9 na False"
        #Takže to je Workaround :D
        response = dialog.run() + 9
        if response:
          self.history.clear()
        dialog.destroy()

class sms_sender:
    def __init__(self):
        self.history = History()
        self.contacts = Contacts()
        self.builder = gtk.Builder()
        self.builder.add_from_file("ui.glade")
        window = self.builder.get_object("window")
        self.message = self.builder.get_object("text")
        ###
        # Menu --> Connect
        self.builder.get_object("history").connect("activate", self.history_browsing)
        self.builder.get_object("contact").connect("activate", self.contact_browsing)
        ###
        window.show_all()
        window.connect("destroy", gtk.main_quit)
        ###
        cancel = self.builder.get_object("cancel")
        cancel.connect("clicked", gtk.main_quit)
        self.builder.get_object("exit").connect("activate", gtk.main_quit)
        ###
        ok = self.builder.get_object("ok")
        ok.connect("clicked", self.ok_clicked)
        ###
        self.check_box = self.builder.get_object("history_check")
        ###
        self.number = self.builder.get_object("number")
        # Doplňování
        self.completion = gtk.EntryCompletion()
        self.store = gtk.TreeStore(str, str)
        self.completion.set_model(self.store)
        self.update_model(self.store)
        # Model creating
        self.completion.set_text_column(0)
        name_cell = gtk.CellRendererText()
        self.completion.pack_start(name_cell)
        self.completion.add_attribute(name_cell, 'text', 1)
        self.number.set_completion(self.completion)
        gtk.main()
    def send(self, target, what):
        print "Sended"
        return True
        '''
        #############################################################''#'
        timestamp = int(time.time())
        data = {
            'timestamp' : timestamp,
            'action'    : 'send',
            'sendingProfile1' : 11,
            'sendingProfile2' : 20,
            'sendingProfile3' : 32,
            'textsms' : what,
            'cislo-prijemce' : target
        }
        try:
            data = urllib.urlencode(data) 
            print('http://www.poslatsms.cz/', data)   
            req = urllib2.Request('http://www.poslatsms.cz/', data) 
            response = urllib2.urlopen(req)
            the_page = str(response.read())
            if 'SMS zprávy přijaty k odeslání!' in the_page:
                return True
            return False
        except:
            return False
        '''
    def update_model(self, model):
        model.clear()
        #GET FROM CONTACTS
        #model.append(None, [str(733685973), "Ondra"])
        try:
          for i in self.contacts.list_all():
              model.append(None, [i[0], i[1]])
        except TypeError:
            print "No contacts stored"
        #GET FROM HISTORY
        try:
          for i in self.history.disctinct_contacts():
              model.append(None, [i[0], ""])
        except TypeError:
            print "History doesnt contain \"non-contact\" numbers"
        return model
    def info(self, msg):
        dialog = gtk.MessageDialog(None, 0,
                    gtk.MESSAGE_INFO,
                    gtk.BUTTONS_OK,
                    msg)
        choice = dialog.run()
        if choice != None:
            dialog.hide()      
    def alert(self, what, msg):
        #call alert from "what" with message "msg"
        dialog = gtk.MessageDialog(None, 0,
                    gtk.MESSAGE_WARNING,
                    gtk.BUTTONS_OK,
                    msg)
        choice = dialog.run()
        if choice != None:
            dialog.hide()
        what.grab_focus()
    def history_browsing(self, widget):
        self.history_window = History_UI()
        self.history_window.builder.get_object("history_dialog").run()
        if self.history_window.result:
          self.number.set_text(str(self.history_window.result[0]))
          self.message.get_buffer().set_text(self.history_window.result[1])
    def contact_browsing(self, widget):
        self.contact_window = Contacts_UI()
        
    def ok_clicked(self, widget):
        self.update_model(self.store)
        try:
            int(self.number.get_text())
            if (len(self.number.get_text()) != 9):
              self.alert(self.number, "Číslo příjemce není 9 místné číslo")
              return 1
        except ValueError:
            self.alert(self.number, "Číslo příjemce není 9 místné číslo")
            return 1
        self.text = self.message.get_buffer().get_text(self.message.get_buffer().get_start_iter(), self.message.get_buffer().get_end_iter())
        if (self.text == ""):
            self.alert(self.message, "Nelze odeslat prázdnou zprávu!")
            return 1
        if not(self.send(int(self.number.get_text()), self.text)):
            self.alert(self, None, "Chyba při odesílání! Změna enginu poskytovatele?")
        else:
            #self.info("Zpráva odeslána!")
            ###
            # ukládání do historie
            if (self.check_box.get_active()):
                self.history.add(int(self.number.get_text()), self.text)
            self.message.get_buffer().set_text("")
            self.number.set_text("")
            
class Contacts_UI:
    def __init__(self, history=History(), contacts=Contacts()):
        self.result = None
        self.history = history
        self.contacts= contacts
        self.builder = gtk.Builder()
        self.builder.add_from_file("contacts.glade")
        self.window = self.builder.get_object("window")
        self.window.connect("destroy", self.on_close_clicked)
        self.builder.get_object("close").connect("clicked", self.on_close_clicked)
        self.builder.get_object("add").connect("clicked", self.on_add_clicked)
        self.builder.get_object("remove").connect("clicked", self.on_remove_clicked)
        self.treeview = self.builder.get_object("treeview1")
        self.store = gtk.TreeStore(str, str)
        self.treeview.set_model(self.store)
        self.treeview.set_model(self.update_model(self.store))
        columns = ["Jméno","Číslo"]
        for i in range(0,len(columns)):
          column = gtk.TreeViewColumn(columns[i])
          cell = gtk.CellRendererText()
          column.pack_start(cell, True)
          column.add_attribute(cell, 'text', i)
          self.treeview.append_column(column)
        self.treeview.set_cursor(0)
        self.window.show_all()
    def update_model(self, model):
        model.clear()
        try:
          for i in self.contacts.list_all():
              model.append(None, [i[1], i[0]])
        except TypeError:
              print "No contacts stored"
        return model
    def on_add_clicked(self, widget):
        dialog = self.builder.get_object("add_contact")
        name = self.builder.get_object("jmeno")
        cislo = self.builder.get_object("cislo")
        response = dialog.run()
        while response:
          dialog.hide()
          if not response:
              break
          #if correct - close
          if ((name.get_text() != "") and (len(cislo.get_text()) == 9) and (isInteger(cislo.get_text()))):
              if not self.contacts.number_used(int(cislo.get_text())):
                  break
              else:
                  error = gtk.MessageDialog(
                      type = gtk.MESSAGE_ERROR,
                      buttons = gtk.BUTTONS_CLOSE,
                      message_format = "Číslo již bylo použito!"
                  )
                  error.run()
                  error.destroy()
                  response = dialog.run()
                
          #if not give another try
          else:
              error = gtk.MessageDialog(
              type = gtk.MESSAGE_ERROR,
              buttons = gtk.BUTTONS_CLOSE,
              message_format = "Číslo musí mít 9 číslic a jméno musí být neprázdné"
              )
              error.run()
              error.destroy()
              response = dialog.run()
        dialog.hide()
        if response:
            self.contacts.add(int(cislo.get_text()), name.get_text())
            self.treeview.set_model(self.update_model(self.store))
        name.set_text("")
        cislo.set_text("")
    def on_close_clicked(self, widget):
        self.window.hide()
    def on_remove_clicked(self, widget):
        cursor = self.treeview.get_cursor()[0]
        if cursor:
            cislo = self.treeview.get_model()[cursor[0]][1]
            jmeno = self.treeview.get_model()[cursor[0]][0]
        dialog = gtk.MessageDialog(
            buttons = gtk.BUTTONS_YES_NO,
            message_format = "Chcete smazat kontakt - '%s' s číslem '%s'" % (jmeno ,cislo)
        )
        response = dialog.run() + 9
        if response:
            self.contacts.remove(int(cislo), jmeno)
            self.treeview.set_model(self.update_model(self.store))
        dialog.destroy()

sms_sender()