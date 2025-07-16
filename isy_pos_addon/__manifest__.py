# -*- coding: utf-8 -*-

{
    'name': "ISY POS",
    'version': '17.0.1.0.0',
    'summary': """
        POS with ISY Card Payment Method
    """,
    'description': """
        POS with ISY Card Payment Method
    """,
    'author': "ISY",
    'website': "https://www.isyedu.org",
    'category': 'Point of sale',
    'depends': ['point_of_sale'],
    'data': [
        'views/res_partner_veiw.xml',
        'views/pos_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'isy_pos_addon/static/src/js/payment_screen.js'
        ],
    },

    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
