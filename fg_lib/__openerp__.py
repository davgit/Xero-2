#!/usr/bin/env python
# -*- encoding: utf-8 -*-



{
    "name": "富光定制单",
    "author": "FG",
    "version": "0.1",
    "depends": ["base",'hr','product'],
    "description": """富光销售部定制杯清单""",
    "website" : "http://www.openerp.cn",
    "init_xml": [],
    'category' : '富光',
    'complexity':"easy",
    "installable": True,
    'init_xml': [],
    'update_xml': ['order_view.xml',
                   'order_workflow.xml'],
    'active': False,
    
}

