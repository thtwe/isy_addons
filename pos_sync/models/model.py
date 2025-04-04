# -*- coding: utf-8 -*-

import time
import datetime
import requests
import base64
import json
from ast import literal_eval
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero
import logging

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class SyncPosRecharge(models.Model):
    _name = 'sync.pos.recharge'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # , 'portal.mixin'
    _description = 'Synced POS Recharge'
    _order = 'date desc'

    name = fields.Char(string='Name', required=True,
                       index=True, copy=False, default='New')
    customer_no = fields.Integer(string='Customer No', store=True, index=True)
    partner_id = fields.Many2one(
        'res.partner', string='Partner', ondelete='cascade')
    date = fields.Datetime(string='Date', store=True)
    recharge_amount = fields.Float(
        string='Recharge Amount', store=True, track_visibility='onchange')
    order_ref = fields.Char(string='Order', store=True)
    payment_type_id = fields.Many2one(
        'sync.pos.type', string='Payment Type', ondelete='cascade')
    sync_payment_type = fields.Char(string='Synced Payment Type', store=True)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.user.company_id, string='Company', readonly=True)
    move_id = fields.Many2one(
        'account.move', string='Journal Entry', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Posted'),
        ('cancel', 'Cancelled')
    ],  readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'sync.pos.recharge') or '/'
        return super(SyncPosRecharge, self).create(vals)

    @api.model
    def sync_data(self):
        try:
            PARAMS = {'key': '336F7A5A9A1FB859A69D8221E585E'}
            URL = 'https://store.isyedu.org/impfiles/odoo_sync.php'
            r = requests.post(url=URL, data=PARAMS)
            mydata = r.json()
            mydata = mydata or []

            for value in mydata:
                if value.get('customer_type') == 'Staff':
                    employee_id = self.env['hr.employee'].search(
                        [('barcode', '=', value.get('customer_number'))])
                    partner = employee_id.address_home_id
                else:
                    partner = self.env['res.partner'].search(
                        [('student_number', '=', value.get('customer_number'))])
                payment_type = self.env['sync.pos.type'].search(
                    [('name', 'ilike', value.get('payment_type'))], limit=1)
                self.create({
                    'customer_no': value.get('customer_number'),
                    'recharge_amount': value.get('recharge_amount'),
                    'date': datetime.datetime.strptime(value.get('transaction_date'), '%Y-%m-%d %H:%M:%S'),
                    'order_ref': value.get('order_id'),
                    'payment_type_id': payment_type.id,
                    'sync_payment_type': value.get('payment_type'),
                    'partner_id': partner.id,
                    'state': 'draft',
                })
        except requests.HTTPError as e:
            _logger.debug("Data request failed with code: %r, msg: %r, content: %r",
                          e.response.status_code, e.response.reason, e.response.content)
            raise

        return True

    def action_move_transaction(self):
        created_moves = self.env['account.move']
        if not self.payment_type_id.journal_id:
            raise UserError(_("No Credit account found for the Journal, please configure one.") % (
                self.payment_type_id.journal_id))
        if not self.payment_type_id.journal_id:
            raise UserError(_("No Debit account found for the account, please configure one.") % (
                self.payment_type_id.journal_id))
        for line in self:
            date = line.date
            name = line.name
            company_currency = line.company_id.currency_id
            currency = line.payment_type_id.journal_id.currency_id
            amount = line.recharge_amount
            converted_amount = currency.compute(amount, company_currency)

            move_line_cash = {
                'name': name,
                'account_id': line.payment_type_id.journal_id.default_account_id.id,
                'debit': converted_amount or 0.0,
                'credit': 0.0,
                'journal_id': line.payment_type_id.journal_id.id,
                'currency_id': currency.id or False,
                'amount_currency': amount or 0.0,
            }
            move_line_payable = {
                'name': name,
                'account_id': line.partner_id.property_account_payable_id.id,
                'credit': converted_amount or 0.0,
                'debit':  0.0,
                'journal_id': line.payment_type_id.journal_id.id,
                'partner_id': line.partner_id.id,
                'currency_id': currency.id or False,
                'amount_currency': - amount or 0.0,
            }

            move_vals = {
                'ref': name,
                'date': date or False,
                'journal_id': line.payment_type_id.journal_id.id,
                'line_ids': [(0, 0, move_line_cash), (0, 0, move_line_payable)],
            }

            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id,
                        'state': 'done',
                        'account_validate_date': time.strftime('%Y-%m-%d'),
                        'account_by_id': line.env.user.id})
            created_moves |= move

        return [x.id for x in created_moves]


