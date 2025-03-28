# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
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
import re
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.tools import email_split
from odoo.addons.resource.models.utils import float_to_time, HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools.translate import _

class HrLeaveAlias(models.Model):
	_inherit = 'hr.leave'

	def action_validate(self):
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
		if any(holiday.state not in ['confirm', 'validate1'] for holiday in self):
			raise UserError(_('Leave request must be confirmed in order to approve it.'))

		self.write({'state': 'validate'})
		self.filtered(lambda holiday: holiday.validation_type == 'both').write({'second_approver_id': current_employee.id})
		self.filtered(lambda holiday: holiday.validation_type != 'both').write({'first_approver_id': current_employee.id})
		for holiday in self:
			holiday.filtered(lambda holiday: holiday.holiday_type != 'employee')
			if holiday.holiday_type == 'category':
				employees = holiday.category_id.employee_ids
			elif holiday.holiday_type == 'company':
				employees = self.env['hr.employee'].search([('company_id', '=', holiday.mode_company_id.id)])
			elif holiday.holiday_type == 'department':
				employees = holiday.department_id.member_ids
			else:
				employees = self.env['hr.employee']

			if self.env['hr.leave'].search_count([('date_from', '<=', holiday.date_to), ('date_to', '>', holiday.date_from),
							   ('state', 'not in', ['cancel', 'refuse']), ('holiday_type', '=', 'employee'),
							   ('employee_id', 'in', employees.ids),('id','!=',holiday.id)]):
				raise ValidationError(_('You can not have 2 leaves that overlaps on the same day.'))

			values = [holiday._prepare_holiday_values(employee) for employee in employees]
			leaves = self.env['hr.leave'].with_context(
				tracking_disable=True,
				mail_activity_automation_skip=True,
				leave_fast_create=True,
			).create(values)
			leaves.action_approve()
			# FIXME RLi: This does not make sense, only the parent should be in validation_type both
			if leaves and leaves[0].validation_type == 'both':
				leaves.action_validate()
		employee_requests = self.filtered(lambda hol: hol.holiday_type == 'employee')
		employee_requests._validate_leave_request()
		if not self.env.context.get('leave_fast_create'):
			employee_requests.activity_update()
		for holiday in self:
			holiday_type_id = holiday.holiday_status_id
			if holiday_type_id.accumulated_leave:				
				accumulated_leave = holiday.employee_id.accumulated_leave
				holiday.employee_id.accumulated_leave = accumulated_leave - holiday.number_of_days_display
			elif holiday_type_id.unpaid_accumulated_leave:
				unpaid_accumulated_leave = holiday.employee_id.unpaid_accumulated_leave
				holiday.employee_id.unpaid_accumulated_leave = unpaid_accumulated_leave - \
					holiday.number_of_days_display
		return True



