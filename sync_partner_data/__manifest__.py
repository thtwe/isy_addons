# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Synchronize Partner Data',
    'category': 'Tools',
    'summary': 'Synchronize Partner Data',
    'version': '1.0',
    'description': """
    """,
    "author": "Odoosoft",
    "website": "https://odoosoft.com/",
    'depends': ['account','contacts'],
    'data': [
        'data/cron_data.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
