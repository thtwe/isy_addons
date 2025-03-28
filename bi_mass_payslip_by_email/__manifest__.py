# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mass Payslip Send by Email in odoo payroll',
    'version': '1.0',
    'sequence': 11,
    'summary': 'Apps helps to send mass payslip for employee in one click.',
    'description': """
send mass email in one click, mass payslip send by email, mass employee payslip send by email,multiple payslip send by email, multiple employee payslip send by email, Send email by payslip, Send email by employee payslip.send multiple payslip report by email, multiple payslip report send by email, employee payslip report send in one click, easy email, email to employee payslip, email employee payslip
	Send Multiple Payslip By Email, Mass Payslip Send by Email in  payroll, mass payslip by email , email all payslip , email all payroll payslip, salary payslip by email , all salary slip by email
	print salary slip , all employee salary slip , salary report send by email, salary reciept by email , salary reciept send by email , send payslip in bulk , bulk pay slip by email 
    hr payslip, print payslip , email payslip, company payslips , all employee payslip
    """,
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'price': '10.00',
    'currency': "EUR",
    'depends': ['base','hr_payroll'],
    'data': [
             'views/employee_payslip.xml',
             'views/employee_template.xml',
             'views/employee_multiple_send_payslip.xml'
             ],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],
}
