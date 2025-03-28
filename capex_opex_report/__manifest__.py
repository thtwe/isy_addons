# -*- coding: utf-8 -*-
{
    'name': 'Capex Opex Report',
    'summary': """""",
    'version': '1.0',
    'description': """

    """,
    'author': 'ISY Odoo Team',
    'company': 'The International School Yangon',
    'website': 'https://www.isyedu.org',
    'category': 'Tools',
    'depends': ['base','account','mt_isy'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/opex_view.xml',
        'views/opex_report.xml',
        'views/x_opex_view.xml',
        'views/x_capex_view.xml',
        'views/account_move_view.xml',
        'wizard/opex_opening_view.xml',
        'data/data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
