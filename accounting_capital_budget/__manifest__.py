# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2018 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
{
    'name': "Capital Budget",
    'summary': """Create budgets easily. Compare budgets in a financial report.""",
    'description': """
        Budget Extension module for extending reports:
            - Add new, extended budgets to an account for a fiscal year and show their information in a financial report.
            - Compare the budgets grouped by account and sorted by the end date.
            - Let the system calculate the recommended period length for the budget.
    """,
    'author': "Aye Myat Say",
    'website': 'http://www.ayemyatsay.com/',
    'category': 'Advanced Reporting',
    'version': '1.0.0',
    'license': 'OPL-1',
    'images': [
        'static/description/main_screenshot.png'
    ],
    'depends': [
        'account_reports',
    ],
    'data': [
        'views/budget.xml',
        'security/ir.model.access.csv',
        'data/budget.xml',
    ],
}
