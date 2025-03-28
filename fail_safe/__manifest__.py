# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Budget Limit Warning on PO',
    'category': 'Accounting',
    'version': '1.1',
    'sequence': 20,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'description': """
    By this module you can get warning in Purchase order if Budget is exceed.
    """,
    'depends': ['accounting_budget_extension_V7', 'purchase'],
    'data': [
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
