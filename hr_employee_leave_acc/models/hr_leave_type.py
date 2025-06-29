# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Jesni Banu (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round

class HrLeaveType(models.Model):
	_inherit = 'hr.leave.type'

	accumulated_leave = fields.Boolean(string='Accumulated leave', default =False)
	unpaid_accumulated_leave = fields.Boolean(string='Unpaid Accumulated Leave', default= False)

	@api.constrains('accumulated_leave', 'unpaid_accumulated_leave')
	def _check_duplicated_accumulated_leave(self):
		if self.accumulated_leave and self.unpaid_accumulated_leave:
			raise ValidationError(_("Accumulated and Unpaid Accumulated cannot enable at the same leave type."))
	
class HrSubLeaveType(models.Model):
	_name = 'hr.sub.leave.type'
	_description = 'Sub Leave Type'
	_inherit = ['mail.thread']

	name = fields.Char(string='Name')
	display_name = fields.Char(string='Display Name', compute='_compute_display_name')
	hr_leave_type_id = fields.Many2one('hr.leave.type', string='Leave Type')
	max_days = fields.Float(string='Max Days')
	active = fields.Boolean(string='Active', default=True)

	def _taken_leave(self):
		employee_id = self.env.user.employee_id
		s_fiscal_date = self.hr_leave_type_id.get_fiscal_date()
		return self.env['hr.leave'].search([
                ('employee_id', '=', employee_id.id),
                ('holiday_status_id', '=', self.hr_leave_type_id.id),
                ('state', 'in', ['validate', 'validate1', 'confirm']),
                ('sub_leave_type_id', '=', self.id),
				('date_from','>',s_fiscal_date)
            ])

	@api.depends_context('holiday_status_display_name', 'employee_id', 'from_manager_leave_form')
	def _compute_display_name(self):
		for record in self:
			name = record.name
			leave_type = record.hr_leave_type_id
			taken_sub_leave_days = record._taken_leave()
			if (
				leave_type.requires_allocation == "yes"
				and not self._context.get('from_manager_leave_form')
			):
				if record.max_days != leave_type.max_leaves:
					taken_sub_leave_days = sum(leave.number_of_days for leave in taken_sub_leave_days)
					remaining = float_round(record.max_days - taken_sub_leave_days, precision_digits=2) or 0.0
				else:
					remaining = float_round(leave_type.virtual_remaining_leaves, precision_digits=2) or 0.0
				max_days = float_round(record.max_days, precision_digits=2) or 0.0
				suffix = _(' hours') if leave_type.request_unit == 'hour' else _(' days')
				name = f"{name} ({_('%g remaining out of %g') % (remaining, max_days)}{suffix})"
			record.display_name = name
