# -*- coding: utf-8 -*-

import math

from odoo import http, _, fields
from odoo.http import request
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.addons.web.controllers.main import Home 


class CustomerPortal(CustomerPortal):
    
    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user
        holidays = request.env['hr.leave']
        holidays_count = holidays.sudo().search_count([
            ('employee_id.user_id', '=', partner.id)
        ])
        values.update({
        'holidays_count': holidays_count,
        })
        return values
    
    @http.route(['/my/leave_request', '/my/leave_request/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_leave_request(self, page=1, sortby=None, **kw):
        if not request.env.user.portal_employee_leave:
        # if not request.env.user.has_group('odoo_leave_request_portal_employee.group_employee_leave'):
            return request.render("odoo_leave_request_portal_employee.not_allowed_leave_request")
        response = super(CustomerPortal, self)
        values = self._prepare_portal_layout_values()
        partner = request.env.user
        holidays_obj = http.request.env['hr.leave']
        domain = [
            ('employee_id.user_id', '=', partner.id),
        ]
        # count for pager
        holidays_count = http.request.env['hr.leave'].sudo().search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/leaves",
            total=holidays_count,
            page=page,
            step=self._items_per_page
        )
        sortings = {
            'date': {'label': _('Newest'), 'order': 'date_from desc'},
        }
        
        order = sortings.get(sortby, sortings['date'])['order']
        
        # content according to pager and archive selected
        holidays = holidays_obj.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'holidays': holidays,
            'page_name': 'holidays',
            'sortings' : sortings,
            'sortby': sortby,
            'pager': pager,
            'default_url': '/my/holidays',
        })
        return request.render("odoo_leave_request_portal_employee.display_leave_request", values)
    

# class CustomLoginRedirect(Home):

#     @http.route('/web/login', type='http', auth='public', website=True, sitemap=False)
#     def web_login(self, redirect=None, **kw):
#         # Call the parent login method
#         response = super().web_login(redirect=redirect, **kw)

#         # Check if login was successful and user exists
#         if request.params.get('login_success') and request.session.uid:
#             user = request.env['res.users'].sudo().browse(request.session.uid)

#             # Redirect portal users (who are now internal-like) to the backend
#             if user.has_group('base.group_portal'):
#                 return http.redirect_with_hash('/web#home')

#         return response  # Otherwise, return the default response