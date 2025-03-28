# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    user_employee_ids = fields.Many2many(
        'hr.employee',
        'employee_user_rel',
        'user_id',
        'employee_id',
        'Employee for Leave')
