# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Create Customer Invoice',
    'category': 'Invoicing Management',
    'version': '1.0',
    'sequence': 20,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'description': """
    You can create customer invoice for individual or multiple customer.
    """,
    'depends': ['account'],
    'data': ['wizard/customer_invoice_view.xml'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
