# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2018 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

import re
import odoo.addons.accounting_budget_extension.models.static as s
from odoo.tests import common

test_formulas = [
    {
        'formula': "test1 + test2 - test3",
        'keys': ["test1", "test2", "test3"]
    }, {
        'formula': "(test1 + test2) - test3",
        'keys': ["test1", "test2", "test3"]
    }, {
        'formula': "test1 + test2-test3",
        'keys': ["test1", "test2", "test3"]
    }, {
        'formula': "test_1 * test2 / test3",
        'keys': ["test_1", "test2", "test3"]
    }
]


class TestStatic(common.TransactionCase):
    """Implements common test functionality of the extended budget treatment"""

    def test_is_float(self):
        """test is_float method"""
        self.assertTrue(s.is_float("3.6"))
        self.assertTrue(s.is_float(".6"))
        self.assertTrue(s.is_float("NaN"))
        self.assertTrue(s.is_float("36"))
        self.assertTrue(s.is_float("0E0"))
        self.assertTrue(s.is_float("3.2359083257896436"))
        self.assertTrue(s.is_float("infinity"))
        self.assertTrue(s.is_float("-iNF"))
        self.assertTrue(s.is_float("-.6"))
        self.assertFalse(s.is_float("foo bar"))
        self.assertFalse(s.is_float(True))
        self.assertFalse(s.is_float(",6"))
        self.assertFalse(s.is_float("(1)"))

    def test_regex(self):
        """test regex for getting keys out of a formula"""
        reg = s.formula_regex

        for formula in test_formulas:
            keylist = re.findall(reg, formula.get('formula'))
            self.assertEqual(keylist, formula.get('keys'))

    def test_calc_balance(self):
        """test calc_balance method. Won't work if test_regex fails!"""
        budget_codes = {
            'test1': [1, 2, 3],
            'test2': [4, 5, 6],
            'test3': [7, 8, 9]
        }

        self.assertEqual(s.calc_balance(
            test_formulas[0].get('formula'), 1, budget_codes
        ), -2)

        self.assertEqual(s.calc_balance(
            test_formulas[1].get('formula'), 1, budget_codes
        ), -2)

        self.assertEqual(s.calc_balance(
            test_formulas[3].get('formula'), 2, budget_codes
        ), 0)

        self.assertEqual(s.calc_balance(
            test_formulas[2].get('formula'), 2, budget_codes
        ), -1)

