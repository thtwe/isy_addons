# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class ResUsers(models.Model):
    _inherit = "res.users"

    def write(self, vals):      
        result_vals = []      
        old_group_ids = self.groups_id.ids
        for key,val in vals.items():
            if key.startswith('sel_groups'):
                groups_ids = key.replace("sel_groups_","").split("_")
                if groups_ids:
                    check=[]
                    for gid in groups_ids:
                        if int(gid) in old_group_ids:
                            check.append(gid)   
                    if len(check)>1:        
                        obj_group = self.env['res.groups'].search([('id','=',max(groups_ids))])
                        old_groups_role_name = obj_group.full_name
                    elif len(check)==1:
                        obj_group = self.env['res.groups'].search([('id','=',check[0])])
                        old_groups_role_name = obj_group.full_name
                    else:
                        old_groups_role_name = "None"
                if val != False:
                    obj_group = self.env['res.groups'].search([('id','=',val)])
                    new_groups_role_name = obj_group.full_name 
                else:
                    new_groups_role_name = "None"
                result_vals.append("FROM: " + old_groups_role_name + " To: " + new_groups_role_name + "\n")
            elif key.startswith('in_group_'):
                group_id = key.replace("in_group_","")
                if val == True:
                    obj_group = self.env['res.groups'].search([('id','=',group_id)])
                    new_groups_role_name = obj_group.full_name
                    old_groups_role_name = "None"
                else:
                    obj_group = self.env['res.groups'].search([('id','=',group_id)])
                    old_groups_role_name = obj_group.full_name
                    new_groups_role_name = "None"

                result_vals.append("FROM: " + old_groups_role_name + " To: " + new_groups_role_name + "\n")
        
        if result_vals:
            template = self.env.ref('notify_group_change.notify_group_change_template')

            body = "<div>Dear Paul,</div><br/>"
            body += "<div>" + self.partner_id.name + " account access have been changed below:  </div><br/>"
            body +="<ul>"
            for rv in result_vals:
                body += "<li>" + rv + "</li>"
            body += "</ul><br/>"
            body += "<div>Changed By: " + self.env.user.partner_id.name + "</div>"
            template.write({'body_html': body})
            self.env['mail.template'].browse(template.id).sudo().send_mail(self.id)
            print (result_vals)
                
        return super(ResUsers, self).write(vals)
