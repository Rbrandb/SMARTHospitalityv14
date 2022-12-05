odoo.define('kitchen_pos.PosOrderRemoval', function (require) {
    'use strict';
  
    var rpc = require('web.rpc');
    var session = require('web.session');
    const Orderline = require("point_of_sale.Orderline");
    
    const interval = setInterval(() => {  
        //If lines removed from kitchen then also removing it from here
        if (Orderline.env.pos && Orderline.env.pos.get_order()){
          var order = Orderline.env.pos.get_order()
          for (let j = 0; j < order.get_orderlines().length; j++) {
            var orderid = {
              'orderid' : order.name,
              'product_id' : order.get_orderlines()[j].product.id,
              'quantity' : order.get_orderlines()[j].quantity,
            }
            console.log(orderid)
            rpc.query({
              model: 'kitchen.pos.order',
              method: 'remove_pos_order_line',
              args: [orderid]
            }).then(function (result) {
              console.log(result)
              if (result == true && (order.get_orderlines()[j].product.kitchen_option)){
                order.remove_orderline(order.get_orderlines()[j])
              }
            })
          }
        }
    }, 5000);
  
  });