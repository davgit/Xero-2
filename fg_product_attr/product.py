# -*- encoding: utf-8 -*-

from osv import fields, osv


class product_attribute(osv.osv):
    _name = "product.attribute"
    _description = "产品属性"
    _rec_name = 'value'
    
    _columns = {
        'name' : fields.char('属性', size=64, required=True),
        'value' : fields.char('值', size=64, required=True),
    }
    
product_attribute()


class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
        'attribute_ids': fields.many2many('product.attribute', 'rel_product_attrs','product_id','attr_id', '属性'),
    }
product_product()