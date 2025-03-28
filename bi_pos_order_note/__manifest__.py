# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "POS Order Note in odoo",
    "version" : "0.2",
    "category" : "Point of Sale",
    "depends" : ['base','sale','point_of_sale'],
    "author": "BrowseInfo",
    'summary': 'This apps helps to add POS order note on TouchScreen, Receipt and Backend Order',
    "description": """
    
    Purpose :- 
    This Module allow us to add bag charges on particular order.
    POS order Note point of sales order note , point of sales note
	


    Add Note on POS

    POS Note

    POS Order line Note

    POS line Note

    POS Receipt Note

    POS backend NOte

    Add note on POS order

    Point Of Sale Note

    POS order Note

    Add Note on POS

    POS line Note

    Point of Sale Order line Note

    Point of Sale line Note

    Point of Sale Receipt Note

    Point of Sale backend NOte

    Add note on Point of Sale order
    """,
    "price": 10,

    "currency": 'EUR',
    "website" : "www.browseinfo.in",
    "data": [
        'views/bi_pos_order_note.xml',
    ],
    'qweb': [
        'static/src/xml/pos_order_note_template.xml',
    ],
    "auto_install": False,
    "installable": True,
    "images":['static/description/Banner.png'],
    'assets': {
        'point_of_sale.assets': [
            'bi_pos_order_note/static/src/js/pos_order_note.js',
        ],
        'web.assets_qweb': [
            'bi_pos_order_note/static/src/xml/pos_order_note_template.xml',
        ],
    },
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
