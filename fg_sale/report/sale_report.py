# -*- coding: utf-8 -*-


import tools
from osv import fields, osv


class sale_report_source_day(osv.osv):
    _name = "fg_sale.order.report.daily.source"
    _auto = False
    _rec_name = 'date'
    
    _columns = {
        'date': fields.date('日期'),
        'amount': fields.float('金额'),
        'source':fields.char('事业部', size=10),
        'due_date_from':fields.function(lambda *a,**k:{}, method=True, type='date',string="开始日期"),
        'due_date_to':fields.function(lambda *a,**k:{}, method=True, type='date',string="结束日期"),
    }
    _order = 'date asc'
    
    def init(self, cr):
           tools.drop_view_if_exists(cr, 'fg_sale_order_report_daily_source')
           cr.execute("""
               create or replace view fg_sale_order_report_daily_source as (
                   SELECT
                        MIN(line."id")AS "id",
                        o.date_order AS DATE,
                        SUM(line.subtotal_amount)AS amount,
                        COALESCE(product.source, '未知来源') as source
                   FROM
                        fg_sale_order_line line
                   INNER JOIN fg_sale_order o ON line.order_id = o. ID
                   INNER JOIN product_product product ON line.product_id = product."id"
                   WHERE
                        (o."state" = 'done' OR o.minus = TRUE)
                   AND(
                        o.date_order > CURRENT_DATE - INTERVAL '3 months'
                   )
                   GROUP BY
                        o.date_order,
                        product."source"
                   ORDER BY
                        o.date_order ASC
               )
               """)


class sale_report_by_day(osv.osv):
    _name = "fg_sale.order.report.daily"
    _auto = False
    _rec_name = 'date'
    
    _columns = {
        'date': fields.char('月份', size=12, readonly=True),
        'amount': fields.float('金额'),
        'source':fields.char('事业部', size=10),
        'partner_id':fields.many2one('res.partner', '客户'),
    }
    _order = 'date asc'

    def init(self, cr):
           tools.drop_view_if_exists(cr, 'fg_sale_order_report_daily')
           cr.execute("""
               create or replace view fg_sale_order_report_daily as (
                   SELECT
                        MIN(line."id")AS "id",
                        o.partner_id,
                        COALESCE(product.source, '未知来源') as source,
                        o.date_order as date,
                        SUM(line.subtotal_amount)AS amount
                   FROM
                        fg_sale_order_line line
                   INNER JOIN fg_sale_order o ON line.order_id = o. ID
                   INNER JOIN product_product product ON line.product_id = product."id"
                   WHERE
                        (o."state" = 'done' or o.minus = TRUE)
                   GROUP BY
                        o.partner_id,
                        o.date_order,
                        product."source"
                   ORDER BY
                        o.partner_id ASC
               )
               """)
               

class sale_plan_progress(osv.osv):
    _name = "fg_sale.plan.progress.month"
    _auto = False
    _rec_name = 'plan_month'

    _columns = {
        'plan_month': fields.char('月份', size=24),
        'partner_id':fields.many2one('res.partner', '客户'),
        'plastic': fields.float('塑胶事业部计划'),
        'plastic_plan':fields.float('塑胶事业部完成'),
        'glass': fields.float('玻璃事业部计划'),
        'glass_plan':fields.float('玻璃事业部完成'),
        'vacuume': fields.float('真空事业部计划'),
        'vacuume_plan': fields.float('真空事业部完成'),
    }
    _order = 'partner_id asc'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'fg_sale_plan_progress_month')
        cr.execute("""
            create or replace view fg_sale_plan_progress_month as (
            SELECT
                       min(line.id) as id,
                        to_char(plan.date_plan, 'YYYY-MM') as plan_month,
                        line.partner_id,
                        line.vacuume,
                        line.plastic,
                        line.glass,
                        SUM(
                                CASE
                                WHEN daily. SOURCE = '塑胶事业部' THEN
                                        daily.amount
                                ELSE
                                        0
                                END
                        )AS plastic_plan,
                        SUM(
                                CASE
                                WHEN daily. SOURCE = '玻璃事业部' THEN
                                        daily.amount
                                ELSE
                                        0
                                END
                        )AS glass_plan,
                        SUM(
                                CASE
                                WHEN daily. SOURCE = '真空事业部' THEN
                                        daily.amount
                                ELSE
                                        0
                                END
                        )AS vacuume_plan
                      FROM
                        fg_sale_monthly_plan_line line
                      JOIN fg_sale_monthly_plan plan ON plan."id" = line.plan_id
                      JOIN fg_sale_order_report_daily daily ON daily.partner_id = line.partner_id
                      WHERE
                        date_trunc('month', plan.date_plan)= date_trunc('month', daily."date")
                      GROUP BY
                        plan.date_plan,
                        line.partner_id,
                        line.vacuume,
                        line.plastic,
                        line.glass
            )""")


class sale_report_by_month(osv.osv):
    _name = "fg_sale.order.report.monthly"
    _auto = False
    _rec_name = 'month'
    
    _columns = {
        'date': fields.char('月份', size=12, readonly=True),
        'year': fields.char('年份', size=12, readonly=True),
        'month': fields.char('月份', size=12, readonly=True),
        'amount': fields.float('金额'),
        'source':fields.char('事业部', size=10),
    }
    _order = 'date asc'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'fg_sale_order_report_monthly')
        cr.execute("""
            create or replace view fg_sale_order_report_monthly as (
            SELECT 
              min(l.id) as id,
              to_char(s.date_order, 'YYYY-MM') as date,
              to_char(s.date_order, 'YYYY') as year,
              to_char(s.date_order, 'MM') as month,
              sum(l.subtotal_amount) as amount,
              COALESCE(p.source, '未知来源') as source
            FROM 
              public.fg_sale_order_line l 
            left join product_product p on (l.product_id=p.id) 
            left join fg_sale_order s on (l.order_id=s.id)
            where s.state = 'done' or s.minus = TRUE 
             group by p.source,date, year, month
            order by date asc 
            )""")
