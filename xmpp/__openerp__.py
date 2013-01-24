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
    
    "depends": ["base"],
    
    "js":  [
            "../web/static/src/js/deploy/*.js",
            "static/js/strophe.js",
            "static/js/strophe.flxhr.js",
            "static/js/xmpp.js",
            ],
    
    'qweb' : [
        "static/xml/*.xml",
    ],   
    
    "css": ["static/css/*.css",],

    'auto_install': False,
    'application' : True,
    #'web_preload': False,
    
}
