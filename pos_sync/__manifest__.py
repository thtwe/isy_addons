# -*- coding: utf-8 -*-

{
    'name': 'POS Sync',
    'version': '1.0',
    'summary': 'Sync POS payment transactions to Odoo',
    'category': 'Extra Tools',
    'author': 'Aye Myat Say Co., Ltd',
    'website': 'http://ayemyatsay.com',
    'images': [
        'static/src/img/icon.png',
    ],
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/cron_data_pos.xml',
        'views/views.xml',
        'views/settings.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
