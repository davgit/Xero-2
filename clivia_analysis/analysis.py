# -*- encoding: utf-8 -*-

from osv import fields, osv
from datetime import datetime
import time
from tools import DEFAULT_SERVER_DATETIME_FORMAT


class stocked_product(osv.osv):
    _name = 'clivia_analysis.stocked_product'
    _description = '君子兰产品'
    _rec_name = 'name'
    
    _columns = {
        'name': fields.char('名称', size=40, required=True),
        'code':fields.char('货号', size=40, required=True),
        'barcode':fields.char('条码', size=40),
    }

class monthly_plan(osv.osv):
    _name = 'clivia_analysis.monthly_plan'
    _rec_name = 'name'
    
    _columns = {
        'name': fields.char('编号', size=64, readonly=True),
        'date_created': fields.date('制定时间', readonly=True),
        'date_month':fields.char('月份', size=12, readonly=True),
        'reporter_id': fields.many2one('res.users', '制定人', readonly=True),
        'plan_line': fields.one2many('clivia_analysis.monthly_plan_line', 'plan_id', '计划明细'),
    }
    
    _defaults = {
        'reporter_id': lambda obj, cr, uid, context: uid,
        'date_created': lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        'date_month': lambda *a: time.strftime('%Y-%m'),
    }
    
    def _get_seq(self, cr, uid):
        obj_sequence = self.pool.get('ir.sequence')
        name = obj_sequence.get(cr, uid, 'clivia_analysis.monthly_plan')
        return name
    
    def create(self, cr, uid, vals, context=None):
        try:
            vals['name'] = self._get_seq(cr, uid)
            id = super(monthly_plan, self).create(cr, uid, vals, context)
            return id
        except Exception as e:
            raise osv.except_osv('错误', '每月只能提交一次计划.')
    
    def copy(self, cr, uid, id, default={}, context=None):
        try:
            default.update({
                'name':self._get_seq(cr, uid),
                'date_month':time.strftime('%Y-%m'),
            })
            res_id = super(monthly_plan, self).copy(cr, uid, id, default, context=context)
            return res_id
        except Exception as e:
            raise osv.except_osv('错误', '每月只能提交一次计划.')
    
    _sql_constraints = [
        ('date_month_uniq', 'unique(date_month)', '每月只能提交一次计划!'),
    ]

class monthly_plan_line(osv.osv):
    _name = 'clivia_analysis.monthly_plan_line'
    _description = '月度计划明细'
    _columns = {
        'date_created': fields.date('制定时间', required=True, readonly=True),
        'plan_id': fields.many2one('clivia_analysis.monthly_plan', 'Plan Reference', required=True, ondelete='cascade', select=True),
        'product_id': fields.many2one('clivia_analysis.stocked_product', '产品', change_default=True , select=True, required=True),
        'hefei_warning_level':fields.float('君子兰警戒库存', digits=(16, 0)),
        'sanhe_warning_level':fields.float('三河警戒库存', digits=(16, 0)),
        'production':fields.float('月计划产量', digits=(16, 0)),
        'note':fields.char('附注', size=100),
    }
    
    _defaults = {
        'date_created': lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
    }

class daily_report(osv.osv):
    _name = 'clivia_analysis.daily_report'
    _description = '每日报表'
    _rec_name = 'date_created'
    
    def _inventory_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for report in self.browse(cr, uid, ids, context=context):
            res[report.id] = {
                'sanhe_total': 0.0,
                'hefei_total': 0.0,
            }
            s = h = 0
            for line in report.report_line:
                h = h + line.hefei_today_inventory
                s = s + line.sanhe_real_inventory
        
            res[report.id]['sanhe_total'] = s
            res[report.id]['hefei_total'] = h
        
        return res
    
    
    _columns = {
        'name': fields.char('编号', size=64, readonly=True),
        'date_created': fields.date('上报时间', required=True, readonly=True),
        'date_confirmed': fields.date('审核时间', readonly=True),
        'reporter_id': fields.many2one('res.users', '上报人', readonly=True),
        'confirmer_id': fields.many2one('res.users', '审核人', readonly=True),
        'report_line': fields.one2many('clivia_analysis.daily_report_line', 'report_id', '报表明细'),
        'sanhe_total': fields.function(_inventory_all, method=True, string='三河总计', multi='sums'),
        'hefei_total': fields.function(_inventory_all, method=True, string='合肥总计', multi='sums'),
        'state': fields.selection([('draft', '未审核'), ('review', '已审核')], '状态', readonly=True),
        'note':fields.text('附注'),
    }
    _sql_constraints = [
        ('date_created_uniq', 'unique(date_created)', '每天只能提交一次报表!'),
    ]
    
    
    def _get_seq(self, cr, uid):
            #obj_sequence = self.pool.get('ir.sequence')
            name = self.pool.get('ir.sequence').get(cr, uid, 'clivia_analysis.daily_report')
            return name
    
    def create(self, cr, uid, vals, context=None):
        try:
            vals['name'] = self._get_seq(cr, uid)
            id = super(daily_report, self).create(cr, uid, vals, context)
        
            return id
        except Exception as e:
            raise osv.except_osv('错误', '每天只能提交一次报表.')
    
    def copy(self, cr, uid, id, default={}, context=None):
        try:
            default.update({
                'name':self._get_seq(cr, uid),
                'date_created':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            })
            res_id = super(daily_report, self).copy(cr, uid, id, default, context=context)
            return res_id
        except Exception as e:
            raise osv.except_osv('错误', '每天只能提交一次报表.')

    def dr_review(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 
            'state': 'review', 
            'confirmer_id': uid, 
            'date_confirmed': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            }
        )
        return True

    _defaults = {
           'date_created': lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
           'reporter_id': lambda obj, cr, uid, context: uid,
           'state': lambda *a: 'draft',
           #'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'clivia_analysis.daily_report'),
       }

class daily_report_line(osv.osv):
    _name = 'clivia_analysis.daily_report_line'
    _description = '报表明细'

    def hefei_changed(self, cr, uid, ids, hefei_last_inventory, produced, sent):
        v = {'hefei_today_inventory' : (hefei_last_inventory+produced-sent)}
        return {'value':v}
    
    def sanhe_changed(self, cr, uid, ids, sanhe_last_inventory, sold, sent):
        num = (sanhe_last_inventory+sent-sold)
        v = {'sanhe_today_inventory' : num, 'sanhe_real_inventory': num}
        return {'value':v}

    _columns = {
          'date_created': fields.date('上报时间', required=True, readonly=True),
          'report_id': fields.many2one('clivia_analysis.daily_report', 'Report Reference', required=True, ondelete='cascade', select=True),
          'product_id': fields.many2one('clivia_analysis.stocked_product', '产品', change_default=True , select=True, required=True),

          'hefei_last_inventory':fields.float('原库存', digits=(16, 0)),
          'produced': fields.float('日产量', digits=(16, 0)),
          'sent': fields.float('发出', digits=(16, 0)),
          'hefei_today_inventory': fields.float('君子兰结存', digits=(16, 0)),

          'sanhe_last_inventory':fields.float('原库存', digits=(16, 0)),
          'sold': fields.float('发送', digits=(16, 0)),        
          'sanhe_today_inventory': fields.float('三河结存', digits=(16, 0)),
          'sanhe_real_inventory': fields.float('实际库存', digits=(16, 0)),

          'notes': fields.text('附注'),
      }
      
    _defaults = {
             'date_created': lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
         }


# raise osv.except_osv(_('Error'), _('No rate found \n' \
#         'for the currency: %s \n' \
#         'at the date: %s') % (currency_symbol, date))
