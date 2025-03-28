# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
from io import StringIO, BytesIO
import io
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)

from odoo.tools import float_round

class ISYOpex(models.Model):
    _name = 'isy.opex'

    name = fields.Char('Name',required=True)
    active = fields.Boolean('Active',default=True)
    show_only_actual = fields.Boolean('Show only Actual?')
    sequence = fields.Integer('sequence',default=1)
    budget_total = fields.Float('Budget',digits=(16,0),compute='compute_monthly',store=True)
    actual_total = fields.Float('Actual',digits=(16,0),compute='compute_monthly',store=False)
    percentage = fields.Float("Percentage (%)",digit=(16,2),compute='compute_monthly',store=False)
    o_type = fields.Many2one('isy.opex.type','Type',required=True)
    budget_july = fields.Float('July Budget',digits=(16,0),compute='compute_monthly',store=True)
    actual_july = fields.Float('July Actual',digits=(16,0),compute='compute_monthly',store=False)
    budget_aug = fields.Float('August Budget',digits=(16,0),compute='compute_monthly',store=True)
    actual_aug = fields.Float('August Actual',digits=(16,0),compute='compute_monthly',store=False)
    budget_sep = fields.Float('September Budget',digits=(16,0),compute='compute_monthly',store=True)
    actual_sep = fields.Float('September Actual',digits=(16,0),compute='compute_monthly',store=False)
    budget_oct = fields.Float('Octomber Budget',digits=(16,0),compute='compute_monthly',store=True)
    actual_oct = fields.Float('Octomber Actual',digits=(16,0),compute='compute_monthly',store=False)
    budget_nov = fields.Float('November Budget',digits=(16,0),compute='compute_monthly',store=True)
    actual_nov = fields.Float('November Actual',digits=(16,0),compute='compute_monthly',store=False)
    budget_dec = fields.Float('December Budget',digits=(16,0),compute='compute_monthly',store=True)
    actual_dec = fields.Float('December Actual',digits=(16,0),compute='compute_monthly',store=False)
    budget_jan = fields.Float('January Budget',digits=(16,0),compute='compute_monthly',store=True)
    actual_jan = fields.Float('January Actual',digits=(16,0),compute='compute_monthly',store=False)
    budget_feb = fields.Float('Febuary Budget',digits=(16,0),compute='compute_monthly',store=True)
    actual_feb = fields.Float('Febuary Actual',digits=(16,0),compute='compute_monthly',store=False)
    budget_mar = fields.Float('March Budget',digits=(16,0),compute='compute_monthly',store=True)
    actual_mar = fields.Float('March Actual',digits=(16,0),compute='compute_monthly',store=False)
    budget_apr = fields.Float('April Budget',digits=(16,0),compute='compute_monthly',store=True)
    actual_apr = fields.Float('April Actual',digits=(16,0),compute='compute_monthly',store=False)
    budget_may = fields.Float('May Budget',digits=(16,0),compute='compute_monthly',store=True)
    actual_may = fields.Float('May Actual',digits=(16,0),compute='compute_monthly',store=False)
    budget_jun = fields.Float('June Budget',digits=(16,0),compute='compute_monthly',store=True)
    actual_jun = fields.Float('June Actual',digits=(16,0),compute='compute_monthly',store=False)
    f_date = fields.Many2one('account.fiscal.year','Year',required=True)
    date_start = fields.Char('Start Year',compute="compute_date",store=True)
    date_end = fields.Char('End Year',compute="compute_date",store=True)
    date_to_forreport = fields.Date('Actual End Date for Report',required=True)
    date_from = fields.Date('Start Date',compute="compute_date",store=True)
    date_to = fields.Date('End Date',compute="compute_date",store=True)
    lines_july = fields.One2many('isy.opex.line','july_opex_id','July Lines')
    lines_aug = fields.One2many('isy.opex.line','aug_opex_id','August Lines')
    lines_sep = fields.One2many('isy.opex.line','sep_opex_id','September Lines')
    lines_oct = fields.One2many('isy.opex.line','oct_opex_id','Octomber Lines')
    lines_nov = fields.One2many('isy.opex.line','nov_opex_id','November Lines')
    lines_dec = fields.One2many('isy.opex.line','dec_opex_id','December Lines')
    lines_jan = fields.One2many('isy.opex.line','jan_opex_id','January Lines')
    lines_feb = fields.One2many('isy.opex.line','feb_opex_id','Febuary Lines')
    lines_mar = fields.One2many('isy.opex.line','mar_opex_id','March Lines')
    lines_apr = fields.One2many('isy.opex.line','apr_opex_id','April Lines')
    lines_may = fields.One2many('isy.opex.line','may_opex_id','May Lines')
    lines_jun = fields.One2many('isy.opex.line','jun_opex_id','June Lines')
    company_id = fields.Many2one('res.company',string="Company",default=lambda self:self.env.user.company_id.id)

    @api.depends('f_date')
    def compute_date(self):
        for rec in self:
            if rec.f_date:
                rec.date_start = str(rec.f_date.date_from)[0:4]
                rec.date_end = str(rec.f_date.date_to)[0:4]
                rec.date_from = str(rec.f_date.date_from)
                rec.date_to = str(rec.f_date.date_to)

    @api.depends('lines_july','lines_aug','lines_sep','lines_oct','lines_nov','lines_dec','lines_jan','lines_feb','lines_mar','lines_apr','lines_may','lines_jun')
    def compute_monthly(self):
        for rec in self:
            budget_amount = 0
            actual_amount = 0
            total_budget = 0
            total_actual = 0
            for line in rec.lines_july:
                budget_amount += line.budget_amount
                actual_amount += line.actual_amount
            rec.budget_july = float_round(budget_amount/1000,0)
            rec.actual_july = float_round(actual_amount/1000,0)
            total_budget += budget_amount
            total_actual += actual_amount

            budget_amount = 0
            actual_amount = 0
            for line in rec.lines_aug:
                budget_amount += line.budget_amount
                actual_amount += line.actual_amount
            rec.budget_aug = float_round(budget_amount/1000,0)
            rec.actual_aug = float_round(actual_amount/1000,0)
            total_budget += budget_amount
            total_actual += actual_amount

            budget_amount = 0
            actual_amount = 0
            for line in rec.lines_sep:
                budget_amount += line.budget_amount
                actual_amount += line.actual_amount
            rec.budget_sep = float_round(budget_amount/1000,0)
            rec.actual_sep = float_round(actual_amount/1000,0)
            total_budget += budget_amount
            total_actual += actual_amount

            budget_amount = 0
            actual_amount = 0
            for line in rec.lines_oct:
                budget_amount += line.budget_amount
                actual_amount += line.actual_amount
            rec.budget_oct = float_round(budget_amount/1000,0)
            rec.actual_oct = float_round(actual_amount/1000,0)
            total_budget += budget_amount
            total_actual += actual_amount

            budget_amount = 0
            actual_amount = 0
            for line in rec.lines_nov:
                budget_amount += line.budget_amount
                actual_amount += line.actual_amount
            rec.budget_nov = float_round(budget_amount/1000,0)
            rec.actual_nov = float_round(actual_amount/1000,0)
            total_budget += budget_amount
            total_actual += actual_amount

            budget_amount = 0
            actual_amount = 0
            for line in rec.lines_dec:
                budget_amount += line.budget_amount
                actual_amount += line.actual_amount
            rec.budget_dec = float_round(budget_amount/1000,0)
            rec.actual_dec = float_round(actual_amount/1000,0)
            total_budget += budget_amount
            total_actual += actual_amount

            budget_amount = 0
            actual_amount = 0
            for line in rec.lines_jan:
                budget_amount += line.budget_amount
                actual_amount += line.actual_amount
            rec.budget_jan = float_round(budget_amount/1000,0)
            rec.actual_jan = float_round(actual_amount/1000,0)
            total_budget += budget_amount
            total_actual += actual_amount

            budget_amount = 0
            actual_amount = 0
            for line in rec.lines_feb:
                budget_amount += line.budget_amount
                actual_amount += line.actual_amount
            rec.budget_feb = float_round(budget_amount/1000,0)
            rec.actual_feb = float_round(actual_amount/1000,0)
            total_budget += budget_amount
            total_actual += actual_amount

            budget_amount = 0
            actual_amount = 0
            for line in rec.lines_mar:
                budget_amount += line.budget_amount
                actual_amount += line.actual_amount
            rec.budget_mar = float_round(budget_amount/1000,0)
            rec.actual_mar = float_round(actual_amount/1000,0)
            total_budget += budget_amount
            total_actual += actual_amount

            budget_amount = 0
            actual_amount = 0
            for line in rec.lines_apr:
                budget_amount += line.budget_amount
                actual_amount += line.actual_amount
            rec.budget_apr = float_round(budget_amount/1000,0)
            rec.actual_apr = float_round(actual_amount/1000,0)
            total_budget += budget_amount
            total_actual += actual_amount

            budget_amount = 0
            actual_amount = 0
            for line in rec.lines_may:
                budget_amount += line.budget_amount
                actual_amount += line.actual_amount
            rec.budget_may = float_round(budget_amount/1000,0)
            rec.actual_may = float_round(actual_amount/1000,0)
            total_budget += budget_amount
            total_actual += actual_amount

            budget_amount = 0
            actual_amount = 0
            for line in rec.lines_jun:
                budget_amount += line.budget_amount
                actual_amount += line.actual_amount
            rec.budget_jun = float_round(budget_amount/1000,0)
            rec.actual_jun = float_round(actual_amount/1000,0)
            total_budget += budget_amount
            total_actual += actual_amount


            # rec.budget_total = rec.budget_july+rec.budget_aug+rec.budget_sep+rec.budget_oct+rec.budget_nov+rec.budget_dec \
            #         +rec.budget_jan+rec.budget_feb+rec.budget_mar+rec.budget_apr+rec.budget_may+rec.budget_jun
            rec.budget_total = float_round(total_budget/1000,0)
            # rec.actual_total = rec.actual_july+rec.actual_aug+rec.actual_sep+rec.actual_oct+rec.actual_nov+rec.actual_dec \
            #         +rec.actual_jan+rec.actual_feb+rec.actual_mar+rec.actual_apr+rec.actual_may+rec.actual_jun
            rec.actual_total = float_round(total_actual/1000,0)
            rec.percentage = abs(float_round(rec.actual_total/rec.budget_total,2)*100) if rec.budget_total else 0

    def unlink(self):
        for rec in self:
            lines = self.env['isy.opex.line'].search(['|',('july_opex_id','=',rec.id),'|',('aug_opex_id','=',rec.id),'|',('sep_opex_id','=',rec.id),'|',('oct_opex_id','=',rec.id),'|',('nov_opex_id','=',rec.id),'|',('dec_opex_id','=',rec.id),'|',('jan_opex_id','=',rec.id),'|',('feb_opex_id','=',rec.id),'|',('mar_opex_id','=',rec.id),'|',('apr_opex_id','=',rec.id),'|',('may_opex_id','=',rec.id),('jun_opex_id','=',rec.id)])
            lines.unlink()
        return super(ISYOpex, self).unlink()

    
