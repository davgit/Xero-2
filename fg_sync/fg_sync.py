# -*- encoding: utf-8 -*-

from osv import osv
from osv import fields
import time
import xmlrpclib, pooler

class RPCProxyOne(object):
    def __init__(self, server, ressource):
        self.server = server
        local_url = 'http://%s:%d/xmlrpc/common'%(server.server_url,server.server_port)
        rpc = xmlrpclib.ServerProxy(local_url)
        self.uid = rpc.login(server.server_db, server.login, server.password)
        local_url = 'http://%s:%d/xmlrpc/object'%(server.server_url,server.server_port)
        self.rpc = xmlrpclib.ServerProxy(local_url)
        self.ressource = ressource
    def __getattr__(self, name):
        return lambda cr, uid, *args, **kwargs: self.rpc.execute(self.server.server_db, self.uid, self.server.password, self.ressource, name, *args)

class RPCProxy(object):
    def __init__(self, server):
        self.server = server
    def get(self, ressource):
        return RPCProxyOne(self.server, ressource)
        

class Config(object):
    def __init__(self, su, sp, sd, lo, ps):
        self.server_url = su
        self.server_port = sp
        self.server_db = sd
        self.login = lo
        self.password = ps


class fg_sync_scheduler(osv.osv):
    _name = "fg_sync.scheduler"
    _description = "order importing."
    
    _columns = {

    }
    
    
    def do_run_scheduler(self, cr, uid, ids=None, context=None):
        """Scheduler for event reminder
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of whatever’s IDs.
        @param context: A standard dictionary for contextual values
        """
        if context is None:
            context = {}
        
        try:
            pool1 = RPCProxy(Config('192.168.0.200', 8069, 'FG', 'admin','zaq1@WSX'))
            target_order_obj = pool1.get('fg_sale.order')
            target_order_line_obj = pool1.get('fg_sale.order.line')
        
            source_order_obj = self.pool.get('fg_sale.order')
            source_order_line_obj = self.pool.get('fg_sale.order.line')
        except:
            print 'can not connect to slave....'
            return True
        
        def do_pull():
            # get all that's not sync-ed
            print 'do pull......................'
            for order_id in source_order_obj.search(cr, uid, [('sync','=',False)]):
                order_data = source_order_obj.copy_data(cr, uid, order_id)
                order = source_order_obj.browse(cr, uid, [order_id])[0]
                
                order['sync'] = True
                order['state'] = order.state
                
                #save order first. get id
                id = target_order_obj.create(cr, order.user_id, order)
                print id,' added.'
        
        do_pull()
        
        return True
    
    
