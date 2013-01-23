# encoding: utf-8

from osv import osv
from osv import fields
import time,tools,xmlrpclib,pooler
from datetime import datetime

class xmpp(osv.osv):

    _name = "xmpp"

    _description = "Xmpp Xero"

    _columns = {
        
	'name': fields.char('JID',size=255),
        'password': fields.char('Password',size=255),
        'server': fields.char('Server', size=255),
        'port': fields.integer('Port'),
        'secure': fields.boolean('Secure'),
        'resource': fields.char('Resource', size=255),
    }

    _defaults = {
      'port': lambda *a: 7070,
      'secure': lambda *a: False,
    }