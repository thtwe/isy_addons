from odoo import api, models, fields


class ResUsers(models.Model):
	_inherit = 'res.users'

	portal_employee_leave = fields.Boolean(string='Portal Employee Leave' ,copy = True, default= False)


	def _is_portal(self):
		self.ensure_one()
		return not self.sudo().portal_employee_leave and self.has_group('base.group_portal')
	
	def _is_internal(self):
		self.ensure_one()
		return self.sudo().portal_employee_leave or super()._is_internal()