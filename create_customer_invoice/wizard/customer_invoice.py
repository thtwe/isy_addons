# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class CustomerInvoice(models.TransientModel):
    _name = 'create.customer.invoice'

    customer_invoice_line_ids = fields.One2many('customer.invoice.line', 'customer_invoice_id')
    invoice_ids = fields.Many2many('account.move', readonly=True)
    x_invoice_date = fields.Date(string='Invoice Date')
    x_invoice_due_date = fields.Date(string='Due Date')
    x_date = fields.Date(string='Accounting Date')
    x_studio_other = fields.Boolean(string='Others')
    x_studio_td = fields.Boolean(string='TD Bank')

    invoice_ids_empty = fields.Boolean(string="Is Invoice List Empty", compute='_compute_invoice_ids_empty', store=True)

    @api.depends('invoice_ids')
    def _compute_invoice_ids_empty(self):
        for record in self:
            record.invoice_ids_empty = len(record.invoice_ids) == 0
    
    def action_create_customer_invoice(self):
        invoice_list = []
        for rec in self:
            active_ids = self._context.get('active_ids')
            for active_id in active_ids:
                res_partner_id = self.env['res.partner'].search([('id', '=', active_id)])
                journal_id = self.env['account.journal'].search([('name','ilike','Customer')])
                if len(journal_id)!=1:
                    raise UserError('There is more than 1 Customer journal. Please contact to Administrator.')
                invoice_data = {'partner_id': res_partner_id.id,
                                # 'account_id': res_partner_id.property_account_receivable_id.id,
                                'move_type': 'out_invoice',
                                'journal_id': journal_id.id,
                                'invoice_date': rec.x_invoice_date,
                                'invoice_date_due': rec.x_invoice_due_date,
                                'date': rec.x_date,
                                'x_studio_others': rec.x_studio_other,
                                'x_studio_td_bank': rec.x_studio_td,
                                }
                account_invoice_id = self.env['account.move'].create(invoice_data)

                account_id = self.env['account.account'].search([('account_type', '=', 'income')], limit=1)
                for line in rec.customer_invoice_line_ids:
                    account_invoice_line_data = {
                        'product_id': line.product_id.id,
                        'quantity': line.quantity,
                        'name': line.name,
                        'move_id': account_invoice_id.id,
                        'price_unit': 0.0,
                        'account_id': account_id.id,
                    }
                    # account_invoice_line_id = self.env['account.move.line'].create(account_invoice_line_data)
                    account_invoice_id.write({'invoice_line_ids':[(0,0,account_invoice_line_data)]})
                    # account_invoice_line_id._onchange_product_id()
                    # account_invoice_line_id.write({'name': line.name})
                #for inv_line in account_invoice_id.invoice_line_ids:
                    #inv_line.with_context(check_move_validity=False)._onchange_product_id()
                    # inv_line._onchange_mark_recompute_taxes()
                    # inv_line._onchange_uom_id()
                    # inv_line._onchange_amount_currency()

                account_invoice_id.with_context(check_move_validity=False)._onchange_quick_edit_line_ids()
                account_invoice_id._recompute_cash_rounding_lines()
                invoice_list.append(account_invoice_id.id)
            rec.invoice_ids = invoice_list
            return {
               'type': 'ir.actions.act_window',
               'res_model': 'create.customer.invoice',
               'view_type': 'form',
               'view_mode': 'form',
               'res_id': rec.id,
               'target': 'new',
            }


class CustomerInvoiceLine(models.TransientModel):
    _name = 'customer.invoice.line'

    customer_invoice_id = fields.Many2one('create.customer.invoice')
    name = fields.Text(string='Description', required=True)
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'),
                            required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')

    @api.onchange('product_id')
    def _onchange_product(self):
        for rec in self:
            rec.name = False
            if rec.product_id:
                rec.name = rec.product_id.display_name
                if not rec.uom_id or rec.product_id.uom_id.category_id.id != rec.uom_id.category_id.id:
                    rec.uom_id = rec.product_id.uom_id.id
