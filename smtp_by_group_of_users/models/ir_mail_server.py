# -*- coding: utf-8 -*-
#################################################################################
#                                                                               #
#    Part of Odoo. See LICENSE file for full copyright and licensing details.   #
#    Copyright (C) 2018 Jupical Technologies Pvt. Ltd. <http://www.jupical.com> #
#                                                                               #
#################################################################################

from odoo import fields, models

class ir_mail_server(models.Model):

    _inherit = "ir.mail_server"

    user_ids = fields.Many2many('res.users', 'mail_server_users_rel', 'server_id', 'user_id', string="Users")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: