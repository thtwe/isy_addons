# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import logging
import base64
import json
import requests
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'hr.employee'

    dcid = fields.Integer(string='DCID')
    x_staff_address = fields.Char(string='Staff Address')
    x_hire_date = fields.Char(string='Joining Date')
    x_gender = fields.Char(string='Gender')
    x_enthnicity = fields.Char(string='Ethnicity')
    x_department = fields.Char(string='Department')
    x_job = fields.Char(string='Job Title')
    x_nrc_passport = fields.Char(string='NRC Or Passport')
    x_last_date = fields.Char(string='Last Date')
    @api.model
    def sync_employee_data(self):
        try:
            myurl = 'https://powerschool.isyedu.org/oauth/access_token/'
            ps_code = '07d8b31f-5904-4932-80cb-08b4e495920d'
            ps_secret = 'e6f48f28-b04f-490f-9412-5b20f19f0684'
            mydata = ps_code + ":" + ps_secret
            data_bytes = mydata.encode("utf-8")
            mysecret = base64.b64encode(data_bytes)
            postFields = {'grant_type':'client_credentials'}
            credentials = ('07d8b31f-5904-4932-80cb-08b4e495920d', 'e6f48f28-b04f-490f-9412-5b20f19f0684')
            headers = { "Authorization" : "Basic " + mysecret.decode("utf-8") }
            params = { "grant_type": "client_credentials"}
            response =  requests.post(myurl, headers = headers, data = params)
            data = response.json()
            access_token = data['access_token']
            hed = {'Authorization': 'Bearer ' + access_token,'Content-Type': 'application/json'}
            myresponse = requests.post("https://powerschool.isyedu.org/ws/schema/query/api.school.pull_odoo_staff?pagesize=0", headers=hed)
            mydata = myresponse.json()
            mydata = mydata and mydata['record'] or []
            _logger.debug(mydata)
            _logger.debug('OHNMAR')
            dcid_list = []
            for value in mydata:
                dcid_list.append(int(value.get('dcid')))
                employee = self.env['hr.employee'].with_context(active_test=False).search([('dcid', '=', int(value.get('dcid')))], limit=1)
                if employee and employee.dcid == int(value.get('dcid')):
                    employee.sudo().write({
                        'dcid': value.get('dcid'),
                        'name': '%s %s' % (value.get('first_name'), value.get('last_name')),
                        'x_staff_address': value.get('staff_address'),
                        'x_hire_date': value.get('hire_date'),
                        'x_gender': value.get('gender'),
                        'x_enthnicity': value.get('ethnicity'),
                        'x_department': value.get('department'),
                        'x_job': value.get('job_title'),
                        'x_nrc_passport': value.get('passport_nrc'),
                        'x_last_date': value.get('last_date'),
                        'work_email': value.get('email_address'),
                        'barcode': value.get('staff_id'),
                        'active': True,
                    })
                    if employee.sudo().user_id and not employee.sudo().user_id.active:
                        employee.sudo().user_id.write({'active':True})
                else:
                    employee = self.sudo().create({
                        'name': '%s %s' % (value.get('first_name'), value.get('last_name')),
                        'dcid': value.get('dcid'),
                        'x_staff_address': value.get('staff_address'),
                        'x_hire_date': value.get('hire_date'),
                        'x_gender': value.get('gender'),
                        'x_enthnicity': value.get('ethnicity'),
                        'x_department': value.get('department'),
                        'x_job': value.get('job_title'),
                        'x_nrc_passport': value.get('passport_nrc'),
                        'x_last_date': value.get('last_date'),
                        'work_email': value.get('email_address'),
                        'barcode': value.get('staff_id'),

                    })
                
                # update is_a_employee=True
                if employee.sudo().address_home_id and not employee.sudo().address_home_id.x_studio_is_a_employee_1:
                    employee.sudo().address_home_id.write({'x_studio_is_a_employee_1':True})
            inactive_emp = self.env['hr.employee'].search([('dcid','not in',dcid_list)])
            inactive_emp.mapped('user_id').write({'active':False})
            # inactive_emp.mapped('address_home_id').write({'active':False})
            inactive_emp.write({'active':False})

        except requests.HTTPError as e:
            _logger.debug("Data request failed with code: %r, msg: %r, content: %r",
                          e.response.status_code, e.response.reason, e.response.content)
            raise

        return True

    def sync_employee_request(self):
        # API_ENDPOINT = 'http://192.168.10.200/Single_Staff_Pull.php'
        for employee in self:
            if employee.dcid:
                try:
                    myurl = 'https://powerschool.isyedu.org/oauth/access_token/'
                    ps_code = '07d8b31f-5904-4932-80cb-08b4e495920d'
                    ps_secret = 'e6f48f28-b04f-490f-9412-5b20f19f0684'
                    mydata = ps_code + ":" + ps_secret
                    data_bytes = mydata.encode("utf-8")
                    mysecret = base64.b64encode(data_bytes)
                    postFields = {'grant_type':'client_credentials'}
                    credentials = ('07d8b31f-5904-4932-80cb-08b4e495920d', 'e6f48f28-b04f-490f-9412-5b20f19f0684')
                    headers = { "Authorization" : "Basic " + mysecret.decode("utf-8") }
                    params = { "grant_type": "client_credentials"}
                    response =  requests.post(myurl, headers = headers, data = params)  
                    data = response.json()
                    access_token = data['access_token']
                    hed = {'Authorization': 'Bearer ' + access_token,'Content-Type': 'application/json'}
                    myparams = {"dcid": employee.dcid }
                    # myresponse = requests.post("https://powerschool.isyedu.org/ws/schema/query/api.school.pull_odoo_student?pagesize=0", headers=hed)
                    myresponse = requests.post("https://powerschool.isyedu.org/ws/schema/query/api.school.pull_single_odoo_staff",
                        data = json.dumps(myparams), headers=hed)
                    mydata = myresponse.json()
                    if mydata and mydata['record']:
                        values = mydata['record'][0]
                        employee.sudo().write({
                            'dcid': values.get('dcid'),
                            'name': '%s %s' % (values.get('first_name'), values.get('last_name')),
                            'x_staff_address': values.get('staff_address'),
                            'x_hire_date': values.get('hire_date'),
                            'x_gender': values.get('gender'),
                            'x_enthnicity': values.get('ethnicity'),
                            'x_department': values.get('department'),
                            'x_job': values.get('job_title'),
                            'x_nrc_passport': values.get('passport_nrc'),
                            'x_last_date': values.get('last_date'),
                            'work_email': values.get('email_address'),
                            'barcode': values.get('staff_id')
                        })
                        # update is_a_employee=True
                        if employee.sudo().address_home_id and not employee.sudo().address_home_id.x_studio_is_a_employee_1:
                            employee.sudo().address_home_id.write({'x_studio_is_a_employee_1':True})

                except requests.HTTPError as e:
                    _logger.debug("Data request failed with code: %r, msg: %r, content: %r",
                                  e.response.status_code, e.response.reason, e.response.content)
                    raise

        return True

