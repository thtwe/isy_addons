# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Synchronize Employee Data',
    'category': 'Tools',
    'summary': 'Synchronize Employee Data',
    'version': '1.0',
    'description': """
    """,
    "author": "Odoosoft",
    "website": "http://www.ayemyatsay.com/",
    'depends': ['hr'],
    'data': [
        'data/cron_data_employee.xml',
        'data/report_paperformat.xml',
	    'views/employee.xml',
        'reports/employee_report_local_bm.xml',
        'reports/employee_report_local_d.xml',
        'reports/employee_report_exp_bm.xml',
        'reports/employee_report_exp_d.xml',
        'reports/resigned_employee_report_exp_bm.xml',
        'reports/resigned_employee_report_exp_d.xml',
        'reports/resigned_employee_report_loc_bm.xml',
        'reports/resigned_employee_report_loc_d.xml',
    ],
    'installable': True,
    'auto_install': False,
    'assets': {
        'web.report_assets_common': [
            'sync_employee_data/static/src/scss/isy_font.scss',
        ],
    },
}
