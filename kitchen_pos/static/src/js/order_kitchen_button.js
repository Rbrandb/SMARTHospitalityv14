odoo.define("kitchen_pos.OrderKitchenButton", function (require) {
  "use strict";

  var rpc = require('web.rpc');
  var core = require('web.core');
  var _t = core._t;
  var PosComponent = require('point_of_sale.PosComponent');
  var ProductScreen = require('point_of_sale.ProductScreen');
  var {
    useListener
  } = require('web.custom_hooks');
  var Registries = require('point_of_sale.Registries');
  
  class OrderKitchenButton extends PosComponent {

    constructor() {
      super(...arguments);
      useListener('click', this.onClick);
    }

    async onClick() {
      var self = this;
      var order_lines = this.env.pos.get_order().get_orderlines();
      var restaurant = this.env.pos.get_order().table;
      var tableInfo = '';
      var orderid = this.env.pos.get_order().name;

      if (restaurant != null) {
        tableInfo = this.env.pos.table.floor.name + ' (' + this.env.pos.table.name + ')';
      }

      if (order_lines.length > 0) {

        var lines = [];
        for (var i = 0; i < order_lines.length; i++) {
          if (order_lines[i].product.kitchen_option || order_lines[i].product.is_pack) {

            var combo_product_details = '';

            if (order_lines[i].product.is_pack) {

              combo_product_details = '<div><small><i>(Combo Product)</i></small></div><div class="font-weight-bold" style="font-size: 12px;">';

              var comboProducts = order_lines[i].get_combo_products();

              if (comboProducts && comboProducts.length > 0){
                for (var j = 0; j < comboProducts.length; j++) {
                    combo_product_details += '<div><small>' + comboProducts[j].display_name + '<span>&#032;</span>' + order_lines[i].quantity + '<span>X</span></small></div>';
                    }
              }


              combo_product_details += '</div>';

            }
            lines.push({
              'product_id': order_lines[i].product.id,
              'product_quantity': order_lines[i].quantity,
              'product_state': order_lines[i].product.food_serve_as[0] == 4 ? 'to go' : 'in progress',
              'food_type': order_lines[i].product.food_type,
              'food_temperature': order_lines[i].product.food_temperature,
              'food_serve_as': order_lines[i].food_serve_as,
              'food_doneness': order_lines[i].food_doneness,
              'table_info': tableInfo,
              'order_id': orderid,
              'cid': order_lines[i].cid,
              'combo_product_details': combo_product_details,
              'unique_line_ref' : order_lines[i].unique_line_ref, 
            })
          }

        }

        if (lines.length > 0) {

          rpc.query({
            model: 'kitchen.pos.order',
            method: 'update_kitchen_order',
            args: [lines]
          }).then(function () {
            $('.order-button').click();
          });

        }

      }

    }

  }

  OrderKitchenButton.template = 'OrderKitchenButton';

  ProductScreen.addControlButton({
    component: OrderKitchenButton,
    condition: function () {
      return true;
    },
  });

  Registries.Component.add(OrderKitchenButton);

  return OrderKitchenButton;

});