class SyncPosTransaction(models.Model):
    _name = 'sync.pos.transaction'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # , 'portal.mixin'
    _description = 'Synced POS Transaction'
    _order = 'date desc'

    name = fields.Char(string='Name', required=True,
                       index=True, copy=False, default='New')
    customer_no = fields.Integer(string='Customer No', store=True, index=True)
    student_id = fields.Many2one(
        'res.partner', string='Student', ondelete='cascade')
    vendor_id = fields.Many2one(
        'res.partner', string='Vendor', ondelete='cascade')
    date = fields.Date(string='Date', store=True)
    transaction_amount = fields.Float(
        string='Transaction Amount', store=True, readonly=True, track_visibility='onchange')
    pos_commission_amount = fields.Float(
        string='Commission (ISY/Agent)', store=True, readonly=True, track_visibility='onchange')
    vendor_payable = fields.Float(
        string='Vendor Payable', store=True, readonly=True, track_visibility='onchange')
    order_ref = fields.Char(string='Order', store=True)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.user.company_id, string='Company', readonly=True)
    move_id = fields.Many2one(
        'account.move', string='Journal Entry', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('post', 'Posted'),
        ('cancel', 'Cancelled'),
    ],  readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    journal_id = fields.Many2one(
        'account.journal', string='Journal', ondelete='cascade')
    agent_id = fields.Many2one(
        'res.partner', string='Agent', ondelete='cascade')
    currency_rate = fields.Float(string='Currency Rate')
    vendor_reconciled = fields.Boolean(string='Vendor Reconciled', default=False)
    agent_reconciled = fields.Boolean(string='Agent Reconciled', default=False)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'sync.pos.transaction') or '/'
        return super(SyncPosTransaction, self).create(vals)

    @api.model
    def sync_data_transaction(self):
        try:
            myurl = 'https://powerschool.isyedu.org/oauth/access_token/'
            ps_code = '194f599c-389d-45e6-9c34-dd91eae3530d'
            ps_secret = '6045b46c-89f0-4cf1-8b4e-3495a7e8350b'
            mydata = ps_code + ":" + ps_secret
            data_bytes = mydata.encode("utf-8")
            mysecret = base64.b64encode(data_bytes)
            postFields = {'grant_type': 'client_credentials'}
            headers = {"Authorization": "Basic " + mysecret.decode("utf-8")}
            params = {"grant_type": "client_credentials"}
            response = requests.post(myurl, headers=headers, data=params)
            data = response.json()
            access_token = data['access_token']
            hed = {'Authorization': 'Bearer ' + access_token,
                   'Content-Type': 'application/json'}
            myresponse = requests.post(
                "https://powerschool.isyedu.org/ws/schema/query/com.isy.odoo.pull_food_order_details?pagesize=0", headers=hed)
            mydata = myresponse.json()
            mydata = mydata and mydata['record'] or []

            for value in mydata:
                if value.get('user_type') == 'Student':
                    partner = self.env['res.partner'].search(
                        [('student_number', '=', value.get('user_number'))])
                else:
                    employee_id = self.env['hr.employee'].search(
                        [('barcode', '=', value.get('user_number'))])
                    partner = employee_id.address_home_id

                vendor_id = self.env['res.partner'].search(
                    [('name', 'ilike', value.get('vendor_name'))], limit=1)

                journal_id = int(self.env['ir.config_parameter'].sudo(
                ).get_param('pos_sync.pos_journal_id'))

                agent = int(self.env['ir.config_parameter'].sudo(
                ).get_param('pos_sync.pos_agent'))

                pos_commission = float(self.env['ir.config_parameter'].sudo(
                ).get_param('pos_sync.pos_commission'))

                last_currency_rate_rec = self.env['pos.currency.rate'].search(
                    [], order="date desc", limit=1)

                currency_rate = float(last_currency_rate_rec.rate)
                transaction_amount = float(value.get('order_price'))
                pos_commission_amount = transaction_amount * pos_commission / 100
                vendor_payable = transaction_amount - pos_commission_amount

                self.create({
                    'customer_no': value.get('user_number'),
                    'transaction_amount': transaction_amount,
                    'vendor_payable': vendor_payable,
                    'currency_rate': currency_rate,
                    'agent_id': agent,
                    'pos_commission_amount': pos_commission_amount,
                    'date': datetime.datetime.strptime(value.get('order_date'), '%Y-%m-%d'),
                    'order_ref': value.get('order_id'),
                    'student_id': partner.id,
                    'state': 'draft',
                    'vendor_id': vendor_id.id,
                    'journal_id': journal_id,
                })
        except requests.HTTPError as e:
            _logger.debug("Data request failed with code: %r, msg: %r, content: %r",
                          e.response.status_code, e.response.reason, e.response.content)
            raise
        return True

    def action_move_transaction(self):
        created_moves = self.env['account.move']
        if not self.journal_id:
            raise UserError(_("No Credit account found for the Journal, please configure one.") % (
                self.journal_id))
        if not self.journal_id:
            raise UserError(_("No Debit account found for the account, please configure one.") % (
                self.journal_id))
        for line in self:
            date = line.date
            name = line.name

            comission_account_id = int(self.env['ir.config_parameter'].sudo(
            ).get_param('pos_sync.pos_commission_account_id'))
            agent_account_id = int(self.env['ir.config_parameter'].sudo(
            ).get_param('pos_sync.pos_agent_account_id'))
            vendor_account_id = int(self.env['ir.config_parameter'].sudo(
            ).get_param('pos_sync.pos_vendor_account_id'))

            currency_rate = line.currency_rate
            currency = line.journal_id.currency_id
            commission_amount = line.pos_commission_amount
            vendor_payable = line.vendor_payable
            transaction_amount = line.transaction_amount

            converted_commission_amount = commission_amount / currency_rate
            converted_vendor_payable = vendor_payable / currency_rate
            converted_transaction_amount = transaction_amount / currency_rate

            move_line_agent = {
                'name': name,
                'account_id': comission_account_id,
                'credit':  0.0,
                'debit': converted_transaction_amount or 0.0,
                'partner_id': line.student_id.id,
                'currency_id': currency.id or False,
                'amount_currency': transaction_amount or 0.0,
            }

            move_line_vendor = {
                'name': name,
                'account_id': vendor_account_id,
                'debit':  0.0,
                'credit': converted_vendor_payable or 0.0,
                'partner_id': line.vendor_id.id,
                'currency_id': currency.id or False,
                'amount_currency': - vendor_payable or 0.0,
            }

            move_line_commission = {
                'name': name,
                'account_id': agent_account_id,
                'debit':  0.0,
                'credit': converted_commission_amount or 0.0,
                'currency_id': currency.id or False,
                'amount_currency': - commission_amount or 0.0,
            }

            move_vals = {
                'ref': name,
                'date': date or False,
                'journal_id': line.journal_id.id,
                'line_ids': [(0, 0, move_line_vendor), (0, 0, move_line_agent), (0, 0, move_line_commission)],
            }

            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id,
                        'state': 'post',
                        'account_validate_date': time.strftime('%Y-%m-%d'),
                        'account_by_id': line.env.user.id})
            created_moves |= move

        return [x.id for x in created_moves]


