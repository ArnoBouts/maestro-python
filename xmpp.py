import os
import slixmpp

def Send(message):

    if 'NOTIFY' in os.environ and os.environ['NOTIFY'] == 'true':

        jid = os.environ['NOTIFY_JID']
        password = os.environ['NOTIFY_PASSWORD']
        recipient = os.environ['NOTIFY_TO']

        x = SendMsg(jid, password, recipient, message)
        x.connect()
        x.process(forever=False)

class SendMsg(slixmpp.ClientXMPP):

    def __init__(self, jid, password, recipient, message):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.recipient = recipient
        self.msg = message

        self.add_event_handler('session_start', self.__send)


    def __send(self, event):
        self.send_presence()
        self.get_roster()

        self.send_message(mto=self.recipient, mbody=self.msg)

        self.disconnect()
