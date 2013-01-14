# -*- coding: utf-8 -*-

import tools
from tools import safe_eval

try:
    # embedded
    import openerp.addons.web.common.http as openerpweb
    from openerp.addons.web.controllers.main import View
except ImportError:
    # standalone
    import web.common.http as openerpweb
    from web.controllers.main import View

from lxml import etree

class GraphView(View):
    _cp_path = '/web_graph/graph'
    
    @tools.cache(timeout=3600)
    def from_db(self, obj, chart_type, title, fields, domain, group_by, context):
        result = {}
        if len(fields)<2:
            return result
        
        field_x = fields[1]
        field_y = fields[2]
        field_z = (len(fields)==4) and fields[3] or ''
        categories = []
        groups = []
        series = []
        ids = obj.search(domain)
            
        if ids:
            records = obj.read(ids)
            
            #field_x
            categories = []
            #field_z
            groups = []
            series = []
            
            if field_z:
                data_set = {}
                for r in records:
                    #get categories.
                    if r[field_x] not in categories:
                        categories.append(r[field_x])
                        
                    if r[field_z] not in groups:
                        groups.append(r[field_z])
                    data_set[str(r[field_x])+str(r[field_z])] = str(r[field_y])
                
                #transform data
                # series

                for g in groups:
                    s = {'name':g, 'data':[]}
                    for cate in categories:
                        print type(cate),type(g)
                        s['data'].append(data_set.get(str(cate)+str(g), 0))
                    series.append(s)

            else:
                data = []
                for r in records:
                    if r[field_x] not in categories:
                        categories.append(r[field_x])
                    data.append(r[field_y])
                
                series.append({'data':data})

        return categories, series
    
    @openerpweb.jsonrequest
    def data_get(self, req, model=None, domain=[], group_by=[], view_id=False, context={}, **kwargs):

        obj = req.session.model(model)
        xml = obj.fields_view_get(view_id, 'graph')
        graph_xml = etree.fromstring(xml['arch'])
        
        chart_type = graph_xml.attrib.get('type') or 'line'
        chart_title = graph_xml.attrib.get('string') or '图表'
        fields = [ element.attrib.get('name') for element in graph_xml.iter() ]
        
        data = self.from_db(obj, chart_type, chart_title, fields, domain, group_by, context)

        result = {
            'title':chart_title,
            'categories':data[0],
            'series':data[1],
            'chart_type':chart_type,
        }
        
        return result

