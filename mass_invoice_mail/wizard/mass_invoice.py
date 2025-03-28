# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   If not, see <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import api, fields, models

class MassInvoice(models.TransientModel):
    _name = "mass.invoice"

    def _defaultTemplate(self):
        templateObj = self.env['mail.template'].search([('model','=','account.move')])
        if templateObj:
            return templateObj[0].id
        return False

    template_id = fields.Many2one(
        'mail.template', 'Use template', index=True,
        domain="[('model', '=', 'account.move')]", default=_defaultTemplate)

    def sendMail(self):
        partial = self.create({})
        return {
            'name': ("Mass Invoice Mail"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'mass.invoice',
            'res_id': partial.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': self._context,
            'domain': '[]',
        }

    def sendMails(self):
        invoiceIds = self._context.get('active_ids')
        failedIds = []
        errorIds = []
        count = 0
        for invoiceId in invoiceIds:
            invoiceObj = self.env['account.move'].browse(invoiceId)
            if not invoiceObj.partner_id.email:
                if invoiceObj.number:
                    failedIds.append(invoiceObj.number)
                else:
                    failedIds.append(str(invoiceObj.id))
                continue
            try:
                data = invoiceObj.action_invoice_sent()
                if 'context' in data:
                    mailObj = self.env['mail.compose.message'].with_context(data['context']).create({})
                    mailObj.onchange_template_id_wrapper()
                    mailObj.action_send_mail()
                    count = count + 1
            except Exception as e:
                if invoiceObj.number:
                    errorIds.append(invoiceObj.number)
                else:
                    errorIds.append(str(invoiceObj.id))
        text = "unable to send email"
        if count:
            text = "{} mail(s) have been sent successfully.".format(count)
        if failedIds:
            invoices = ", ".join(failedIds)
            text = "{} \nunable to send email for invoices : {} Reason : email id is not present".format(text, invoices)
        if errorIds:
            invoices = ",".join(errorIds)
            text = "{} \n unable to send email for invoices : {} Reason : Connection Issue".format(text, invoices)
        return self.env['wk.wizard.message'].genrated_message(text)
