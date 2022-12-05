# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ProductServeAs(models.Model):
    _name = 'product.serve.as'
    _description = 'Product Serve As'

    name = fields.Char(string='Name', required=True)

    _sql_constraints = [
        ('serve_as_uniq', 'unique(name)', _('Same Serve as Already Exists!!'))
    ]

class ProductDoneness(models.Model):
    _name = 'product.food.doneness'
    _description = 'Product Doneness'

    name = fields.Char(string='Name', required=True)

    _sql_constraints = [
        ('doneness_uniq', 'unique(name)', _('Same doneness Already Exists!!'))
    ]

class Product(models.Model):
    _inherit = 'product.template'

    food_type = fields.Selection([('kitchen', 'Kitchen'), ('bar', 'Bar')], string='Type', required=False)
    food_temperature = fields.Selection([('hot', 'Hot'), ('cold', 'Cold')], string='Temperature', required=False)
    food_serve_as = fields.Many2one('product.serve.as', string='Serve As', required=False)
    food_doneness = fields.Many2one('product.food.doneness', string='Doneness', required=False)
    kitchen_option = fields.Boolean(string='Hospitality Product', default=False)