class PosPaymentTransaction(models.Model):
    _name = 'pos.payment.transaction'
    _inherit = ['mail.thread', 'mail.activity.mixin']#, 'portal.mixin'
    _description = 'POS Payment'

    name = fields.Char(string='Name', required=True,
                       index=True, copy=False, default='New')
    vendor_id = fields.Many2one(
        'res.partner', string='Vendor', ondelete='cascade')
    payable_total = fields.Float(
        string='Payable Amount')
    journal_id = fields.Many2one(
        'account.journal', string='Journal', ondelete='cascade')
    payment_amount = fields.Float(string='Agent Received Amount', compute="_compute_payment_amount")
    # amount_diff = fields.Float(
    #     string='Amount Difference', compute='_compute_amount_diff')
    # write_off_account = fields.Many2one(
    #     'account.account', string='Account', ondelete='cascade')
    # write_off_note = fields.Char(string='Write-off Note', store=True)
    # write_off = fields.Boolean(string='Write Off')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Posted'),
        ('cancel', 'Cancelled')
    ],  readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    move_id = fields.Many2one(
        'account.move', string='Journal Entry', readonly=True)
    trans_type = fields.Selection([('vendor_payment', 'Vendor Payment'), ('agent_payment', 'Agent Payment')], string="Transaction Type")
    income_amount = fields.Float(string='Receive From Agent Amount')
    payment_date = fields.Date(string="Payment Date", default=fields.Datetime.now().date())
    received_amount = fields.Float(string="Received Amount ( ISY )")

    @api.depends('income_amount')
    def _compute_payment_amount(self):
        for rec in self:
            if rec.income_amount:
                rec.payment_amount = rec.payable_total - rec.income_amount
                commission_rate = float(rec.env['ir.config_parameter'].sudo().get_param('pos_sync.pos_commission'))
                rec.received_amount = rec.income_amount - (rec.payable_total * (100 - commission_rate) / 100) or 0

    @api.onchange('from_date', 'to_date', 'vendor_id', 'trans_type')
    def onchange_date_from_to(self):
        if self.from_date and self.to_date and self.vendor_id and self.trans_type:
            if self.trans_type == 'vendor_payment':
                domain = [('date', '>=', self.from_date), ('date', '<=', self.to_date), ('vendor_reconciled', '=', False), ('vendor_id', '=', self.vendor_id.id)]
            elif self.trans_type == 'agent_payment':
                domain = [('date', '>=', self.from_date), ('date', '<=', self.to_date), ('agent_reconciled', '=', False), ('vendor_id', '=', self.vendor_id.id)]
            obj_sync_trans = self.env['sync.pos.transaction'].search(domain)
            amount = 0
            for obj_sync_tran in obj_sync_trans:
                if self.trans_type == 'vendor_payment':
                    amount += obj_sync_tran.vendor_payable
                elif self.trans_type == 'agent_payment':
                    amount += obj_sync_tran.transaction_amount
            self.payable_total = amount

    @ api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'pos.payment.transaction') or '/'
        return super(PosPaymentTransaction, self).create(vals)
    #
    # @ api.onchange('vendor_id')
    # def _compute_payable(self):
    #     for rec in self:
    #         if rec.vendor_id:
    #             aml_obj = self.env['account.move.line']
    #             domain = [('partner_id', '=', rec.vendor_id.id), ('account_id',
    #                                                             '=', rec.vendor_id.property_account_payable_id.id)]
    #             where_query = aml_obj._where_calc(domain)
    #             aml_obj._apply_ir_rules(where_query, 'read')
    #             from_clause, where_clause, where_clause_params = where_query.get_sql()
    #             select = "SELECT sum(credit) - sum(debit) from " + from_clause + " where " + where_clause
    #             self.env.cr.execute(select, where_clause_params)
    #             payable_total = self.env.cr.fetchone()[0]
    #
    #             last_currency_rate_rec = self.env['pos.currency.rate'].search(
    #                 [], order="date desc", limit=1)
    #
    #             currency_rate = float(last_currency_rate_rec.rate)
    #
    #             rec.payable_total = payable_total * currency_rate

    # @ api.onchange('payment_amount', 'payable_total')
    # def _compute_amount_diff(self):
    #     for rec in self:
    #         rec.amount_diff = rec.payable_total - rec.payment_amount
    #         if rec.amount_diff != rec.payable_total and rec.amount_diff > 0.0:
    #             rec.write_off = True

    def action_move_transaction(self):
        created_moves = self.env['account.move']
        if not self.journal_id:
            raise UserError(_("No Credit account found for the Journal, please configure one.") % (
                self.journal_id))
        if not self.journal_id:
            raise UserError(_("No Debit account found for the account, please configure one.") % (
                self.journal_id))
        # if self.write_off == True and not self.write_off_account:
        #     raise UserError(_("Please choose an account for write-off amount!"))
        for line in self:
            date = line.payment_date
            name = line.name

            last_currency_rate_rec = self.env['pos.currency.rate'].search(
                [], order="date desc", limit=1)

            currency_rate = float(last_currency_rate_rec.rate)

            currency = line.journal_id.currency_id

            payable_total = line.payable_total
            payment_amount = line.income_amount
            amount_diff = self.payment_amount
            converted_payable_total = payable_total / currency_rate
            received_amount = line.received_amount
            commission_amount = amount_diff + received_amount

            if self.trans_type == 'vendor_payment':
                converted_payment_amount = converted_payable_total
            else:
                converted_payment_amount = self.income_amount / currency_rate
                converted_received_amount = received_amount / currency_rate
                converted_commission_amount = commission_amount / currency_rate

            converted_amount_diff = amount_diff / currency_rate

            pos_income_account_id = int(self.env['ir.config_parameter'].sudo(
            ).get_param('pos_sync.pos_income_account_id'))

            pos_vendor_account_id = int(self.env['ir.config_parameter'].sudo().get_param('pos_sync.pos_vendor_account_id'))

            pos_agent_account_id = int(self.env['ir.config_parameter'].sudo().get_param('pos_sync.pos_agent_account_id'))

            pos_agent = int(self.env['ir.config_parameter'].sudo().get_param('pos_sync.pos_agent'))

            comission_account_id = int(self.env['ir.config_parameter'].sudo(
            ).get_param('pos_sync.pos_commission_account_id'))

            pos_revenue_account_id = int(self.env['ir.config_parameter'].sudo(
            ).get_param('pos_sync.pos_revenue_account_id'))

            if not pos_vendor_account_id:
                raise(_("Please ask administrator to setup pos vendor account id."))
            elif not pos_income_account_id:
                raise(_("Please ask administrator to setup pos income account id."))
            elif not pos_agent:
                raise(_("Please ask administrator to setup pos agent."))
            if self.trans_type == 'agent_payment':
                #total transactions debit student
                move_line_payable = {
                    'name': name,
                    'account_id': comission_account_id,
                    'debit': 0.0,
                    'credit': converted_payable_total,
                    'currency_id': currency.id or False,
                    'amount_currency': -payable_total or 0.0,
                }
                #cash received debit
                move_line_payment = {
                    'name': name,
                    'account_id': line.journal_id.default_account_id.id,
                    'debit':  converted_payment_amount,
                    'credit':  0.0,
                    'currency_id': currency.id or False,
                    'amount_currency': payment_amount or 0.0,
                }

                #School Income
                move_line_income = {
                    'name': name,
                    'label': '',
                    'account_id': pos_revenue_account_id,
                    'partner_id': line.vendor_id.id,
                    'debit':  0.0,
                    'credit': converted_received_amount or 0.0,
                    'currency_id': currency.id or False,
                    'amount_currency': - received_amount or 0.0,
                }
                #sale commission
                move_line_commission = {
                    'name': name,
                    'account_id': pos_agent_account_id,
                    'debit':  converted_commission_amount,
                    'credit':  0.0,
                    'currency_id': currency.id or False,
                    'amount_currency': commission_amount or 0.0,
                }
                _logger.info("=======================Starting=========================")
                _logger.info("2C2P Receivable credit" + str(converted_payable_total) + "--USD" + str(payable_total))
                _logger.info("Cash debit" + str(converted_payment_amount) + "--USD" + str(payment_amount))
                _logger.info("441003 School Canteen Commission ( Rev )" + str(converted_received_amount) + "--USD" + str(received_amount))
                _logger.info("POS Sales Commission ( TMP A\C )" + str(converted_commission_amount) + "--USD" + str(commission_amount))
                move_vals = {
                    'ref': name,
                    'date': date or False,
                    'journal_id': line.journal_id.id,
                    'line_ids': [(0, 0, move_line_payable), (0, 0, move_line_payment), (0, 0, move_line_income), (0, 0, move_line_commission)],
                }
            else:
                move_line_payable = {
                    'name': name,
                    'account_id': pos_vendor_account_id,
                    'debit': converted_payable_total or 0.0,
                    'credit':  0.0,
                    'partner_id': line.vendor_id.id,
                    'currency_id': currency.id or False,
                    'amount_currency': payable_total or 0.0,
                }

                move_line_payment = {
                    'name': name,
                    'account_id': line.journal_id.default_account_id.id,
                    'debit':  0.0,
                    'credit': converted_payment_amount or 0.0,
                    'currency_id': currency.id or False,
                    'amount_currency': - payment_amount or 0.0,
                }

                move_vals = {
                    'ref': name,
                    'date': date or False,
                    'journal_id': line.journal_id.id,
                    'line_ids': [(0, 0, move_line_payable), (0, 0, move_line_payment)],
                }

            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id,
                        'state': 'done',
                        'account_validate_date': time.strftime('%Y-%m-%d'),
                        'account_by_id': line.env.user.id})
            created_moves |= move
        if self.trans_type == 'vendor_payment':
            domain = [('date', '>=', self.from_date), ('date', '<=', self.to_date), ('vendor_reconciled', '=', False), ('vendor_id', '=', self.vendor_id.id)]
            val = {'vendor_reconciled': True}
        elif self.trans_type == 'agent_payment':
            domain = [('date', '>=', self.from_date), ('date', '<=', self.to_date), ('agent_reconciled', '=', False), ('vendor_id', '=', self.vendor_id.id)]
            val = {'agent_reconciled': True}
        obj_sync_trans = self.env['sync.pos.transaction'].search(domain)
        obj_sync_trans.write(val)
        return [x.id for x in created_moves]


class SyncPosType(models.Model):
    _name = 'sync.pos.type'
    _description = 'Synced POS Payment Type'

    name = fields.Char(string='Name', store=True, index=True, copy=False)
    journal_id = fields.Many2one(
        'account.journal', string='Journal', ondelete='cascade')
    active = fields.Boolean(string='Active', default=True)


class PosCurrencyRate(models.Model):
    _name = 'pos.currency.rate'
    _description = 'POS Currency Rate'

    date = fields.Datetime(string='Date')
    rate = fields.Float(string='Rate', store=True)
