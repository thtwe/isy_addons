# -*- coding: utf-8 -*-
""" HR Payroll Multi Currency """

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    '''HR Payroll Multi-Currency
    
    Add currency in payslip to allow generate journal entry based on it'''

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  states={'draft': [('readonly', False)]},
                                  readonly=True,
                                  required=True, default=lambda
            self: self.contract_id.currency_id.id or self.env.user.company_id.currency_id.id)

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        '''update currency if contract changed'''
        result = super(HrPayslip, self)._onchange_employee()
        if self.contract_id:
            self.currency_id = self.contract_id.currency_id.id
        return result

    def _action_create_account_move(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')

        # Add payslip without run
        payslips_to_post = self.filtered(lambda slip: not slip.payslip_run_id)

        # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
        payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
        for run in payslip_runs:
            if run._are_payslips_ready():
                payslips_to_post |= run.slip_ids

        # A payslip need to have a done state and not an accounting move.
        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)

        # Check that a journal exists on all the structures
        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError(_('One of the contract for these payslips has no structure type.'))
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))

        # Map all payslips by structure journal and pay slips month.
        # {'journal_id': {'month': [slip_ids]}}
        slip_mapped_data = {slip.struct_id.journal_id.id: {fields.Date().end_of(slip.date_to, 'month'): self.env['hr.payslip']} for slip in payslips_to_post}
        for slip in payslips_to_post:
            slip_mapped_data[slip.struct_id.journal_id.id][fields.Date().end_of(slip.date_to, 'month')] |= slip

        for journal_id in slip_mapped_data: # For each journal_id.
            for slip_date in slip_mapped_data[journal_id]: # For each month.
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0
                date = slip_date
                move_dict = {
                    'narration': '',
                    'ref': date.strftime('%B %Y'),
                    'journal_id': journal_id,
                    'date': date,
                }
                for slip in slip_mapped_data[journal_id][slip_date]:
                    move_dict['narration'] += slip.number or '' + ' - ' + slip.employee_id.name or ''
                    move_dict['narration'] += '\n'
                    for line in slip.line_ids.filtered(lambda line: line.category_id):
                        amount = -line.total if slip.credit_note else line.total
                        if line.code == 'NET': # Check if the line is the 'Net Salary'.
                            for tmp_line in slip.line_ids.filtered(lambda line: line.category_id):
                                if tmp_line.salary_rule_id.not_computed_in_net: # Check if the rule must be computed in the 'Net Salary' or not.
                                    if amount > 0:
                                        amount -= abs(tmp_line.total)
                                    elif amount < 0:
                                        amount += abs(tmp_line.total)
                        from_cur = slip.currency_id
                        base_cur = self.env.user.company_id.currency_id.with_context(
                            date=slip.date or slip.date_to or fields.Date.context_today(self))
                        base_amount = from_cur.compute(amount,base_cur)
                        if float_is_zero(amount, precision_digits=precision):
                            continue
                        debit_account_id = line.salary_rule_id.account_debit.id
                        credit_account_id = line.salary_rule_id.account_credit.id

                        if debit_account_id: # If the rule has a debit account.
                            debit = base_amount if base_amount > 0.0 else 0.0
                            credit = -base_amount if base_amount < 0.0 else 0.0

                            debit_line = self._get_existing_lines(
                                line_ids, line, debit_account_id, debit, credit)

                            if not debit_line:
                                debit_line = self._prepare_line_values(line, debit_account_id, date, debit, credit)
                                debit_line['tax_ids'] = [(4, tax_id) for tax_id in line.salary_rule_id.account_debit.tax_ids.ids]
                                line_ids.append(debit_line)
                            else:
                                debit_line['debit'] += debit
                                debit_line['credit'] += credit
                            debit_line['amount_currency'] = amount if slip.currency_id.id != slip.company_id.currency_id.id else False
                            debit_line['currency_id'] = from_cur.id if slip.currency_id.id != slip.company_id.currency_id.id else False

                        if credit_account_id: # If the rule has a credit account.
                            debit = -base_amount if base_amount < 0.0 else 0.0
                            credit = base_amount if base_amount > 0.0 else 0.0
                            credit_line = self._get_existing_lines(
                                line_ids, line, credit_account_id, debit, credit)

                            if not credit_line:
                                credit_line = self._prepare_line_values(line, credit_account_id, date, debit, credit)
                                credit_line['tax_ids'] = [(4, tax_id) for tax_id in line.salary_rule_id.account_credit.tax_ids.ids]
                                line_ids.append(credit_line)
                            else:
                                credit_line['debit'] += debit
                                credit_line['credit'] += credit
                            credit_line['amount_currency'] = -amount if slip.currency_id.id != slip.company_id.currency_id.id else False 
                            credit_line['currency_id'] = from_cur.id if slip.currency_id.id != slip.company_id.currency_id.id else False

                for line_id in line_ids: # Get the debit and credit sum.
                    debit_sum += line_id['debit']
                    credit_sum += line_id['credit']

                # The code below is called if there is an error in the balance between credit and debit sum.
                if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                    acc_id = slip.journal_id.default_account_id.id
                    if not acc_id:
                        raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (slip.journal_id.name))
                    existing_adjustment_line = (
                        line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                    )
                    adjust_credit = next(existing_adjustment_line, False)

                    debit_credit_sum = base_cur.compute((debit_sum - credit_sum),from_cur)
                    if not adjust_credit:
                        adjust_credit = {
                            'name': _('Adjustment Entry'),
                            'partner_id': False,
                            'account_id': acc_id,
                            'journal_id': slip.journal_id.id,
                            'date': date,
                            'debit': 0.0,
                            'credit': debit_sum - credit_sum,
                            'currency_id': from_cur.id if slip.currency_id.id != slip.company_id.currency_id.id else False,
                            'amount_currency': debit_credit_sum if slip.currency_id.id != slip.company_id.currency_id.id else False,
                        }
                        line_ids.append(adjust_credit)
                    else:
                        adjust_credit['credit'] = debit_sum - credit_sum
                        adjust_credit['amount_currency'] = debit_credit_sum

                elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                    acc_id = slip.journal_id.default_account_id.id
                    if not acc_id:
                        raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (slip.journal_id.name))
                    existing_adjustment_line = (
                        line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                    )
                    adjust_debit = next(existing_adjustment_line, False)

                    credit_debit_sum = base_cur.compute((credit_sum - debit_sum),from_cur)
                    if not adjust_debit:
                        adjust_debit = {
                            'name': _('Adjustment Entry'),
                            'partner_id': False,
                            'account_id': acc_id,
                            'journal_id': slip.journal_id.id,
                            'date': date,
                            'debit': credit_sum - debit_sum,
                            'credit': 0.0,
                            'currency_id': from_cur.id if slip.currency_id.id != slip.company_id.currency_id.id else False,
                            'amount_currency':credit_debit_sum if slip.currency_id.id != slip.company_id.currency_id.id else False,
                        }
                        line_ids.append(adjust_debit)
                    else:
                        adjust_debit['debit'] = credit_sum - debit_sum
                        adjust_debit['amount_currency'] = credit_debit_sum if slip.currency_id.id != slip.company_id.currency_id.id else False,

                # Add accounting lines in the move
                move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                move = self.env['account.move'].create(move_dict)
                for slip in slip_mapped_data[journal_id][slip_date]:
                    slip.write({'move_id': move.id, 'date': date})
        return True

    """
    def action_payslip_done(self):
        '''override main function to allow to generate journal entry
        based on payslip currency_id'''
        precision = self.env['decimal.precision'].precision_get('Payroll')
        for slip in self:
            slip.compute_sheet()
            slip.write({'state': 'done'})
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = slip.date or slip.date_to
            name = _('Payslip of %s') % (slip.employee_id.name)
            move_dict = {
                'narration': name,
                'ref': slip.number,
                'journal_id': slip.journal_id.id,
                'date': date,
            }
            for line in slip.line_ids:
                amount = slip.credit_note and -line.total or line.total
                # get company base amount
                from_cur = slip.currency_id
                currency = line.env.user.company_id.currency_id.with_context(
                    date=slip.date or slip.date_to or fields.Date.context_today(
                        self))
                base_amount = from_cur.compute(amount,
                                               currency)

                if float_is_zero(base_amount, precision_digits=precision):
                    continue
                debit_account_id = line.salary_rule_id.account_debit.id
                credit_account_id = line.salary_rule_id.account_credit.id
                if debit_account_id:
                    debit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': line._get_partner_id(
                            credit_account=False),
                        'account_id': debit_account_id,
                        'journal_id': slip.journal_id.id,
                        'date': date,
                        'debit': base_amount > 0.0 and base_amount or 0.0,
                        'credit': base_amount < 0.0 and -base_amount or 0.0,
                        'amount_currency': amount if slip.currency_id.id != slip.company_id.currency_id.id else False,
                        'currency_id': from_cur.id if slip.currency_id.id != slip.company_id.currency_id.id else False,
                        'analytic_account_id': line.salary_rule_id.analytic_account_id.id,
                        'tax_line_id': line.salary_rule_id.account_tax_id.id,
                    })
                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2][
                        'credit']
                if credit_account_id:
                    credit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': line._get_partner_id(credit_account=True),
                        'account_id': credit_account_id,
                        'journal_id': slip.journal_id.id,
                        'date': date,
                        'debit': base_amount < 0.0 and -base_amount or 0.0,
                        'credit': base_amount > 0.0 and base_amount or 0.0,
                        'amount_currency': -amount if slip.currency_id.id != slip.company_id.currency_id.id else False,
                        'currency_id': from_cur.id if slip.currency_id.id != slip.company_id.currency_id.id else False,
                        'analytic_account_id': line.salary_rule_id.analytic_account_id.id,
                        'tax_line_id': line.salary_rule_id.account_tax_id.id,
                    })
                    line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2][
                        'debit']
            if float_compare(credit_sum, debit_sum,
                             precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_account_id.id
                if not acc_id:
                    raise UserError(_(
                        'The Expense Journal "%s" has not properly configured the Credit Account!') % (
                                        slip.journal_id.name))

                # get company debit_sum - credit_sum
                debit_credit_sum = currency.compute((debit_sum - credit_sum),
                                                    from_cur)
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': 0.0,
                    'credit': debit_sum - credit_sum,
                    'currency_id': from_cur.id if slip.currency_id.id != slip.company_id.currency_id.id else False,
                    'amount_currency': -debit_credit_sum  if slip.currency_id.id != slip.company_id.currency_id.id else False,
                })
                line_ids.append(adjust_credit)
            elif float_compare(debit_sum, credit_sum,
                               precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_account_id.id
                if not acc_id:
                    raise UserError(_(
                        'The Expense Journal "%s" has not properly configured the Debit Account!') % (
                                        slip.journal_id.name))

                # get company credit_sum - debit_sum
                credit_debit_sum = currency.compute(
                    (credit_sum - debit_sum),
                    from_cur)
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': credit_sum - debit_sum,
                    'currency_id': from_cur.id if slip.currency_id.id != slip.company_id.currency_id.id else False,
                    'amount_currency': credit_debit_sum  if slip.currency_id.id != slip.company_id.currency_id.id else False,
                    'credit': 0.0,
                })
                line_ids.append(adjust_debit)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            slip.write({'move_id': move.id, 'date': date})
            move.post()
    """
