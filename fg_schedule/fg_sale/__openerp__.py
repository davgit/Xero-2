# -*- encoding: utf-8 -*-

{
    'name': '富光业务部销售',
    'version': '1.0',
    'category' : '富光',
    'description': """富光业务部销售子系统""",
    'author': 'Daniel',
    'website': 'http://www.ide.fm',
    'depends': ['base', 'board', 'product', 'fg_data'],
    'init_xml': [],
    'update_xml': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'wizard/order_import.xml',
        'wizard/report.xml',
        'report/sale_report_views.xml',
        'cust_order_view.xml',
        'fg_sale_view.xml',
        'sale_plan_view.xml',
        'fg_sale_sequence.xml',
        'board.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'application':True,
}