from odoo import fields, models, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _get_fields_for_order_line(self):
        fields = super(PosOrder, self)._get_fields_for_order_line()
        kitchen_fields = ['food_type', 'food_temperature', 'food_serve_as', 'food_doneness', 'kitchen_option']
        fields = fields + kitchen_fields
        return fields

    def unlink(self):
        removed = False
        for record in self:
            line = self.env['kitchen.pos.order.line'].sudo().search([('order_id', '=', record.pos_reference)])
            if line:
                line.unlink()
                if not removed:
                    removed = True
        if removed:
            kitchen_order = self.env['kitchen.pos.order'].search([], limit=1)
            kitchen_order.write({'last_update_made': fields.Datetime.now()})
        return super(PosOrder, self).unlink()
