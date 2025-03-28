# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta

class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    prev_month_salary = fields.Monetary(string="Last Month Salary", compute="_compute_prev_sal", store=True)
    variance = fields.Monetary(string="Variance", compute="_compute_variance", store=True)

    @api.depends('amount', 'date_from', 'date_to')
    def _compute_prev_sal(self):
        for line in self:
            if line.category_id.id == 5:
                pre_month = line.date_from - timedelta(days=1)
                cate_id = 5
                payslip_line = self.env['hr.payslip.line'].search([
                    ('date_to', '=', pre_month),
                    ('employee_id', '=', line.employee_id.id),
                    ('contract_id', '=', line.contract_id.id),
                    ('category_id', '=', cate_id)
                ], limit=1)
                line.prev_month_salary = payslip_line.total if payslip_line else 0.0     

    @api.depends('prev_month_salary')
    def _compute_variance(self):
        for line in self:
            if line.category_id.id == 5:
                line.variance = line.total - line.prev_month_salary