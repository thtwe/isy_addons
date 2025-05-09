# Copyright 2015 LasLabs Inc.
# Copyright 2018 Modoolar <info@modoolar.com>.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{

    'name': 'Password Security',
    "summary": "Allow admin to set password security requirements.",
    'version': '1.1.0',
    'author':
        "LasLabs, "
        "Kaushal Prajapati, "
        "Tecnativa, "
        "Odoo Community Association (OCA)",
    'category': 'Base',
    'depends': [
        'auth_signup',
        'auth_password_policy',
        'auth_password_policy_signup',
    ],
    "website": "https://github.com/OCA/server-auth",
    "license": "LGPL-3",
    "data": [
        'views/password_security.xml',
        'views/res_config_settings_views.xml',
        'views/signup_templates.xml',
        'security/ir.model.access.csv',
        'security/res_users_pass_history.xml',
    ],
    "demo": [
        'demo/res_users.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/password_security/static/src/js/signup_policy.js',
        ],
        'web.assets_common': [
            '/password_security/static/src/js/password_gauge.js',
            ]
    },
    'installable': True,
}
