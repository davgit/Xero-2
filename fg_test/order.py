#!/usr/bin/env python
# -*- coding: utf-8 -*-

from osv import osv, fields
import time

class order(osv.osv):
    _name = "cust_order"
    _description = "test"
    
    def get_employee(self, cr, uid, context={}):
        obj = self.pool.get('hr.employee')
        ids = obj.search(cr, uid, [('user_id','=',uid)])
        res = obj.read(cr, uid, ids, ['id','name'], context)
        return res and res[0]['id'] or 0
    
    def updateModule(self, cr, uid, ids, context={}):
        mod_obj = self.pool.get('ir.module.module')
        ids = mod_obj.search(cr, uid, [('name','=',self._module)])
        mod_obj.button_upgrade(cr, uid, ids)
        objs = self.pool.get('base.module.upgrade')
        objs.upgrade_module(cr, uid, ids, context=None)
        return True

    _columns = {
        'name': fields.char('单号', size=64,   select=True ),
        'date_order': fields.date('日期',   ),
        'date_confirm': fields.date('审核日期', ),
        'contact':fields.char('联系人', size=64,  ),
        'phone':fields.char('联系电话', size=64, ),
        'date_delivery':fields.date('交货日期', ),
        'delivery_delivery':fields.char('交货地址', size=128, ),
        'amount_paid': fields.float('已付金额', digits=(10,2), ),
        'invoice_type':fields.char('发票类型',size=64, ),
        'amount_left': fields.char('余额支付说明', size=64,),
        'delivery_method':fields.char('交货方式', size=64, ),
        'delivery_fee':fields.char('运费承担方', size=64, ),      
        'state': fields.selection([('draft', '未审核'), ('approve', '已审核'), ('done', '已核清'),('cancel','已取消')], '订单状态',  select=True),
        'note': fields.text('备注'),
        #'order_id': fields.many2one('res.partner', '订单',   select=True),
        'product_uom_qty': fields.float('数量',   digits=(16,0)),
        'unit_price': fields.float('开票价',   digits=(16,2)),
        'cust_price': fields.float('版费',   digits=(16,2)),
        'subtotal_amount': fields.float('小计', digits=(16,4)),
    } 

    _defaults = {
        'name': 'test'
    }
    _order = 'id desc'

order()

