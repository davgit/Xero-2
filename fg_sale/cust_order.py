# -*- encoding: utf-8 -*-
import pooler, time
from osv import fields, osv
from tools import get_initial



class cust_order(osv.osv):
    _name = "fg_sale.cust.order"
    _description = "富光销售部定制杯清单"
    
    def _get_logs(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        log_obj = self.pool.get('res.log')
        
        for id in ids:
            logs = log_obj.search(cr, uid, [('res_model','=','fg_sale.cust.order'),('res_id', '=', id)])
            if logs:
                res[id] = logs
            else:
                res[id] = False
    
        return res
        
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = { 'amount_total':0.0 }
            amount = 0
            for line in order.order_line:
                amount = amount + line.subtotal_amount
            res[order.id]['amount_total'] = amount
        return res
    
    _columns = {
        'name': fields.char('单号', size=64, select=True, readonly=True),
        'date_order': fields.date('日期', required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'date_confirm': fields.date('审核日期', readonly=True, select=True),
        'due_date_from':fields.function(lambda *a,**k:{}, method=True, type='date',string="开始日期"),
        'due_date_to':fields.function(lambda *a,**k:{}, method=True, type='date',string="结束日期"),
        
        'user_id': fields.many2one('res.users', '填单人', select=True, readonly=True),
        'confirmer_id': fields.many2one('res.users', '业务接单人', select=True, readonly=True),
        'partner_id': fields.many2one('res.partner', '客户', readonly=True, states={'draft': [('readonly', False)]}, change_default=True, select=True),
        'client': fields.char('客户', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'contact':fields.char('联系人', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'phone':fields.char('联系电话', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'date_delivery':fields.date('交货日期', readonly=True, states={'draft': [('readonly', False)]}),
        'date_arrival_req':fields.date('要求到货日期', readonly=True, states={'draft': [('readonly', False)]}),
        'delivery_addr':fields.char('交货地址', size=128, readonly=True, states={'draft': [('readonly', False)]}),
        'amount_paid': fields.float('已付金额', digits=(10,2), readonly=True, states={'draft': [('readonly', False)]}),
        
        'type':fields.selection([('common','普通单'),('partner','客户单')], '定制单类型', readonly=True, states={'draft': [('readonly', False)]}),
        'invoice_type':fields.selection([('none','不开票'),('common','普通发票'),('va','增值税发票')], '发票类型', readonly=True, states={'draft': [('readonly', False)]}),
        'invoice_title':fields.char('发票抬头', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        
        'amount_left_info': fields.char('余额支付说明', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'delivery_method':fields.char('交货方式', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'delivery_fee':fields.char('运费承担方', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        
        'amount_total': fields.function(_amount_all, string='金额', store=False, multi='sums'),
        'order_line': fields.one2many('fg_sale.cust.order.line', 'order_id', '订单明细', readonly=True, states={'draft': [('readonly', False)]}),
        'logs':fields.function(_get_logs, type="one2many", readonly=True, relation="res.log"),
        
        'state': fields.selection([('draft', '未审核'), ('submit', '已提交'), ('review', '已审核'),], '订单状态', readonly=True, select=True),
        'note': fields.text('备注'),
        'cust_orders':fields.one2many('fg_sale.order', 'cust_order_id', '关联业务单', required=False),
        'reset':fields.boolean('是否打回'),
    }
    
    
    def create(self, cr, uid, vals, context=None):
        if not vals.get('partner_id') and not vals.get('client'):
            raise osv.except_osv('没有填写客户名称', '请填写客户名称.')
        
        if not vals.has_key('name'):
            obj_sequence = self.pool.get('ir.sequence')
            vals['name'] = obj_sequence.get(cr, uid, 'fg_sale.cust.order')
            
            
        id = super(cust_order, self).create(cr, uid, vals, context)
        #self.log(cr, uid, id, '创新了新的订单 %s' % vals['name'],'由用户%s'%uid, context)
        
        return id
    
    def write(self, cr, uid, ids, vals, context=None):
        
        for o in self.browse(cr, uid, ids):
            if not o.partner_id and not o.client:
                raise osv.except_osv('没有填写客户名称', '请填写客户名称.')
        
        return super(cust_order, self).write(cr, uid, ids, vals, context)
    
    
    _defaults = {
        'date_order': fields.date.context_today,
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'type': 'common',
    }
    
    def copy(self, cr, uid, id, default={}, context=None):
        raise osv.except_osv('不允许复制', '订单不允许复制.')


    def button_dummy(self, cr, uid, ids, context=None):

        return True

    def button_submit(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 
            'state': 'submit',
            'reset':False,
            }
        )
        for o in self.browse(cr, uid, ids):
            self.log(cr, uid, o.id, '定制单 %s 提交到业务部' % o.name, '由用户 %s 操作.'% uid, context)
        
        return True
    
    def button_review(self, cr, uid, ids, context=None):
        id_dict = {u'真空事业部':448, u'玻璃事业部':447, u'塑胶事业部':446, u'安全帽事业部':729}

        sale_dep_id = 65
        default_uom_id = 11
        
        self.write(cr, uid, ids, {
            'state': 'review',
            'date_confirm':fields.date.context_today(self, cr, uid, context=context),
            'confirmer_id':uid,
            }
        )
        # create order lines.
        # calculate fee.
        order_obj = self.pool.get('fg_sale.order')
        order_line_obj = self.pool.get('fg_sale.order.line')
        product_obj = self.pool.get('product.product')
        partner_obj = self.pool.get('res.partner')
        
        
        order_id = 1
        
        for co in self.browse(cr, uid, ids):
            order_data = {}
            order_data['note'] = co.note or ''
            
            if co.type == 'common':
                order_data['partner_id'] = sale_dep_id
                order_data['note'] = co.client + ' ' + order_data['note']
                
            elif co.type =='partner':
                order_data['partner_id'] = co.partner_id.id
            
            addr = partner_obj.address_get(cr, uid, [order_data['partner_id']], ['default'])['default']
            order_data['partner_shipping_id'] = addr
            
            order_id = order_obj.create(cr, uid, order_data)
            
            self.write(cr, uid, [co.id], {'ref_order_id':order_id})

            #lines.
            for line in co.order_line:
                line_data = {
                    'order_id':order_id,
                    'product_id':line.product_id.id,
                    'product_uom_qty':line.product_uom_qty,
                    'product_uom': default_uom_id, 
                    'unit_price':line.unit_price,
                    'aux_qty':line.product_uom_qty,
                    'note':line.note or '',
                }
                
                line_data['subtotal_amount'] = line.unit_price * line.product_uom_qty + line.extra_amount
                if line.extra_amount:
                    #print line_data['note']
                    line_data['note'] = line_data['note'] + ('. 包含附加费 %s' % line.extra_amount)
                
                order_line_obj.create(cr, uid, line_data)
                
                if line.cust_price and id_dict.get(line.product_id.source):
                    
                    cust_line_date = {
                        'order_id':order_id,
                        'product_id':id_dict.get(line.product_id.source),
                        'product_uom_qty':1,
                        'product_uom': default_uom_id,
                        'unit_price':line.cust_price,
                        'aux_qty':1,
                        'subtotal_amount':line.cust_price,
                    }
                    order_line_obj.create(cr, uid, cust_line_date)
                    
            self.log(cr, uid, co.id, '定制单 %s 已经生成业务单' % co.name, '由用户 %s 操作.'% uid, context)
            
        action = {
            'type': 'ir.actions.act_window',
            'name': '业务单',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'fg_sale.order',
            'res_id': order_id,
            'context': context,
        }
        return action

    
    def button_reset(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 
            'state': 'draft',
            'reset':True,
            }
        )
        for o in self.browse(cr, uid, ids):
            self.log(cr, uid, o.id, '定制单 %s 打回到销售部' % o.name, '由用户 %s 操作.'% uid, context)
        
        return True
        

    _sql_constraints = [
        ('cust_order_name_uniq', 'unique(name)', '订单编号不能重复!'),
    ]

    _order = 'id desc'


class cust_order_line(osv.osv):
    _name = "fg_sale.cust.order.line"
    _description = "富光销售部定制杯清单"

    _columns = {
        'order_id': fields.many2one('fg_sale.cust.order', '订单', required=True, ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', '产品', required=True, domain=[('sale_ok', '=', True)], change_default=True),
        'product_uom_qty': fields.float('数量(只)', required=True, digits=(16,0)),
        'unit_price': fields.float('开票价', required=True, digits=(16,4)),
        'cust_price': fields.float('版费', required=True, digits=(16,4)),
        'extra_amount':fields.float('附加费用', digits=(16,4)),
        'subtotal_amount': fields.float('小计', digits=(16,4)),
        'note': fields.char('附注', size=100),
    }
    
    #def product_uom_qty_change(self, cr, uid, ids, context=None):
    #    return {'domain': {}, 'value':{'product_uom_qty':0, 'unit_price':0,
    #        'subtotal_amount':0}}
    
    def amount_change(self, cr, uid, ids, product_id, product_uom_qty, unit_price, cust_price, extra_amount, context=None):
        product_obj = self.pool.get('product.product')
        product = product_obj.browse(cr, uid, product_id, context=context)
        if unit_price>0 and unit_price < product.lst_price:
            #return {'warning':{'title':'价格警告', 'message':'输入的开票价低于出厂价, 请仔细检查。'}}
            raise osv.except_osv('价格警告', '输入的开票价低于出厂价, 请仔细检查。.')
        
        subtotal_amount = unit_price * product_uom_qty + cust_price + extra_amount

        return {'domain': {}, 'value':{'subtotal_amount':subtotal_amount}}

class sale_order(osv.osv):
    _inherit = 'fg_sale.order'
    _columns = {
        'cust_order_id': fields.many2one('fg_sale.cust.order', '原定制单', required=False),
    }