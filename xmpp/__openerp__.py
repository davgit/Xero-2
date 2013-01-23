# encoding: utf-8
{
    "name": "XMPP",
    "category": "",
    "description":
        """
            OpenERP XMPP Xero.
        """,
    "version": "2.0",
    "init_xml": [],
    
    'update_xml': [
        "xmpp.xml",
    ],
    
    "depends": ["base",'web'],
    
    "js":  [
            "static/js/strophe.js",
            "static/js/xmpp.js",
            ],
    
    'qweb' : [
        "static/xml/*.xml",
    ],   
    
    "css": ["static/css/*.css",],

    'auto_install': False,
    #'web_preload': False,
    
}
