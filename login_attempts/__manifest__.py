# -*- coding: utf-8 -*-
{
    'name'      : 'SW - Login Attempts Log',
    'summary': "View & keep all login trials for all user accounts.",
    'license':  "Other proprietary",
    'author'    : 'Smart Way Business Solutions',
    'website'   : 'https://www.smartway.co',
    'category'  : 'Extra Tools',
    'version'   : '1.0',
    'depends': ['base', 'mail'],
    'data': [
        'data/update_user_status.xml',
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/login_user_views.xml',
        'views/res_users.xml',
        'views/res_config_view.xml'
        ],
    'images':  ["static/description/image.png"],
    'price' : 50,
    'currency' :  'EUR',
    'installable': True,
    'auto_install': False,
    'application' :False,
}
