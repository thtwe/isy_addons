from odoo import fields, models

class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'


    activity_ids = fields.One2many(
        'mail.activity', 'res_id', 'Activities',
        auto_join=True,
        groups="base.group_user,base.group_portal",)
