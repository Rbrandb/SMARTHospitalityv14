# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api, _


class KitchenPosOrder(models.Model):
    _name = 'kitchen.pos.order'
    _description = 'Kitchen POS Order'
    _rec_name = 'name'
    _order = "create_date desc"

    name = fields.Char(string='Name', required=True)
    lines = fields.One2many('kitchen.pos.order.line', 'kitchen_pos_order', string='Lines', readonly=True)
    kitchen = fields.Html(string='Kitchen', compute='compute_kitchen', sanitize=False, readonly=True)
    notify_count = fields.Integer(string='Notify Count', readonly=True)
    last_update_made = fields.Datetime()

    def product_class_attr(self, line):
        product_class_attr = \
            ' class="kitchen-td-product d-flex" draggable="true" ondragstart="drag(event)"'\
            f'kitchen-line-id="{line.id}" order_name="{line.order_id}" id="{line.id}"'
        return product_class_attr

    def product_info(self, line):
        if line.food_doneness:
            product_info = \
                '<div class="rest-content">' \
                '<div class="text-left">' \
                f'{line.product_id.name} {int(line.product_quantity)}x' \
                '<button class="btn btn-secondary border border-primary remove-from-kitchen ml-3" type="button"><i class="fa fa-close"></i></button>' \
                f'<div><small><i><b>({line.food_doneness.name})</b></i></small></div><div class="font-weight-bold" style="font-size: 12px;">' \
                f'{line.combo_product_details}' \
                '</div>' \
                '</div>'
        else:
            product_info = \
                '<div class="rest-content">' \
                '<div class="text-left">' \
                f'{line.product_id.name} {int(line.product_quantity)}x' \
                '<button class="btn btn-secondary border border-primary remove-from-kitchen ml-3" type="button"><i class="fa fa-close"></i></button>' \
                f'{line.combo_product_details}' \
                '</div>' \
                '</div>'
        return product_info

    def product_table_info(self, line):
        product_table_info = \
            '<div>' \
            f'{line.table_info if line.table_info else ""}' \
            '</div>'
        return product_table_info

    def kitchen_products(self):
        category_wise_kitchen_hot_products = ''
        category_wise_kitchen_cold_products = ''
        hot_categories = ''
        cold_categories = ''
        lines = self.lines
        kb_type = self._context.get('type')

        if kb_type == 1:
            # Creating HOT dynamic category wise products
            hot_lines = self.lines.filtered(lambda ln : ln.food_type == 'kitchen' and ln.food_temperature == 'hot' and ln.product_state == 'in progress')
            hot_categories = hot_lines.mapped('food_serve_as').mapped('name')
            hot_line_dict = {}
            for ht_categ in hot_categories:
                hot_line_dict[ht_categ] = hot_lines.filtered(lambda ht : ht.food_serve_as.name == ht_categ)
            hot_order_ids = list(set(hot_lines.mapped('order_id')))
            hot_category_wise_order = {}
            for category,lines in hot_line_dict.items():
                hot_table_wise_order = {}
                for order in hot_order_ids:
                    hot_table_wise_order[order] = lines.filtered(lambda ln : ln.order_id == order)
                hot_category_wise_order[category] = hot_table_wise_order

            for category,hot_table_wise_order in hot_category_wise_order.items():
                kitchen_hot_products = ''
                for hot_table,hot_order_lines in hot_table_wise_order.items():
                    if hot_order_lines:
                        product_info = ''
                        for line in hot_order_lines:
                            product_info += \
                                f'<td{self.product_class_attr(line=line)}>{self.product_info(line=line)}</td>'
                        kitchen_hot_products += \
                            '<tr>' \
                            f'<td class="in_progress_items" ondragover="allowDrop(event)" ondrop="drop(event)"><span>{self.product_table_info(line=hot_order_lines[0])}</span><table class="table table-responsive table-bordered table-hover w-100 d-block d-md-table no-footer"><tbody><tr>{product_info}</tr></tbody></table></td>' \
                            '</tr>'
                category_wise_kitchen_hot_products += \
                f'<td><table><tbody><tr><td>{kitchen_hot_products}</td></tr></tbody></table></td>'

            # Creating COLD dynamic category wise products
            cold_lines = self.lines.filtered(lambda ln : ln.food_type == 'kitchen' and ln.food_temperature == 'cold' and ln.product_state == 'in progress')
            cold_categories = cold_lines.mapped('food_serve_as').mapped('name')
            cold_line_dict = {}
            for cld_categ in cold_categories:
                cold_line_dict[cld_categ] = cold_lines.filtered(lambda cld : cld.food_serve_as.name == cld_categ)
            cold_order_ids = list(set(cold_lines.mapped('order_id')))
            cold_category_wise_order = {}
            for category,lines in cold_line_dict.items():
                cold_table_wise_order = {}
                for order in cold_order_ids:
                    cold_table_wise_order[order] = lines.filtered(lambda ln : ln.order_id == order)
                cold_category_wise_order[category] = cold_table_wise_order

            for category,cold_table_wise_order in cold_category_wise_order.items():
                kitchen_cold_products = ''
                for cold_table,cold_order_lines in cold_table_wise_order.items():
                    if cold_order_lines:
                        product_info = ''
                        for line in cold_order_lines:
                            product_info += \
                                f'<td{self.product_class_attr(line=line)}>{self.product_info(line=line)}</td>'
                        kitchen_cold_products += \
                            '<tr>' \
                            f'<td class="in_progress_items" ondragover="allowDrop(event)" ondrop="drop(event)"><span>{self.product_table_info(line=cold_order_lines[0])}</span><table class="table table-responsive table-bordered table-hover w-100 d-block d-md-table no-footer"><tbody><tr>{product_info}</tr></tbody></table></td>' \
                            '</tr>'
                category_wise_kitchen_cold_products += \
                f'<td><table><tbody><tr><td>{kitchen_cold_products}</td></tr></tbody></table></td>'

            return {
                'category_wise_kitchen_hot_products' : category_wise_kitchen_hot_products,
                'category_wise_kitchen_cold_products' : category_wise_kitchen_cold_products,
                'hot_categories' : hot_categories,
                'cold_categories' : cold_categories,
            }
   
        if kb_type == 2:
            # Creating HOT dynamic category wise products
            hot_lines = self.lines.filtered(lambda ln : ln.food_type == 'kitchen' and ln.food_temperature == 'hot' and ln.product_state == 'in progress')
            hot_categories = hot_lines.mapped('food_serve_as').mapped('name')
            hot_line_dict = {}
            for ht_categ in hot_categories:
                hot_line_dict[ht_categ] = hot_lines.filtered(lambda ht : ht.food_serve_as.name == ht_categ)
            hot_order_ids = list(set(hot_lines.mapped('order_id')))
            hot_category_wise_order = {}
            for category,lines in hot_line_dict.items():
                hot_table_wise_order = {}
                for order in hot_order_ids:
                    hot_table_wise_order[order] = lines.filtered(lambda ln : ln.order_id == order)
                hot_category_wise_order[category] = hot_table_wise_order

            for category,hot_table_wise_order in hot_category_wise_order.items():
                kitchen_hot_products = ''
                for hot_table,hot_order_lines in hot_table_wise_order.items():
                    if hot_order_lines:
                        product_info = ''
                        for line in hot_order_lines:
                            product_info += \
                                f'<td{self.product_class_attr(line=line)}>{self.product_info(line=line)}</td>'
                        kitchen_hot_products += \
                            '<tr>' \
                            f'<td class="in_progress_items" ondragover="allowDrop(event)" ondrop="drop(event)"><span>{self.product_table_info(line=hot_order_lines[0])}</span><table class="table table-responsive table-bordered table-hover w-100 d-block d-md-table no-footer"><tbody><tr>{product_info}</tr></tbody></table></td>' \
                            '</tr>'
                category_wise_kitchen_hot_products += \
                f'<td><table><tbody><tr><td>{kitchen_hot_products}</td></tr></tbody></table></td>'

            return {
                'category_wise_kitchen_hot_products' : category_wise_kitchen_hot_products,
                'category_wise_kitchen_cold_products' : category_wise_kitchen_cold_products,
                'hot_categories' : hot_categories,
                'cold_categories' : cold_categories,
            }

        if kb_type == 3:
            # Creating COLD dynamic category wise products
            cold_lines = self.lines.filtered(lambda ln : ln.food_type == 'kitchen' and ln.food_temperature == 'cold' and ln.product_state == 'in progress')
            cold_categories = cold_lines.mapped('food_serve_as').mapped('name')
            cold_line_dict = {}
            for cld_categ in cold_categories:
                cold_line_dict[cld_categ] = cold_lines.filtered(lambda cld : cld.food_serve_as.name == cld_categ)
            cold_order_ids = list(set(cold_lines.mapped('order_id')))
            cold_category_wise_order = {}
            for category,lines in cold_line_dict.items():
                cold_table_wise_order = {}
                for order in cold_order_ids:
                    cold_table_wise_order[order] = lines.filtered(lambda ln : ln.order_id == order)
                cold_category_wise_order[category] = cold_table_wise_order

            for category,cold_table_wise_order in cold_category_wise_order.items():
                kitchen_cold_products = ''
                for cold_table,cold_order_lines in cold_table_wise_order.items():
                    if cold_order_lines:
                        product_info = ''
                        for line in cold_order_lines:
                            product_info += \
                                f'<td{self.product_class_attr(line=line)}>{self.product_info(line=line)}</td>'
                        kitchen_cold_products += \
                            '<tr>' \
                            f'<td class="in_progress_items" ondragover="allowDrop(event)" ondrop="drop(event)"><span>{self.product_table_info(line=cold_order_lines[0])}</span><table class="table table-responsive table-bordered table-hover w-100 d-block d-md-table no-footer"><tbody><tr>{product_info}</tr></tbody></table></td>' \
                            '</tr>'
                category_wise_kitchen_cold_products += \
                f'<td><table><tbody><tr><td>{kitchen_cold_products}</td></tr></tbody></table></td>'

            return {
                'category_wise_kitchen_hot_products' : category_wise_kitchen_hot_products,
                'category_wise_kitchen_cold_products' : category_wise_kitchen_cold_products,
                'hot_categories' : hot_categories,
                'cold_categories' : cold_categories,
            }

    def bar_products(self):
        category_wise_bar_hot_products = ''
        category_wise_bar_cold_products = ''
        hot_categories = ''
        cold_categories = ''
        lines = self.lines

        # Creating HOT dynamic category wise products for BAR
        hot_lines = self.lines.filtered(lambda ln : ln.food_type == 'bar' and ln.food_temperature == 'hot' and ln.product_state == 'in progress')
        hot_categories = hot_lines.mapped('food_serve_as').mapped('name')
        hot_line_dict = {}
        for ht_categ in hot_categories:
            hot_line_dict[ht_categ] = hot_lines.filtered(lambda ht : ht.food_serve_as.name == ht_categ)
        hot_order_ids = list(set(hot_lines.mapped('order_id')))
        hot_category_wise_order = {}
        for category,lines in hot_line_dict.items():
            hot_table_wise_order = {}
            for order in hot_order_ids:
                hot_table_wise_order[order] = lines.filtered(lambda ln : ln.order_id == order)
            hot_category_wise_order[category] = hot_table_wise_order

        for category,hot_table_wise_order in hot_category_wise_order.items():
            bar_hot_products = ''
            for hot_table,hot_order_lines in hot_table_wise_order.items():
                if hot_order_lines:
                    product_info = ''
                    for line in hot_order_lines:
                        product_info += \
                            f'<td{self.product_class_attr(line=line)}>{self.product_info(line=line)}</td>'
                    bar_hot_products += \
                        '<tr>' \
                        f'<td class="in_progress_items" ondragover="allowDrop(event)" ondrop="drop(event)"><span>{self.product_table_info(line=hot_order_lines[0])}</span><table class="table table-responsive table-bordered table-hover w-100 d-block d-md-table no-footer"><tbody><tr>{product_info}</tr></tbody></table></td>' \
                        '</tr>'
            category_wise_bar_hot_products += \
            f'<td><table><tbody><tr><td>{bar_hot_products}</td></tr></tbody></table></td>'

        # Creating COLD dynamic category wise products
        cold_lines = self.lines.filtered(lambda ln : ln.food_type == 'bar' and ln.food_temperature == 'cold' and ln.product_state == 'in progress')
        cold_categories = cold_lines.mapped('food_serve_as').mapped('name')
        cold_line_dict = {}
        for cld_categ in cold_categories:
            cold_line_dict[cld_categ] = cold_lines.filtered(lambda cld : cld.food_serve_as.name == cld_categ)
        cold_order_ids = list(set(cold_lines.mapped('order_id')))
        cold_category_wise_order = {}
        for category,lines in cold_line_dict.items():
            cold_table_wise_order = {}
            for order in cold_order_ids:
                cold_table_wise_order[order] = lines.filtered(lambda ln : ln.order_id == order)
            cold_category_wise_order[category] = cold_table_wise_order

        for category,cold_table_wise_order in cold_category_wise_order.items():
            bar_cold_products = ''
            for cold_table,cold_order_lines in cold_table_wise_order.items():
                if cold_order_lines:
                    product_info = ''
                    for line in cold_order_lines:
                        product_info += \
                            f'<td{self.product_class_attr(line=line)}>{self.product_info(line=line)}</td>'
                    bar_cold_products += \
                        '<tr>' \
                        f'<td class="in_progress_items" ondragover="allowDrop(event)" ondrop="drop(event)"><span>{self.product_table_info(line=cold_order_lines[0])}</span><table class="table table-responsive table-bordered table-hover w-100 d-block d-md-table no-footer"><tbody><tr>{product_info}</tr></tbody></table></td>' \
                        '</tr>'
            category_wise_bar_cold_products += \
            f'<td><table><tbody><tr><td>{bar_cold_products}</td></tr></tbody></table></td>'

        return {
            'category_wise_bar_hot_products' : category_wise_bar_hot_products,
            'category_wise_bar_cold_products' : category_wise_bar_cold_products,
            'hot_categories' : hot_categories,
            'cold_categories' : cold_categories,
        }

    def kitchen_screen(self):
        result = self.kitchen_products()
        kitchen_hot_products = result.get('category_wise_kitchen_hot_products')
        kitchen_cold_products = result.get('category_wise_kitchen_cold_products')
        hot_category , cold_category = '', ''
        for categ_name in result.get('hot_categories'):
            hot_category += \
                f'<th class="hot-kitchen-bg">{categ_name}</th>'
        for categ_name in result.get('cold_categories'):
            cold_category += \
                f'<th class="cold-kitchen-bg">{categ_name}</th>'
        if not hot_category and not cold_category:
            hot_category = \
                f'<th class="hot-kitchen-bg">There are no products available</th>'
        if not kitchen_hot_products and not kitchen_cold_products:
            kitchen_hot_products = \
                f'<td class="in_progress_items" ondragover="allowDrop(event)" ondrop="drop(event)"> <div style="height: 30px; overflow:hidden;"></div></td>'
        kitchen_screen = \
            '<div class="kitchen-screen">' \
            '<table class="table table-responsive table-bordered table-hover kitchen-table w-100 d-block d-md-table">' \
            '<thead>' \
            '<tr>' \
            f'{hot_category}' \
            f'{cold_category}' \
            '</tr>' \
            '</thead>' \
            '<tbody>' \
            '<tr>' \
            f'{kitchen_hot_products}' \
            f'{kitchen_cold_products}' \
            '</tr>' \
            '</tbody>' \
            '</table>' \
            '</div>'
        return kitchen_screen

    def bar_screen(self):
        result = self.bar_products()
        category_wise_bar_hot_products = result.get('category_wise_bar_hot_products')
        category_wise_bar_cold_products = result.get('category_wise_bar_cold_products')
        hot_category , cold_category = '', ''
        for categ_name in result.get('hot_categories'):
            hot_category += \
                f'<th class="hot-kitchen-bg">{categ_name}</th>'
        for categ_name in result.get('cold_categories'):
            cold_category += \
                f'<th class="cold-kitchen-bg">{categ_name}</th>'
        if not hot_category and not cold_category:
            hot_category = \
                f'<th class="hot-kitchen-bg">There are no products available</th>'
        if not category_wise_bar_hot_products and not category_wise_bar_cold_products:
            category_wise_bar_hot_products = \
                f'<td class="in_progress_items" ondragover="allowDrop(event)" ondrop="drop(event)"> <div style="height: 30px; overflow:hidden;"></div></td>'
        bar_screen = \
            '<div class="kitchen-screen">' \
            '<table class="table table-responsive table-bordered table-hover kitchen-table w-100 d-block d-md-table">' \
            '<thead>' \
            '<tr>' \
            f'{hot_category}' \
            f'{cold_category}' \
            '</tr>' \
            '</thead>' \
            '<tbody>' \
            '<tr>' \
            f'{category_wise_bar_hot_products}' \
            f'{category_wise_bar_cold_products}' \
            '</tr>' \
            '</tbody>' \
            '</table>' \
            '</div>'
        return bar_screen

    def ready_products(self):
        lines = self.lines
        kb_type = self._context.get('type')
        if kb_type == 1:
            lines = lines.filtered(lambda l: l.product_state == 'ready' and l.food_type == 'kitchen')
        if kb_type == 2:
            lines = lines.filtered(
                lambda l: l.product_state == 'ready' and l.food_type == 'kitchen' and l.food_temperature == 'hot')
        if kb_type == 3:
            lines = lines.filtered(
                lambda l: l.product_state == 'ready' and l.food_type == 'kitchen' and l.food_temperature == 'cold')
        if kb_type == 4:
            lines = lines.filtered(lambda l: l.product_state == 'ready' and l.food_type == 'bar')
        if kb_type == 5:
            lines = lines.filtered(lambda l: l.product_state == 'ready' and l.food_type in ('kitchen','bar'))
        ready_products = ''
        for line in lines:
            ready_products += \
                f'<div draggable="true" ondragstart="drag(event)" id="{line.id}" class="kitchen-item remove-from-kitchen {"hot-kitchen-cl" if line.food_temperature == "hot" else "cold-kitchen-cl"}" kitchen-line-id="{line.id}" order_name="{line.order_id}">' \
                '<div class="special-text">' \
                f'{line.table_info if line.table_info else ""}' \
                '</div>' \
                '<div class="rest-content">' \
                '<div class="text-right">' \
                '<button disable="disable" class="btn btn-secondary border border-primary" type="button"><i class="fa fa-close"></i></button>' \
                '</div>' \
                '<div>' \
                f'<span>{line.product_id.name} {line.combo_product_details}</span>' \
                f'</div>' \
                f'<div>' \
                f'<span>{int(line.product_quantity)}x</span>' \
                '</div>' \
                '</div>' \
                '</div>'
        ready_products = \
            '<div class="row mt32">' \
            '<div ondragover="allowDrop(event)" ondrop="drop(event)" class="ready-products col-lg-12 d-flex" style="overflow-x: auto; white-space: nowrap;">' \
            '<div class="kitchen-item kitchen-ready-item">' \
            '<div>' \
            '<span>' \
            + _('Ready') + \
            '</span>' \
            '</div>' \
            '</div>' \
            f'{ready_products}' \
            '</div>' \
            '</div>'
        return ready_products

    def togo_products(self):
        lines = self.lines
        kb_type = self._context.get('type')
        if kb_type == 1:
            lines = lines.filtered(lambda l: l.product_state == 'to go' and l.food_type == 'kitchen')
        if kb_type == 2:
            lines = lines.filtered(
                lambda l: l.product_state == 'to go' and l.food_type == 'kitchen' and l.food_temperature == 'hot')
        if kb_type == 3:
            lines = lines.filtered(
                lambda l: l.product_state == 'to go' and l.food_type == 'kitchen' and l.food_temperature == 'cold')
        if kb_type == 4:
            lines = lines.filtered(lambda l: l.product_state == 'to go' and l.food_type == 'bar')
        togo_products = ''
        for line in lines:
            togo_products += \
                f'<div class="kitchen-item remove-from-kitchen {"hot-kitchen-cl" if line.food_temperature == "hot" else "cold-kitchen-cl"}" kitchen-line-id="{line.id}" order_name="{line.order_id}">' \
                '<div class="special-text">' \
                f'{line.table_info if line.table_info else ""}' \
                '</div>' \
                '<div class="rest-content">' \
                '<div class="text-right">' \
                '<button class="btn btn-secondary border border-primary remove-from-kitchen" type="button"><i class="fa fa-close"></i></button>' \
                '</div>' \
                '<div>' \
                f'<span>{line.product_id.name}</span>' \
                f'</div>' \
                f'<div>' \
                f'{line.combo_product_details}' \
                f'</div>' \
                f'<div>' \
                f'<span>{int(line.product_quantity)}x</span>' \
                '</div>' \
                '</div>' \
                '</div>'
        togo_products = \
            '<div class="row mt32">' \
            '<div class="col-lg-12 d-flex" style="overflow-x: auto; white-space: nowrap;">' \
            '<div class="kitchen-item kitchen-togo-item">' \
            '<div>' \
            '<span>' \
            + _('To Go') + \
            '</span>' \
            '</div>' \
            '</div>' \
            f'{togo_products}' \
            '</div>' \
            '</div>'
        return togo_products

    def compute_kitchen(self):
        kb_type = self._context.get('type')
        for record in self:
            record.kitchen = f'<audio id="myAudio" muted="true" autoplay>' \
                             f'<source src="/kitchen_pos/static/src/js/notification.mp3" type="audio/mpeg">' \
                             f'</audio>' \
                             f'<div class="row">' \
                             '<div class="col-lg-12 col-12">' \
                             f'{record.kitchen_screen() if kb_type in [1, 2, 3] else ""}' \
                             f'{record.bar_screen() if kb_type == 4 else ""}' \
                             '</div>' \
                             '</div>' \
                             f'{record.ready_products()}' \
                             f'<input type="hidden" value="{kb_type}" name="kb_type" class="kb_type"/>'

    @api.model
    def product_to_ready(self, line):
        line = self.env['kitchen.pos.order.line'].search([('id', '=', int(line))])
        line.write({'product_state': 'ready'})
        user_ids = self.env['res.users'].search([])
        notification_ids = []
        for user in user_ids:
            if user.has_group('kitchen_pos.group_kitchen_notify'):
                notification_ids.append((0, 0, {
                    'res_partner_id': user.partner_id.id,
                    'notification_type': 'inbox',
                }))

                self.env['mail.message'].create([{
                    'message_type': 'notification',
                    'subject': '%s' % line.table_info,
                    'body': '%s Product %s has been ready to serv' % (line.table_info, line.product_id.name),
                    'author_id': self.env.user.partner_id.id,
                    'model': self._name,
                    'res_id': line.kitchen_pos_order.id,
                    'notification_ids': notification_ids,
                }])
        return line
    
    @api.model
    def product_to_inprogress(self, line):
        line = self.env['kitchen.pos.order.line'].search([('id', '=', int(line))])
        line.write({'product_state': 'in progress'})
        user_ids = self.env['res.users'].search([])
        notification_ids = []
        for user in user_ids:
            if user.has_group('kitchen_pos.group_kitchen_notify'):
                notification_ids.append((0, 0, {
                    'res_partner_id': user.partner_id.id,
                    'notification_type': 'inbox',
                }))

                self.env['mail.message'].create([{
                    'message_type': 'notification',
                    'subject': '%s' % line.table_info,
                    'body': '%s Product %s returned in in Progress mode' % (line.table_info, line.product_id.name),
                    'author_id': self.env.user.partner_id.id,
                    'model': self._name,
                    'res_id': line.kitchen_pos_order.id,
                    'notification_ids': notification_ids,
                }])
        return line

    @api.model
    def remove_from_kitchen(self, line):
        line = self.env['kitchen.pos.order.line'].search([('id', '=', int(line))])
        # pos_order = self.env["pos.order"].sudo().search([('pos_reference', '=', line.order_id)])
        # order_line = pos_order.lines.filtered(lambda ln : ln.product_id.id == line.product_id.id and ln.qty == line.product_quantity and ln.order_id.pos_reference == line.order_id)
        # if order_line:
        #     order_line[0].is_kitchen_line_removed = True
        line.unlink()

    @api.model
    def remove_order(self, line):
        line = self.env['kitchen.pos.order.line'].search([('id', '=', int(line))], limit=1)
        reference = line.order_id
        self.env['kitchen.pos.order.line'].search([('order_id', '=', reference)]).sudo().unlink()
        self.env['pos.order'].search([('pos_reference', '=', reference)], limit=1).sudo().unlink()

    @api.model
    def update_kitchen_order(self, lines):
        if lines:
            for line in lines:
                kitchen_pos_lines = self.env['kitchen.pos.order.line'].search([('order_id', '=', line.get('order_id'))])
                if kitchen_pos_lines:
                    kitchen_pos_lines.sudo().unlink()
        kitchen_order = self.env['kitchen.pos.order'].search([], limit=1)
        for line in lines:
            line.update({'kitchen_pos_order': kitchen_order.id})
            if line.get('food_serve_as'):
                line['food_serve_as'] = self.env['product.serve.as'].search([('name', '=', line.get('food_serve_as'))]).id
            else:
                line['food_serve_as'] = ''
            if line.get('food_doneness'):
                line['food_doneness'] = self.env['product.food.doneness'].search([('name', '=', line.get('food_doneness'))]).id
            else:
                line['food_doneness'] = ''
            self.env['kitchen.pos.order.line'].create(line)
        kitchen_order.write({'last_update_made': fields.Datetime.now()})

    @api.model
    def check_new_products(self):
        kitchen_order = self.env['kitchen.pos.order'].search([], limit=1)
        if kitchen_order.notify_count != len(kitchen_order.lines):
            kitchen_order.notify_count = len(kitchen_order.lines)
            return True
        else:
            return True

    @api.model
    def remove_kitchen_order_line(self, line):
        if line:
            line = line[0]
            kitchen_pos_lines = self.env['kitchen.pos.order.line'].search([('order_id', '=', line.get('orderid')),('product_id', '=', line.get('productid')), ('product_quantity', '=', line.get('quantity'))],limit=1)
            if kitchen_pos_lines:
                kitchen_pos_lines.sudo().unlink()
    
    @api.model
    def remove_pos_order_line(self, orderid):
        order = self.env["pos.order"].sudo().search([('pos_reference', '=', orderid.get('orderid'))])
        lines_vals = []
        if order:
            for line in order.lines:
                kitchan_order_line = self.env["kitchen.pos.order.line"].sudo().search([('product_id', '=', line.product_id.id),('product_quantity', '=', line.qty),('order_id', '=', order.pos_reference)])
                if not kitchan_order_line:
                    new_values = {
                        'product_id' : line.product_id.id,
                        'qty' : line.qty,
                        'orderid' : orderid.get('orderid')
                    }
                    lines_vals.append(new_values)
                    line.sudo().unlink()
        return lines_vals

    @api.model
    def remove_pos_order_line(self, orderid):
        pos_order = self.env["pos.order"].sudo().search([('pos_reference', '=', orderid.get('orderid'))])
        order_line = pos_order.lines.filtered(lambda line : line.product_id.id == orderid.get('product_id') and line.qty == orderid.get('quantity') and line.order_id.pos_reference == orderid.get('orderid') and line.is_kitchen_line_removed == True)
        if order_line:
            order_line[0].unlink()
            return True
        return False