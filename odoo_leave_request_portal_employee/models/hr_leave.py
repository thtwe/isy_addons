from odoo import models

class HrLeave(models.Model):
	_inherit = 'hr.leave'

	def _get_responsible_for_approval(self):
		if self.employee_id.user_id.portal_employee_leave:
			return self.employee_id.user_id
		return super(HrLeave, self)._get_responsible_for_approval()
     