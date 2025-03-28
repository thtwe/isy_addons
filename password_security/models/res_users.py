# Copyright 2016 LasLabs Inc.
# Copyright 2017 Kaushal Prajapati <kbprajapati@live.com>.
# Copyright 2018 Modoolar <info@modoolar.com>.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import re
import logging

from datetime import datetime, timedelta

from odoo import api, fields, models, _

from ..exceptions import PassError

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def delta_now(**kwargs):
    dt = datetime.now() + timedelta(**kwargs)
    return fields.Datetime.to_string(dt)


class ResUsers(models.Model):
    _inherit = 'res.users'

    password_write_date = fields.Datetime(
        'Last password update',
        default=fields.Datetime.now,
        readonly=True,
    )
    password_history_ids = fields.One2many(
        string='Password History',
        comodel_name='res.users.pass.history',
        inverse_name='user_id',
        readonly=True,
    )

    @api.model
    def create(self, vals):
        vals['password_write_date'] = fields.Datetime.now()
        return super(ResUsers, self).create(vals)

    def write(self, vals):
        if vals.get('password'):
            self._check_password(vals['password'])
            vals['password_write_date'] = fields.Datetime.now()
        return super(ResUsers, self).write(vals)

    @api.model
    def get_password_policy(self):
        data = super(ResUsers, self).get_password_policy()
        company_id = self.env.user.company_id
        data.update(
            {
                "password_lower": company_id.password_lower,
                "password_upper": company_id.password_upper,
                "password_numeric": company_id.password_numeric,
                "password_special": company_id.password_special,
                "password_length": company_id.password_length,
            }
        )
        return data

    def _check_password_policy(self, passwords):
        result = super(ResUsers, self)._check_password_policy(passwords)

        for password in passwords:
            if not password:
                continue
            self._check_password(password)

        return result

    def password_match_message(self):
        self.ensure_one()
        company_id = self.company_id
        message = []
        if company_id.password_lower or company_id.password_upper or company_id.password_numeric or company_id.password_special:
            message.append('Password doesn\'t meet the requirements!')
        
        if message:
            raise UserError('\r'.join(message))
        return True
        #return '\r'.join(message)

    def _check_password(self, password):
        self._check_password_rules(password)
        self._check_password_history(password)
        return True

    def _check_password_rules(self, password):
        self.ensure_one()
        if not password:
            return True
        company_id = self.company_id
        password_regex = [
            '^',
            '(?=.*?[a-z]){' + str(company_id.password_lower) + ',}',
            '(?=.*?[A-Z]){' + str(company_id.password_upper) + ',}',
            '(?=.*?\\d){' + str(company_id.password_numeric) + ',}',
            r'(?=.*?[\W_]){' + str(company_id.password_special) + ',}',
            '.{%d,}$' % int(company_id.password_length),
        ]
        if not re.search(''.join(password_regex), password):
            raise PassError(self.password_match_message())
        return True

    def _password_has_expired(self):
        self.ensure_one()
        if not self.password_write_date:
            return True

        if not self.company_id.password_expiration:
            return False

        days = (fields.Datetime.now() - self.password_write_date).days
        return days > self.company_id.password_expiration

    def action_expire_password(self):
        expiration = delta_now(days=+1)
        for rec_id in self:
            rec_id.mapped('partner_id').signup_prepare(
                signup_type="reset", expiration=expiration
            )

    def _validate_pass_reset(self):
        """ It provides validations before initiating a pass reset email
        :raises: PassError on invalidated pass reset attempt
        :return: True on allowed reset
        """
        for rec_id in self:
            pass_min = rec_id.company_id.password_minimum
            if pass_min <= 0:
                pass
            write_date = rec_id.password_write_date
            delta = timedelta(hours=pass_min)
            if write_date + delta > datetime.now():
                raise PassError(
                    _('Passwords can only be reset every %d hour(s). '
                      'Please contact an administrator for assistance.') %
                    pass_min,
                )
        return True

    def _check_password_history(self, password):
        """ It validates proposed password against existing history
        :raises: PassError on reused password
        """
        crypt = self._crypt_context()
        for user in self:
            password_history = user.company_id.password_history
            recent_passes = user.password_history_ids
            # If 0 - disable check
            if password_history == 0:
                _logger.info(
                    "Password History for %s is disabled",
                    user.company_id.name
                )
                continue
            # If negative - check all of previous passwords
            elif password_history < 0:
                _logger.info(
                    "Password History for %s is infinite",
                    user.company_id.name
                )
                recent_passes = user.password_history_ids
            # Otherwise - check count of previous passwords
            else:
                _logger.info(
                    "Password History for %s is %d",
                    user.company_id.name, password_history
                )
                recent_passes = user.password_history_ids[
                    0: password_history - 1
                ]
            if recent_passes.filtered(
                    lambda r: crypt.verify(password, r.password_crypt)):
            
                if recent_passes < 0:
                    error_msg = _('Cannot use passwords that were previously used.')
                else:
                    error_msg = _('Cannot use the most recent %d passwords') % recent_passes
                raise PassError(error_msg)


    def _set_encrypted_password(self, uid, pw):
        """ It saves password crypt history for history rules """
        super(ResUsers, self)._set_encrypted_password(uid, pw)

        self.write({"password_history_ids": [(0, 0, {"password_crypt": pw})]})
