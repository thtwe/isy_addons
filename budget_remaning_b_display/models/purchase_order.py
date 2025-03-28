# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrderLine(models.Model):
	_inherit = "purchase.order.line"
	practical_amount = fields.Float(compute='_compute_practical_amount', string='Practical Amount', digits=0)
	planned_amount = fields.Float(compute='_compute_planned_amount', string='Planned Amount', digits=0)
	amount_difference = fields.Float(compute='_compute_difference', string='Remaining Balance', digits=0)
	
	def _compute_planned_amount(self):
		for line in self:
			product_id = line.product_id
			date_planned = line.date_planned.date()
			if product_id.property_account_expense_id:
				account_id = product_id.property_account_expense_id
				if account_id:
					domain = [('start_date', '<=', date_planned), ('end_date', '>=', date_planned),
					('state', '=', 2), ('planned_amount', '>', 0), ('account_id', '=', account_id.id)]
					budget_id = self.env['budgetextension.budget'].search(domain)
			elif product_id.categ_id.property_account_expense_categ_id:
				account_id = product_id.categ_id.property_account_expense_categ_id
				if account_id:
					domain = [('start_date', '<=', date_planned), ('end_date', '>=', date_planned),
					('state', '=', 2), ('planned_amount', '>', 0), ('account_id', '=', account_id.id)]
					budget_id = self.env['budgetextension.budget'].search(domain)
			elif product_id.asset_category_id:
				account_id = product_id.asset_category_id.account_asset_id
				if account_id:
					domain = [('start_date', '<=', date_planned), ('end_date', '>=', date_planned),
					('state', '=', 2), ('planned_amount', '>', 0), ('account_id', '=', account_id.id)]
					budget_id = self.env['capital.budget'].search(domain)
			line.planned_amount = abs(budget_id.sudo().planned_amount)
			   
	def _compute_practical_amount(self):
		for line in self:
			product_id = line.product_id
			date_planned = line.date_planned.date()
			if product_id.property_account_expense_id:
				account_id = product_id.property_account_expense_id
				if account_id:
					domain = [('start_date', '<=', date_planned), ('end_date', '>=', date_planned),
					('state', '=', 2), ('planned_amount', '>', 0), ('account_id', '=', account_id.id)]
					budget_id = self.env['budgetextension.budget'].search(domain)
			elif product_id.categ_id.property_account_expense_categ_id:
				account_id = product_id.categ_id.property_account_expense_categ_id
				if account_id:
					domain = [('start_date', '<=', date_planned), ('end_date', '>=', date_planned),
					('state', '=', 2), ('planned_amount', '>', 0), ('account_id', '=', account_id.id)]
					budget_id = self.env['budgetextension.budget'].search(domain)
			elif product_id.asset_category_id:
				account_id = product_id.asset_category_id.account_asset_id
				if account_id:
					domain = [('start_date', '<=', date_planned), ('end_date', '>=', date_planned),
					('state', '=', 2), ('planned_amount', '>', 0), ('account_id', '=', account_id.id)]
					budget_id = self.env['capital.budget'].search(domain)
			line.practical_amount = abs(budget_id.sudo().practical_amount)
			
	def _compute_difference(self):
		for line in self:
			line.amount_difference = line.planned_amount - line.practical_amount
	
