# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SyncPosRechargeWizard(models.TransientModel):
    _name = 'sync.pos.recharge.wizard'
    _description = 'Sync POS Recharge Wizard'

    def update_recharge_state(self):
        for rec in self:
            rec.state = 'done'

            