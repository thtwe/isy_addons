# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_asset = fields.Boolean(string="Asset")

    def budget_account_dict(self, account_id, price_subtotal, budget_account_dict, account_analytic):
        if account_id.id in account_analytic:
            budget_account_dict[account_id.id].append(price_subtotal)
        else:
            account_analytic.append(account_id.id)
            budget_account_dict[account_id.id] = [price_subtotal]
        return {'budget_account_dict': budget_account_dict,
                'account_analytic': account_analytic,
                'account_id': account_id}

    def calculate_tax(self, line):
        taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id,
                                          line.product_qty,line.product_id, line.order_id.partner_id)
        price_subtotal = taxes['total_included']
        return {'price_subtotal': price_subtotal}

    def accouting_budget_warning(self, order, order_line, warning_msg, budget_account_dict, account_analytic, update=False):
        for line in order_line:
            if not update:
                product_id = line.product_id
                date_planned = line.date_planned.date()
                if line.taxes_id:
                    vals = self.calculate_tax(line)
                    price_subtotal = vals['price_subtotal']
                else:
                    price_subtotal = (line.price_unit * line.product_qty)
                account_id = False
                asset = False
                if product_id.property_account_expense_id:
                    account_id = product_id.property_account_expense_id
                elif product_id.categ_id.property_account_expense_categ_id:
                    account_id = product_id.categ_id.property_account_expense_categ_id
                elif product_id.asset_category_id:
                    account_id = product_id.asset_category_id.account_asset_id
                    asset = True
                if account_id:
                    vals = self.budget_account_dict(account_id, price_subtotal, budget_account_dict, account_analytic)
            else:
                if not isinstance(line[1], int):
                    line = line[2]
                    date_planned = line['date_planned']
                    product_id = self.env['product.product'].browse(line['product_id'])
                    if line['taxes_id'][0][2]:
                        taxes_id = self.env['account.tax'].browse(line['taxes_id'][0][2])
                        taxes = taxes_id.compute_all(line['price_unit'], order.currency_id,
                                          line['product_qty'],line['product_id'], order.partner_id)
                        price_subtotal = taxes['total_included']
                    else:
                        price_subtotal = (line['price_unit'] * line['product_qty'])
                else:
                    line = self.order_line.browse(line[1])
                    product_id = line.product_id
                    date_planned = line.date_planned
                    if line.taxes_id:
                        vals = self.calculate_tax(line)
                        price_subtotal = vals['price_subtotal']
                    else:
                        price_subtotal = (line.price_unit * line.product_qty)
                account_id = False
                asset = False
                if product_id.property_account_expense_id:
                    account_id = product_id.property_account_expense_id
                elif product_id.categ_id.property_account_expense_categ_id:
                    account_id = product_id.categ_id.property_account_expense_categ_id
                elif product_id.asset_category_id:
                    account_id = product_id.asset_category_id.account_asset_id
                    asset = True
                if account_id:
                    vals = self.budget_account_dict(account_id,price_subtotal, budget_account_dict, account_analytic)
            if account_id:
                if asset:
                    domain = [('start_date', '<=', date_planned), ('end_date', '>=', date_planned),
                    ('state', '=', 2), ('planned_amount', '>', 0), ('account_id', '=', account_id.id)]
                    budget_id = self.env['capital.budget'].search(domain)
                    if budget_id:
                        total_price = (sum(budget_account_dict.get(budget_id.account_id.id)))
                        if line.order_id.currency_id and line.order_id.company_id and line.order_id.currency_id != line.order_id.company_id.currency_id:
                            currency_id = line.order_id.currency_id
                            rate = currency_id.with_context(date=self.date_order)
                            total_price = currency_id._convert(total_price, line.order_id.company_id.currency_id, line.order_id.company_id, line.order_id.date_order or fields.Date.today())
                        if (abs(budget_id.sudo().practical_amount) + abs(total_price)) >= abs(
                                budget_id.planned_amount):
                            warning_msg.append('\"The budget limit for account code (%s) is exceeded. \n Please contact the Director or COO\". \n' % product_id.name)
                else:
                    domain = [('start_date', '<=', date_planned), ('end_date', '>=', date_planned),
                    ('state', '=', 2), ('planned_amount', '>', 0), ('account_id', '=', account_id.id)]
                    budget_id = self.env['budgetextension.budget'].search(domain)
                    if budget_id:
                        total_price = (sum(budget_account_dict.get(budget_id.account_id.id)))
                        if line.order_id.currency_id and line.order_id.company_id and line.order_id.currency_id != line.order_id.company_id.currency_id:
                            currency_id = line.order_id.currency_id
                            rate = currency_id.with_context(date=self.date_order)
                            total_price = currency_id._convert(total_price, line.order_id.company_id.currency_id, line.order_id.company_id, line.order_id.date_order or fields.Date.today())
                        if (abs(budget_id.sudo().practical_amount) + abs(total_price)) >= abs(
                                budget_id.planned_amount):
                            warning_msg.append('\"The budget limit for account code (%s) is exceeded. \n Please contact the Director or COO\". \n' % product_id.name)
        if warning_msg:
            raise UserError(_(''.join(warning_msg)))
    @api.model
    def create(self, values):
        """
            Create a new record
            :return: Newly created record ID
        """
        res = super(PurchaseOrder, self).create(values)
        warning_msg = []
        budget_account_dict = {}
        account_analytic = []   
        self.accouting_budget_warning(res, res.order_line, warning_msg, budget_account_dict, account_analytic, update=False)
        return res

    def write(self, values):
        """
            Update an existing record.
            :param values: current records fields data
            :return: Current update record ID
        """
        res = super(PurchaseOrder, self).write(values)
        for rec in self:
            warning_msg = []
            budget_account_dict = {}
            account_analytic = []
            if 'order_line' in values:  
                    rec.accouting_budget_warning(rec, rec.order_line, warning_msg, budget_account_dict, account_analytic, update=True)
        return res
