#!/usr/bin/env python
# -*- coding: utf-8 -*-

from osv import osv, fields
import time
from time import strptime, strftime
import datetime

class order(osv.osv):
    _name = "cust_order"
    _description = "安徽省富光实业股份有限公司订制杯清单"
    
    
    def get_employee(self, cr, uid, context={}):
        obj = self.pool.get('hr.employee')
        ids = obj.search(cr, uid, [('user_id','=',uid)])
        res = obj.read(cr, uid, ids, ['id','name'], context)
        return res and res[0]['id'] or 0
    
     
     

    
    _columns = {
        'name': fields.char('单号', size=64, select=True ),
        'date_order': fields.date('日期', readonly=True, states={'draft':[('readonly',False)]}),
        'date_confirm': fields.date('审核日期', readonly=True),
        'user_id': fields.many2one('hr.employee', '填单人', select=True, readonly=True),
        'confirmer_id': fields.many2one('hr.employee', '业务经办人', select=True, readonly=True),
        'partner_id': fields.many2one('res.partner', '客户', readonly=True, states={'draft':[('readonly',False)]}, required=True, change_default=True),
        'contact':fields.char('联系人', size=64, readonly=True, states={'draft':[('readonly',False)]}),
        'phone':fields.char('联系电话', size=64, readonly=True, states={'draft':[('readonly',False)]}),
        'date_delivery':fields.date('交货日期', readonly=True, states={'draft':[('readonly',False)]}),
        'delivery_delivery':fields.char('交货地址', size=128, readonly=True, states={'draft':[('readonly',False)]}),
        'amount_paid': fields.float('已付金额', digits=(10,2), readonly=True, states={'draft':[('readonly',False)]}),
        'invoice_type':fields.char('发票类型',size=64, readonly=True, states={'draft':[('readonly',False)]}),
        'amount_left': fields.char('余额支付说明', size=64, readonly=True, states={'draft':[('readonly',False)]}),
        'delivery_method':fields.char('交货方式', size=64, readonly=True, states={'draft':[('readonly',False)]}),
        'delivery_fee':fields.char('运费承担方', size=64, readonly=True, states={'draft':[('readonly',False)]}),      
        'state': fields.selection([('draft', '未审核'), ('approve', '已审核'), ('done', '已核清'),('cancel','已取消')], '订单状态', readonly=True, select=True),
        'note': fields.text('备注'),
        #'order_id': fields.many2one('res.partner', '订单', required=True, select=True),
        'product_id': fields.many2one('product.product', '产品名称',change_default=True),
        'product_uom_qty': fields.float('数量', digits=(16,0)),
        'unit_price': fields.float('开票价', digits=(16,2)),
        'cust_price': fields.float('版费', digits=(16,2)),
        'subtotal_amount': fields.float('小计', digits=(16,4)),
        "date2":fields.date("截止"),
        "date3":fields.char("计算",size=64),
    } 
    
   
    
    
    _defaults = {
        'date_order': fields.date.context_today,
        'user_id': lambda self,cr,uid,context: self.get_employee(cr,uid,context),
        'state': lambda *a:'draft',
    }
    _sql_constraints = [
        ('name_value', 'unique(name)', "That contract is already registered in the system.")
    ]
    _order = 'id desc'
    
    
    
    def button_dummy(self, cr, uid, ids, context=None):
        pool1= RPCProxy(Config('localhost', 8000, 'fga', 'admin','123'))
        pool2= RPCProxy(Config('localhost', 8069, 'DEMO', 'admin','123'))
        user_obj1= pool1.get('lunch.category')
        user_obj2=pool2.get("lunch.category")
        user2_ids = user_obj2.search(cr, uid,[], offset=0, limit=None, order=None,context=None, count=False)
        user1_ids = user_obj1.search(cr, uid,[], offset=0, limit=None, order=None,context=None, count=False)
        #idea_id = user_obj1.create(cr, uid,{ 'name': 'www','description' : 'spam & eggs', 'category_id':"1"})
        #idea_id = user_obj2.create(cr, uid,{ 'name': 'www','description' : 'spam & eggs', 'category_id':"1"})
        #idea_write = user_obj.write(cr,uid,user_ids,{"state":"open"}),
        #idea_unlink = user_obj.unlink(cr, uid,range(6,30))
        #user2 = user_obj2.read(cr,uid,[33],[],context=None),
        #print user2
        #val=user_obj1.perm_read(cr,uid,[100])
        #print val
        #cr.execute('update lunch_category set create_date=%s where ID=%s',(val[0]["create_date"],102))
        #cr.execute('update lunch_category set create_date=%s where ID=%s',('2012-07-18 05:08:56.347',102))
        
        #val.update({"category_id":val["category_id"][0],"user_id":val["user_id"][0]})
        #val=val[0]
        #del val["child_ids"]
        #del val["complete_name"]
        #print user2
        #a=user_obj2.create(cr,uid,{"name":3})
        #print a
        
        #user1 = user_obj2.read(cr, uid,[a], []),
        #print user1
        #cr.execute('update lunch_category set id=%s where id=%s', (8,a))
        
        #a=user_obj2.write(cr,uid,[2],val,context=context)
        #user1 = user_obj1.read(cr, uid,user1_ids, []),
        create_date2=user_obj2.perm_read(cr,uid,user2_ids)
        create_date1=user_obj1.perm_read(cr,uid,user1_ids)
        maxdate1={}
        maxdate2={}
        for a in create_date2:
            if a["create_date"]>maxdate2:
                maxdate2=a["create_date"]
        for b in create_date1:
            if b["create_date"]>maxdate1:
                maxdate1=b["create_date"]
        user1_ids.sort()
        user2_ids.sort()
        
        for id1 in user1_ids:
                    if id1 not in user2_ids:
                        create_date1=user_obj1.perm_read(cr,uid,[id1])
                        print create_date1[0]["create_date"]
                        if create_date1[0]["create_date"]>maxdate2:
                                    val = user_obj1.read(cr,uid,id1,[])
                                    b=user_obj2.create(cr,uid,val,context=context)
                                    cr.execute('UPDATE lunch_category SET id=%s,create_date=%s WHERE id=%s',(id1,create_date1[0]["create_date"],b))
                                    cr.commit()
                        else :
                                    user_obj1.unlink(cr,uid,id1,context=context)
            


                       
        #将最大日期改成一致（创建时改不掉createdate,等第二次调用时同步最大ID的时间）
        #cr.execute('update lunch_category set create_date=%s where ID=%s',(maxdate1,user1_ids[-1]))
                    
                
                            
                    
        #print user2
        #user_obj1.unlink(cr,uid,[1],context=context)   
        #print user2_ids
        
        #user_obj2_id =user_obj2.browse(cr,uid,user2_ids,context=context)
        #print user2_ids
        
        #for a in user_obj2_id :
            #print a.name


     
        return True

                

order()




import xmlrpclib,pooler



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
        return RPCProxyOne(self.server,ressource)
        

class Config(object):
    def __init__(self, su, sp, sd, lo, ps):
        self.server_url = su
        self.server_port = sp
        self.server_db = sd
        self.login = lo
        self.password = ps
