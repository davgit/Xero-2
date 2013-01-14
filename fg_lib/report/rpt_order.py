# -*- encoding: utf-8 -*-

import time
from report import report_sxw
from osv import osv


class rpt_order(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(rpt_order, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            })
            
            
report_sxw.report_sxw('report.order_rpt_order','cust_order','addons/FG_SALE_/report/rpt_order.rml',parser=rpt_order,header=False)

