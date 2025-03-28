# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2018 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
from datetime import datetime, timedelta
from odoo import exceptions
from odoo.tests import common
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class TestExtendedBudget(common.TransactionCase):
    """Implements common test functionality of the extended budget treatment"""

    def setUp(self):
        super(TestExtendedBudget, self).setUp()
        # Create custom account
        acc_type_id = self.env['account.account.type'].search(
            [('name', '=', 'Income')], limit=1
        ).id
        account_account = self.env['account.account']
        self.account = account_account.create({
            'code': '1337',
            'name': 'STNI Account',
            'user_type_id': acc_type_id,
        })

        # Create custom budget
        fiscal_d = self.env.user.company_id.fiscalyear_last_day
        fiscal_m = self.env.user.company_id.fiscalyear_last_month
        budgetextension_budget = self.env['budgetextension.budget']
        self.budget = budgetextension_budget.create({
            'name': 'STNI Test Budget',
            'end_date': datetime.strptime(
                "2001-%s-%s" % (fiscal_m, fiscal_d),
                DEFAULT_SERVER_DATE_FORMAT
            ),
            'start_date': datetime.strptime(
                "2000-%s-%s" % (fiscal_m, fiscal_d),
                DEFAULT_SERVER_DATE_FORMAT
            ) + timedelta(days=1),
            'account_id': self.account.id,
            'planned_amount': '12000',
        })

    def test_compute_state(self):
        """Test _compute_state method"""
        fiscal_d = self.env.user.company_id.fiscalyear_last_day
        fiscal_m = self.env.user.company_id.fiscalyear_last_month

        budgetextension_budget = self.env['budgetextension.budget']
        temp_budget = budgetextension_budget.create({
            'name': 'STNI Test Budget',
            'end_date': datetime.strptime(
                str(self.budget.start_date),
                DEFAULT_SERVER_DATE_FORMAT
            )-timedelta(days=1),
            'start_date': datetime.strptime(
                str(self.budget.start_date),
                DEFAULT_SERVER_DATE_FORMAT
            ) - timedelta(days=2),
            'account_id': self.account.id,
            'planned_amount': '12000',
        })
        temp_budget._compute_state()
        self.assertEqual(temp_budget.state, 1)

        temp_budget = budgetextension_budget.create({
            'name': 'STNI Test Budget',
            'end_date': datetime.strptime(
                "3000-%s-%s" % (fiscal_m, fiscal_d),
                DEFAULT_SERVER_DATE_FORMAT
            ),
            'start_date': datetime.strptime(
                "2999-%s-%s" % (fiscal_m, fiscal_d),
                DEFAULT_SERVER_DATE_FORMAT
            ) + timedelta(days=1),
            'account_id': self.account.id,
            'planned_amount': '12000',
        })
        temp_budget._compute_state()
        self.assertEqual(temp_budget.state, 3)

    def test_compute_duration_days(self):
        """Test _compute_duration_days method"""
        self.assertEqual(self.budget.duration_days, 365)

    def test_copy(self):
        """Test copy method"""
        budget = self.budget
        copy = budget.copy()
        copy2 = budget.copy()

        self.assertEqual(copy.name, "Copy of %s" % budget.name,
                         "copy name should be 'Copy of STNI Test Budget'")
        self.assertEqual(copy2.name, "Copy of %s (1)" % budget.name,
                         "copy name should be 'Copy of STNI Test Budget(1)'")

        self.assertEqual(
            (datetime.strptime(str(copy.end_date), DEFAULT_SERVER_DATE_FORMAT)
             + timedelta(days=1)),
            datetime.strptime(str(copy2.start_date), DEFAULT_SERVER_DATE_FORMAT),
            "start date of copy2 should be the day after the end date of copy2"
        )

    def test_python_constrains(self):
        """Test _check_account_time_period method"""
        fiscal_d = self.env.user.company_id.fiscalyear_last_day
        fiscal_m = self.env.user.company_id.fiscalyear_last_month

        with self.assertRaises(exceptions.ValidationError):
            budgetextension_budget = self.env['budgetextension.budget']
            budgetextension_budget.create({
                'name': 'STNI Test Budget',
                'end_date': datetime.strptime(
                    "2001-%s-%s" % (fiscal_m, fiscal_d),
                    DEFAULT_SERVER_DATE_FORMAT
                ),
                'start_date': datetime.strptime(
                    "2000-%s-%s" % (fiscal_m, fiscal_d),
                    DEFAULT_SERVER_DATE_FORMAT
                ) + timedelta(days=1),
                'account_id': self.account.id,
                'planned_amount': '12000',
            })

        with self.assertRaises(exceptions.ValidationError):
            budgetextension_budget = self.env['budgetextension.budget']
            budgetextension_budget.create({
                'name': 'STNI Test Budget',
                'end_date': datetime.strptime(
                    "2001-%s-%s" % (fiscal_m, fiscal_d),
                    DEFAULT_SERVER_DATE_FORMAT
                ),
                'start_date': datetime.strptime(
                    "2000-%s-%s" % (fiscal_m, fiscal_d),
                    DEFAULT_SERVER_DATE_FORMAT
                ) + timedelta(days=1),
                'account_id': self.account.id,
                'planned_amount': '12000',
            })

        with self.assertRaises(exceptions.ValidationError):
            budgetextension_budget = self.env['budgetextension.budget']
            budgetextension_budget.create({
                'name': 'STNI Test Budget',
                'start_date': datetime.strptime(
                    "2003-%s-%s" % (fiscal_m, fiscal_d),
                    DEFAULT_SERVER_DATE_FORMAT
                ),
                'end_date': datetime.strptime(
                    "2000-%s-%s" % (fiscal_m, fiscal_d),
                    DEFAULT_SERVER_DATE_FORMAT
                ) + timedelta(days=1),
                'account_id': self.account.id,
                'planned_amount': '12000',
            })
