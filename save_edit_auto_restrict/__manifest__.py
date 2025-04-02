{
    'name': 'Save Edit Auto Restrict',
    'version': '17.0.1.0.0',
    'category': 'Web',
    'summary': 'Restrict auto-save and customize save/discard buttons',
    'description': """
        This module:
        - Restricts auto-save functionality
        - Customizes save and discard button appearance
    """,
    'author': 'ISY',
    'company': 'ISY',
    'website': "https://www.isyedu.org",
    'depends': ['web', 'base'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'save_edit_auto_restrict/static/src/css/button.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
} 