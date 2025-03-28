# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2018 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from datetime import datetime, timedelta
from odoo import api, exceptions, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta

class Budget(models.Model):
	_name = 'capital.budget'
	_description = 'Capital Budget for a fiscal year'
	_order = 'end_date desc'

	@api.model
	def _default_start_date(self):
		fiscal_day = self.env.user.company_id.fiscalyear_last_day
		fiscal_month = self.env.user.company_id.fiscalyear_last_month
		now = datetime.now()
		if now < datetime.strptime(
				"%s-%s-%s" % (now.year, fiscal_month, fiscal_day),
				DEFAULT_SERVER_DATE_FORMAT
		):
			temp = datetime.strptime(
				"%s-%s-%s" % (now.year - 1, fiscal_month, fiscal_day),
				DEFAULT_SERVER_DATE_FORMAT
			)
		else:
			temp = datetime.strptime(
				"%s-%s-%s" % (now.year, fiscal_month, fiscal_day),
				DEFAULT_SERVER_DATE_FORMAT
			)
		return str(temp + timedelta(days=1))

	@api.model
	def _default_end_date(self):
		fiscal_day = self.env.user.company_id.fiscalyear_last_day
		fiscal_month = self.env.user.company_id.fiscalyear_last_month
		now = datetime.now()
		if now < datetime.strptime(
				"%s-%s-%s" % (now.year, fiscal_month, fiscal_day),
				DEFAULT_SERVER_DATE_FORMAT
		):
			temp = datetime.strptime(
				"%s-%s-%s" % (now.year, fiscal_month, fiscal_day),
				DEFAULT_SERVER_DATE_FORMAT
			)
		else:
			temp = datetime.strptime(
				"%s-%s-%s" % (now.year + 1, fiscal_month, fiscal_day),
				DEFAULT_SERVER_DATE_FORMAT
			)
		return str(temp)

	name = fields.Char(string="Budget Name", required=True,
					   help="Required to distinguish the budgets")
	account_id = fields.Many2one(comodel_name='account.account', string="Account",
								 index=True, required=True)
	start_date = fields.Date(string="Start Date",
							 default=_default_start_date, required=True,
							 help="Start date of period")
	end_date = fields.Date(string="End Date",
						   default=_default_end_date, required=True,
						   help="End date of period")
	planned_amount = fields.Float(string="Budget Amount", digits=0,
								  required=True)
	last_year_planned_amount = fields.Float(compute='_compute_planned_amount',string="Previous Year Budget", digits=0,
								  required=True)
	duration_days = fields.Integer(readonly=True,
								   compute='_compute_duration_days')
	practical_amount = fields.Float(compute='_compute_practical_amount', string='Actual Amount', digits=0)

	different_amount = fields.Float(compute='_compute_different_amount', string='Variance', digits=0)


	
	state = fields.Selection(selection=[('1', _("past")),
										('2', _("present")),
										('3', _("future"))],
							 compute='_compute_state',
							 store=True,
						 default='2')

	def _compute_planned_amount(self):
		for budget in self:
			start_date = budget.start_date + relativedelta(years=-1)
			end_date = budget.end_date + relativedelta(years=-1)
			last_year_budget = self.search([('start_date', '=', start_date), ('end_date', '=', end_date), ('account_id', '=', budget.account_id.id)], limit=1)
			start_date = budget.start_date + relativedelta(years=-2)
			end_date = budget.end_date + relativedelta(years=-2)
			last_2_year_budget = self.search([('start_date', '=', start_date), ('end_date', '=', end_date), ('account_id', '=', budget.account_id.id)], limit=1)
			budget.last_year_planned_amount = last_year_budget.planned_amount


	def _compute_different_amount(self):
		for line in self:
			line.different_amount = line.planned_amount - line.last_year_planned_amount

	def _compute_practical_amount(self):
		for line in self:
			aml_obj = self.env['account.move.line']
			domain = [('account_id', '=',
				line.account_id.id),
				('date', '>=', line.start_date),
				('date', '<=', line.end_date)
				]
			where_query = aml_obj._where_calc(domain)
			aml_obj._apply_ir_rules(where_query, 'read')
			from_clause, where_clause, where_clause_params = where_query.get_sql()
			select = 'SELECT SUM(debit) FROM' + from_clause + ' WHERE ' + where_clause
			self.env.cr.execute(select, where_clause_params)
			line.practical_amount = self.env.cr.fetchone()[0] or 0.0
		
	@api.depends('start_date', 'end_date')
	def _compute_duration_days(self):
		for record in self:
			ed = datetime.strptime(str(record.end_date), "%Y-%m-%d")
			sd = datetime.strptime(str(record.start_date), "%Y-%m-%d")
			record.duration_days = (ed - sd).days + 1

	@api.depends('end_date')
	def _compute_state(self):
		for record in self:
			end_date = datetime.strptime(str(record.end_date),
										 DEFAULT_SERVER_DATE_FORMAT)
			fd = self.env.user.company_id.fiscalyear_last_day
			fm = self.env.user.company_id.fiscalyear_last_month
			now = datetime.now()
			e_fiscal_date = datetime.strptime(
				"%s-%s-%s" % (now.year, fm, fd),
				DEFAULT_SERVER_DATE_FORMAT
			)
			if now >= e_fiscal_date:
				e_fiscal_date = datetime.strptime(
					"%s-%s-%s" % (now.year + 1, fm, fd),
					DEFAULT_SERVER_DATE_FORMAT
				) + timedelta(days=1)
			s_fiscal_date = datetime.strptime(
				"%s-%s-%s" % (e_fiscal_date.year-1, fm, fd),
				DEFAULT_SERVER_DATE_FORMAT
			) + timedelta(days=1)
			if end_date < s_fiscal_date:
				record.state = '1'
			elif end_date > e_fiscal_date:
				record.state = '3'
			else:
				record.state = '2'

	def copy(self, default=None):
		default = dict(default or {})
		name = self.name
		cc = self.search_count([('name', '=like', _("Copy of %s") % name)])
		if not cc:
			new_name = _("Copy of %s") % name
		else:
			new_name = _("Copy of %s (%r)") % (name, cc)
		default['name'] = new_name
		(default['start_date'],
		 default['end_date']) = self._get_suggested_dates()

		return super(Budget, self).copy(default)

	@api.constrains('account_id', 'start_date', 'end_date')
	def _check_account_time_period(self):
		err_msg = ""
		for record in self:
			err_msg = self._get_error_message(record)
			if err_msg:
				raise exceptions.ValidationError(err_msg)

	@api.onchange('account_id')
	def _onchange_account_id(self):
		if (
				self.account_id.id
				and self.account_id.id is not self._origin.account_id.id
		):
			(self.start_date,
			 self.end_date) = self._get_suggested_dates()
			self.name = _("%s Budget %s") % (
				self.account_id.code,
				datetime.strptime(
					str(self.end_date),
					DEFAULT_SERVER_DATE_FORMAT
				).year
			)

	@api.onchange('name')
	def _onchange_name(self):
		"""Suggest an account for the budget"""
		if self.name:
			possible_accounts = self.name.split(" ")
			for possible_account in possible_accounts:
				if possible_account.isdigit():
					new_acc = self.env["account.account"].search(
						[('code', '=', possible_account)],
						limit=1)
					if new_acc:
						self.account_id = new_acc
						return

	def _cron_compute_state(self):
		res = self.search([('state', '!=', '1')])
		for record in res:
			record._compute_state()

	def _get_suggested_dates(self):
		temp_date = self.search([('account_id', '=', self.account_id.id)],
								limit=1, order='end_date desc').end_date
		if temp_date:
			latest_date = datetime.strptime(str(temp_date),
											DEFAULT_SERVER_DATE_FORMAT)
			fiscal_day = self.env.user.company_id.fiscalyear_last_day
			fiscal_month = self.env.user.company_id.fiscalyear_last_month
			e_fiscal_date = datetime.strptime(
				"%s-%s-%s" % (latest_date.year, fiscal_month, fiscal_day),
				DEFAULT_SERVER_DATE_FORMAT
			)
			if latest_date >= e_fiscal_date:
				e_fiscal_date = datetime.strptime(
					"%s-%s-%s" % (latest_date.year + 1,
								  fiscal_month,
								  fiscal_day),
					DEFAULT_SERVER_DATE_FORMAT
				)
			if latest_date + timedelta(days=2) > e_fiscal_date:
				latest_date += timedelta(days=2)
				start_date = latest_date
				end_date = datetime.strptime(
					"%s-%s-%s" % (latest_date.year, fiscal_month, fiscal_day),
					DEFAULT_SERVER_DATE_FORMAT
				)
			else:
				latest_date += timedelta(days=1)
				start_date = latest_date
				end_date = datetime.strptime(
					"%s-%s-%s" % (latest_date.year, fiscal_month, fiscal_day),
					DEFAULT_SERVER_DATE_FORMAT
				)
			return str(start_date), str(end_date)
		else:
			return self._default_start_date(), self._default_end_date()

	def _get_error_message(self, record):
		if record:
			date_from = datetime.strptime(str(record.start_date),
										  DEFAULT_SERVER_DATE_FORMAT)
			date_to = datetime.strptime(str(record.end_date),
										DEFAULT_SERVER_DATE_FORMAT)
			fiscal_d = self.env.user.company_id.fiscalyear_last_day
			fiscal_m = self.env.user.company_id.fiscalyear_last_month
			e_fiscal_date = datetime.strptime(
				"%s-%s-%s" % (date_to.year, fiscal_m, fiscal_d),
				DEFAULT_SERVER_DATE_FORMAT
			)
			s_fiscal_date = datetime.strptime(
				"%s-%s-%s" % (date_to.year - 1, fiscal_m, fiscal_d),
				DEFAULT_SERVER_DATE_FORMAT
			)

			periods = self.search([('account_id', '=', record.account_id.id),
								   ('start_date', '<=', record.end_date),
								   ('end_date', '>=', record.start_date),
								   ('id', '!=', record.id)])
			err_msg = []
			if (date_to > e_fiscal_date or
					date_from < s_fiscal_date):
				err_msg.append(_("the year of the dates must be identical"))
			if date_from >= date_to:
				err_msg.append(_("the end date must be subsequent "
								 "to the start date"))
			if len(periods) > 0:
				err_msg.append(_("the time period should be unique and "
								 "shouldn't overlap another budget with the "
								 "same account"))
			separator = _("and")
			if len(err_msg) is not 0:
				return (" \n%s " % separator).join(str(msg) for msg in err_msg)
			return ""
