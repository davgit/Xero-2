# encoding: utf-8
{
    "name": "Web Homepage",
    "category": "",
    "description":
        """
            OpenERP Web Homepage Xero.
        """,
    "version": "2.0",
    "init_xml": [],
    'update_xml': [
        "web_home.xml",
        "security/group.xml",
        "security/ir.model.access.csv",
    ],
    "depends": ["base","web_dashboard"],
    "js": ["static/js/*.js",],
    'qweb' : [
        "static/xml/*.xml",
    ],
    "css": ["static/css/*.css",],
    'auto_install': False,
    #'web_preload': False,
    
}
