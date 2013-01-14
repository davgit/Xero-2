#!/usr/bin/env python
# -*- encoding: utf-8 -*-

{
    "name": "test unit",
    "author": "J.W",
    "version": "1.0",
    "category": "富光",
    "depends": ['base','web_ht'],
    "description": """test unit""",
    "website" : "http://www.openerp.cn",
    "init_xml": [],
    "installable": True,
    'init_xml': [],
    'update_xml': ['order_view.xml',],
    'active': False,
    'application':True,
    'js': ["static/src/js/forkit.js","static/src/js/test.js"],
    'css': ['static/src/css/test.css','static/src/css/stroll.min.css'],
    'qweb': [],
}

