# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_is_zero
from datetime import date, datetime, time

from odoo.osv import expression


import logging
_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    capex_group_id = fields.Many2one('x.capex.group',string="Capex Group")
    workinprocess = fields.Boolean('Work in Process (Capex)',related='account_id.workinprocess',store=True)


class AccountAccount(models.Model):
    _inherit = 'account.account'

    workinprocess = fields.Boolean('Work in Process (Capex)')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('order_line')
    def capex_group_required_compute(self):
        for rec in self:
            workinprocess = False
            for line in rec.order_line:
                account_id = line.product_id.property_account_expense_id or line.product_id.categ_id.property_account_expense_categ_id
                if account_id.workinprocess:
                    workinprocess = True
            rec.capex_group_required = workinprocess

    capex_group_required = fields.Boolean('Capex required?',compute='capex_group_required_compute')
    capex_group_id = fields.Many2one('x.capex.group',string="Capex Group")


class EmployeeAdvanceExpense(models.Model):
    _inherit = 'employee.advance.expense'

    @api.depends('x_studio_anticipated_account_code','advance_expense_line_ids')
    def capex_group_required_compute(self):
        for rec in self:
            workinprocess = False
            if rec.adv_exp_type=='advance':
                account_id = rec.x_studio_anticipated_account_code.property_account_expense_id or rec.x_studio_anticipated_account_code.categ_id.property_account_expense_categ_id
                if account_id.workinprocess:
                    workinprocess = True
            else:
                for line in rec.advance_expense_line_ids:
                    account_id = line.product_id.property_account_expense_id or line.product_id.categ_id.property_account_expense_categ_id
                    if account_id.workinprocess:
                        workinprocess = True
            rec.capex_group_required = workinprocess

    capex_group_required = fields.Boolean('Capex required?',compute='capex_group_required_compute')
    capex_group_id = fields.Many2one('x.capex.group',string="Capex Group")
    x_studio_anticipated_account_code = fields.Many2one('product.product',string="Anticipated Account Code")