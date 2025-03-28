# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    user_analytic_ids = fields.Many2many(
        'account.analytic.account',
        'analytic_user_rel',
        'user_id',
        'account_analytic_id',
        'Allowd Cost Centers')
