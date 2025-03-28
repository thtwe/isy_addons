# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    period_to_unblock = fields.Integer(
        'Lift Block In', help="Set the time needed before a user is unblocked.",related="company_id.period_to_unblock",readonly=False)

    period_to_unblock_unit = fields.Selection([('second','Second'),('minute','Minute'),('hour','Hour',),('day','Day')]
                                              , readonly=False, related="company_id.period_to_unblock_unit")

class Company(models.Model):
    _inherit = 'res.company'
    
    period_to_unblock = fields.Integer('Period To Unblock',default=1)
    
    period_to_unblock_unit = fields.Selection([('second','Second'),('minute','Minute'),('hour','Hour',),('day','Day')] ,default='day', help="Set the time needed before a user is unblocked.")