# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _


class KitchenBeep(models.Model):
    _name = 'kitchen.beep'
    _description = 'Kitchen Beep'

    name = fields.Char(string='Kitchen Beep', default='Kitchen Beep')
    user_id = fields.Many2one('res.users', string='Users', required=True)
    number_of_lines = fields.Integer(string='Number of lines')
    last_update_made = fields.Datetime()

    @api.model
    def check_beep(self, user_id):
        kitchen_beep = self.env['kitchen.beep'].sudo().search([('user_id', '=', int(user_id))], limit=1)
        if not kitchen_beep:
            kitchen_beep = self.env['kitchen.beep'].sudo().create({'user_id': int(user_id), 'number_of_lines': 0})
        kitchen_order = self.env['kitchen.pos.order'].search([], limit=1)
        if kitchen_beep.last_update_made != kitchen_order.last_update_made:
            kitchen_beep.write({'last_update_made': kitchen_order.last_update_made})
            return True
        else:
            return False
