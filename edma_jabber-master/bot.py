#!/usr/bin/python

import jabberbot

class StupidEchoBot(jabberbot.JabberBot):
    def bot_echo( self, mess, args):
        "The command description goes here"
        return 'You said: ' + args

    def bot_subscribe( self, mess, args):
        "HIDDEN (Authorize the presence subscription request)"
        # The docstring for this command has "HIDDEN" in it, so
        # the help output does not show this command.
        f = mess.getFrom()
        self.conn.Roster.Authorize( f)
        return 'Authorized.'

    def unknown_command( self, mess, cmd, args):
        "This optional method, if present, gets called if the\
        command is not recognized."
        if args.split()[0].startswith( 'cheese'):
            return 'Sorry, cheesy commands not available.'
        else:
            # if we return None, the default 'unknown command' text will get printed.
            return None

username = 'admin'
password = '123'

bot = StupidEchoBot(username, password)
bot.serve_forever()