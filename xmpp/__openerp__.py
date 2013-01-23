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
    "js": ["static/js/strophe.js","static/js/flXHR.js","static/js/strophe.flxhr.js",],
    'qweb' : [
        "static/xml/*.xml",
    ],   
    "css": ["static/css/*.css",],
    'auto_install': False,
    #'web_preload': False,
    
}
