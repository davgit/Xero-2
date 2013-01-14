# -*- coding: utf-8 -*-

from osv import osv
#import pyodbc
from tools import DEFAULT_SERVER_DATETIME_FORMAT,get_initial
import report


#CONN_STR = 'DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=fg;UID=bi;PWD=xixihaha'
CONN_STR = 'DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=AIS20101008134938;UID=bi;PWD=xixihaha'
#CONN_STR = 'DRIVER={SQL Server};SERVER=192.168.209.128;DATABASE=jt;UID=erp;PWD=erp'

ratio_dict = {
    '吴秀屏':0.35,
    '徐明':0.35,
    '孔德彬':0.35,
    '李世桂':0.3,
    '钱铭':0.3,
    '郑奎军':0.25,
    '周伯利':0.25,
    '杨辉':0.35,
    '李莹':0.35,
    '茹志斌':0.35,
    '郭治峰':0.35,
    '王云朋':0.35,
    '颜晓杰':0.35,
    '刘春桥':0.35,
    '吕祥华':0.35,
    '葛伦明':0.35,
    '华新荣':0.35,
    '杭州新富光':0.3,
    '卢进军':0.35,
    '杨行超':0.35,
    '上官斌':0.35,
    '梁健康':0.3,
    '徐达报':0.3,
    '郭毅':0.3,
    '张灵川':0.3,
    '潘志发':0.3,
    '朱庆丰':0.3,
    '万会平':0.35,
    '应永泉':0.35,
    '万红平':0.35,
    '吴和志':0.35,
    '史亚凤':0.35,
    '庞金山':0.35,
    '杨小红':0.3,
    '田明':0.3,
    '殷新文':0.3,
    '姚金添':0.3,
    '李凯亮':0.3,
    '喻萍花':0.3,
    '陈一欢':0.3,
    '杨文英':0.3,
    '李蒙':0.3,
    '上海办事处':0.3,
    '陈杨超':0.3,
    '林棋森':0.3,
    '海南宏丰':0.3,
    '南宁秋实':0.3,
}

def clear_field(i, r=None):
    if not i:
        return ''
    e_list = {
        'FGC002.1573':'囍',
        'FGC002.575':'福州小糸大億',
        'FGC002.601':'中投证劵',
        'FGC002.945':'倪贇同学',
        'FGC002.977':'祝倪贇同学',
        '16401':'董玥',
    }
    if r:
        if e_list.has_key(r):
            return e_list.get(r) 
    try:
        s = ("%s" % i).decode('GB2312').encode('utf-8')
    except:
        s = ("%s" % i)
    return s

class customer_import(osv.osv_memory):
    _name = "fg_sale.customer.wizard.import"
    _description = "customer importing."
    
    _columns = {
        
    }
    
    def import_customer(self, cr, uid, ids, context=None):
        #todo!!!! this is for importing FGC001 clients. where item.FNumber = 'FGC001'
        sql = """
        SELECT
                org.FNumber,
                org.FName,
                org.FContact,
                org.FPhone,
                org.FFax,
                org.FAddress,
                org.FCity,
                org.FProvince,
                org.FCountry,
                item.FName AS Category,
                item.FNumber AS Category_Number
        FROM
                t_Organization org
        JOIN t_Item item ON item.FItemID = org.FParentID
        ORDER BY
                org.FItemID ASC
        """
        ## todo: notice...
        ##where item.FNumber = 'FGC001'
        state_sql = """
            select DISTINCT(FProvince) from t_Organization
        """
        # save state
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute(state_sql)
        rows = cursor.fetchall()
        state_dict = {}
        state_obj = self.pool.get('res.country.state')
        for row in rows:
            if row:
                name = clear_field(row[0])
                id = state_obj.create(cr, uid, {'name':name, 'code':get_initial(name), 'country_id':49,})
                state_dict[clear_field(row[0])] = id
        
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()

        #save category first
        cate_dict = dict()
        partner_cate_obj = self.pool.get('res.partner.category')
        partner_obj = self.pool.get('res.partner')
        address_obj = self.pool.get('res.partner.address')
        
        for row in rows:
            number = clear_field(row[10])
            name = clear_field(row[9])
            if not cate_dict.has_key(number):
                id = partner_cate_obj.create(cr, uid, {'name':name})
                cate_dict[number] = id
            
            cate_id = cate_dict.get(number)

            partner = {
                'fullnum':clear_field(row[0]),
                'name':clear_field(row[1], clear_field(row[0])),
                'customer':True,
                'category_id':[(6, 0, [cate_id])],
            }
            partner['ratio'] = ratio_dict.get(partner['name'], 1)
            
            partner_id = partner_obj.create(cr, uid, partner)
            
            address = {
                'partner_id': partner_id,
                'type':'default',
                'country_id':49,
                
                }
            if row[2]:
                address['name'] = clear_field(row[2])
            else:
                address['name'] = partner['name']
            if row[7]:
                address['state_id'] = state_dict.get(clear_field(row[7]))
            if row[6]:
                address['city'] = clear_field(row[6])
            if row[3]:
                address['mobile'] = clear_field(row[3])
            if row[4]:
                address['phone'] = clear_field(row[4])
            if row[5]:
                address['street'] = clear_field(row[5])
            address_obj.create(cr, uid, address)

        return {'type': 'ir.actions.act_window_close'}


