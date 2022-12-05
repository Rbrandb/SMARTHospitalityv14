/*
 *  Copyright 2019 LevelPrime
 *  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
 */

odoo.define("pos_order_remove_line.Orderline", function (require) {
    "use strict";
    var rpc = require('web.rpc');
    const Orderline = require("point_of_sale.Orderline");
    const Registries = require("point_of_sale.Registries");

    const PosOrderline = (Orderline) =>
        class extends Orderline {
            removeLine() {
                var lines_vals = [{
                    'orderid' : this.env.pos.get_order().name,
                    'quantity' : this.props.line.quantity,
                    'productid' : this.props.line.product.id,
                }]
                rpc.query({
                    model: 'kitchen.pos.order',
                    method: 'remove_kitchen_order_line',
                    args: [lines_vals]
                  }).then(function () {
                  });
                  this.props.line.set_quantity("remove");
            }
        };
    Registries.Component.extend(Orderline, PosOrderline);
    return Orderline;
});
