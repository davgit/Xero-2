# -*- encoding: utf-8 -*-

import tools
from osv import fields, osv


class common_report(osv.osv):
    _name = "clivia_analysis.production_report"
    _description = "报表视图"
    
    _auto = False
    _rec_name = 'date'
    
    _columns = {
        'year': fields.char('年份', size=4, readonly=True),
        'month': fields.selection([('01', '一月'), ('02', '二月'), ('03', '三月'), ('04', '四月'), 
            ('05', '五月'), ('06', '六月'), ('07', '七月'), ('08', '八月'), ('09', '九月'), ('10', '十月'), 
            ('11', '十一月'), ('12', '十二月')], '月份', readonly=True),
        'date': fields.date('上报时间', required=True, readonly=True),
        'product_id': fields.many2one('clivia_analysis.stocked_product', '产品', readonly=True),
        'produced': fields.integer('生产', readonly=True),
        'sent': fields.float('发出', readonly=True),
        'sold': fields.integer('销售', readonly=True),
        'hefei_today_inventory':fields.integer('君子兰结存', readonly=True),
        'sanhe_last_inventory':fields.integer('三河实际库存', readonly=True),
    }
    
    _order = 'date desc'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'clivia_analysis_production_report')
        cr.execute("""
            CREATE OR REPLACE VIEW clivia_analysis_production_report AS 
             SELECT DISTINCT ON (product.id) product.id, product.id AS product_id, 
             mpl.production AS produced, 
             mpl.hefei_warning_level, 
             mpl.sanhe_warning_level, 
             drl.hefei_today_inventory AS hefei_today_inventory, 
             drl.sanhe_real_inventory AS sanhe_real_inventory, 
             dr.date_created date, 
             to_char(dr.date_created::timestamp with time zone, 'YYYY'::text) AS year, 
             to_char(dr.date_created::timestamp with time zone, 'MM'::text) AS month, 
             drl.sent, 
             drl.sold
               FROM clivia_analysis_stocked_product product
               JOIN clivia_analysis_daily_report_line drl ON product.id = drl.product_id
               JOIN clivia_analysis_daily_report dr ON dr.id = drl.report_id
               JOIN clivia_analysis_monthly_plan_line mpl ON mpl.product_id = product.id
              WHERE dr.state::text = 'review'::text
              ORDER BY product.id, dr.date_created DESC;
        """)
