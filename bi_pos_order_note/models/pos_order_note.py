# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class PosOrderNote(models.Model):
	_inherit = 'pos.order.line'

	notes_product_line = fields.Char('Notes')
class PosOrder(models.Model):
	_inherit = 'pos.order'
	pos_ordernote = fields.Text(string='Internal Notes')
