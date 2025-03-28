#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

{
    'name'          : "Mass Invoice: Send By Mail",
    'version'       : '1.1',
    'summary'       : """Mass Invoice: Send By Mail""",
    'author'        : 'Webkul Software Pvt. Ltd.',
    'website'       : 'https://store.webkul.com/Odoo-Mass-Invoice-Send-By-Mail.html',
    "license"       :  "Other proprietary",
    'category'      : 'website',
    "live_test_url" : "http://odoodemo.webkul.com/?module=mass_invoice_mail",
    'description'   : """

This module works very well with latest version of Odoo 12.0
--------------------------------------------------------------
    """,
    'depends'       : [
        'account', 'wk_wizard_messages'
    ],

    'data'          : [
        'data/mass_server_actions.xml',
        'views/mass_invoice_view.xml',
    ],
    "images"        :  ['static/description/Banner.png'],
    "application"   :  True,
    "installable"   :  True,
    "auto_install"  :  False,
    "price"         :  15,
    "currency"      :  "EUR",
    'sequence'      :   1,
}