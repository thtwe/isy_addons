# -*- coding: utf-8 -*-

{
    'name': "POS Multi Currency",
    'summary': """
        Support multi currency payment in pos
    """,
    'description': """
        Support multi currency payment in pos
    """,
    'author': "Odoosoft",
    'website': "https://odoosoft.com",
    'category': 'Point of sale',
    'version': '1.0',
    'depends': ['point_of_sale'],
    # 'qweb': ['static/src/xml/pos_multi_currency.xml'],
    'data': [
        'views/pos_multi_currency.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_multi_currency/static/src/js/models.js',
            'pos_multi_currency/static/src/js/screen.js',
            'pos_multi_currency/static/src/scss/pos_multi_currency.scss',
        ],
        'web.assets_qweb': [
            'pos_multi_currency/static/src/xml/pos_multi_currency.xml',
        ],
    },
}
