# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class KitchenPosLine(models.Model):
    _name = "kitchen.pos.order.line"
    _description = "Kitchen POS Order Line"

    kitchen_pos_order = fields.Many2one('kitchen.pos.order', string='Kitchen Order')
    product_id = fields.Many2one('product.product', string='Product', readonly=True, required=True)
    product_quantity = fields.Float(string='Product Quantity', readonly=True, required=True)
    product_state = fields.Selection([('in progress', 'In Progress'), ('to go', 'To Go'), ('ready', 'Ready')],
                                     readonly=True, required=True, default='in progress')
    food_type = fields.Selection([('kitchen', 'Kitchen'), ('bar', 'Bar')], string='Type', readonly=True, required=False)
    food_temperature = fields.Selection([('hot', 'Hot'), ('cold', 'Cold')], string='Temperature', readonly=True,
                                        required=False)
    food_serve_as = fields.Many2one('product.serve.as', string='Serve As', readonly=True, required=False)
    food_doneness = fields.Many2one('product.food.doneness', string='Doneness', readonly=True, required=False)
    table_info = fields.Char(string='Table Info')
    order_id = fields.Char(string='POS Order')
    cid = fields.Char(string='POS Line Id(CID)')
    combo_product_details = fields.Html(string='Combo Details', sanitize=False)
    unique_line_ref = fields.Char("UniqueLineRef")
