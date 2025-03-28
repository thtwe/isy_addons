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



class HrLeaveType(models.Model):
	_inherit = 'hr.leave.type'

	accumulated_leave = fields.Boolean(string='Accumulated leave', default =False)
	unpaid_accumulated_leave = fields.Boolean(string='Unpaid Accumulated Leave', default= False)

	@api.constrains('accumulated_leave', 'unpaid_accumulated_leave')
	def _check_duplicated_accumulated_leave(self):
		if self.accumulated_leave and self.unpaid_accumulated_leave:
			raise ValidationError(_("Accumulated and Unpaid Accumulated cannot enable at the same leave type."))
	



