# -*- coding: utf-8 -*-

import tools, base64
from osv import fields, osv
import xlwt, cStringIO



class fuguang_discount_product(osv.osv_memory):
    _name = "fg_sale.fuguang.product.discount.wizard"
    _description = "促销单品统计"
    
    _columns = {
        'partner_id': fields.many2one('res.partner', '客户', required=True),
        'date_start': fields.date('开始日期', required=True),
        'date_end': fields.date('截止日期', required=True),
    }
    
    _defaults = {
        'date_end': fields.date.context_today,
    }
    
    def show_result(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        sql = """
        SELECT
                product.name_template,
                SUM (line.product_uom_qty) AS uom_qty,
                SUM (line.aux_qty) AS aux_qty
        FROM
                product_product product
        JOIN fg_sale_order_line line ON line.product_id = product."id"
        JOIN fg_sale_order o ON line.order_id = o."id"
        WHERE
                (
                        o."state" = 'done'
                        OR o.minus = TRUE
                )
        AND o.note LIKE '%%促销%%'
        AND o.partner_id = %s
        AND o.date_order >= '%s'
        AND o.date_order <= '%s'
        GROUP BY
                product.name_template
        """
        
        cr.execute(sql % (this.partner_id.id, this.date_start, this.date_end))
        report_obj = self.pool.get('fg_data.report.horizontal')
        
        ids = [report_obj.create(cr, uid, {'name':p[0], 'value':p[1], 'desc':('共 %s 只'%p[2])}) for p in cr.fetchall()]
        
        act_obj = self.pool.get('ir.actions.act_window')
        mod_obj = self.pool.get('ir.model.data')
        
        result = mod_obj.get_object_reference(cr, uid, 'fg_data', 'action_fg_data_report_horizontal')
        id = result and result[1] or False
        
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['domain'] = "[('id','in', ["+','.join(map(str, ids))+"])]"
        result['limit'] = 1000
        return result
        


class fuguang_product_sale_toplist(osv.osv_memory):
    _name = "fg_sale.fuguang.product.sale.toplist.wizard"
    _description = "单品销售排行"
    
    _columns = {
        'name': fields.char('文件名', 16, readonly=True),
        'product': fields.many2one('product.product', '产品', required=True),
        'date_start': fields.date('开始日期', required=True),
        'date_end': fields.date('截止日期', required=True),
        'data': fields.binary('文件', readonly=True),
        'state': fields.selection( [('choose','choose'),   # choose 
                                     ('get','get'),         # get the file
                                   ] ),
    }
    _defaults = {
        'date_end': fields.date.context_today,
        'state': lambda *a: 'choose',
        'name': '单品销售排行.xls',
    }
    
    def export_result(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        sql = """
        SELECT
                P ."name",
                product.name_template,
                product.default_code,
                SUM (line.aux_qty) AS qty
        FROM
                fg_sale_order_line line
        JOIN product_product product ON product."id" = line.product_id
        JOIN fg_sale_order o ON o."id" = line.order_id
        JOIN res_partner P ON P ."id" = o.partner_id
        WHERE
                line.product_id = %s
        AND (
                o."state" = 'done'
                OR o.minus = TRUE
        )
        AND o.date_order >= '%s'
        AND o.date_order <= '%s'
        GROUP BY
                P ."name",
                product.default_code,
                product.name_template
        ORDER BY
                qty DESC
        """
        
        cr.execute(sql % (this.product.id, this.date_start, this.date_end))
        
        book = xlwt.Workbook(encoding='utf-8')
        sheet = book.add_sheet(u'排序')
        
        sheet.write(0,0,'客户')
        sheet.write(0,1,'产品')
        sheet.write(0,2,'货号')
        sheet.write(0,3,'销售只数')
        
        for p in cr.fetchall():
            c = 0
            row_count = len(sheet.rows)
            for x in p:
                sheet.write(row_count, c, x)
                c = c + 1
        
        buf=cStringIO.StringIO()
        book.save(buf)
        
        out=base64.encodestring(buf.getvalue())
        
        return self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':this.name }, context=context)

class fuguang_amount_by_partner_product(osv.osv_memory):
    _name = "fg_sale.fuguang.partner.product.export.wizard"
    _description = "根据客户的产品销量统计"
    
    _columns = {
        'name': fields.char('文件名', 16, readonly=True),
        'partner_id': fields.many2one('res.partner', '客户', required=True),
        'date_start': fields.date('开始日期', required=True),
        'date_end': fields.date('截止日期', required=True),
        'data': fields.binary('文件', readonly=True),
        'state': fields.selection( [('choose','choose'),   # choose 
                                     ('get','get'),         # get the file
                                   ] ),
    }
    
    _defaults = {
        'date_end': fields.date.context_today,
        'state': lambda *a: 'choose',
        'name': 'report.xls',
    }
    
    def export_result(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        sql = """
        SELECT
                product.name_template,
                product.default_code,
                product."source",
                SUM(line.aux_qty) as aux_qty,
                SUM(line.subtotal_amount) as amount
        FROM
                fg_sale_order_line line
        JOIN fg_sale_order o ON o."id" = line.order_id
        JOIN product_product product ON product. ID = line.product_id
        WHERE
                o.partner_id = %s
        AND (
            o."state" = 'done'
            OR o.minus = TRUE
        )

        AND o.date_order >= '%s'
        AND o.date_order <= '%s'
        GROUP BY
                line.product_id,
                product.default_code,
                product.name_template,
                product."source"
        """
        
        cr.execute(sql % (this.partner_id.id, this.date_start, this.date_end))
        
        book = xlwt.Workbook(encoding='utf-8')
        
        sheet_dict = {}
        def _new_sheet(name):
            sheet = book.add_sheet(name)
            sheet_dict[name] = len(sheet_dict)
            
            sheet.write(0,0,'产品名称')
            sheet.write(0,1,'产品型号')
            sheet.write(0,2,'事业部')
            sheet.write(0,3,'只数')
            sheet.write(0,4,'金额')
            return sheet

        def _get_or_create_sheet(name):
            if not sheet_dict.has_key(name):
                return _new_sheet(name)
            else:
                return book.get_sheet(sheet_dict[name])
        
        def _write_line(sheet, data):
            i = 0
            row_count = len(sheet.rows)
            for item in data:
                sheet.write(row_count, i, item)
                i = i + 1

        def _write_line(sheet, data):
            i = 0
            row_count = len(sheet.rows)
            for item in data:
                sheet.write(row_count, i, item)
                i = i + 1
        
        for p in cr.fetchall():
            sheet = _get_or_create_sheet(p[2] or '未知来源')
            _write_line(sheet, p)
        
        # TODO: here, is cr did not fetch anything, xlwr will raise errors.
        
        buf=cStringIO.StringIO()
        book.save(buf)
        
        out=base64.encodestring(buf.getvalue())
        
        return self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':this.name }, context=context)


class amount_by_parter_product(osv.osv_memory):
    _name = "fg_sale.fga.partner.product.export.wizard"
    _description = "FGA根据客户的产品销量统计"

    _columns = {
        'name': fields.char('文件名', 16, readonly=True),
        'date_start': fields.date('开始日期', required=True),
        'date_end': fields.date('截止日期', required=True),
        'data': fields.binary('文件', readonly=True),
        'state': fields.selection( [('choose','choose'),   # choose 
                                     ('get','get'),         # get the file
                                   ] ),
    }
    _defaults = {
        'date_end': fields.date.context_today,
        'state': lambda *a: 'choose',
        'name': 'report.xls',
    }
    
    def export_result(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        sql = """
        SELECT
                partner."name",
                product.default_code,
                product.name_template,
                product."source",
                SUM (line.aux_qty) AS qty,
                SUM (line.subtotal_amount) AS amount
        FROM
                fg_sale_order_line line
        JOIN fg_sale_order o ON line.order_id = o."id"
        JOIN product_product product ON product."id" = line.product_id
        JOIN res_partner partner ON ((partner. ID = o.partner_id))
        JOIN res_partner_category_rel rel ON rel.partner_id = partner."id"
        JOIN res_partner_category cate ON cate."id" = rel.category_id
        WHERE
                (
                        o."state" = 'done'
                        OR o.minus = TRUE
                )
                AND product.default_code <> ''
                AND cate."id" = 4
                AND o.date_order >= '%s'
                AND o.date_order <= '%s'
        GROUP BY
                partner."name",
                line.product_id,
                product.default_code,
                product.name_template,
                product."source"
        ORDER BY
                product.default_code ASC
        """
        
        cr.execute(sql % (this.date_start, this.date_end))
        
        book = xlwt.Workbook(encoding='utf-8')
        
        sheet_dict = {}
        def _new_sheet(name):
            sheet = book.add_sheet(name)
            sheet_dict[name] = len(sheet_dict)
            
            sheet.write(0,0, u'客户')
            sheet.write(0,2, u'产品型号')
            sheet.write(0,3, u'产品名称')
            sheet.write(0,4, u'事业部')
            sheet.write(0,5, u'只数')
            sheet.write(0,6, u'金额')
            return sheet
        
        def _get_or_create_sheet(name):
            if not sheet_dict.has_key(name):
                return _new_sheet(name)
            else:
                return book.get_sheet(sheet_dict[name])
        
        def _write_line(sheet, data):
            i = 0
            row_count = len(sheet.rows)
            for item in data:
                sheet.write(row_count, i, item)
                i = i + 1

        for p in cr.fetchall():
            sheet = _get_or_create_sheet(p[0])
            _write_line(sheet, p)
            
        
        buf=cStringIO.StringIO()
        book.save(buf)
        
        out=base64.encodestring(buf.getvalue())
        
        return self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':this.name }, context=context)


class amount_by_fga_product(osv.osv_memory):
    _name = "fg_sale.fga.product.export.wizard"
    _description = "FGA产品销量统计"
    
    _columns = {
        'name': fields.char('文件名', 16, readonly=True),
        'date_start': fields.date('开始日期', required=True),
        'date_end': fields.date('截止日期', required=True),
        'data': fields.binary('文件', readonly=True),
        'state': fields.selection( [('choose','choose'),   # choose 
                                     ('get','get'),         # get the file
                                   ] ),
    }
    _defaults = {
        'date_end': fields.date.context_today,
        'state': lambda *a: 'choose',
        'name': 'report.xls',
    }
    
    
    def export_result(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        
        sql = """
        SELECT
                product.name_template,
                product.default_code,
                SUM (line.subtotal_amount) AS amount,
                SUM (line.aux_qty) AS qty
        FROM
                fg_sale_order_line line
        JOIN fg_sale_order o ON o."id" = line.order_id
        JOIN product_product product ON product."id" = line.product_id
        WHERE
                (
                        o."state" = 'done'
                        OR o.minus = TRUE
                )
        AND (
                product.default_code LIKE 'FS%s'
                OR product.default_code LIKE 'FB%s'
                OR product.default_code LIKE 'FZ%s'
        )
        AND o.date_order >= to_date('%s', 'YYYY-MM-DD')
        AND o.date_order <= to_date('%s', 'YYYY-MM-DD')
        GROUP BY
                product.name_template,
                product.default_code
        """
        
        cr.execute(sql % ('%', '%', '%', this.date_start, this.date_end))
        
        book = xlwt.Workbook(encoding='utf-8')
        sheet1 = book.add_sheet(u'统计')
        
        r = 0
        for p in cr.fetchall():
            c = 0
            for x in p:
                sheet1.write(r, c, x)
                c = c + 1
            
            r = r + 1
        
        buf=cStringIO.StringIO()
        book.save(buf)
        
        out=base64.encodestring(buf.getvalue())
        
        return self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':this.name }, context=context)
        

class amount_by_fga_partner(osv.osv_memory):
    _name = "fg_sale.fga.partner.export.wizard"
    _description = "FGA客户销量统计"
    
    _columns = {
        'name': fields.char('文件名', 16, readonly=True),
        'date_start': fields.date('开始日期', required=True),
        'date_end': fields.date('截止日期', required=True),
        'source':fields.boolean('分事业部统计'),
        'data': fields.binary('文件', readonly=True),
        'state': fields.selection( [('choose','choose'),   # choose 
                                     ('get','get'),         # get the file
                                   ] ),
    }
    _defaults = {
        'date_end': fields.date.context_today,
        'state': lambda *a: 'choose',
        'name': 'report.xls',
    }
    
    
    def export_result(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        
        sql = """
        SELECT
                p."name",
                SUM (amount)
        FROM
                fg_sale_order_report_daily d
        JOIN res_partner P ON P ."id" = d.partner_id
        JOIN res_partner_category_rel rel ON rel.partner_id = P ."id"
        JOIN res_partner_category cate ON cate."id" = rel.category_id
        WHERE
                cate."id" = 4
        AND d."date" >= to_date('%s', 'YYYY-MM-DD')
        AND d."date" <= to_date('%s', 'YYYY-MM-DD')
        GROUP BY
                p."name",
                d.partner_id
        ORDER BY
                d.partner_id
        
        """
        if this.source:
            sql = """
                SELECT
                        p."name",
                        d."source",
                        SUM (amount)
                FROM
                        fg_sale_order_report_daily d
                JOIN res_partner P ON P ."id" = d.partner_id
                JOIN res_partner_category_rel rel ON rel.partner_id = P ."id"
                JOIN res_partner_category cate ON cate."id" = rel.category_id
                WHERE
                        cate."id" = 4
                AND d."date" >= to_date('%s', 'YYYY-MM-DD')
                AND d."date" <= to_date('%s', 'YYYY-MM-DD')
                GROUP BY
                        p."name",
                        d.partner_id,
                        d."source"
                ORDER BY
                        d.partner_id
                
                """
        
        cr.execute(sql % (this.date_start, this.date_end))
        
        book = xlwt.Workbook(encoding='utf-8')
        sheet1 = book.add_sheet(u'统计')
        
        r = 0
        for p in cr.fetchall():
            c = 0
            for x in p:
                sheet1.write(r, c, x)
                c = c + 1
            
            r = r + 1
        
        buf=cStringIO.StringIO()
        book.save(buf)
        
        out=base64.encodestring(buf.getvalue())
        
        return self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':this.name }, context=context)
        



class amount_by_partner_wizard(osv.osv_memory):
    _name = "fg_sale.amount.parnter.wizard"
    _description = "客户销量统计"
    _columns = {
        'date_start': fields.date('开始日期', required=True),
        'date_end': fields.date('截止日期', required=True),
        'source':fields.boolean('分事业部统计'),
    }
    _defaults = {
        'date_end': fields.date.context_today,
    }
    
    def show_result(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        sql = """
        SELECT
                P . NAME,
                SUM(amount)
        FROM
                fg_sale_order_report_daily d
        JOIN res_partner P ON P ."id" = d.partner_id
        WHERE
                d."date" >= to_date('%s', 'YYYY-MM-DD')
        AND d."date" <= to_date('%s', 'YYYY-MM-DD')
        GROUP BY
                P . NAME
        """
        if this.source:
            sql = """
            SELECT
                P . NAME,
                SUM(amount),
                source
            FROM
                fg_sale_order_report_daily d
            JOIN res_partner P ON P ."id" = d.partner_id
            WHERE
                d."date" >= to_date('%s', 'YYYY-MM-DD')
            AND d."date" <= to_date('%s', 'YYYY-MM-DD')
            GROUP BY
                P . NAME,
                source
             ORDER BY
                p."name"
            """
        
        cr.execute(sql % (this.date_start, this.date_end))
        
        report_obj = self.pool.get('fg_data.report.horizontal')
        
        ids = [report_obj.create(cr, uid, {'name':p[0], 'value':p[1], 'desc':(len(p)==3) and p[2] or ''}) for p in cr.fetchall()]
        
        act_obj = self.pool.get('ir.actions.act_window')
        mod_obj = self.pool.get('ir.model.data')
        
        result = mod_obj.get_object_reference(cr, uid, 'fg_data', 'action_fg_data_report_horizontal')
        id = result and result[1] or False
        
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['domain'] = "[('id','in', ["+','.join(map(str, ids))+"])]"
        return result


class amount_by_source_wizard(osv.osv_memory):
    _name = "fg_sale.amount.source.wizard"
    _description = "事业部销量统计"
    _columns = {
        'date_start': fields.date('开始日期', required=True),
        'date_end': fields.date('截止日期', required=True),
    }
    _defaults = {
        'date_end': fields.date.context_today,
    }
    
    def show_result(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        
        sql = """
        SELECT
                "source",
                SUM (amount)
        FROM
                fg_sale_order_report_daily
        WHERE
                DATE >= to_date('%s', 'YYYY-MM-DD')
        AND DATE <= to_date('%s', 'YYYY-MM-DD')
        GROUP BY
                "source"
        """
        
        cr.execute(sql % (this.date_start, this.date_end))
        
        report_obj = self.pool.get('fg_data.report.horizontal')
        
        ids = [report_obj.create(cr, uid, {'name':p[0], 'value':p[1]}) for p in cr.fetchall()]
        
        act_obj = self.pool.get('ir.actions.act_window')
        mod_obj = self.pool.get('ir.model.data')
        
        result = mod_obj.get_object_reference(cr, uid, 'fg_data', 'action_fg_data_report_horizontal')
        id = result and result[1] or False
        
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['domain'] = "[('id','in', ["+','.join(map(str, ids))+"])]"
        return result

class report_order(osv.osv_memory):
    _name = "fg_sale.order.export.wizard"
    _description = "导出订单明细"
    
    _columns = {
        'name': fields.char('文件名', 16, readonly=True),
        'date_start': fields.date('开始日期', required=True),
        'date_end': fields.date('截止日期', required=True),
        'source':fields.selection([(u'真空事业部',u'真空事业部'),
                            (u'塑胶事业部',u'塑胶事业部'),(u'玻璃事业部',u'玻璃事业部'), (u'财务部',u'财务部'),
                            (u'安全帽事业部',u'安全帽事业部'),(u'其他',u'其他'),(u'塑胶制品',u'塑胶制品')], '事业部'),
        'data': fields.binary('文件', readonly=True),
        'state': fields.selection( [('choose','choose'),   # choose 
                                     ('get','get'),         # get the file
                                   ] ),
    }
    
    _defaults = {
        'date_end': fields.date.context_today,
        'state': lambda *a: 'choose',
        'name': 'lines.xls',
    }
    
    def export_excel(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        order_obj = self.pool.get('fg_sale.order')
        
        book = xlwt.Workbook(encoding='utf-8')
        sheet1 = book.add_sheet(u'总体统计')
        
        order_list = order_obj.search(cr, uid, [
                ('date_order','>=', this.date_start),
                ('date_order','<=', this.date_end),
                '|',('state','=','done'), ('minus','=', True)
            ], order='date_order asc')
        cols = ['日期','发票号码','产品名称','规格型号','购货单位','单位','数量','数量/只','单价','金额','事业部','摘要']
        i = 0
        for c in cols:
            sheet1.write(0, i, c)
            i = i + 1
            
        i = 1
        _first = True
        for order in order_obj.browse(cr, uid, order_list):
                for line in order.order_line:
                    if this.source:
                        if this.source != line.product_id.source:
                            continue
                    if _first:
                        sheet1.write(i, 0, order.date_order)
                        sheet1.write(i, 1, order.name)
                        _first = False
                    
                    sheet1.write(i, 2, line.product_id.name)
                    sheet1.write(i, 3, line.product_id.default_code or '')
                    sheet1.write(i, 4, order.partner_id.name)
                    sheet1.write(i, 5, line.product_uom.name)
                    sheet1.write(i, 6, line.product_uom_qty)
                    sheet1.write(i, 7, line.aux_qty)
                    sheet1.write(i, 8, line.unit_price)
                    sheet1.write(i, 9, line.subtotal_amount)
                    sheet1.write(i, 10, line.product_id.source)
                    sheet1.write(i, 11, line.note or '')
                    i = i + 1
                _first = True
        
        buf=cStringIO.StringIO()
        book.save(buf)

        out=base64.encodestring(buf.getvalue())

        return self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':this.name }, context=context)


class report_product(osv.osv_memory):
    _name = "fg_sale.product.export.wizard"
    _description = "按单品统计"
    
    _columns = {
        'name': fields.char('文件名', 16, readonly=True),
        'date_start': fields.date('开始日期', required=True),
        'date_end': fields.date('截止日期', required=True),
        'data': fields.binary('文件', readonly=True),
        'state': fields.selection( [('choose','choose'),   # choose 
                                     ('get','get'),         # get the file
                                   ] ),
    }
    
    _defaults = {
        'date_end': fields.date.context_today,
        'state': lambda *a: 'choose',
        'name': 'report.xls',
    }
    
    def export_excel(self, cr, uid, ids, context=None):
        book = xlwt.Workbook(encoding='utf-8')
        sheet1 = book.add_sheet(u'总体统计')
        sheet2 = book.add_sheet(u'塑胶事业部')
        sheet3 = book.add_sheet(u'真空事业部')
        sheet4 = book.add_sheet(u'玻璃事业部')
        sheet5 = book.add_sheet(u'财务部')
        sheet6 = book.add_sheet(u'安全帽事业部')
        sheet7 = book.add_sheet(u'塑胶制品')
        sheet8 = book.add_sheet(u'其他')
        sources = ['总体统计', '塑胶事业部', '真空事业部', '玻璃事业部', '财务部', '安全帽事业部', '塑胶制品', '其他']
        
        for i in range(len(sources)):
            book.get_sheet(i).write(0,0,'排名')
            book.get_sheet(i).write(0,1,'产品')
            book.get_sheet(i).write(0,2,'货号')
            book.get_sheet(i).write(0,3,'事业部')
            book.get_sheet(i).write(0,4,'售出只数')
            book.get_sheet(i).write(0,5,'金额')
        
        this = self.browse(cr, uid, ids)[0]

        sql = """
        SELECT
            product.id,
                product.name_template,
                product.default_code,
                product.source,
                SUM(line.aux_qty)AS qty,
                SUM(line.subtotal_amount)AS amount
        FROM
                product_product product
        JOIN fg_sale_order_line line ON line.product_id = product."id"
        JOIN fg_sale_order o ON o."id" = line.order_id
        WHERE
                product."source" IS NOT NULL
        AND (o."state" = 'done' OR o."minus" = TRUE )
        AND o.date_order >= to_date('%s', 'YYYY-MM-DD')
        AND o.date_order <= to_date('%s', 'YYYY-MM-DD')
        GROUP BY
            product.id,
                product.name_template,
                product.source,
                product.default_code
        ORDER BY
                amount DESC
        """
        
        def _write_cell(s, r, p):
            s.write(r, 0, r)
            s.write(r, 1, p[1])
            s.write(r, 2, p[2])
            s.write(r, 3, p[3])
            s.write(r, 4, p[4])
            s.write(r, 5, p[5])
        cr.execute(sql % (this.date_start, this.date_end))
        i = 1
        for p in cr.fetchall():
            _write_cell(sheet1, i, p)
            i = i + 1
            
            if p[3] in sources:
                sheet = book.get_sheet(sources.index(p[3]))
                if sheet:
                    row_count = len(sheet.rows)
                    _write_cell(sheet, row_count, p)
        
        _write_cell(sheet1, len(sheet1.rows), ['','统计时间: %s 到 %s' % (this.date_start, this.date_end),'','','',''])
        
        buf=cStringIO.StringIO()
        book.save(buf)
        
        out=base64.encodestring(buf.getvalue())
        
        return self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':this.name }, context=context)
