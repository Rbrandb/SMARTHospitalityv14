from odoo import fields, models, api, _


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    food_type = fields.Selection([('kitchen', 'Kitchen'), ('bar', 'Bar')], string='Type', required=False)
    food_temperature = fields.Selection([('hot', 'Hot'), ('cold', 'Cold')], string='Temperature', required=False)
    food_serve_as = fields.Many2one('product.serve.as', string='Serve As', required=False)
    food_doneness = fields.Many2one('product.food.doneness', string='Doneness', required=False)
    kitchen_option = fields.Boolean(related='product_id.kitchen_option')
    is_kitchen_line_removed = fields.Boolean(string="Is Kitchen Line removed")

    @api.model
    def create(self, vals):
        if vals.get('food_serve_as'):
            vals['food_serve_as'] = self.env['product.serve.as'].search([('name', '=', vals.get('food_serve_as'))]).id
        if vals.get('food_doneness'):
            vals['food_doneness'] = self.env['product.food.doneness'].search([('name', '=', vals.get('food_doneness'))]).id
        pos_order_line = super(PosOrderLine, self).create(vals)
        product = pos_order_line.product_id
        if product.kitchen_option:
            pos_order_line.write({
                'food_type': product.food_type,
                'food_temperature': product.food_temperature,
                'kitchen_option': product.kitchen_option,
            })
        return pos_order_line
