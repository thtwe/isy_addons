# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Niyas Raphy(<https://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo.addons.web.controllers import main
from odoo.http import request
import odoo
import odoo.modules.registry
from odoo.tools.translate import _
from odoo import http
import ast

class DataSet(main.DataSet):

    @http.route(['/web/dataset/call_kw', '/web/dataset/call_kw/<path:path>'], type='json', auth="user")
    def call_kw(self, model, method, args, kwargs, path=None):
        if request.uid:
            user_rec = request.env['res.users'].sudo().search([('id', '=', request.uid)])
            if user_rec.allowed_ips:
                ip_address = request.httprequest.environ['REMOTE_ADDR']
                ip_list = []
                print("ip_list", ip_list)
                for rec in user_rec.allowed_ips:
                    ip_list.append(rec.ip_address)
                    print("Dataset call_kw------", ip_list)
                if not ip_address in ip_list:
                    main.Session.logout(self)
        return self._call_kw(model, method, args, kwargs)

    @http.route('/web/dataset/load', type='json', auth="user")
    def load(self, model, id, fields):
        if request.uid:
            user_rec = request.env['res.users'].sudo().search([('id', '=', request.uid)])
            if user_rec.allowed_ips:
                ip_address = request.httprequest.environ['REMOTE_ADDR']
                ip_list = []
                print("ip_list", ip_list)
                for rec in user_rec.allowed_ips:
                    ip_list.append(rec.ip_address)
                    print("DataSet load------", ip_list)
                if not ip_address in ip_list:
                    main.Session.logout(self)

        value = {}
        r = request.env[model].browse([id]).read()
        if r:
            value = r[0]
        return {'value': value}


class Action(main.Action):

    @http.route('/web/action/load', type='json', auth="user")
    def load(self, action_id, additional_context=None):
        Actions = request.env['ir.actions.actions']
        value = False
        request.uid = request.session.uid
        if request.uid:
            user_rec = request.env['res.users'].sudo().search([('id', '=', request.uid)])
            if user_rec.allowed_ips:
                ip_address = request.httprequest.environ['REMOTE_ADDR']
                ip_list = []
                print("ip_list", ip_list)
                for rec in user_rec.allowed_ips:
                    ip_list.append(rec.ip_address)
                    print("Action load------", ip_list)
                if not ip_address in ip_list:
                    main.Session.logout(self)

        try:
            action_id = int(action_id)
        except ValueError:
            try:
                action = request.env.ref(action_id)
                assert action._name.startswith('ir.actions.')
                action_id = action.id
            except Exception:
                action_id = 0   # force failed read
        base_action = Actions.browse([action_id]).sudo().read(['type'])
        if base_action:
            ctx = dict(request.context)
            action_type = base_action[0]['type']
            if action_type == 'ir.actions.report':
                ctx.update({'bin_size': True})
            if additional_context:
                ctx.update(additional_context)
            request.context = ctx
            action = request.env[action_type].sudo().browse([action_id]).read()
            if action:
                value = main.clean_action(action[0], env=request.env)
        return value


class Home(main.Home):

    # ideally, this route should be `auth="user"` but that don't work in non-monodb mode.
    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        main.ensure_db()
        if not request.session.uid:
            return request.redirect('/web/login', 303)
        if kw.get('redirect'):
            #return werkzeug.utils.redirect(kw.get('redirect'), 303)
            return request.redirect(kw.get('redirect'), 303)

        request.uid = request.session.uid
        if request.uid:
            user_rec = request.env['res.users'].sudo().search([('id', '=', request.uid)])
            if user_rec.allowed_ips:
                ip_address = request.httprequest.environ['REMOTE_ADDR']
                ip_list = []
                print("ip_list", ip_list)
                for rec in user_rec.allowed_ips:
                    ip_list.append(rec.ip_address)
                    print("web_client checking-----", ip_list)
                if not ip_address in ip_list:
                    # return werkzeug.utils.redirect('/web/login?error=Not allowed to login from this IP')
                    return request.redirect('/web/login?error=Not allowed to login from this IP')
        try:
            context = request.env['ir.http'].webclient_rendering_context()
            response = request.render('web.webclient_bootstrap', qcontext=context)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        except AccessError:
            # return werkzeug.utils.redirect('/web/login?error=access')
            return request.redirect('/web/login?error=access')

    @http.route('/web/login', type='http', auth="public")
    def web_login(self, redirect=None, **kw):
        main.ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()

        # This is from odoo_web_login
        param_obj = request.env['ir.config_parameter'].sudo()
        values['disable_footer'] = True
        values['disable_database_manager'] = True

        # change_background = ast.literal_eval(param_obj.get_param('login_form_change_background_by_hour')) or False

        values['background_src'] = param_obj.get_param('login_form_background_default') or ''
        # End

        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            ip_address = request.httprequest.environ['REMOTE_ADDR']
            if request.params['login']:
                user_rec = request.env['res.users'].sudo().search(
                    [('login', '=', request.params['login'])])
                if user_rec.allowed_ips:
                    ip_list = []
                    for rec in user_rec.allowed_ips:
                        ip_list.append(rec.ip_address)
                    if ip_address in ip_list:
                        try:
                            uid = request.session.authenticate(
                                request.session.db,
                                request.params[
                                    'login'],
                                request.params[
                                    'password'])
                            request.params['login_success'] = True
                            return request.redirect(
                                self._login_redirect(uid, redirect=redirect))
                        except odoo.exceptions.AccessDenied as e:
                            request.uid = old_uid
                            if e.args == odoo.exceptions.AccessDenied().args:
                                values['error'] = _("Wrong login/password")
                    else:
                        request.uid = old_uid
                        values['error'] = _("Not allowed to login from this IP")
                else:
                    try:
                        uid = request.session.authenticate(request.session.db,
                                                           request.params[
                                                               'login'],
                                                           request.params[
                                                               'password'])
                        request.params['login_success'] = True
                        return request.redirect(
                            self._login_redirect(uid, redirect=redirect))
                    except odoo.exceptions.AccessDenied as e:
                        request.uid = old_uid
                        if e.args == odoo.exceptions.AccessDenied().args:
                            values['error'] = _("Wrong login/password")

        return request.render('web.login', values)
