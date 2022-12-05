from odoo import models, fields, api
from itertools import groupby
from odoo.tools import float_compare


class PosConfig(models.Model):
    _inherit = 'pos.config'

    use_combo = fields.Boolean()
    combo_pack_price = fields.Selection(
        [('all_product', 'Total of all combo items'), ('main_product', 'Take Price from the Main product')],
        'Total Combo Price')


class pos_order_line(models.Model):
    _inherit = 'pos.order.line'

    combo_prod_ids = fields.Many2many('product.product', string='Combo Produts')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_pack = fields.Boolean('Pos Product Options')
    pack_ids = fields.One2many('product.pack', 'bi_product_template', 'Product pack')


class ProductPack(models.Model):
    _name = 'product.pack'

    is_required = fields.Boolean('Required')
    category_id = fields.Many2one('pos.category', 'Category', required=True)
    name = fields.Char(related='category_id.name', string='Category Name')
    product_ids = fields.Many2many('product.product', string='Product', required=True, domain="[('pos_categ_id', '=', category_id)]")
    bi_product_template = fields.Many2one('product.template', 'Product pack')
    bi_product_product = fields.Many2one('product.product', related='bi_product_template.product_variant_id',
                                         string='Product pack')

    @api.onchange('category_id')
    def onchange_category_id(self):
        if self.category_id:
            self.product_ids = False


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _create_move_from_pos_order_lines(self, lines):
        self.ensure_one()
        lines_by_product = groupby(sorted(lines, key=lambda l: l.product_id.id), key=lambda l: l.product_id.id)
        for product, lines in lines_by_product:
            order_lines = self.env['pos.order.line'].concat(*lines)
            first_line = order_lines[0]
            current_move = self.env['stock.move'].create(
                self._prepare_stock_move_vals(first_line, order_lines)
            )
            if first_line.combo_prod_ids:
                vals = self._prepare_stock_move_vals(first_line, order_lines)
                for product in first_line.combo_prod_ids:
                    vals.update({'product_uom': product.uom_id.id, 'product_id': product.id})
                    current_move += self.env['stock.move'].create(vals)
            confirmed_moves = current_move._action_confirm()
            for move in confirmed_moves:
                if first_line.product_id == move.product_id and first_line.product_id.tracking != 'none':
                    if self.picking_type_id.use_existing_lots or self.picking_type_id.use_create_lots:
                        for line in order_lines:
                            sum_of_lots = 0
                            for lot in line.pack_lot_ids.filtered(lambda l: l.lot_name):
                                if line.product_id.tracking == 'serial':
                                    qty = 1
                                else:
                                    qty = abs(line.qty)
                                ml_vals = move._prepare_move_line_vals()
                                ml_vals.update({'qty_done': qty})
                                if self.picking_type_id.use_existing_lots:
                                    existing_lot = self.env['stock.production.lot'].search([
                                        ('company_id', '=', self.company_id.id),
                                        ('product_id', '=', line.product_id.id),
                                        ('name', '=', lot.lot_name)
                                    ])
                                    if not existing_lot and self.picking_type_id.use_create_lots:
                                        existing_lot = self.env['stock.production.lot'].create({
                                            'company_id': self.company_id.id,
                                            'product_id': line.product_id.id,
                                            'name': lot.lot_name,
                                        })
                                    quant = existing_lot.quant_ids.filtered(
                                        lambda q: q.quantity > 0.0 and q.location_id.parent_path.startswith(
                                            move.location_id.parent_path))[-1:]
                                    ml_vals.update({
                                        'lot_id': existing_lot.id,
                                        'location_id': quant.location_id.id or move.location_id.id
                                    })
                                else:
                                    ml_vals.update({
                                        'lot_name': lot.lot_name,
                                    })
                                self.env['stock.move.line'].create(ml_vals)
                                sum_of_lots += qty
                            if abs(line.qty) != sum_of_lots:
                                difference_qty = abs(line.qty) - sum_of_lots
                                ml_vals = current_move._prepare_move_line_vals()
                                if line.product_id.tracking == 'serial':
                                    ml_vals.update({'qty_done': 1})
                                    for i in range(int(difference_qty)):
                                        self.env['stock.move.line'].create(ml_vals)
                                else:
                                    ml_vals.update({'qty_done': difference_qty})
                                    self.env['stock.move.line'].create(ml_vals)
                    else:
                        move._action_assign()
                        for move_line in move.move_line_ids:
                            move_line.qty_done = move_line.product_uom_qty
                        if float_compare(move.product_uom_qty, move.quantity_done,
                                         precision_rounding=move.product_uom.rounding) > 0:
                            remaining_qty = move.product_uom_qty - move.quantity_done
                            ml_vals = move._prepare_move_line_vals()
                            ml_vals.update({'qty_done': remaining_qty})
                            self.env['stock.move.line'].create(ml_vals)

                else:
                    move._action_assign()
                    for move_line in move.move_line_ids:
                        move_line.qty_done = move_line.product_uom_qty
                    if float_compare(move.product_uom_qty, move.quantity_done,
                                     precision_rounding=move.product_uom.rounding) > 0:
                        remaining_qty = move.product_uom_qty - move.quantity_done
                        ml_vals = move._prepare_move_line_vals()
                        ml_vals.update({'qty_done': remaining_qty})
                        self.env['stock.move.line'].create(ml_vals)
                    move.quantity_done = move.product_uom_qty
