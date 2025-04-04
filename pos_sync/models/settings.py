# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_commission_account_id = fields.Many2one(
        'account.account', string='Commission Account', ondelete='cascade')
    pos_agent_account_id = fields.Many2one(
        'account.account', string='Agent Account', ondelete='cascade')
    pos_vendor_account_id = fields.Many2one(
        'account.account', string='Vendor Account', ondelete='cascade')
    pos_commission = fields.Float(string='Commision (%)')
    pos_journal_id = fields.Many2one(
        'account.journal', string='Journal', ondelete='cascade')
    pos_agent = fields.Many2one(
        'res.partner', string='Agent', ondelete='cascade')
    pos_income_account_id = fields.Many2one(
        'account.account', string='Income Account', ondelete='cascade')
    pos_revenue_account_id = fields.Many2one(
        'account.account', string='Revenue Account', ondelete='cascade')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            pos_commission_account_id=int(params.get_param(
                'pos_sync.pos_commission_account_id')),
            pos_agent_account_id=int(params.get_param(
                'pos_sync.pos_agent_account_id')),
            pos_vendor_account_id=int(params.get_param(
                'pos_sync.pos_vendor_account_id')),
            pos_commission=float(params.get_param('pos_sync.pos_commission')),
            pos_journal_id=int(params.get_param('pos_sync.pos_journal_id')),
            pos_agent=int(params.get_param('pos_sync.pos_agent')),
            pos_income_account_id=int(params.get_param(
                'pos_sync.pos_income_account_id')),
            pos_revenue_account_id=int(params.get_param('pos_sync.pos_revenue_account_id')),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        pos_commission_account_id = self.pos_commission_account_id and self.pos_commission_account_id.id or False
        pos_agent_account_id = self.pos_agent_account_id and self.pos_agent_account_id.id or False
        pos_vendor_account_id = self.pos_vendor_account_id and self.pos_vendor_account_id.id or False
        pos_commission = self.pos_commission or False
        pos_journal_id = self.pos_journal_id and self.pos_journal_id.id or False
        pos_agent = self.pos_agent and self.pos_agent.id or False
        pos_income_account_id = self.pos_income_account_id and self.pos_income_account_id.id or False
        pos_revenue_account_id = self.pos_revenue_account_id and self.pos_revenue_account_id.id or False

        param.set_param('pos_sync.pos_commission_account_id',
                        pos_commission_account_id)
        param.set_param('pos_sync.pos_agent_account_id', pos_agent_account_id)
        param.set_param('pos_sync.pos_vendor_account_id', pos_vendor_account_id)
        param.set_param('pos_sync.pos_commission', pos_commission)
        param.set_param('pos_sync.pos_journal_id', pos_journal_id)
        param.set_param('pos_sync.pos_agent', pos_agent)
        param.set_param('pos_sync.pos_income_account_id', pos_income_account_id)
        param.set_param('pos_sync.pos_revenue_account_id', pos_revenue_account_id)
