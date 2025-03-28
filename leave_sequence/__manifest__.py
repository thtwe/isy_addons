# -*- coding: utf-8 -*-

{
    'name': 'Leave Request Sequence',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Add sequence to leave requests',
    'description': """
This module add sequences to leave requests.
""",
    'depends': ['hr','hr_holidays'],
    'data': [
        'data/leave_sequence.xml',
	'view/hr_leave.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
