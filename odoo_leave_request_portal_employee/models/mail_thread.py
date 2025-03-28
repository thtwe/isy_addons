from odoo import models, fields

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    message_attachment_count = fields.Integer('Attachment Count', compute='_compute_message_attachment_count', groups="base.group_user,base.group_portal")
