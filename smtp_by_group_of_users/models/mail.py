# -*- coding: utf-8 -*-
#################################################################################
#                                                                               #
#    Part of Odoo. See LICENSE file for full copyright and licensing details.   #
#    Copyright (C) 2018 Jupical Technologies Pvt. Ltd. <http://www.jupical.com> #
#                                                                               #
#################################################################################

from odoo import fields, models, api

class Mail(models.Model):

    _inherit = "mail.mail"

    @api.model
    def create(self, vals):
        if 'uid' in self._context:
            active_user_id = self.env['res.users'].browse(self._context.get('uid'))
            if active_user_id:
                out_mail_sever = self.env['ir.mail_server'].sudo().search([('user_ids', '=',active_user_id.id)], limit=1)
                if out_mail_sever:
                    email_from = active_user_id.partner_id.name + " " + "<" + out_mail_sever.smtp_user + ">"
                    reply_to   = active_user_id.partner_id.name + " " + "<" +active_user_id.partner_id.email or out_mail_sever.smtp_user
                    vals.update({'mail_server_id':out_mail_sever.id, 'email_from':email_from, 'reply_to':reply_to})
        # if vals.get('email_to') and 'cjanzen@isyedu.org' in vals.get('email_to'):
        #     if vals.get('email_cc'):
        #         vals['email_cc'] = (vals['email_cc'] or '') + ',psicard@isyedu.org'
        #     else:
        #         vals['email_cc'] = 'psicard@isyedu.org'
        """
        # cancel email if author and email_to are the same.
        if vals.get('email_to'):
            email_to = vals.get('email_to')
            author_email = self.env.user.login
            if email_to==author_email:
                vals['state']='cancel'
        """
        result = super(Mail, self).create(vals)
        return result

class MailMessage(models.Model):

    _inherit = "mail.message"

    @api.model
    def create(self, vals):
        active_user_id = self._uid
        out_mail_sever = self.env['ir.mail_server'].sudo().search([('user_ids', '=', active_user_id)], limit=1)
        if out_mail_sever:
            vals.update({'mail_server_id':out_mail_sever.id})
        result = super(MailMessage, self).create(vals)
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: