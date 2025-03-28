# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from odoo import models, fields, api
from email.utils import formataddr
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)
from lxml import etree


class ResUsers(models.Model):
        
    _inherit = 'res.users'
    _name = 'res.users'

    _inherit = ['res.users', 'mail.thread']
    
    login_locked = fields.Selection([('blocked','Blocked'),('active','Active')], string="Login Status", track_visibility='onchange')
    
    
    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ResUsers, self)._fields_view_get(view_id, view_type, toolbar, submenu)
        group = self.env.ref('login_attempts.group_view_logins_admin').id
        if view_type == 'form':
            if not self.env.user.has_group('base.group_system'):
                doc = etree.XML(res['arch'])
                node = doc.xpath("//field[@name='in_group_%s']"%group )
                if node:
                    node = node[0]
                    node.set('invisible', '1')
                res['arch'] = etree.tostring(doc, encoding='unicode')
            else:
                doc = etree.XML(res['arch'])
                node = doc.xpath("//field[@name='in_group_%s']"%group )
                if node:
                    node[0].set('invisible', '0')
                res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    
    
    @api.model
    def update_user_login_state(self, cron_mode=True):
        recs = self.search([('login_locked', '=', 'blocked')])
        period_to_unblock = self.env.user.company_id.period_to_unblock
        period_to_unblock_unit = self.env.user.company_id.period_to_unblock_unit
        for rec in recs:
            current_time = datetime.now()
            loginlocked_time = datetime.strptime(str(rec.login_locked_time), '%Y-%m-%d %H:%M:%S.%f')
            diff = (current_time - loginlocked_time)
            if period_to_unblock_unit == 'day':
                div = 86400
            if period_to_unblock_unit == 'hour':
                div = 3600
            if period_to_unblock_unit == 'minute':
                div = 60
            if period_to_unblock_unit == 'second':
                div = 1
            result = divmod(diff.days * 86400  + diff.seconds, div)

            if result[0] >= period_to_unblock:
                rec.write({'login_locked':'active', 'login_locked_time':None})
                rec.create_mail_message(body='User')
                _logger.info('User **'+ str(rec.name) +'** Login Restored')
        return True

    def unlock_user_login(self):
        res = super(ResUsers, self).unlock_user_login()
        self.create_mail_message(body='User')
        return res

    def _get_default_from(self):
        self.ensure_one()
        if self.env.user.email:
            return formataddr((self.env.user.name, self.env.user.email))
        raise UserError(_("Unable to send email, please configure the sender's email address or alias."))

    def create_mail_message(self, body):
         user_admin = self.env.user
         for user in self:
             if  user.login_locked == 'active' :
                 body += ' '+str(user.name)+': has been Un-locked'
             vals = {
                 'message_type': 'notification',
                 'author_id': user_admin.partner_id.id,
                 'date': datetime.strptime(str(datetime.now())[:19],'%Y-%m-%d %H:%M:%S'),
                 'email_from': self._get_default_from(),
                 'model': 'res.partner',
                 'res_id': user.partner_id.id,
                 'subtype_id': 2,
                 'body': body}
             self.env['mail.message'].create(vals)
