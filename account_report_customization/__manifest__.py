{
    'name': 'Accounting Report Customization',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Customize accounting report formats and styles',
    'description': """
        This module customizes the format and style of accounting reports including:
        - Profit and Loss Report
        - Balance Sheet Report
        - Cash Flow Report
        
        Features:
        - Custom header and footer
        - Enhanced styling
        - Improved readability
    """,
    'author': 'ISY',
    'website': 'https://sas.isyedu.org',
    'depends': ['account_reports'],
    'data': [
        'data/pdf_export_template.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'account_report_customization/static/src/css/account_report.css',
    #     ],
    # },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
} 