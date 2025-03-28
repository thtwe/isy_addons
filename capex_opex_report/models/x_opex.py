# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)

from odoo.tools import float_round
from dateutil.relativedelta import relativedelta
import datetime


class XOpexWizard(models.TransientModel):
    _name = 'x_opex.wizard'

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
        ],string='Month For',required=True)

    def action_create_line(self):
        if self.month_for == '07':
            raise UserError("You cannot generate opex lines automatically for month July. You will need to generate manually.")
        opex_objs = self.env['x_opex'].browse(self._context.get('active_ids' or []))
        opex_data = []
        for opex_obj in opex_objs:
            opex_lines = self.get_opex_line(opex_obj,int(self.month_for))
            if not opex_lines:
                opex_lines_prev = self.get_opex_line(opex_obj,int(self.month_for)-1)
                for line in opex_lines_prev:
                    opex_data.append({
                        'x_account_id':line.x_account_id.id,
                        'x_budget':line.x_budget.id,
                        'x_from_date': (line.x_to_date+relativedelta(months=1)).replace(day=1),
                        'x_to_date': ((line.x_to_date+relativedelta(months=2)).replace(day=1))-relativedelta(days=1),
                        'x_opex': opex_obj.id,
                        })
        if opex_data:
            opex_lines.create(opex_data)


    def get_opex_line(self,opex_obj,month_for):
        if month_for == 7:
            return opex_obj.x_opex_july
        elif month_for == 8:
            return opex_obj.x_opex_august
        elif month_for == 9:
            return opex_obj.x_opex_september
        elif month_for == 10:
            return opex_obj.x_opex_october
        elif month_for == 11:
            return opex_obj.x_opex_november
        elif month_for in (12,0):
            return opex_obj.x_opex_december
        elif month_for == 1:
            return opex_obj.x_opex_january
        elif month_for == 2:
            return opex_obj.x_opex_february
        elif month_for == 3:
            return opex_obj.x_opex_march
        elif month_for == 4:
            return opex_obj.x_opex_april
        elif month_for == 5:
            return opex_obj.x_opex_may
        elif month_for == 6:
            return opex_obj.x_opex_june
        

        