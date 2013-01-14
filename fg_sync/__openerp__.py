# -*- encoding: utf-8 -*-

{
    'name': 'FG Order Scheduler',
    'version': '1.0',
    'category' : 'utils',
    'description': """FG Order Scheduler.
    Do install this on Master Name!!!!!""",
    'author': 'openerp',
    'website': 'http://www.openerp.org',
    'depends': ['base', 'fg_sale'],
    'init_xml': [],
    'update_xml': [
        'fg_sync.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'application':False,
}