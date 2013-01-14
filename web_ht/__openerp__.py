{
    "name" : "Base Html",
    "category": "Hidden",
    "description":
        """
        OpenERP Web ht view.
        """,
    "version" : "2.0",
    "depends" : ["web"],
    "js": [
        "static/src/js/html.js"
    ],
    "css": [
        "static/src/css/html.css"
    ],
    'qweb' : [
        "static/src/xml/*.xml",
    ],
    'auto_install': True,
}
