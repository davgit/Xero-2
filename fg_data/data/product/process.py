#!/usr/bin/env python
# encoding: utf-8
"""
process.py

Created by Daniel Yang on 2011-08-25.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

xml = """<?xml version="1.0" encoding="utf-8"?>
<openerp>
    <data>
                %s
                </data>
        </openerp>
"""

cate_xml = """
<record id="product_category_%s" model="product.category">
    <field name="parent_id" ref="%s"/>
    <field name="name">%s</field>
</record>
"""
attr_xml = """<record id="product_color_%s" model="product.attribute">
        <field name="name">颜色</field>
                <field name="value">%s</field>
</record>
"""

product_xml_with_attr = """
<record id="product_product_%s" model="product.product">
    <field name="sale_ok">1</field>
    <field name="purchase_ok">1</field>
    <field name="default_code">%s</field>
    <field name="ean13">%s</field>
    <field name="supply_method">produce</field>
    <field name="list_price">%s</field>
    <field name="standard_price">%s</field>
    <field name="uom_id" ref="%s"/>
    <field name="uom_po_id" ref="%s"/>
    <field name="sale_delay">2.0</field>
    <field name="name">%s</field>
    <field name="type">product</field>
    <field name="categ_id" ref="%s"/>
    <field name="state">sellable</field>
    <field name="attribute_ids" eval="[(6, 0, [%s])]"/>
    <field name="fullnum">%s</field>
</record>
"""
product_xml_without_attr = """
<record id="product_product_%s" model="product.product">
    <field name="sale_ok">1</field>
    <field name="purchase_ok">1</field>
    <field name="default_code">%s</field>
    <field name="ean13">%s</field>
    <field name="supply_method">produce</field>
    <field name="list_price">%s</field>
    <field name="standard_price">%s</field>
    <field name="uom_id" ref="%s"/>
    <field name="uom_po_id" ref="%s"/>
    <field name="sale_delay">2.0</field>
    <field name="name">%s</field>
    <field name="type">product</field>
    <field name="categ_id" ref="%s"/>
    <field name="state">sellable</field>
    <field name="fullnum">%s</field>
</record>
"""

package_xml = """
<record id="product_packaging_%s" model="product.packaging">
    <field name="ul" ref="product_ul_box_%s"/>
    <field name="product" ref="product_product_%s"/>
    <field name="qty">%s</field>
</record>
"""

ul_xml = """
<record id="product_ul_box_%s" model="product.ul">
    <field name="name">%s</field>
    <field name="type">box</field>
