# -*- encoding: utf-8 -*-

from report import report_sxw
from osv import osv
import tools
import sale_report

class fg_order_html(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fg_order_html, self).__init__(cr, uid, name, context)
        pass
    
class fg_order_notice_html(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fg_order_notice_html, self).__init__(cr, uid, name, context)
        pass

class fg_order_ship_html(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fg_order_ship_html, self).__init__(cr, uid, name, context)
        pass

report_sxw.report_sxw('report.fg_sale.order.html', 'fg_sale.order',
                      'addons/fg_sale/report/order.html',parser=fg_order_html)

report_sxw.report_sxw('report.fg_sale.order.notice.html', 'fg_sale.order',
                    'addons/fg_sale/report/notice.html',parser=fg_order_notice_html)
                    
report_sxw.report_sxw('report.fg_sale.order.ship.html', 'fg_sale.order',
                    'addons/fg_sale/report/ship.html',parser=fg_order_ship_html)
