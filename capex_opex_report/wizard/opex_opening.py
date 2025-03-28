# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
from odoo.tools import float_round
import math

class ISYOpexOpening(models.TransientModel):
    _name = 'isy.opex.opening'

    f_date = fields.Many2one('account.fiscal.year','Template',required=True)

    def generate_opex(self):
        for rec in self:
            account_ids = self.env['account.account'].sudo().search([('user_type_id','in',(13,14,16))])
            datas = self.env['budgetextension.budget'].sudo().search_read([('start_date', '>=', str(rec.f_date.date_from))
                , ('end_date', '<=', str(rec.f_date.date_to))]
                ,['account_id','planned_amount_100','x_studio_group','x_studio_type','name'])
            
            year_start = str(rec.f_date.date_from)[0:4]
            year_end = str(rec.f_date.date_to)[0:4]
            opex_result = {}
            for account_id in account_ids:
                budget_data = list(filter(lambda x: x.get('account_id') and x.get('account_id')[0]==account_id.id and 'inactive' not in x.get('name').lower(), datas))
                sequence = 1
                if budget_data:
                    budget_data = budget_data[0]
                    budget_id = budget_data['id']
                    # name = budget_data['x_studio_group'][1]
                    o_group = self.env['isy.opex.group'].search([('account_ids','in',account_id.id)],limit=1)
                    name = o_group.name or 'BUDGET-'+budget_data['x_studio_group'][1]
                    sequence = o_group.sequence or 1
                    o_type = 'income' if 'income' in (budget_data['x_studio_type'][1]).lower() else 'expense'
                    budget_amount = budget_data['planned_amount_100']
                    if o_type=='expense':
                        budget_amount *= -1
                else:
                    if 'income' in account_id.account_type.name.lower():
                        budget_id = False
                        name = self.env['isy.opex.group'].search([('account_ids','in',account_id.id)],limit=1).name or 'Inactive-Income'
                        o_type = 'income'
                        budget_amount = 0
                    else:
                        budget_id = False
                        name = self.env['isy.opex.group'].search([('account_ids','in',account_id.id)],limit=1).name or 'Inactive-Expense'
                        o_type = 'expense'
                        budget_amount = 0
                opex_result.update({name:{
                    'name': name,
                    'sequence' : sequence,
                    'f_date': rec.f_date.id,
                    'date_to_forreport': rec.f_date.date_to,
                    'o_type': self.env['isy.opex.type'].search([('type','=',o_type)]).id,
                    'lines_july': [(0,0,{
                        'account_id':account_id.id,
                        'budget_id':budget_id,
                        'date_start':year_start+'-07-01',
                        'date_end':year_start+'-07-31',
                        # 'budget_amount': int(budget_amount/12.0*100)/100,
                        'budget_amount': budget_amount/12.0,
                        })]+((opex_result.get(name) or {}).get('lines_july') or []),
                    'lines_aug': [(0,0,{
                        'account_id':account_id.id,
                        'budget_id':budget_id,
                        'date_start':year_start+'-08-01',
                        'date_end':year_start+'-08-31',
                        # 'budget_amount': int(budget_amount/12.0*100)/100,
                        'budget_amount': budget_amount/12.0,
                        })]+((opex_result.get(name) or {}).get('lines_aug') or []),
                    'lines_sep': [(0,0,{
                        'account_id':account_id.id,
                        'budget_id':budget_id,
                        'date_start':year_start+'-09-01',
                        'date_end':year_start+'-09-30',
                        # 'budget_amount': int(budget_amount/12.0*100)/100,
                        'budget_amount': budget_amount/12.0,
                        })]+((opex_result.get(name) or {}).get('lines_sep') or []),
                    'lines_oct': [(0,0,{
                        'account_id':account_id.id,
                        'budget_id':budget_id,
                        'date_start':year_start+'-10-01',
                        'date_end':year_start+'-10-31',
                        # 'budget_amount': int(budget_amount/12.0*100)/100,
                        'budget_amount': budget_amount/12.0,
                        })]+((opex_result.get(name) or {}).get('lines_oct') or []),
                    'lines_nov': [(0,0,{
                        'account_id':account_id.id,
                        'budget_id':budget_id,
                        'date_start':year_start+'-11-01',
                        'date_end':year_start+'-11-30',
                        # 'budget_amount': int(budget_amount/12.0*100)/100,
                        'budget_amount': budget_amount/12.0,
                        })]+((opex_result.get(name) or {}).get('lines_nov') or []),
                    'lines_dec': [(0,0,{
                        'account_id':account_id.id,
                        'budget_id':budget_id,
                        'date_start':year_start+'-12-01',
                        'date_end':year_start+'-12-31',
                        # 'budget_amount': int(budget_amount/12.0*100)/100,
                        'budget_amount': budget_amount/12.0,
                        })]+((opex_result.get(name) or {}).get('lines_dec') or []),
                    'lines_jan': [(0,0,{
                        'account_id':account_id.id,
                        'budget_id':budget_id,
                        'date_start':year_end+'-01-01',
                        'date_end':year_end+'-01-31',
                        # 'budget_amount': int(budget_amount/12.0*100)/100,
                        'budget_amount': budget_amount/12.0,
                        })]+((opex_result.get(name) or {}).get('lines_jan') or []),
                    'lines_feb': [(0,0,{
                        'account_id':account_id.id,
                        'budget_id':budget_id,
                        'date_start':year_end+'-02-01',
                        'date_end':year_end+'-02-28',
                        # 'budget_amount': int(budget_amount/12.0*100)/100,
                        'budget_amount': budget_amount/12.0,
                        })]+((opex_result.get(name) or {}).get('lines_feb') or []),
                    'lines_mar': [(0,0,{
                        'account_id':account_id.id,
                        'budget_id':budget_id,
                        'date_start':year_end+'-03-01',
                        'date_end':year_end+'-03-31',
                        # 'budget_amount': int(budget_amount/12.0*100)/100,
                        'budget_amount': budget_amount/12.0,
                        })]+((opex_result.get(name) or {}).get('lines_mar') or []),
                    'lines_apr': [(0,0,{
                        'account_id':account_id.id,
                        'budget_id':budget_id,
                        'date_start':year_end+'-04-01',
                        'date_end':year_end+'-04-30',
                        # 'budget_amount': int(budget_amount/12.0*100)/100,
                        'budget_amount': budget_amount/12.0,
                        })]+((opex_result.get(name) or {}).get('lines_apr') or []),
                    'lines_may': [(0,0,{
                        'account_id':account_id.id,
                        'budget_id':budget_id,
                        'date_start':year_end+'-05-01',
                        'date_end':year_end+'-05-31',
                        # 'budget_amount': int(budget_amount/12.0*100)/100,
                        'budget_amount': budget_amount/12.0,
                        })]+((opex_result.get(name) or {}).get('lines_may') or []),
                    'lines_jun': [(0,0,{
                        'account_id':account_id.id,
                        'budget_id':budget_id,
                        'date_start':year_end+'-06-01',
                        'date_end':year_end+'-06-30',
                        # 'budget_amount': int(budget_amount/12.0*100)/100,
                        'budget_amount': budget_amount/12.0,
                        })]+((opex_result.get(name) or {}).get('lines_jun') or []),
                }})
            opex_result = list(opex_result.values())
            self.env['isy.opex'].create(opex_result)