</record>"""

EANS = dict()
PACKAGES = dict()
ULS = dict()
COLORS = dict()
PRODUCT_COLORS = dict()

def get_uom(s):
    if s.find('只')>-1:
        #件(40只)
        if s == '只':
            return 'product_uom_cup_item'
        return s.replace('件(', 'product_uom_cup_item_').replace('只)', '')
    if s.find('套')>-1:
        if s == '套':
            return 'product_uom_cup_set'
        return s.replace('件(', 'product_uom_cup_set_').replace('套)', '')
    if s == '把':
        return 'product_uom_cup_ba'
    if s =='件':
        return 'product_uom_cup_article'
    
    if s == '斤':
        return 'product_uom_jin'
        
    if s == '公斤':
        return 'product.product_uom_kgm'


def process_all(lines):
        cs = {'塑胶事业部':'cat_pc','玻璃事业部':'cat_glass', '真空事业部':'cat_vacuum', 
        '安全帽事业部':'cat_helmet', '塑胶制品': 'cat_plastic', '财务部':'cat_finance', '*':'cat_other'}
        
        need_add_source = False
        file_output = open('category_ex.xml', 'w')
        file_product = open('product.xml', 'w')
        file_package = open('package.xml', 'w')
        pid = 1
        cid = 1
        c_doc = ""
        p_doc = ""
        ean_count = 0
        current_category = ''
        for line in lines:

            data = line.split(',') #got 11 elm.
            if data[1].strip()=='FALSE':
                #category, hold it.
                current_category = data[0].strip()
                #print 'getting category', current_category, cid
                need_add_source = True
                
            else:
                cate = 'product_category_%s' % 6
                if current_category and need_add_source:
                    c = cs[data[5]]
                    c_doc = c_doc + cate_xml % (cid, c, current_category)
                    cate = 'product_category_%s' % (cid)
                    cid = cid + 1
                    need_add_source = False
                    current_category = ''
                    
                #product
                name = data[0].strip().replace('/', '／')
                #print 'getting ', name
                code = data[2].strip()
                
                if data[5].strip() == '财务部':
                    cate = 'cat_finance'
                    
                if data[5].strip() == '*':
                    cate = 'cat_other'
                
                ean= ''
                if code:
                    ean = EANS.get(code, '')
                else:
                    ean = EANS.get(name, '')
                if ean:
                    ean_count = ean_count + 1
                
                package = get_uom(data[4])
                price = data[7].strip()
                fullnum = data[8].strip()
                #color 
                #ref('res_partner_category_8'), ref('res_partner_category_9')
                #get colors by name
                if PRODUCT_COLORS.has_key(name):
                    p_colors = PRODUCT_COLORS.get(name)
                
                    t = ""
                    #get color id
                    refs = []
                    for c in p_colors:
                        if COLORS.has_key(c):
                            cid = COLORS.get(c)
                            refs.append("ref('product_color_%s')"%cid)
                
                    t = product_xml_with_attr % (pid, code, ean, price, price, package, package, name, cate, ','.join(refs), fullnum)
                else:
                    t = product_xml_without_attr % (pid, code, ean, price, price, package, package, name, cate, fullnum)
                p_doc =  p_doc+ t
                pid = pid + 1
                    
        file_output.write(xml % c_doc)
        file_product.write(xml % p_doc)
        file_output.close()
        file_product.close()
        file_package.close()
        print 'done'
        print 'get eans', ean_count

def process_ul(lines):
    i = 1
    doc = ''
    file_output = open('ul.xml', 'w')
    for line in lines:
        data = line.split(',')
        print data[0]
        if data[6]!='':
            t = ul_xml % (i, data[6].strip())
            ULS[data[6].strip()] = ('product_ul_box_%s' % i)
            doc = t+doc
            i = i + 1
    
    file_output.write(xml%doc)
    file_output.close()
    
def join_ean13():
    file_ean = open('barcode-20111003.txt', 'r')
    eans_prev = file_ean.readlines()
    file_ean.close()
    
    for ean in eans_prev:
        data = ean.split(',')
        if len(data) == 4:
            EANS[data[3].strip()] = data[0].strip()
    
    file_ean = open('barcode_20111011.txt', 'r')
    eans_new = file_ean.readlines()
    file_ean.close()
    
    for ean in eans_new:
        data = ean.split(',')
        if (len(data) == 3) and (data[2].strip() != ''):
            product = data[0].strip()
            barcode = data[1].strip()
            code = data[2].strip()
            if product and not EANS.has_key(product):
                EANS[product] = barcode
            if code and not EANS.has_key(code):
                EANS[code] = barcode
                if '-' in code:
                    EANS[code.replace('-', '--')] = barcode
                if '--' in code:
                    EANS[code.replace('--', '-')] = barcode

    print 'get ean13 codes ', len(EANS)
    
def process_color():
        file_input = open('color.csv', 'r')
        lines = file_input.readlines()
        file_input.close()
        i = 1
        
        for line in lines:
            line = line.strip()
            data = line.split(',')
            
            if len(data)==5 and data[2]:
                #for write in colors
                if not COLORS.has_key(data[2]):
                    COLORS[data[2]] = i

                #for product colors
                l = PRODUCT_COLORS.get(data[0], [])
                if data[2] not in l:
                    l.append(data[2])
                PRODUCT_COLORS[data[0]] = l
                i = i + 1
                
        color_xml = ""
        file_output = open('color.xml', 'w')
        for c in COLORS:
            color_xml = color_xml + (attr_xml % (COLORS[c], c))
        file_output.write((xml % color_xml))
        file_output.close()
            
def main():
        process_color()
        file_input = open('20120425.txt', 'r')
        lines = file_input.readlines()
        file_input.close()
        join_ean13()
        process_ul(lines)
        process_all(lines)
        

if __name__ == '__main__':
        main()

