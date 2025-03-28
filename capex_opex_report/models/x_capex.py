# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)

from odoo.tools import float_round
from dateutil.relativedelta import relativedelta
import datetime


class XCapexWizard(models.TransientModel):
    _name = 'x_capex.wizard'

    month_for = fields.Selection([
        ('07','July'),
        ('08','August'),
        ('09','September'),
        ('10','Octomber'),
        ('11','November'),
        ('12','December'),
        ('01','January'),
        ('02','Febuary'),
        ('03','March'),
        ('04','April'),
        ('05','May'),
        ('06','June'),
        ],string='Month For',required='1')
    year_for = fields.Char('Year For',default=lambda x: str(datetime.date.today().year),required=True)

    def action_create_line(self):
        # if self.month_for == '07':
        #     raise UserError("You cannot generate capex lines automatically for month July. You will need to generate manually.")
        capex_objs = self.env['x_capex'].browse(self._context.get('active_ids' or []))
        capex_data = []
        non_group = []
        for capex_obj in capex_objs:
            capex_lines = self.get_capex_line(capex_obj,int(self.month_for))
            if not capex_lines:
                date_from = datetime.date.today().replace(day=1).replace(month=int(self.month_for)).replace(year=int(self.year_for))
                date_to = (date_from+relativedelta(months=1))-relativedelta(days=1)
                # capex_lines_prev = self.get_capex_line(capex_obj,int(self.month_for)-1)
                capex_group_ids = self.env['x.capex.group'].search([('name','ilike',capex_obj.x_name)])
                if not capex_group_ids:
                    non_group.append(capex_obj.x_name)
                account_ids = capex_group_ids.sudo().account_ids
                if capex_obj.x_type != '1income':
                    account_ids += self.env['account.account'].search([('workinprocess','=',True)])
                for acc in account_ids:
                    capex_data.append({
                        'x_account_id':acc.id,
                        # 'x_budget':line.x_budget.id,
                        'x_from_date': date_from,
                        'x_to_date': date_to,
                        'x_capex': capex_obj.id,
                        })
        if non_group:
            _logger.debug('There is no Capex Group mapping for "%s".'%(', '.join(non_group)))
        if capex_data:
            capex_lines.create(capex_data)


    def get_capex_line(self,capex_obj,month_for):
        if month_for == 7:
            return capex_obj.x_capex_july
        elif month_for == 8:
            return capex_obj.x_capex_august
        elif month_for == 9:
            return capex_obj.x_capex_september
        elif month_for == 10:
            return capex_obj.x_capex_october
        elif month_for == 11:
            return capex_obj.x_capex_november
        elif month_for in (12,0):
            return capex_obj.x_capex_december
        elif month_for == 1:
            return capex_obj.x_capex_january
        elif month_for == 2:
            return capex_obj.x_capex_february
        elif month_for == 3:
            return capex_obj.x_capex_march
        elif month_for == 4:
            return capex_obj.x_capex_april
        elif month_for == 5:
            return capex_obj.x_capex_may
        elif month_for == 6:
            return capex_obj.x_capex_june
        

class XCapexGroup(models.Model):
    _name = 'x.capex.group'

    def get_users_from_group(self,group_id):
        users_ids = []
        sql_query = """select uid from res_groups_users_rel where gid = %s"""                
        params = (group_id,)
        self.env.cr.execute(sql_query, params)
        results = self.env.cr.fetchall()
        for users_id in results:
            users_ids.append(users_id[0])
        return users_ids
        
    def _get_group_budget_ccm_user(self):
        group_id = self.env.ref('mt_isy.group_budget_ccm_user_capex').id
        user_ids = self.get_users_from_group(group_id)
        return [('id','in',user_ids)]

    name = fields.Char('Name',required=True)
    account_ids = fields.Many2many('account.account', string='Accounts')
    sequence = fields.Integer('Sequence',default='1')
    user_ids = fields.Many2many('res.users',string="Allowed Users",domain=_get_group_budget_ccm_user)