# encoding: utf-8

from osv import osv
from osv import fields
import time,tools,xmlrpclib,pooler

class users(osv.osv):
    """ Inherits users """
    _inherit = 'res.users'

    _columns = {
        'end_date': fields.datetime('Connection End', readonly=True),
    }
    
    def login(self, db, login, password):
        
        super(users, self).login(db, login, password)
        
        if not password:
            return False
        cr = pooler.get_db(db).cursor()
        try:
            # autocommit: our single request will be performed atomically.
            # (In this way, there is no opportunity to have two transactions
            # interleaving their cr.execute()..cr.commit() calls and have one
            # of them rolled back due to a concurrent access.)
            # We effectively unconditionally write the res_users line.
            cr.autocommit(True)
            # Even w/ autocommit there's a chance the user row will be locked,
            # in which case we can't delay the login just for the purpose of
            # update the last login date - hence we use FOR UPDATE NOWAIT to
            # try to get the lock - fail-fast
            cr.execute("""SELECT id from res_users
                          WHERE login=%s AND password=%s
                                AND active FOR UPDATE NOWAIT""",
                       (tools.ustr(login), tools.ustr(password)))
            cr.execute("""UPDATE res_users
                            SET date = now(),end_date = Null
                            WHERE login=%s AND password=%s AND active
                            RETURNING id""",
                       (tools.ustr(login), tools.ustr(password)))
        except Exception:
            # Failing to acquire the lock on the res_users row probably means
            # another request is holding it. No big deal, we don't want to
            # prevent/delay login in that case. It will also have been logged
            # as a SQL error, if anyone cares.
            cr.execute("""SELECT id from res_users
                          WHERE login=%s AND password=%s
                                AND active""",
                       (tools.ustr(login), tools.ustr(password)))
        finally:
            res = cr.fetchone()
            cr.close()
            if res:
                return res[0]
        return False

class web_home(osv.osv):
    
    _inherit = 'board.board'
    _description = "Web Home"
    
    _columns = {

    }
    