class user_import(osv.osv_memory):
    _name = "fg_sale.user.wizard.import"
    _description = "user importing."

    _columns = {

    }

    def import_user(self, cr, uid, ids, context=None):
        # save user
        user_sql = """
        SELECT
                FUserID,
                FName,
                FForbidden
        FROM
                t_User
        WHERE
                FSID IS NOT NULL
        ORDER BY
                FUserID ASC
        """
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute(user_sql)
        rows = cursor.fetchall()
        user_obj = self.pool.get('res.users')
        for row in rows:
            name = clear_field(row[1], clear_field(row[0]))
            user_obj.create(cr, uid, {
                'login': name,
                'name': name,
                'jid':row[0],
                'password':'8751888',
                'signature': name,
                'company_id':1,
                'groups_id':[(6,0,[7])],
                'active':row[2]==0,
            })

        return {'type': 'ir.actions.act_window_close'}


class product_import(osv.osv_memory):
    _name = "fg_sale.product.wizard.import"
    _description = "product importing."

    _columns = {
        
    }

    def import_product(self, cr, uid, ids, context=None):
        cate_sql = """
        SELECT
                FNumber,
                FName
            FROM
                t_Item
            WHERE
                FItemClassID = 4
            AND FLevel = 1
        ORDER BY FItemID ASC
        """
        uom_sql = """
        SELECT
                tmu.FNumber,
                tmu.FName,
                tmu.FCoefficient
        FROM
                t_MeasureUnit tmu
        ORDER BY
                FItemID ASC
        """
        product_sql = """
        SELECT
                icitem.FModel,
                icitem.FName,
                icitem.FNumber,
                icitem.FSalePrice,
                icitem.FNote,
                item.FName AS Category_Name,
                item.FNumber AS Category_Num,
                unit.FNumber AS Unit_Num,
                unit.FName AS Unit_Name,
                dep.FName AS Dep_Name
        FROM
                t_icitem icitem
        JOIN t_Item item ON item.FItemID = icitem.FParentID
        JOIN t_MeasureUnit unit ON unit.FItemID = icitem.FSaleUnitID
        JOIN t_Department dep ON dep.FItemID = icitem.FSource
        WHERE
                icitem.FSource > 0
        ORDER BY
                icitem.FItemID ASC
        """
        product_sql_no_srouce = """
        SELECT
                icitem.FModel,
                icitem.FName,
                icitem.FNumber,
                icitem.FSalePrice,
                icitem.FNote,
                item.FName AS Category_Name,
                item.FNumber AS Category_Num,
                unit.FNumber AS Unit_Num,
                unit.FName AS Unit_Name
        FROM
                t_icitem icitem
        JOIN t_Item item ON item.FItemID = icitem.FParentID
        JOIN t_MeasureUnit unit ON unit.FItemID = icitem.FSaleUnitID
        WHERE
                icitem.FSource = 0
        ORDER BY
                icitem.FItemID ASC
        """
        product_cate_obj = self.pool.get('product.category')
        product_uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        cate_dict = dict()
        uom_dict = dict()
        conn = pyodbc.connect(CONN_STR)
        #category
        cursor = conn.cursor()
        cursor.execute(cate_sql)
        rows = cursor.fetchall()
        for row in rows:
            id = product_cate_obj.create(cr, uid, {'name': clear_field(row[1]), 'fullnum':clear_field(row[0])})
            cate_dict[clear_field(row[0])] = id

        #uom
        cursor = conn.cursor()
        cursor.execute(uom_sql)
        rows = cursor.fetchall()
        for row in rows:
            uom = {
                'fullnum':clear_field(row[0]),
                'name':clear_field(row[1]),
                'rounding':1,
                'factor':row[2],
                'category_id':1,
                'uom_type': (row[2] > 1) and 'bigger' or 'smaller'
            }
            id = product_uom_obj.create(cr, uid, uom)
            uom_dict[clear_field(row[0])] = id

        #product
        cursor = conn.cursor()
        cursor.execute(product_sql)
        rows = cursor.fetchall()
        for row in rows:
            if not uom_dict.has_key(clear_field(row[7])):
                print row[2], 'uom not found'
                break
            if not cate_dict.has_key(clear_field(row[6])):
                print row[2], 'category not found'
                break
            product = {
                'sale_ok':True,
                'purchase_ok':True,
                'supply_method':'produce',
                'list_price':row[3],
                'standard_price':row[3],
                'uom_id':uom_dict.get(clear_field(row[7])),
                'uom_po_id':uom_dict.get(clear_field(row[7])),
                'sale_delay':1,
                'name':clear_field(row[1]),
                'type':'product',
                'categ_id':cate_dict.get(clear_field(row[6])),
                'state':'sellable',
                'fullnum':clear_field(row[2]),
                'source':clear_field(row[9]),
                'description':clear_field(row[4]) or ''
            }

            if row[0]:
                product['default_code'] = clear_field(row[0].replace('--', '-').replace('-', '-').replace('--', '-'))
            else:
                product['default_code'] = ''
            product_obj.create(cr, uid, product)
        #no source.
        cursor = conn.cursor()
        cursor.execute(product_sql_no_srouce)
        rows = cursor.fetchall()
        for row in rows:
            if not uom_dict.has_key(clear_field(row[7])):
                print row[2], 'uom not found'
                break
            if not cate_dict.has_key(clear_field(row[6])):
                print row[2], 'category not found'
                break
            product = {
                'sale_ok':True,
                'purchase_ok':True,
                'supply_method':'produce',
                'default_code':clear_field(row[0]) or '',
                'list_price':row[3],
                'standard_price':row[3],
                'uom_id':uom_dict.get(clear_field(row[7])),
                'uom_po_id':uom_dict.get(clear_field(row[7])),
                'sale_delay':1,
                'name':clear_field(row[1]),
                'type':'product',
                'categ_id':cate_dict.get(clear_field(row[6])),
                'state':'sellable',
                'fullnum':clear_field(row[2]),
                'source':u'其他',
                'description':clear_field(row[4]) or ''
            }
            product_obj.create(cr, uid, product)
        return {'type': 'ir.actions.act_window_close'}
        
