# -*- coding: utf-8 -*-
#################################################################################
#                                                                               #
#    Part of Odoo. See LICENSE file for full copyright and licensing details.   #
#    Copyright (C) 2018 Jupical Technologies Pvt. Ltd. <http://www.jupical.com> #
#                                                                               #
#################################################################################

{
    "name": """SMTP BY GROUP OF USERS""",
    "summary": """configure different outgoing mail server for group of users""",
    "version": "1.1",
    "category": "Mail",
    "images": ["static/description/poster_image.png"],
    "application": False,
    "author": "Jupical Technologies Pvt. Ltd.",
    "website": "http://www.jupical.com",
    "license": "LGPL-3",
    "depends": [
        "mail"
    ],
    "data": [
        "views/ir_mail_server_view.xml",
    ],
    "auto_install": False,
    "installable": True,
    'images': ['static/description/poster_image.png'],
    'price': 15.00,
    'currency': 'USD',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: