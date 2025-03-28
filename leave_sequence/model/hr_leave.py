# -*- coding: utf-8 -*-

from odoo import fields, models, api

class HolidaysRequest(models.Model):
	_inherit = 'hr.leave'

	sequence_id = fields.Char('Sequence', readonly=True, store=True, default='New')

	@api.model
	def create(self, vals): 
		if vals.get('sequence_id', 'New') == 'New':
			vals['sequence_id'] = self.env['ir.sequence'].next_by_code('leave_seq') or 'New'
		return super(HolidaysRequest, self).create(vals)
		return result

