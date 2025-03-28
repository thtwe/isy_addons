# -*- coding: utf-8 -*-
{
    'name': "HR Payroll Variance Report",

    'summary': """
        Custom HR Payslip Line calculations for previous month salary and variance""",

    'description': """
       This module adds custom fields to hr.payslip.line for tracking the last month\'s salary and variance.
    """,

    'author': "ISY Team",
    'website': "https://isyedu.org",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_payslip_line_views.xml',
    ],
    'license': 'GPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
