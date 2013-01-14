# -*- encoding: utf-8 -*-

{
    'name': '君子兰分析模块',
    'version': '1.3',
    'category' : '君子兰',
    'description': """一般性库存和销售分析""",
    'author': '杨振宇',
    'website': 'http://www.ide.fm',
    'depends': ['base'],
    'init_xml': [],
    'update_xml': [
        'analysis.xml',
        'security/group.xml',
        'security/ir.model.access.csv',
        'report/analysis_report.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'application':True,
}