class order_import(osv.osv_memory):
    _name = "fg_sale.order.wizard.import"
    _description = "order importing."
    
    _columns = {
        
        
    }

    def import_fg_order(self, cr, uid, ids, context=None):
        user_dict = dict()
        cr.execute('SELECT id, jid from res_users;')
        for u in cr.fetchall():
            user_dict[u[1]] = u[0]
            
        partner_dict = dict()
        cr.execute('SELECT id, fullnum from res_partner;')
        for p in cr.fetchall():
            partner_dict[p[1]] = p[0]
        order_obj = self.pool.get('fg_sale.order')
        partner_obj = self.pool.get('res.partner')
        order_sql = """
        SELECT
            FBillNo,
            FDate,
            t_Item.FNumber,
            FNote,
            FBillerID,
            FInvoiceAmount,
            FROB,
            FCheckerID,
            FCheckDate,
            FCancellation
        FROM
            ICSale
        JOIN t_Item ON FCustID = t_Item.FItemID
        """
        #get orders
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute(order_sql)
        rows = cursor.fetchall()
        l = len(rows)
        
        for row in rows:
            if not partner_dict.has_key(clear_field(row[2])):
                print row[0], row[2], 'partner not found.'
                break
            if not user_dict.has_key(str(row[4])):
                print 'user', row[4], 'not found in order', row[0]
                break
            if row[7]:
                if not user_dict.has_key(str(row[7])):
                    print 'user', row[7], 'not found in order', row[0]
                    break


            order = {
                'name':clear_field(row[0]),
                'date_order': row[1],
                'partner_id': partner_dict.get(clear_field(row[2])),
                'note':clear_field(row[3]),
                'user_id':user_dict.get(str(row[4])),
                'amount_total': float(row[5]),
                'minus':(row[6]<0),
            }
            addr = partner_obj.address_get(cr, uid, [order['partner_id']], ['default'])['default']
            order['partner_shipping_id'] = addr

            if row[7]:
                #checked.
                order['date_confirm'] = row[8]
                order['confirmer_id'] = user_dict.get(str(row[7]))
                order['state'] = 'done'
            else:
                order['state'] = 'draft'
            if row[9] == 1:
                order['state'] = 'cancel'

            order_obj.create(cr, uid, order)
            l = l - 1
            print l


        return {'type': 'ir.actions.act_window_close'}
        
    def import_fg_order_line(self, cr, uid, ids, context=None):
        #uom
        uom_dict = dict()
        uom_sql = "SELECT id, fullnum from product_uom where fullnum is not null;"
        cr.execute(uom_sql)
        for u in cr.fetchall():
            uom_dict[u[1]] = u[0]

        #product
        product_dict = dict()
        product_sql = "SELECT id, fullnum from product_product;"
        cr.execute(product_sql)
        for p in cr.fetchall():
            product_dict[p[1]] = p[0]

        #order
        order_list = dict()
        cr.execute("""
                  SELECT
                           ID,
                           NAME
                   FROM
                           fg_sale_order;
                  """)
        for u in cr.fetchall():
           order_list[u[1].encode('utf-8')] = u[0]
           
        order_line_sql = """
            SELECT 
                ic.FBillNo,
                ics.FEntryID,
                item.FNumber,
                t007.FNumber,
                ics.FAuxQty,
                ics.FQty,
                ics.FEntrySelfI0441,
                ics.FPrice,
                ics.FAllAmount,
                ics.FNote
            FROM
                ICSaleEntry ics
            INNER JOIN t_MeasureUnit t007 ON t007.FItemID = ics.FUnitID
            INNER JOIN ICSale ic ON ic.FInterID = ics.FInterID
            INNER JOIN t_IcItem item ON item.FItemID = ics.FItemID
        """
        order_line_obj = self.pool.get('fg_sale.order.line')
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute(order_line_sql)
        rows = cursor.fetchall()
        l = len(rows)
        for row in rows:
            if not order_list.has_key(clear_field(row[0])):
                print 'order % not found' % row[0]
                break
            if not product_dict.has_key(clear_field(row[2])):
                print 'product % not found in order %s' % (row[2], row[0])
                break
            if not uom_dict.has_key(clear_field(row[3])):
                print 'product uom % not found in order' % row[3]
                break

            line = {}
            line['order_id'] = order_list.get(clear_field(row[0]))
            line['sequence'] = int(row[1])
            line['product_id'] = product_dict.get(clear_field(row[2]))
            line['product_uom'] = uom_dict.get(clear_field(row[3]))
            line['product_uom_qty'] = int(row[4])
            line['aux_qty'] = int(row[5])
            line['unit_price'] = float(row[6])
            #line['unit_price_discount'] = float(row[7])
            line['subtotal_amount'] = float(row[8])
            line['note'] = clear_field(row[9]) or ''
            order_line_obj.create(cr, uid, line)
            l = l - 1
            print l
        return {'type': 'ir.actions.act_window_close'}