class ISYOpexLine(models.Model):
    _name = 'isy.opex.line'
    _rec_name = 'account_id'

    account_id = fields.Many2one('account.account','Account',required=True) # domain="[('user_type_id','in',(13,14,16))]"
    budget_id = fields.Many2one('budgetextension.budget','Budget')
    budget_planned_amount = fields.Float('Yearly Budget Planned',related='budget_id.planned_amount_100')
    date_start = fields.Date('Start Date',required=True)
    date_end = fields.Date('End Date',required=True)
    budget_amount = fields.Float('Budget Amount',digits=(16,2),compute='compute_budget_amount',store=True)
    actual_amount = fields.Float('Actual Amount',digits=(16,2),compute='compute_actual')

    july_opex_id = fields.Many2one('isy.opex','July Opex',ondelete='cascade')
    aug_opex_id = fields.Many2one('isy.opex','August Opex',ondelete='cascade')
    sep_opex_id = fields.Many2one('isy.opex','September Opex')
    oct_opex_id = fields.Many2one('isy.opex','Octomber Opex')
    nov_opex_id = fields.Many2one('isy.opex','November Opex')
    dec_opex_id = fields.Many2one('isy.opex','December Opex')
    jan_opex_id = fields.Many2one('isy.opex','January Opex')
    feb_opex_id = fields.Many2one('isy.opex','Febuary Opex')
    mar_opex_id = fields.Many2one('isy.opex','March Opex')
    apr_opex_id = fields.Many2one('isy.opex','April Opex')
    may_opex_id = fields.Many2one('isy.opex','May Opex')
    jun_opex_id = fields.Many2one('isy.opex','June Opex')

    @api.onchange('account_id','date_start','date_end')
    def change_account_id(self):
        for rec in self:
            if rec.account_id and rec.date_start and rec.date_end:
                budget_id = self.env['budgetextension.budget'].sudo().search([('account_id','=',rec.account_id.id),('start_date','<=',rec.date_start),('end_date','>=',rec.date_end)])
    #             budget_amount = budget_id.planned_amount_100/12.0
    #             rec.budget_id = budget_id.id
    #             rec.budget_amount = budget_amount*-1

    @api.depends('budget_id.planned_amount_100','budget_planned_amount')
    def compute_budget_amount(self):
        for rec in self:
            if rec.budget_id:
                budget_amount = rec.budget_id.planned_amount_100/12.0
                o_type = rec.july_opex_id.o_type or rec.aug_opex_id.o_type or rec.sep_opex_id.o_type or rec.oct_opex_id.o_type \
                or rec.nov_opex_id.o_type or rec.dec_opex_id.o_type or rec.jan_opex_id.o_type or rec.feb_opex_id.o_type or \
                rec.mar_opex_id.o_type or rec.apr_opex_id.o_type or rec.may_opex_id.o_type or rec.jun_opex_id.o_type
                if o_type.type and o_type.type.lower()=='expense':
                    rec.budget_amount = budget_amount*-1
                else:
                    rec.budget_amount = budget_amount

    #@api.depends('account_id','date_start','date_end','date_to_forreport')
    @api.depends('account_id','date_start','date_end','july_opex_id.date_to_forreport','aug_opex_id.date_to_forreport','sep_opex_id.date_to_forreport','oct_opex_id.date_to_forreport','nov_opex_id.date_to_forreport','dec_opex_id.date_to_forreport','jan_opex_id.date_to_forreport','feb_opex_id.date_to_forreport','mar_opex_id.date_to_forreport','apr_opex_id.date_to_forreport','may_opex_id.date_to_forreport','jun_opex_id.date_to_forreport')
    def compute_actual(self):
        line_obj = self.env['account.move.line']
        for rec in self:
            date_to_forreport = rec.july_opex_id.date_to_forreport or rec.aug_opex_id.date_to_forreport or rec.sep_opex_id.date_to_forreport or rec.oct_opex_id.date_to_forreport or rec.nov_opex_id.date_to_forreport or rec.dec_opex_id.date_to_forreport or rec.jan_opex_id.date_to_forreport or rec.feb_opex_id.date_to_forreport or rec.mar_opex_id.date_to_forreport or rec.apr_opex_id.date_to_forreport or rec.may_opex_id.date_to_forreport or rec.jun_opex_id.date_to_forreport
            domain = [('account_id', '=', rec.account_id.id), ('date', '>=', rec.date_start), ('date', '<=', rec.date_end),('date','<=',date_to_forreport)]
            where_query = line_obj._where_calc(domain)
            line_obj._apply_ir_rules(where_query, 'read')
            from_clause,  where_clause, where_clause_params = where_query.get_sql()
            select = "SELECT sum(credit)-sum(debit) from " + from_clause + " left join account_move am on account_move_line.move_id=am.id where am.state='posted' and " + where_clause
            self.env.cr.execute(select, where_clause_params)
            actual_amount = self.env.cr.fetchone()
            rec.actual_amount = float_round((actual_amount[0] or 0),2)if actual_amount else 0

    @api.constrains('budget_amount')
    def amount_validate(self):
        for rec in self:
            if rec.budget_id.sudo():
                budget_id = rec.budget_id.sudo()
                opex_id = rec.july_opex_id or rec.aug_opex_id or rec.sep_opex_id or rec.oct_opex_id or rec.nov_opex_id or \
                    rec.dec_opex_id or rec.jan_opex_id or rec.feb_opex_id or rec.mar_opex_id or rec.apr_opex_id or rec.may_opex_id or rec.jun_opex_id
                lines = self.search(['&',('budget_id','=',budget_id.id),'|',('july_opex_id','=',opex_id.id),'|',('aug_opex_id','=',opex_id.id),'|',('sep_opex_id','=',opex_id.id),'|',('oct_opex_id','=',opex_id.id),'|',('nov_opex_id','=',opex_id.id),'|',('dec_opex_id','=',opex_id.id),'|',('jan_opex_id','=',opex_id.id),'|',('feb_opex_id','=',opex_id.id),'|',('mar_opex_id','=',opex_id.id),'|',('apr_opex_id','=',opex_id.id),'|',('may_opex_id','=',opex_id.id),('jun_opex_id','=',opex_id.id)])
                budget_amt = round(float_round(sum(lines.mapped('budget_amount')),2),2)
                if round(abs(budget_id.planned_amount_100)) < round(abs(budget_amt)):
                    _logger.info(budget_amt)
                    _logger.info(lines.mapped('budget_amount'))
                    _logger.info(sum(lines.mapped('budget_amount')))
                    _logger.info(round(float_round(sum(lines.mapped('budget_amount')),2),2))
                    _logger.info(budget_id.planned_amount_100)
                    raise UserError('Total Monthly Budget Amount is %s over %s of %s.'%(budget_amt,budget_id.planned_amount_100,budget_id.name))

    @api.constrains('date_start','date_end')
    def date_validate(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                if rec.july_opex_id and str(rec.date_start)[0:4]<rec.july_opex_id.date_start and str(rec.date_end)[0:4]>rec.july_opex_id.date_end:
                    raise UserError('Date is out of range.')
                elif rec.aug_opex_id and str(rec.date_start)[0:4]<rec.aug_opex_id.date_start and str(rec.date_end)[0:4]>rec.aug_opex_id.date_end:
                    raise UserError('Date is out of range.')
                elif rec.sep_opex_id and str(rec.date_start)[0:4]<rec.sep_opex_id.date_start and str(rec.date_end)[0:4]>rec.sep_opex_id.date_end:
                    raise UserError('Date is out of range.')
                elif rec.oct_opex_id and str(rec.date_start)[0:4]<rec.oct_opex_id.date_start and str(rec.date_end)[0:4]>rec.oct_opex_id.date_end:
                    raise UserError('Date is out of range.')
                elif rec.nov_opex_id and str(rec.date_start)[0:4]<rec.nov_opex_id.date_start and str(rec.date_end)[0:4]>rec.nov_opex_id.date_end:
                    raise UserError('Date is out of range.')
                elif rec.dec_opex_id and str(rec.date_start)[0:4]<rec.dec_opex_id.date_start and str(rec.date_end)[0:4]>rec.dec_opex_id.date_end:
                    raise UserError('Date is out of range.')
                elif rec.jan_opex_id and str(rec.date_start)[0:4]<rec.jan_opex_id.date_start and str(rec.date_end)[0:4]>rec.jan_opex_id.date_end:
                    raise UserError('Date is out of range.')
                elif rec.feb_opex_id and str(rec.date_start)[0:4]<rec.feb_opex_id.date_start and str(rec.date_end)[0:4]>rec.feb_opex_id.date_end:
                    raise UserError('Date is out of range.')
                elif rec.mar_opex_id and str(rec.date_start)[0:4]<rec.mar_opex_id.date_start and str(rec.date_end)[0:4]>rec.mar_opex_id.date_end:
                    raise UserError('Date is out of range.')
                elif rec.apr_opex_id and str(rec.date_start)[0:4]<rec.apr_opex_id.date_start and str(rec.date_end)[0:4]>rec.apr_opex_id.date_end:
                    raise UserError('Date is out of range.')
                elif rec.may_opex_id and str(rec.date_start)[0:4]<rec.may_opex_id.date_start and str(rec.date_end)[0:4]>rec.may_opex_id.date_end:
                    raise UserError('Date is out of range.')
                elif rec.jun_opex_id and str(rec.date_start)[0:4]<rec.jun_opex_id.date_start and str(rec.date_end)[0:4]>rec.jun_opex_id.date_end:
                    raise UserError('Date is out of range.')
                

class ISYOpexType(models.Model):
    _name = 'isy.opex.type'

    name = fields.Char('Name',required=True)
    sequence = fields.Integer('sequence',default=1)
    type = fields.Selection([('income','Income'),('expense','Expense')],string='Type',required=True)


class ISYOpexGroup(models.Model):
    _name = 'isy.opex.group'

    name = fields.Char('Name',required=True)
    account_ids = fields.Many2many('account.account', string='Accounts')
    sequence = fields.Integer('sequence',default=1)